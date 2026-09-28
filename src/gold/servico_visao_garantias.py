"""Serviço de geração da visão Gold: Relatório Consolidado de Garantias.

Conforme Seção 7.2 (Item 7) do Planejamento do Sistema BD Crédito.
Consolida garantias vinculadas, prazos, vencimentos, cobertura e status.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from common.identificadores import normalizar_cnpj_coluna
from control.logger import obter_logger


def exportar_visao_garantias_gold(context: Any) -> dict[str, Any]:
    run_id = f"V_GAR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = obter_logger("bdc.gold.garantias", Path("LOGS/gold") / f"{run_id}__servico_visao_garantias.log")
    logger.info("Construindo Visão Gold de Garantias...")

    rel_fact_dir = context.path("relational_facts")
    rel_dim_dir = context.path("relational_dimensions")

    path_gar = rel_fact_dir / "garantias" / "fato_garantia.parquet"
    if not path_gar.exists():
        path_gar = rel_fact_dir / "credito" / "fato_garantia.parquet"

    if not path_gar.exists():
        logger.warning("Fato Garantia não encontrada em %s. Abortando Gold.", path_gar)
        return {"status": "SEM_FATO_GARANTIA", "total_garantias": 0}

    df_gar = pd.read_parquet(path_gar)
    if df_gar.empty:
        logger.info("Fato Garantia vazia.")
        return {"status": "SEM_DADOS", "total_garantias": 0}

    col_cnpj = "CNPJ_CONTRAPARTE" if "CNPJ_CONTRAPARTE" in df_gar.columns else "CNPJ"
    if col_cnpj in df_gar.columns:
        df_gar["CNPJ"] = df_gar[col_cnpj].apply(normalizar_cnpj_coluna)

    # Enriquecer com Dimensão Contraparte
    path_dim = rel_dim_dir / "contrapartes" / "dim_contraparte.parquet"
    if not path_dim.exists():
        path_dim = context.path("saidas") / "relational" / "dimensions" / "dim_contraparte.parquet"

    if path_dim.exists() and "CNPJ" in df_gar.columns:
        df_dim = pd.read_parquet(path_dim)
        if not df_dim.empty and "CNPJ" in df_dim.columns:
            df_dim["CNPJ"] = df_dim["CNPJ"].apply(normalizar_cnpj_coluna)
            cols_dim = [c for c in ["CNPJ", "NOME", "SIGLA", "GRUPO_ECONOMICO"] if c in df_dim.columns]
            df_gar = pd.merge(df_gar, df_dim[cols_dim].drop_duplicates("CNPJ"), on="CNPJ", how="left")

    gold_dir = context.path("saidas") / "gold" / "visao_garantias"
    gold_dir.mkdir(parents=True, exist_ok=True)

    hoje = datetime.now()
    out_parquet = gold_dir / f"Visao_Garantias_{hoje.strftime('%Y%m%d')}.parquet"
    out_latest = gold_dir / "Visao_Garantias_LATEST.parquet"
    out_csv = gold_dir / "Visao_Garantias_LATEST.csv"

    df_gar.to_parquet(out_parquet, index=False)
    df_gar.to_parquet(out_latest, index=False)
    df_gar.to_csv(out_csv, index=False, sep=";", decimal=",", encoding="utf-8-sig")

    logger.info("Visão Gold de Garantias gerada com sucesso: %d registros.", len(df_gar))
    return {
        "status": "SUCESSO",
        "total_garantias": len(df_gar),
        "arquivo": str(out_latest),
    }
