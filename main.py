"""
main.py

Orquestrador principal para executar os pipelines do projeto BDC em sequência.
"""

import argparse
import sys
from pathlib import Path
from typing import Callable, NamedTuple, Any
from datetime import datetime
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from app.bootstrap import carregar_contexto 

# --- IMPORTS DOS SERVIÇOS ---
from cli import rodar_fichas_comercializadoras
# from cli import rodar_fichas_consumidores

from domain.credito.servico_risco import rodar_pipeline_risco
from domain.credito.servico_fato_analise_credito import construir_fato_analise_credito
from domain.auditoria.servico_auditoria import registrar_inicio_pipeline, registrar_fim_pipeline

# from domain.contratos.servico_contratos_denodo import processar_contratos_denodo
# from domain.contrapartes.servico_enquadramento import calcular_enquadramento_consumidor
# from domain.mtm.servico_mtm import inserir_dados_mtm
# from domain.mtm.servico_denodo_mtm_reconciliacao import executar_reconciliacao_denodo_mtm
# from domain.salesforce.servico_salesforce import inserir_dados_salesforce
# from domain.salesforce.servico_salesforce_reconciliacao import executar_reconciliacao_fichas_salesforce
# from domain.cadastro.servico_receita import inserir_dados_receita
# from domain.garantias.servico_garantia import inserir_dados_garantias
# from domain.carga_manual.servico_carga_manual import inserir_dados_carga_manual
# from domain.credito.servico_override import processar_solicitacao_override
# from gold.service_gold import exportar_visao_consolidada_gold
# from domain.contrapartes.servico_dim_contraparte import criar_dim_contraparte
# from domain.cadastro.servico_bureau import inserir_dados_bureau

def preparar_e_rodar_risco(context):
    mtm_path = context.path("silver") / "mtm_consolidado_silver" / "mtm_agregado_contraparte.parquet"
    df_mtm = pd.read_parquet(mtm_path) if mtm_path.exists() else pd.DataFrame()
    if df_mtm.empty: return
        
    df_fichas = pd.DataFrame()
    for segmento_dir in ["fichas_comercializadoras_extraidas", "fichas_consumidores_extraidas"]:
        seg_path = context.path("silver") / segmento_dir
        if seg_path.exists():
            parquets = list(seg_path.glob("*.parquet"))
            if parquets:
                df_seg = pd.read_parquet(max(parquets, key=lambda f: f.stat().st_mtime))
                df_fichas = pd.concat([df_fichas, df_seg], ignore_index=True)
                
    df_mtm["CNPJ"] = df_mtm["CNPJ"].astype(str).str.zfill(14)
    df_exposicoes = df_mtm.copy()
    
    if not df_fichas.empty and "CNPJ" in df_fichas.columns:
        df_fichas["CNPJ"] = df_fichas["CNPJ"].astype(str).str.zfill(14)
        if "_VERSAO_REGISTRO" in df_fichas.columns:
            df_fichas = df_fichas.sort_values("_VERSAO_REGISTRO").drop_duplicates("CNPJ", keep="last")
        elif "DT_PROCESSAMENTO" in df_fichas.columns:
            df_fichas = df_fichas.sort_values("DT_PROCESSAMENTO").drop_duplicates("CNPJ", keep="last")
            
        cols_ficha = ["CNPJ"]
        if "PD_FINAL" in df_fichas.columns: cols_ficha.append("PD_FINAL")
        if "SEGMENTO_PD" in df_fichas.columns: cols_ficha.append("SEGMENTO_PD")
        df_exposicoes = pd.merge(df_exposicoes, df_fichas[cols_ficha], on="CNPJ", how="left")
        if "SEGMENTO_PD" in df_exposicoes.columns:
            df_exposicoes["SEGMENTO_METODOLOGICO"] = df_exposicoes["SEGMENTO_PD"]
            
    if "PD_FINAL" not in df_exposicoes.columns: df_exposicoes["PD_FINAL"] = None
    if "SEGMENTO_METODOLOGICO" not in df_exposicoes.columns: df_exposicoes["SEGMENTO_METODOLOGICO"] = "NAO_ENQUADRADO"
    return rodar_pipeline_risco(context, df_exposicoes=df_exposicoes)

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

    from domain.contrapartes.servico_dim_contraparte import criar_dim_contraparte
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

# ==============================================================================
# PIPELINE OFICIAL
# ==============================================================================
class PipelineStep(NamedTuple):
    name: str
    func: Callable[[Any], Any]

PIPELINE_STEPS = [
    PipelineStep(name="Fichas Comercializadoras", func=lambda ctx: rodar_fichas_comercializadoras.main()),
    # PipelineStep(name="Fichas Consumidores", func=lambda ctx: run_fichas_consumidores.main()),
    # PipelineStep(name="Ingestão de Contratos (Denodo)", func=ingest_contratos_denodo),
    # PipelineStep(name="Enquadramento de Consumidores", func=lambda ctx: calcular_enquadramento_consumidor(datetime.now().strftime("%Y%m"), ctx)),
    # PipelineStep(name="Ingestão de MtM", func=ingest_mtm_data),
    # PipelineStep(name="Reconciliação Denodo x MtM", func=executar_reconciliacao_denodo_mtm),
    # PipelineStep(name="Ingestão do Salesforce", func=ingest_salesforce_data),
    # PipelineStep(name="Reconciliação Fichas x Salesforce", func=executar_reconciliacao_fichas_salesforce),
    # PipelineStep(name="Ingestão da Receita Federal", func=ingest_receita_data), 
    # PipelineStep(name="Ingestão de Bureau (RISK3)", func=ingest_bureau_data),
    # PipelineStep(name="Ingestão de Garantias", func=ingest_garantias_data),
    # PipelineStep(name="Pipeline de Risco de Crédito", func=preparar_e_rodar_risco),
    # PipelineStep(name="Dimensão Contraparte", func=preparar_dim_contraparte),
    # PipelineStep(name="Fato Análise de Crédito", func=preparar_fato_analise),
    # PipelineStep(name="Carga Manual (Log Eventos)", func=ingest_carga_manual),
    # PipelineStep(name="Solicitações de Override", func=processar_solicitacao_override),
    # PipelineStep(name="Visão Consolidada Gold", func=exportar_visao_consolidada_gold),
]

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--configs-dir", default=str(Path("ENTRADAS") / "configs"))
    args = parser.parse_args()

    try:
        context = carregar_contexto(Path(args.configs_dir))
    except Exception as e:
        print(f"[ERRO CRÍTICO] Falha ao inicializar: {e}")
        return 1

    run_id = f"RUN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    control_dir = context.path("saidas") / "relational" / "control" if hasattr(context, "path") else Path("SAIDAS/relational/control")
    registro_inicio = registrar_inicio_pipeline(run_id, len(PIPELINE_STEPS), control_dir)

    exit_codes = []
    metricas_operacionais = {}
    
    for step in PIPELINE_STEPS:
        try:
            print(f"\n{'=' * 60}\nExecutando Etapa: {step.name}\n{'=' * 60}")
            import inspect
            sig = inspect.signature(step.func)
            if len(sig.parameters) > 0:
                result = step.func(context)
            else:
                result = step.func()
                
            if step.name == "Visão Consolidada Gold" and isinstance(result, dict):
                metricas_operacionais = result
                
            print(f"[OK] '{step.name}' concluído com sucesso.")
            exit_codes.append(0)
        except Exception as e:
            print(f"[ERRO] '{step.name}' falhou com a exceção: {e}")
            import traceback
            traceback.print_exc()
            exit_codes.append(1)
            
            if step.name in ["Ingestão de Contratos (Denodo)", "Reconciliação Denodo x MtM"]:
                print(f"[ERRO FATAL] Interrompendo pipeline devido à falha crítica em '{step.name}'.")
                return 1

    etapas_ok = sum(1 for code in exit_codes if code == 0)
    etapas_falha = sum(1 for code in exit_codes if code != 0)
    registrar_fim_pipeline(registro_inicio, etapas_ok, etapas_falha, control_dir)

    print(f"\n{'=' * 60}\nResumo Final da Execução do Pipeline:")
    for step, code in zip(PIPELINE_STEPS, exit_codes):
        print(f"  - {step.name}: {'OK' if code == 0 else f'FALHOU (código {code})'}")
        
    if metricas_operacionais:
        print(f"\n{'=' * 60}\nRESUMO DA VISÃO OPERACIONAL (MVP DO NEGÓCIO):\n{'=' * 60}")
        print(f"1. Total de Contrapartes detectadas:       {metricas_operacionais.get('total_contrapartes', 0)}")
        print(f"2. Possuem Contrato Vigente:               {metricas_operacionais.get('contrato_vigente', 0)}")
        print(f"3. Possuem Contrato Futuro:                {metricas_operacionais.get('contrato_futuro', 0)}")
        print(f"4. Possuem Análise de Crédito Vigente:     {metricas_operacionais.get('analise_vigente', 0)}")
        print(f"5. Contrato Vigente SEM Análise Vigente (Total): {metricas_operacionais.get('contrato_vig_sem_analise_vig', 0)} ⚠️")
        print(f"   ├─ Irregulares (>= 5 MWm sem DF): {metricas_operacionais.get('contrato_irregular_sem_df', 0)} 🚨 (Exposição Descoberta: R$ {metricas_operacionais.get('ead_descoberto', 0.0):,.2f})")
        print(f"   └─ Pendentes de Bureau (< 5 MWm): {metricas_operacionais.get('contrato_pendente_bureau', 0)} ⏳")
        print(f"6. Possuem Análise Vencida:                {metricas_operacionais.get('analise_vencida', 0)} ⏰ (Requer Revisão)")
        print(f"7. Possuem Ficha mas SEM Contrato:         {metricas_operacionais.get('ficha_sem_contrato', 0)}")
        print(f"8. Possuem Contrato mas NUNCA tiveram Ficha: {metricas_operacionais.get('contrato_sem_ficha', 0)} ⚠️")
        print(f"9. Cadastro Incompleto (Sem Receita Fed.): {metricas_operacionais.get('dados_incompletos', 0)}")
        
        pe_global = pd.read_parquet(context.path("relational_facts") / "fato_exposicao_risco_LATEST.parquet")["PE_REAIS"].sum()
        print(f"10. Perda Esperada (PE) Total da Carteira: R$ {pe_global:,.2f}")

    print(f"{'=' * 60}")

    return 1 if any(code != 0 for code in exit_codes) else 0

if __name__ == "__main__":
    sys.exit(main())