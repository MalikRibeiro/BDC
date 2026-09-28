"""Serviço de geração da visão Gold: Matriz e Histórico de Migração de Rating.

Conforme Seção 7.2 (Item 5) do Planejamento do Sistema BD Crédito.
Enriquece fato_migracao_rating com dados cadastrais e consolida saídas Gold.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from common.identificadores import normalizar_cnpj_coluna
from control.logger import obter_logger


def exportar_visao_migracao_rating_gold(context: Any) -> dict[str, Any]:
    run_id = f"MIGR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = obter_logger("bdc.gold.migracao", Path("LOGS/gold") / f"{run_id}__servico_migracao_rating.log")
    logger.info("Construindo Visão Gold de Migração de Rating...")

    rel_fact_dir = context.path("relational_facts")
    rel_dim_dir = context.path("relational_dimensions")

    path_migr = rel_fact_dir / "credito" / "fato_migracao_rating.parquet"
    if not path_migr.exists():
        logger.warning("Fato Migração de Rating não encontrada em %s. Abortando Gold.", path_migr)
        return {"status": "SEM_FATO_MIGRACAO", "total_migracoes": 0}

    df_migr = pd.read_parquet(path_migr)
    if df_migr.empty:
        logger.info("Fato Migração de Rating vazia (nenhuma migração histórica registrada).")
        return {"status": "SEM_DADOS", "total_migracoes": 0}

    df_migr["CNPJ"] = df_migr["CNPJ"].apply(normalizar_cnpj_coluna)

    # Enriquecer com Dimensão Contraparte
    path_dim = rel_dim_dir / "contrapartes" / "dim_contraparte.parquet"
    if not path_dim.exists():
        path_dim = context.path("saidas") / "relational" / "dimensions" / "dim_contraparte.parquet"

    if path_dim.exists():
        df_dim = pd.read_parquet(path_dim)
        if not df_dim.empty and "CNPJ" in df_dim.columns:
            df_dim["CNPJ"] = df_dim["CNPJ"].apply(normalizar_cnpj_coluna)
            cols_dim = [c for c in ["CNPJ", "NOME", "SIGLA", "GRUPO_ECONOMICO", "SETOR", "SEGMENTO_METODOLOGICO"] if c in df_dim.columns]
            df_migr = pd.merge(df_migr, df_dim[cols_dim].drop_duplicates("CNPJ"), on="CNPJ", how="left")

    gold_dir = context.path("saidas") / "gold" / "visao_migracao_rating"
    gold_dir.mkdir(parents=True, exist_ok=True)

    hoje = datetime.now()
    out_parquet = gold_dir / f"Visao_Migracao_Rating_{hoje.strftime('%Y%m%d')}.parquet"
    out_latest = gold_dir / "Visao_Migracao_Rating_LATEST.parquet"
    out_csv = gold_dir / "Visao_Migracao_Rating_LATEST.csv"

    df_migr.to_parquet(out_parquet, index=False)
    df_migr.to_parquet(out_latest, index=False)
    df_migr.to_csv(out_csv, index=False, sep=";", decimal=",", encoding="utf-8-sig")

    logger.info("Visão Gold de Migração de Rating gerada com sucesso: %d registros.", len(df_migr))
    return {
        "status": "SUCESSO",
        "total_migracoes": len(df_migr),
        "arquivo": str(out_latest),
    }
