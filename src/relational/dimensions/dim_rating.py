"""Serviço de materialização da Dimensão de Rating.

Conforme a Seção 7.4 do Planejamento v1.2:
- A fonte de verdade canônica permanece única em ENTRADAS/control/configs/pd_faixas.json.
- A tabela relacional dim_rating.parquet é gerada automaticamente pelo pipeline para
  consumo analítico direto pelo Power BI e consultas SQL.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from app.context import AppContext
from control.logger import obter_logger
from common.json import ler_json


ORDEM_MAPA = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "ISENTO_INTERCOMPANY": 98, "N/A": 99}
CLASSE_MAPA = {
    "A": "BAIXO",
    "B": "BAIXO",
    "C": "MEDIO",
    "D": "ALTO",
    "E": "CRITICO",
    "F": "CRITICO",
    "ISENTO_INTERCOMPANY": "ISENTO",
    "N/A": "ISENTO"
}


def processar_dim_rating(context: AppContext) -> dict[str, Any]:
    """Orquestra a leitura de pd_faixas.json e materialização de dim_rating.parquet."""
    run_id = f"DIM_RAT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = obter_logger("bdc.dim_rating", Path("LOGS/relational") / f"{run_id}__dim_rating.log")
    logger.info("Iniciando materialização da Dimensão de Rating (run_id=%s)...", run_id)

    try:
        caminho_faixas = context.path("control") / "configs" / "pd_faixas.json"
    except Exception:
        caminho_faixas = Path("ENTRADAS/control/configs/pd_faixas.json")
    if not caminho_faixas.exists():
        caminho_faixas = Path("ENTRADAS/control/configs/pd_faixas.json")

    if not caminho_faixas.exists():
        logger.error("Arquivo pd_faixas.json não encontrado em: %s", caminho_faixas)
        return {"run_id": run_id, "linhas": 0, "status": "ERRO_ARQUIVO_INEXISTENTE"}

    dados_faixas = ler_json(caminho_faixas)
    registros = []

    for segmento, ratings in dados_faixas.items():
        if not isinstance(ratings, dict):
            continue
        for rating, faixa in ratings.items():
            if not isinstance(faixa, dict):
                continue
            r_str = str(rating).strip().upper()
            pd_min = float(faixa.get("min", 0.0))
            pd_max = float(faixa.get("max", 1.0))
            ordem = ORDEM_MAPA.get(r_str, 99)
            classe = CLASSE_MAPA.get(r_str, "INDEFINIDO")

            registros.append({
                "RATING_KEY": f"{segmento}_{r_str}",
                "SEGMENTO_METODOLOGICO": segmento,
                "RATING": r_str,
                "ORDEM_RATING": ordem,
                "PD_MIN": pd_min,
                "PD_MAX": pd_max,
                "CLASSE_RISCO": classe,
                "VERSAO_REGRA": "NT_v7",
                "DATA_MATERIALIZACAO": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "_STATUS_REGISTRO": "VIGENTE"
            })

    df_rating = pd.DataFrame(registros)
    if not df_rating.empty:
        df_rating = df_rating.sort_values(by=["SEGMENTO_METODOLOGICO", "ORDEM_RATING"]).reset_index(drop=True)

    relational_dir = context.path("relational_dimensions") / "ratings"
    relational_dir.mkdir(parents=True, exist_ok=True)

    # Persistência em Parquet e CSV para suporte total ao Power BI
    parquet_path = relational_dir / "dim_rating.parquet"
    csv_path = relational_dir / "dim_rating.csv"
    
    df_rating.to_parquet(parquet_path, index=False)
    df_rating.to_csv(csv_path, sep=";", index=False, encoding="utf-8-sig")

    # Materialização da Escala Canônica de Rating (Chave primária única de 1 linha por nota para relacionamentos 1:N no Power BI)
    escalas = [
        {"RATING": "A", "ORDEM_RATING": 1, "CLASSE_RISCO": "BAIXO", "DESCRICAO": "Risco Muito Baixo"},
        {"RATING": "B", "ORDEM_RATING": 2, "CLASSE_RISCO": "BAIXO", "DESCRICAO": "Risco Baixo"},
        {"RATING": "C", "ORDEM_RATING": 3, "CLASSE_RISCO": "MEDIO", "DESCRICAO": "Risco Médio"},
        {"RATING": "D", "ORDEM_RATING": 4, "CLASSE_RISCO": "ALTO", "DESCRICAO": "Risco Alto"},
        {"RATING": "E", "ORDEM_RATING": 5, "CLASSE_RISCO": "CRITICO", "DESCRICAO": "Risco Crítico / Default"},
        {"RATING": "F", "ORDEM_RATING": 6, "CLASSE_RISCO": "CRITICO", "DESCRICAO": "Risco Crítico / Default"},
        {"RATING": "ISENTO_INTERCOMPANY", "ORDEM_RATING": 98, "CLASSE_RISCO": "ISENTO", "DESCRICAO": "Operações Intragrupo Isentas de Risco"},
        {"RATING": "N/A", "ORDEM_RATING": 99, "CLASSE_RISCO": "ISENTO", "DESCRICAO": "Não Aplicável / Outros"}
    ]
    df_escala = pd.DataFrame(escalas)
    df_escala.to_parquet(relational_dir / "dim_escala_rating.parquet", index=False)
    df_escala.to_csv(relational_dir / "dim_escala_rating.csv", sep=";", index=False, encoding="utf-8-sig")

    logger.info("Dimensões Rating e Escala Rating materializadas com sucesso em %s.", relational_dir)
    return {"run_id": run_id, "linhas": len(df_rating), "status": "SUCESSO"}
