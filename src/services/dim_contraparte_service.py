"""Construção da dimensão de Contrapartes (dim_contraparte)."""
from __future__ import annotations
import logging
from datetime import datetime
from typing import Any
import pandas as pd
from app.context import AppContext
from storage.silver_store import write_silver_dataset

def build_dim_contraparte(context: AppContext, df_silver_receita: pd.DataFrame, df_silver_segmentacao: pd.DataFrame) -> dict[str, Any]:
    run_id = f"DIM_CTR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = logging.getLogger("bdc.gold.dim_contraparte")

    if df_silver_receita.empty:
        df_silver_receita = pd.DataFrame(columns=["CNPJ", "SITUACAO_CADASTRAL", "NATUREZA_JURIDICA", "CNAE_PRINCIPAL"])
    if df_silver_segmentacao.empty:
        df_silver_segmentacao = pd.DataFrame(columns=["CNPJ", "VOLUME_ENQUADRAMENTO_MWM", "POSSUI_PELO_MENOS_5_MWM", "SEGMENTO_METODOLOGICO"])

    # NORMALIZAÇÃO ESTRITA
    df_silver_receita["CNPJ"] = df_silver_receita["CNPJ"].astype(str).str.replace(r"\D", "", regex=True).str.zfill(14)
    df_silver_segmentacao["CNPJ"] = df_silver_segmentacao["CNPJ"].astype(str).str.replace(r"\D", "", regex=True).str.zfill(14)

    for col in ["SITUACAO_CADASTRAL", "CNAE_PRINCIPAL"]:
        if col not in df_silver_receita.columns: df_silver_receita[col] = "NAO_INFORMADO"
    for col in ["SEGMENTO_METODOLOGICO"]:
        if col not in df_silver_segmentacao.columns: df_silver_segmentacao[col] = "NAO_ENQUADRADO"

    # OUTER JOIN PARA SALVAR O SEGMENTO MESMO SEM RECEITA FEDERAL
    df_dim = pd.merge(df_silver_receita, df_silver_segmentacao, on="CNPJ", how="outer")
    df_dim = df_dim.dropna(subset=["CNPJ"])
    
    df_dim["CNPJ_RAIZ"] = df_dim["CNPJ"].str[:8]
    df_dim["SITUACAO_CADASTRAL"] = df_dim["SITUACAO_CADASTRAL"].fillna("NAO_INFORMADO")
    df_dim["SEGMENTO_METODOLOGICO"] = df_dim["SEGMENTO_METODOLOGICO"].fillna("NAO_ENQUADRADO")

    schema_dim = {"CNPJ": "CNPJ", "CNPJ_RAIZ": "CNPJ_RAIZ", "SITUACAO_CADASTRAL": "SITUACAO_CADASTRAL", "CNAE_PRINCIPAL": "SETOR", "SEGMENTO_METODOLOGICO": "SEGMENTO_METODOLOGICO"}
    df_final = df_dim[list(schema_dim.keys())].rename(columns=schema_dim).copy()
    
    relational_dir = context.path("relational_dimensions")
    relational_dir.mkdir(parents=True, exist_ok=True)
    write_silver_dataset(records=df_final.to_dict(orient="records"), output_dir=relational_dir, filename="dim_contraparte")
    return {"run_id": run_id, "linhas": len(df_final), "status": "SUCESSO"}