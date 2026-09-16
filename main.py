import argparse
import sys
import pandas as pd
import subprocess

from pathlib import Path
from typing import Callable, NamedTuple, Any
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from app.bootstrap import carregar_contexto 
from control.logger import obter_logger

from cli import rodar_fichas_comercializadoras
from cli import rodar_fichas_consumidores

from domain.auditoria.servico_auditoria import registrar_inicio_pipeline, registrar_fim_pipeline
from domain.contratos.servico_contratos_denodo import processar_contratos_denodo
from domain.contrapartes.servico_enquadramento import calcular_enquadramento_consumidor
from domain.mtm.servico_mtm import inserir_dados_mtm
from domain.salesforce.servico_salesforce import inserir_dados_salesforce
from domain.cadastro.servico_receita import inserir_dados_receita
from domain.garantias.servico_garantia import inserir_dados_garantias
from domain.carga_manual.servico_carga_manual import inserir_dados_carga_manual
from domain.credito.servico_override import processar_solicitacao_override
from domain.cadastro.servico_bureau import inserir_dados_bureau
from domain.controlador.servico_controlador import inserir_dados_controladoras
from gold.servico_gold import exportar_visao_consolidada_gold
from relational.facts.fato_exposicao_risco import construir_fato_exposicao_risco
from relational.facts.fato_analise_credito import construir_fato_analise_credito
from relational.facts.fato_reconciliacao_fichas_salesforce import executar_reconciliacao_fichas_salesforce
from relational.dimensions.dim_contraparte import criar_dim_contraparte
from relational.facts.fato_reconciliacao_contrato_mtm import executar_reconciliacao_denodo_mtm
from relational.facts.fato_alertas import gerar_fato_alertas_credito
from relational.facts.fato_alertas_manuais import gerar_fato_alertas_manuais
from relational.facts.fato_garantia import gerar_fato_garantia
from relational.dimensions.dim_contraparte import processar_dim_contraparte
from relational.facts.fato_analise_credito import processar_fato_analise_credito
from relational.facts.fato_exposicao_risco import processar_fato_exposicao_risco
from gold.servico_limites import exportar_arquivo_limites

def rodar_interface_streamlit():
    app_path = PROJECT_ROOT / "src" / "ui" / "app.py"
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", str(app_path)
    ])

class PipelineStep(NamedTuple):
    name: str
    func: Callable[[Any], Any]
    is_critical: bool = False
    allow_degraded: bool = False

PIPELINE_STEPS = [
    # BLOCO 1: INGESTaO CORE E OVERRIDES (ATIVO)
    PipelineStep(name="Fichas Comercializadoras", func=lambda ctx: rodar_fichas_comercializadoras.main()),
    PipelineStep(name="Fichas Consumidores", func=lambda ctx: rodar_fichas_consumidores.main()),
    
    # BLOCO 2: APIS EXTERNAS E CONECTORES
    PipelineStep(name="Ingestao de Contratos (Denodo)", func=processar_contratos_denodo, is_critical=True),
    PipelineStep(name="Enquadramento de Consumidores", func=lambda ctx: calcular_enquadramento_consumidor(datetime.now().strftime("%Y%m"), ctx)),
    PipelineStep(name="Ingestao de MtM", func=inserir_dados_mtm),
    PipelineStep(name="Ingestao do Salesforce", func=inserir_dados_salesforce),
    PipelineStep(name="Ingestao da Receita Federal", func=inserir_dados_receita), 
    PipelineStep(name="Ingestao de Bureau (RISK3)", func=inserir_dados_bureau),
    PipelineStep(name="Ingestao de Controladoras", func=inserir_dados_controladoras, allow_degraded=True),
    PipelineStep(name="Ingestao de Garantias", func=inserir_dados_garantias),
    PipelineStep(name="Solicitacoes de Override", func=processar_solicitacao_override),
    PipelineStep(name="Carga Manual (Eventos e Overrides)", func=lambda ctx: inserir_dados_carga_manual(ctx)),

    # BLOCO 3: MOTOR DE CRÉDITO E CAMADAS RELACIONAIS
    PipelineStep(name="Dimensao Contraparte", func=processar_dim_contraparte),
    PipelineStep(name="Fato Analise de Credito", func=processar_fato_analise_credito),
    PipelineStep(name="Fato Garantia", func=gerar_fato_garantia),
    PipelineStep(name="Fato Exposicao de Risco", func=processar_fato_exposicao_risco),
    PipelineStep(name="Fato Reconciliacao Denodo x MtM", func=executar_reconciliacao_denodo_mtm, is_critical=True),
    PipelineStep(name="Fato Reconciliacao Fichas x Salesforce", func=executar_reconciliacao_fichas_salesforce),
    PipelineStep(name="Alertas de Carga Manual e Exceções", func=gerar_fato_alertas_manuais),
    PipelineStep(name="Visao Consolidada Gold", func=exportar_visao_consolidada_gold),
    PipelineStep(name="Fato Alertas de Credito", func=gerar_fato_alertas_credito),
    PipelineStep(name="Exportacao de Limites", func=exportar_arquivo_limites),

    # BLOCO 4: INTERFACE
    PipelineStep(name="Interface Streamlit", func=lambda ctx: rodar_interface_streamlit()),
]
def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--configs-dir", default=str(Path("ENTRADAS") / "configs"))
    parser.add_argument("--ui", action="store_true", help="Abre apenas a interface, sem rodar o pipeline")
    parser.add_argument("--no-ui", action="store_true", help="Roda apenas o pipeline, sem abrir a interface no final")
    args = parser.parse_args()

    if args.ui:
        rodar_interface_streamlit()
        return 0

    try:
        context = carregar_contexto(Path(args.configs_dir))
    except Exception as e:
        print(f"[ERRO CRÍTICO] Falha ao inicializar: {e}")
        return 1

    run_id = f"RUN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger_runner = obter_logger("bdc.runner", context.path("log_runner") / f"{run_id}__orquestrador_principal.log")

    control_dir = context.path("saidas") / "relational" / "control" if hasattr(context, "path") else Path("SAIDAS/relational/control")
    registro_inicio = registrar_inicio_pipeline(run_id, len(PIPELINE_STEPS), control_dir)

    exit_codes = []
    metricas_operacionais = {}
    
    for step in PIPELINE_STEPS:
        try:
            logger_runner.info(f"\n{'=' * 60}\nExecutando Etapa: {step.name}\n{'=' * 60}")
            
            result = step.func(context)
                
            logger_runner.info(f"[OK] '{step.name}' concluido com sucesso.")
            exit_codes.append(0)
            
        except Exception as e:
            if step.allow_degraded:
                logger_runner.warning(
                    f"[DEGRADADO] A etapa '{step.name}' falhou. "
                    f"O pipeline operará em modo degradado. Erro: {e}"
                )
                exit_codes.append(1)
                continue
                
            logger_runner.error(f"[ERRO] '{step.name}' falhou com a excecao: {e}", exc_info=True)
            exit_codes.append(1)
            
            if step.is_critical:
                logger_runner.error(f"[ERRO FATAL] Interrompendo pipeline devido a falha critica em '{step.name}'.")
                return 1

    etapas_ok = sum(1 for code in exit_codes if code == 0)
    etapas_falha = sum(1 for code in exit_codes if code != 0)
    registrar_fim_pipeline(registro_inicio, etapas_ok, etapas_falha, control_dir)

    logger_runner.info(f"\n{'=' * 60}\nResumo Final da Execucao do Pipeline:")
    for step, code in zip(PIPELINE_STEPS, exit_codes):
        logger_runner.info(f"  - {step.name}: {'OK' if code == 0 else f'FALHOU (codigo {code})'}")
        
    logger_runner.info(f"{'=' * 60}")

    return 1 if any(code != 0 for code in exit_codes) else 0

if __name__ == "__main__":
    sys.exit(main())