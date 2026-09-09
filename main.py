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
from gold.servico_gold import exportar_visao_consolidada_gold
from relational.facts.fato_exposicao_risco import construir_fato_exposicao_risco
from relational.facts.fato_analise_credito import construir_fato_analise_credito
from relational.facts.fato_reconciliacao_fichas_salesforce import executar_reconciliacao_fichas_salesforce
from relational.dimensions.dim_contraparte import criar_dim_contraparte
from relational.facts.fato_reconciliacao_contrato_mtm import executar_reconciliacao_denodo_mtm
from relational.facts.fato_alertas import gerar_fato_alertas_credito
from relational.facts.fato_garantia import gerar_fato_garantia


def rodar_interface_streamlit():
    app_path = PROJECT_ROOT / "src" / "ui" / "app.py"
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", str(app_path)
    ])

def preparar_e_rodar_risco(context):
    mtm_path = context.path("silver") / "mtm_consolidado_silver" / "mtm_agregado_contraparte.parquet"
    df_mtm = pd.read_parquet(mtm_path) if mtm_path.exists() else pd.DataFrame()
    if df_mtm.empty: return
        
    fato_path = context.path("relational_facts") / "fato_analise_credito.parquet"
    df_fichas = pd.read_parquet(fato_path) if fato_path.exists() else pd.DataFrame()

    df_mtm["CNPJ"] = df_mtm["CNPJ"].astype(str).str.zfill(14)
    df_exposicoes = df_mtm.copy()
    
    if not df_fichas.empty and "CNPJ" in df_fichas.columns:
        df_fichas["CNPJ"] = df_fichas["CNPJ"].astype(str).str.zfill(14)
        if "DATA_ANALISE" in df_fichas.columns:
            df_fichas = df_fichas.sort_values("DATA_ANALISE").drop_duplicates("CNPJ", keep="last")
            
        cols_ficha = ["CNPJ"]
        if "PD_PERCENTUAL" in df_fichas.columns: cols_ficha.append("PD_PERCENTUAL")
        if "SEGMENTO_METODOLOGICO_FICHA" in df_fichas.columns: cols_ficha.append("SEGMENTO_METODOLOGICO_FICHA")
        
        df_exposicoes = pd.merge(df_exposicoes, df_fichas[cols_ficha], on="CNPJ", how="left")
        
        if "PD_PERCENTUAL" in df_exposicoes.columns:
            df_exposicoes["PD_FINAL"] = df_exposicoes["PD_PERCENTUAL"]
        if "SEGMENTO_METODOLOGICO_FICHA" in df_exposicoes.columns:
            df_exposicoes["SEGMENTO_METODOLOGICO"] = df_exposicoes["SEGMENTO_METODOLOGICO_FICHA"]
            
    if "PD_FINAL" not in df_exposicoes.columns: df_exposicoes["PD_FINAL"] = None
    if "SEGMENTO_METODOLOGICO" not in df_exposicoes.columns: df_exposicoes["SEGMENTO_METODOLOGICO"] = "NAO_ENQUADRADO"
    
    return construir_fato_exposicao_risco(context, df_exposicoes=df_exposicoes)

def preparar_dim_contraparte(context):
    receita_path = context.path("silver") / "receita_silver" / "receita_cadastral_silver.parquet"
    enquadra_path = context.path("relational_configs") / f"enquadramento_consumidores_{datetime.now().strftime('%Y%m')}.csv"
    salesforce_path = context.path("silver") / "salesforce_silver" / "account" / "salesforce_account.parquet"
    
    df_receita = pd.read_parquet(receita_path) if receita_path.exists() else pd.DataFrame()
    df_seg = pd.read_csv(enquadra_path) if enquadra_path.exists() else pd.DataFrame()
    df_sf_account = pd.read_parquet(salesforce_path) if salesforce_path.exists() else pd.DataFrame()
    
    df_fichas = pd.DataFrame()
    for segmento_dir in ["fichas_comercializadoras_extraidas", "fichas_consumidores_extraidas"]:
        seg_path = context.path("silver") / segmento_dir
        if seg_path.exists():
            parquets = list(seg_path.glob("*.parquet"))
            if parquets:
                df_seg_fichas = pd.read_parquet(max(parquets, key=lambda f: f.stat().st_mtime))
                df_fichas = pd.concat([df_fichas, df_seg_fichas], ignore_index=True)

    from relational.dimensions.dim_contraparte import criar_dim_contraparte
    return criar_dim_contraparte(
        context, 
        df_silver_receita=df_receita, 
        df_silver_segmentacao=df_seg,
        df_silver_salesforce_account=df_sf_account,
        df_silver_fichas=df_fichas
    )
    
def preparar_fato_analise(context):
    df_fichas = pd.DataFrame()
    for segmento_dir in ["fichas_comercializadoras_extraidas", "fichas_consumidores_extraidas"]:
        seg_path = context.path("silver") / segmento_dir
        if seg_path.exists():
            parquets = list(seg_path.glob("*.parquet"))
            if parquets:
                df_seg = pd.read_parquet(max(parquets, key=lambda f: f.stat().st_mtime))
                df_fichas = pd.concat([df_fichas, df_seg], ignore_index=True)
                
    dim_path = context.path("relational_dimensions") / "dim_contraparte.parquet"
    if not dim_path.exists():
        dim_path = context.path("saidas") / "relational" / "dimensions" / "dim_contraparte.parquet"
    df_dim = pd.read_parquet(dim_path) if dim_path.exists() else pd.DataFrame()
    return construir_fato_analise_credito(context, df_silver_analises=df_fichas, df_dim_contraparte=df_dim)

class PipelineStep(NamedTuple):
    name: str
    func: Callable[[Any], Any]

PIPELINE_STEPS = [
    # BLOCO 1: INGESTaO CORE E OVERRIDES (ATIVO)
    PipelineStep(name="Fichas Comercializadoras", func=lambda ctx: rodar_fichas_comercializadoras.main()),
    # PipelineStep(name="Fichas Consumidores", func=lambda ctx: rodar_fichas_consumidores.main()),
    
    # BLOCO 2: APIS EXTERNAS E CONECTORES
    # PipelineStep(name="Ingestao de Contratos (Denodo)", func=processar_contratos_denodo),
    # PipelineStep(name="Enquadramento de Consumidores", func=lambda ctx: calcular_enquadramento_consumidor(datetime.now().strftime("%Y%m"), ctx)),
    # PipelineStep(name="Ingestao de MtM", func=inserir_dados_mtm),
    # PipelineStep(name="Ingestao do Salesforce", func=inserir_dados_salesforce),
    # PipelineStep(name="Ingestao da Receita Federal", func=inserir_dados_receita), 
    # PipelineStep(name="Ingestao de Bureau (RISK3)", func=inserir_dados_bureau),
    # PipelineStep(name="Ingestao de Garantias", func=inserir_dados_garantias),
    # PipelineStep(name="Solicitacoes de Override", func=processar_solicitacao_override),
    # PipelineStep(name="Carga Manual (Eventos e Overrides)", func=lambda ctx: inserir_dados_carga_manual(ctx)),

    # BLOCO 3: MOTOR DE CRÉDITO E CAMADAS RELACIONAIS
    # PipelineStep(name="Dimensao Contraparte", func=preparar_dim_contraparte),
    # PipelineStep(name="Fato Analise de Credito", func=preparar_fato_analise),
    # PipelineStep(name="Fato Garantia", func=gerar_fato_garantia),
    # PipelineStep(name="Fato Exposicao de Risco", func=preparar_e_rodar_risco),
    # PipelineStep(name="Fato Reconciliacao Denodo x MtM", func=executar_reconciliacao_denodo_mtm),
    # PipelineStep(name="Fato Reconciliacao Fichas x Salesforce", func=executar_reconciliacao_fichas_salesforce),
    # PipelineStep(name="Fato Alertas de Credito", func=gerar_fato_alertas_credito),

    # PipelineStep(name="Visao Consolidada Gold", func=exportar_visao_consolidada_gold),

    # BLOCO 4: INTERFACE
    # PipelineStep(name="Interface Streamlit", func=lambda ctx: rodar_interface_streamlit()),
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
            import inspect
            sig = inspect.signature(step.func)
            if len(sig.parameters) > 0:
                result = step.func(context)
            else:
                result = step.func()
                
            if step.name == "Visao Consolidada Gold" and isinstance(result, dict):
                metricas_operacionais = result
                
            logger_runner.info(f"[OK] '{step.name}' concluido com sucesso.")
            exit_codes.append(0)
        except Exception as e:
            logger_runner.error(f"[ERRO] '{step.name}' falhou com a excecao: {e}", exc_info=True)
            exit_codes.append(1)
            
            if step.name in ["Ingestao de Contratos (Denodo)", "Reconciliacao Denodo x MtM"]:
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