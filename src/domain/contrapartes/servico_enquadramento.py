"""Serviço de cálculo do volume de enquadramento (≥ 5 MWm) para consumidores."""

from __future__ import annotations

import pandas as pd
from pathlib import Path
from typing import Any

from app.context import AppContext
from control.logger import obter_logger

logger = obter_logger("bdc.enquadramento")



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
        df_vazio = pd.DataFrame(columns=["CNPJ", "VOLUME_ENQUADRAMENTO_MWM", "POSSUI_PELO_MENOS_5_MWM", "SEGMENTO_METODOLOGICO"])
        _salvar_enquadramento(context, competencia_base, df_vazio)
        return df_vazio

    df_contratos = pd.read_parquet(parquet_path)

    if df_contratos.empty:
        df_enquadramento = pd.DataFrame(
            columns=["CNPJ", "VOLUME_ENQUADRAMENTO_MWM", "POSSUI_PELO_MENOS_5_MWM", "SEGMENTO_METODOLOGICO"]
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
            columns=["CNPJ", "VOLUME_ENQUADRAMENTO_MWM", "POSSUI_PELO_MENOS_5_MWM", "SEGMENTO_METODOLOGICO"]
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

    # --- FALLBACK 2: VOLUME MWM VIA COTAÇÕES APROVADAS SALESFORCE ---
    df_sf_cot_val = pd.DataFrame()
    try:
        sf_cot_path = context.path("silver") / "salesforce_silver" / "cotacao" / "salesforce_cotacao.parquet"
        if sf_cot_path.exists():
            df_sf_cot = pd.read_parquet(sf_cot_path)
            if not df_sf_cot.empty and "Maior_Volume_Mwm__c" in df_sf_cot.columns and "CNPJ" in df_sf_cot.columns:
                if "Cotacao_Aprovada__c" in df_sf_cot.columns:
                    mask_aprov = df_sf_cot["Cotacao_Aprovada__c"].astype(str).str.strip().str.upper().isin(["TRUE", "1", "S", "SIM"])
                    df_sf_cot_val = df_sf_cot[mask_aprov].copy()
                else:
                    df_sf_cot_val = df_sf_cot.copy()

                from common.numeros import to_float_br
                from common.identificadores import normalizar_cnpj_coluna

                df_sf_cot_val["CNPJ"] = df_sf_cot_val["CNPJ"].apply(normalizar_cnpj_coluna)
                df_sf_cot_val["CNPJ_RAIZ"] = df_sf_cot_val["CNPJ"].str[:8]
                df_sf_cot_val["VOL_SF"] = df_sf_cot_val["Maior_Volume_Mwm__c"].apply(to_float_br)
                df_sf_cot_val = df_sf_cot_val.dropna(subset=["CNPJ_RAIZ", "VOL_SF"])

                if not df_sf_cot_val.empty:
                    df_sf_max = df_sf_cot_val.groupby("CNPJ_RAIZ", as_index=False)["VOL_SF"].max()
                    # Outer join garante que contrapartes com cotação aprovada no Salesforce não sejam perdidas
                    df_enq_raiz = pd.merge(df_enq_raiz, df_sf_max, on="CNPJ_RAIZ", how="outer")
                    mask_denodo_valido = df_enq_raiz["VOLUME_ENQUADRAMENTO_MWM"].notna() & (df_enq_raiz["VOLUME_ENQUADRAMENTO_MWM"] > 0)
                    df_enq_raiz.loc[~mask_denodo_valido, "VOLUME_ENQUADRAMENTO_MWM"] = df_enq_raiz.loc[~mask_denodo_valido, "VOL_SF"]
                    df_enq_raiz.drop(columns=["VOL_SF"], inplace=True)
    except Exception as exc:
        logger.warning("Falha ao carregar fallback de volume do Salesforce: %s", exc)
    # -----------------------------------------------------------------

    LIMIAR_MWM = 5.0

    df_enq_raiz["POSSUI_PELO_MENOS_5_MWM"] = (
        df_enq_raiz["VOLUME_ENQUADRAMENTO_MWM"] >= LIMIAR_MWM
    )
    df_enq_raiz["SEGMENTO_METODOLOGICO"] = df_enq_raiz["POSSUI_PELO_MENOS_5_MWM"].map(
        {True: "CONSUMIDOR_GT_5", False: "CONSUMIDOR_LE_5"}
    ).fillna("CONSUMIDOR_LE_5")

    # Mapear de volta para todos os CNPJs completos (Denodo + Salesforce)
    df_cnpjs_base = df_ativos[["CNPJ", "CNPJ_RAIZ"]].drop_duplicates()
    if not df_sf_cot_val.empty:
        df_cnpjs_sf = df_sf_cot_val[["CNPJ", "CNPJ_RAIZ"]].drop_duplicates()
        df_cnpjs_base = pd.concat([df_cnpjs_base, df_cnpjs_sf], ignore_index=True).drop_duplicates("CNPJ")

    df_enquadramento = pd.merge(
        df_cnpjs_base,
        df_enq_raiz,
        on="CNPJ_RAIZ",
        how="inner",
    ).drop(columns=["CNPJ_RAIZ"])

    _salvar_enquadramento(context, competencia_base, df_enquadramento)
    return df_enquadramento

def _salvar_enquadramento(context: AppContext, competencia_base: str, df: pd.DataFrame) -> None:
    relational_dir = context.path("relational_configs")
    relational_dir.mkdir(parents=True, exist_ok=True)
    output_path = relational_dir / f"enquadramento_consumidores_{competencia_base}.csv"
    df.to_csv(output_path, index=False, encoding="utf-8-sig")