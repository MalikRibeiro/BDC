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
    simultâneo por raiz de CNPJ (Matriz + Filiais) e retorna a base consolidada
    de enquadramento propagada para todos os CNPJs completos.
    """
    silver_dir = context.path("silver") / "denodo_contratos_padronizados"
    parquet_path = silver_dir / f"contratos_correntes_{competencia_base}.parquet"

    if not parquet_path.exists():
        df_vazio = pd.DataFrame(columns=["CNPJ", "VOLUME_ENQUADRAMENTO_MWM", "POSSUI_PELO_MENOS_5_MWM"])
        _salvar_enquadramento(context, competencia_base, df_vazio)
        return df_vazio

    df_contratos = pd.read_parquet(parquet_path)

    if df_contratos.empty:
        df_enquadramento = pd.DataFrame(
            columns=["CNPJ", "VOLUME_ENQUADRAMENTO_MWM", "POSSUI_PELO_MENOS_5_MWM"]
        )
        _salvar_enquadramento(context, competencia_base, df_enquadramento)
        return df_enquadramento

    status_excluidos = ["CANCELADO", "DISTRATADO", "ENCERRADO", "REJEITADO", "INATIVO"]
    if "STATUS" in df_contratos.columns:
        df_contratos["STATUS_UP"] = (
            df_contratos["STATUS"]
            .astype(str)
            .str.upper()
        )

        df_ativos = df_contratos[
            ~df_contratos["STATUS_UP"].isin(status_excluidos)
        ].copy()
    else:
        df_ativos = df_contratos.copy()

    if df_ativos.empty:
        df_enquadramento = pd.DataFrame(
            columns=["CNPJ", "VOLUME_ENQUADRAMENTO_MWM", "POSSUI_PELO_MENOS_5_MWM"]
        )
        _salvar_enquadramento(context, competencia_base, df_enquadramento)
        return df_enquadramento

    if "CNPJ_RAIZ" not in df_ativos.columns:
        from common.identificadores import normalizar_cnpj
        df_ativos["CNPJ_RAIZ"] = df_ativos["CNPJ"].apply(lambda x: normalizar_cnpj(x).raiz if normalizar_cnpj(x).valido else None)

    col_ano = next((c for c in df_ativos.columns if c.upper() == "ANO"), None)
    col_mes = next((c for c in df_ativos.columns if c.upper() == "MES"), None)

    col_vol = next(
        (c for c in df_ativos.columns if c.upper() in {"VOLUME_CONTRATADO_MENSAL_MWM", "VOLUME_MWM"}),
        None,
    )
    if col_vol is None:
        raise KeyError(
            "Coluna de volume (VOLUME_CONTRATADO_MENSAL_MWM ou VOLUME_MWM) "
            "não encontrada na base de contratos."
        )
    if col_vol != "VOLUME_CONTRATADO_MENSAL_MWM":
        df_ativos = df_ativos.rename(columns={col_vol: "VOLUME_CONTRATADO_MENSAL_MWM"})

    if "COMPETENCIA" not in df_ativos.columns and col_ano and col_mes:
        df_ativos["COMPETENCIA"] = (
            df_ativos[col_ano].astype(str).str.replace(r"\.0$", "", regex=True)
            + df_ativos[col_mes].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(2)
        )

    df_mensal = (
        df_ativos.groupby(
            ["CNPJ_RAIZ", "COMPETENCIA"],
            as_index=False,
        )["VOLUME_CONTRATADO_MENSAL_MWM"]
        .sum()
        .rename(
            columns={
                "VOLUME_CONTRATADO_MENSAL_MWM": "VOLUME_CONSOLIDADO_MENSAL"
            }
        )
    )

    df_enq_raiz = (
        df_mensal.groupby(
            "CNPJ_RAIZ",
            as_index=False,
        )["VOLUME_CONSOLIDADO_MENSAL"]
        .max()
        .rename(
            columns={
                "VOLUME_CONSOLIDADO_MENSAL": "VOLUME_ENQUADRAMENTO_MWM"
            }
        )
    )

    LIMIAR_MWM = 5.0

    df_enq_raiz["POSSUI_PELO_MENOS_5_MWM"] = (
        df_enq_raiz["VOLUME_ENQUADRAMENTO_MWM"] >= LIMIAR_MWM
    )

    df_enquadramento = pd.merge(
        df_ativos[["CNPJ", "CNPJ_RAIZ"]].drop_duplicates(),
        df_enq_raiz,
        on="CNPJ_RAIZ",
        how="left",
    ).drop(columns=["CNPJ_RAIZ"])

    _salvar_enquadramento(context, competencia_base, df_enquadramento)
    return df_enquadramento

def _salvar_enquadramento(context: AppContext, competencia_base: str, df: pd.DataFrame) -> None:
    relational_dir = context.path("relational_configs")
    relational_dir.mkdir(parents=True, exist_ok=True)
    output_path = relational_dir / f"enquadramento_consumidores_{competencia_base}.csv"
    df.to_csv(output_path, index=False, encoding="utf-8-sig")