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
        raise FileNotFoundError(
            f"Base Silver de contratos do Denodo não encontrada para a competência "
            f"{competencia_base} em: {parquet_path}. "
            "Execute a ingestão (T2.1.2) primeiro."
        )

    df_contratos = pd.read_parquet(parquet_path)

    if df_contratos.empty:
        return pd.DataFrame(
            columns=[
                "CNPJ",
                "VOLUME_ENQUADRAMENTO_MWM",
                "POSSUI_PELO_MENOS_5_MWM",
            ]
        )

    # 1. Filtra apenas contratos ativos/válidos se houver coluna de status
    if "STATUS" in df_contratos.columns:
        # Padroniza para capturar variações como:
        # 'Ativo', 'ATIVO', 'Ativo/Fechado', etc.
        df_contratos["STATUS_UP"] = (
            df_contratos["STATUS"]
            .astype(str)
            .str.upper()
        )

        df_ativos = df_contratos[
            df_contratos["STATUS_UP"].str.contains("ATIVO", na=False)
        ].copy()
    else:
        df_ativos = df_contratos.copy()

    if df_ativos.empty:
        return pd.DataFrame(
            columns=[
                "CNPJ",
                "VOLUME_ENQUADRAMENTO_MWM",
                "POSSUI_PELO_MENOS_5_MWM",
            ]
        )

    # 2. Cria/valida a raiz do CNPJ para agregar Matriz e Filiais.
    # Prefere a coluna CNPJ_RAIZ já vinda padronizada da Silver (8 dígitos garantidos).
    # Caso não exista (bases legadas), recalcula a partir do CNPJ de 14 dígitos.
    if "CNPJ_RAIZ" not in df_ativos.columns:
        df_ativos["CNPJ_RAIZ"] = (
            df_ativos["CNPJ"]
            .astype(str)
            .str.replace(r"\D", "", regex=True)
            .str[:8]
        )

    # Resolução case-insensitive das colunas de competência (ANO/ano, MES/mes).
    # A Silver do Denodo pode entregar em maiúsculas ou minúsculas dependendo
    # da versão da ingestão.
    col_ano = next((c for c in df_ativos.columns if c.upper() == "ANO"), None)
    col_mes = next((c for c in df_ativos.columns if c.upper() == "MES"), None)

    # Resolução case-insensitive da coluna de volume
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

    # Garante competência: se não existir como coluna, monta a partir de ANO+MES
    if "COMPETENCIA" not in df_ativos.columns and col_ano and col_mes:
        df_ativos["COMPETENCIA"] = (
            df_ativos[col_ano].astype(str).str.replace(r"\.0$", "", regex=True)
            + df_ativos[col_mes].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(2)
        )

    # 3. Agrupa por CNPJ_RAIZ e Competência para somar volumes
    # simultâneos de Matriz + Filiais do mesmo grupo.
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

    # 4. Regra de Negócio:
    # O volume de enquadramento do Grupo é o MAIOR volume mensal consolidado.
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

    # 5. Deriva o indicador booleano de corte.
    # Parametrizado em 5.0 MWm conforme Planejamento §6.2.
    LIMIAR_MWM = 5.0

    df_enq_raiz["POSSUI_PELO_MENOS_5_MWM"] = (
        df_enq_raiz["VOLUME_ENQUADRAMENTO_MWM"] >= LIMIAR_MWM
    )

    # 6. Propaga o enquadramento da raiz de volta para todos os CNPJs
    # completos (14 dígitos) encontrados na base.
    #
    # Isso garante que:
    # - a Matriz herde o volume consolidado das Filiais;
    # - as Filiais herdem o mesmo enquadramento da Matriz;
    # - todos os estabelecimentos do mesmo grupo tenham o mesmo critério
    #   de enquadramento.
    df_enquadramento = pd.merge(
        df_ativos[["CNPJ", "CNPJ_RAIZ"]].drop_duplicates(),
        df_enq_raiz,
        on="CNPJ_RAIZ",
        how="left",
    ).drop(columns=["CNPJ_RAIZ"])

    # Persiste o resultado resumido na camada Relacional
    # (Dimensions/Configs).
    relational_dir = context.path("relational_configs")
    relational_dir.mkdir(parents=True, exist_ok=True)

    output_path = (
        relational_dir
        / f"enquadramento_consumidores_{competencia_base}.csv"
    )

    df_enquadramento.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

    return df_enquadramento