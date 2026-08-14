"""Serviço de cálculo do volume de enquadramento (≥ 5 MWm) para consumidores."""

from __future__ import annotations

import pandas as pd
from pathlib import Path
from typing import Any

from app.context import AppContext


def calcular_enquadramento_consumidor(
    competencia_base: str,
    context: AppContext,
) -> pd.DataFrame:
    """
    Lê os contratos normalizados da Silver do Denodo, calcula o maior volume mensal
    simultâneo por CNPJ e retorna a base consolidada de enquadramento.
    """
    silver_dir = context.path("silver") / "denodo_contratos_padronizados"
    parquet_path = silver_dir / f"contratos_correntes_{competencia_base}.parquet"

    if not parquet_path.exists():
        raise FileNotFoundError(
            f"Base Silver de contratos do Denodo não encontrada para a competência {competencia_base} em: {parquet_path}. "
            "Execute a ingestão (T2.1.2) primeiro."
        )

    df_contratos = pd.read_parquet(parquet_path)

    if df_contratos.empty:
        return pd.DataFrame(columns=["CNPJ", "VOLUME_ENQUADRAMENTO_MWM", "POSSUI_PELO_MENOS_5_MWM"])

    # 1. Filtra apenas contratos ativos/válidos se houver coluna de status
    if "STATUS" in df_contratos.columns:
        # Padroniza para capturar variações como 'Ativo', 'ATIVO', 'Ativo/Fechado'
        df_contratos["STATUS_UP"] = df_contratos["STATUS"].astype(str).str.upper()
        df_ativos = df_contratos[df_contratos["STATUS_UP"].str.contains("ATIVO", na=False)].copy()
    else:
        df_ativos = df_contratos.copy()

    if df_ativos.empty:
        return pd.DataFrame(columns=["CNPJ", "VOLUME_ENQUADRAMENTO_MWM", "POSSUI_PELO_MENOS_5_MWM"])

    # 2. Agrupa por CNPJ e Competência para somar volumes simultâneos
    df_mensal = (
        df_ativos.groupby(["CNPJ", "COMPETENCIA"], as_index=False)["VOLUME_CONTRATADO_MENSAL_MWM"]
        .sum()
        .rename(columns={"VOLUME_CONTRATADO_MENSAL_MWM": "VOLUME_CONSOLIDADO_MENSAL"})
    )

    # 3. Regra de Negócio: O volume de enquadramento é o MAIOR volume mensal
    df_enquadramento = (
        df_mensal.groupby("CNPJ", as_index=False)["VOLUME_CONSOLIDADO_MENSAL"]
        .max()
        .rename(columns={"VOLUME_CONSOLIDADO_MENSAL": "VOLUME_ENQUADRAMENTO_MWM"})
    )

    # 4. Deriva o indicador booleano de corte (Parametrizado em 5.0 MWm conforme Planejamento §6.2)
    LIMIAR_MWM = 5.0
    df_enquadramento["POSSUI_PELO_MENOS_5_MWM"] = (
        df_enquadramento["VOLUME_ENQUADRAMENTO_MWM"] >= LIMIAR_MWM
    )

    # Persiste o resultado resumido na camada Relacional (Dimensions/Configs)
    relational_dir = context.path("relational_configs")
    relational_dir.mkdir(parents=True, exist_ok=True)
    output_path = relational_dir / f"enquadramento_consumidores_{competencia_base}.csv"
    
    df_enquadramento.to_csv(output_path, index=False, encoding="utf-8-sig")

    return df_enquadramento