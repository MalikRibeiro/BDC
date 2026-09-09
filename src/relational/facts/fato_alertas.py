"""Serviço de geração de alertas de crédito no padrão Star Schema (Fato Alerta)."""
import pandas as pd
from datetime import datetime
from typing import Any

from pathlib import Path
from control.logger import obter_logger
from storage.escrever_dados import escrever_conjunto_de_dados_silver

def gerar_fato_alertas_credito(context: Any) -> dict[str, Any]:
    run_id = f"ALERT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = obter_logger("bdc.alertas", Path("LOGS/relacional") / f"{run_id}__servico_alertas.log")
    logger.info("Iniciando geração da Fato Alerta de Crédito (Star Schema)...")

    colunas_exigidas = [
        "CNPJ", "CODIGO_ALERTA", "SEVERIDADE", "REGRA", "MENSAGEM_DESCRITIVA", 
        "DATA_DETECCAO", "CAMPO_AFETADO", "VALOR_OBSERVADO", "LIMITE_ESPERADO", 
        "STATUS_TRATAMENTO", "RESPONSAVEL", "EVIDENCIA_ENCERRAMENTO"
    ]

    path_gold = context.path("saidas") / "gold" / "visao_operacional_negocio" / "Visao_Operacional_BDC_LATEST.parquet"
    if not path_gold.exists():
        logger.warning(f"Base Gold LATEST não encontrada em {path_gold}. Abortando alertas.")
        return {"run_id": run_id, "alertas_gerados": 0, "status": "SEM_BASE"}

    df_gold = pd.read_parquet(path_gold)
    
    alertas = []
    agora = datetime.now()

    for _, row in df_gold.iterrows():
        cnpj = row.get("CNPJ")
        if pd.isna(cnpj) or not str(cnpj).strip():
            continue
            
        status_contratual = str(row.get("STATUS_CONTRATUAL", ""))
        sit_analise = str(row.get("SITUACAO_ANALISE", ""))
        metodologia = str(row.get("METODOLOGIA_EXIGIDA", ""))
        vol_mwm = pd.to_numeric(row.get("VOLUME_MWM"), errors="coerce")
        if pd.isna(vol_mwm): vol_mwm = 0.0

        if status_contratual == "CONTRATO_VIGENTE" and sit_analise == "VENCIDA":
            alertas.append({
                "CNPJ": cnpj,
                "CODIGO_ALERTA": "ANA_001",
                "SEVERIDADE": "ALTO",
                "REGRA": "Análise Vencida com Contrato Vigente",
                "MENSAGEM_DESCRITIVA": "A contraparte possui contrato ativo, mas sua análise de crédito encontra-se expirada.",
                "DATA_DETECCAO": agora,
                "CAMPO_AFETADO": "SITUACAO_ANALISE",
                "VALOR_OBSERVADO": sit_analise,
                "LIMITE_ESPERADO": "VIGENTE",
                "STATUS_TRATAMENTO": pd.NA,
                "RESPONSAVEL": pd.NA,
                "EVIDENCIA_ENCERRAMENTO": pd.NA
            })

        if status_contratual == "CONTRATO_VIGENTE" and metodologia == "DF_DETALHADA" and sit_analise != "VIGENTE":
            alertas.append({
                "CNPJ": cnpj,
                "CODIGO_ALERTA": "SEG_001",
                "SEVERIDADE": "CRITICO",
                "REGRA": ">= 5MWm sem DF ou Irregular",
                "MENSAGEM_DESCRITIVA": "Volume exige demonstração financeira (>= 5 MWm), mas análise não está vigente.",
                "DATA_DETECCAO": agora,
                "CAMPO_AFETADO": "METODOLOGIA_EXIGIDA",
                "VALOR_OBSERVADO": f"Volume: {vol_mwm:.2f} MWm",
                "LIMITE_ESPERADO": "DF Vigente",
                "STATUS_TRATAMENTO": pd.NA,
                "RESPONSAVEL": pd.NA,
                "EVIDENCIA_ENCERRAMENTO": pd.NA
            })

        if status_contratual == "CONTRATO_VIGENTE" and metodologia == "BUREAU" and sit_analise != "VIGENTE":
            alertas.append({
                "CNPJ": cnpj,
                "CODIGO_ALERTA": "SEG_002",
                "SEVERIDADE": "MEDIO",
                "REGRA": "< 5MWm sem Bureau",
                "MENSAGEM_DESCRITIVA": "Volume permite Bureau (< 5 MWm), mas não há análise vigente.",
                "DATA_DETECCAO": agora,
                "CAMPO_AFETADO": "METODOLOGIA_EXIGIDA",
                "VALOR_OBSERVADO": f"Volume: {vol_mwm:.2f} MWm",
                "LIMITE_ESPERADO": "Bureau Vigente",
                "STATUS_TRATAMENTO": pd.NA,
                "RESPONSAVEL": pd.NA,
                "EVIDENCIA_ENCERRAMENTO": pd.NA
            })

    if alertas:
        df_alertas = pd.DataFrame(alertas)
    else:
        df_alertas = pd.DataFrame(columns=colunas_exigidas)
        
    df_alertas = df_alertas[colunas_exigidas]

    out_dir = context.path("relational_facts") / "alertas"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_parquet = out_dir / "fato_alerta_credito.parquet"
    
    df_alertas.to_parquet(out_parquet, index=False)
    
    escrever_conjunto_de_dados_silver(
        records=df_alertas.to_dict(orient="records"), 
        output_dir=out_dir, 
        filename="fato_alerta_credito"
    )

    logger.info(f"Fato Alerta gerada com sucesso. Total de alertas: {len(df_alertas)}")
    
    return {
        "status": "SUCESSO",
        "total_alertas": len(df_alertas)
    }
