"""Construção da tabela Fato de Análise de Crédito (fato_analise_credito)."""
from __future__ import annotations
import logging
from datetime import datetime
from typing import Any
import pandas as pd
from app.context import AppContext
from storage.escrever_dados import escrever_conjunto_de_dados_silver

def construir_fato_analise_credito(
    context: AppContext,
    df_silver_analises: pd.DataFrame,
    df_dim_contraparte: pd.DataFrame,
) -> dict[str, Any]:
    run_id = f"FATO_ANL_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = logging.getLogger("bdc.gold.fato_analise_credito")
    logger.info("Iniciando carga de fato_analise_credito (run_id=%s).", run_id)

    if df_silver_analises.empty:
        return {"run_id": run_id, "linhas": 0, "status": "SEM_DADOS"}

    df_fato = df_silver_analises.copy()
    df_fato["CNPJ"] = df_fato["CNPJ"].astype(str).str.replace(r"\D", "", regex=True).str.zfill(14)

    # CORREÇÃO DOS MAPEAMENTOS DA FONTE
    if "DATA_CALCULO" in df_fato.columns and "DATA_ANALISE" not in df_fato.columns:
        df_fato["DATA_ANALISE"] = df_fato["DATA_CALCULO"]
    if "RATING_FINAL" not in df_fato.columns and "RATING_COPEL" in df_fato.columns:
        df_fato["RATING_FINAL"] = df_fato["RATING_COPEL"]
    if "MODELO_METODOLOGICO" not in df_fato.columns and "versao_ficha" in df_fato.columns:
        df_fato["MODELO_METODOLOGICO"] = df_fato["versao_ficha"]
        
    # Adicionando PATRIMONIO_LIQUIDO, SITUACAO_DF e SITUACAO_ANALISE na lista de colunas esperadas
    for col in ["ANALISE_ID", "DATA_ANALISE", "RATING_FINAL", "PD_FINAL", "SCORE_CALCULADO", "CLASSE_RISCO", "MODELO_METODOLOGICO", "DATA_DEMONSTRACAO_FINANCEIRA", "SEGMENTO_PD", "TIPO_FICHA", "PATRIMONIO_LIQUIDO", "SITUACAO_DF", "SITUACAO_ANALISE"]:
        if col not in df_fato.columns: df_fato[col] = None

    rename_map = {
        "CNPJ": "CNPJ", "DATA_ANALISE": "DATA_ANALISE", "RATING_FINAL": "RATING",
        "PD_FINAL": "PD_PERCENTUAL", "SCORE_CALCULADO": "SCORE", "CLASSE_RISCO": "CLASSE",
        "MODELO_METODOLOGICO": "MODELO", "DATA_DEMONSTRACAO_FINANCEIRA": "DATA_BALANCO_USADO",
        "SEGMENTO_PD": "SEGMENTO_METODOLOGICO_FICHA", "TIPO_FICHA": "TIPO_FICHA",
        "PATRIMONIO_LIQUIDO": "PATRIMONIO_LIQUIDO", "SITUACAO_DF": "SITUACAO_DF",
        "SITUACAO_ANALISE": "SITUACAO_ANALISE"
    }
    
    # Previne KeyError garantindo que só renomeia o que existe
    df_final = df_fato[[c for c in rename_map.keys() if c in df_fato.columns]].rename(columns=rename_map).copy()
    
    df_final["ETL_RUN_ID"] = run_id
    relational_dir = context.path("relational_facts")
    relational_dir.mkdir(parents=True, exist_ok=True)
    escrever_conjunto_de_dados_silver(records=df_final.to_dict(orient="records"), output_dir=relational_dir, filename="fato_analise_credito")
    return {"run_id": run_id, "linhas": len(df_final), "status": "SUCESSO"}