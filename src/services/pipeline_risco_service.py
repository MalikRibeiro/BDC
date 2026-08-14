"""Orquestrador do Pipeline de Risco de Crédito."""

from __future__ import annotations
import logging
from datetime import datetime
from typing import Any
import pandas as pd

from app.context import AppContext
from common.logging_utils import get_logger
from domain.credito.ead_engine import calcular_ead
from domain.credito.lgd_engine import calcular_lgd
from domain.credito.pe_engine import calcular_perda_esperada
from domain.credito.taxa_risco_engine import calcular_taxa_risco
from storage.silver_store import write_silver_dataset

def run_pipeline_risco(
    context: AppContext,
    df_exposicoes: pd.DataFrame,
    fator_conversao_ead: float = 1.0,
    config_lgd: dict[str, Any] | None = None
) -> dict[str, Any]:
    run_id = f"RSK_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = get_logger("bdc.risco", context.path("log_runner") / f"{run_id}__pipeline_risco.log")
    logger.info("Iniciando Pipeline de Risco de Crédito (run_id=%s)", run_id)
    
    garantias_path = context.path("silver") / "garantias_silver" / "fato_garantia.parquet"
    df_garantias = pd.read_parquet(garantias_path) if garantias_path.exists() else pd.DataFrame()

    resultados_fatos = []
    pe_total_carteira = 0.0
    notional_total_carteira = 0.0
    alertas = []

    df_exposicoes["MTM_POSITIVO_TOTAL"] = pd.to_numeric(df_exposicoes.get("MTM_POSITIVO_TOTAL", 0), errors="coerce").fillna(0.0)
    df_exposicoes["NOTIONAL_TOTAL"] = pd.to_numeric(df_exposicoes.get("NOTIONAL_TOTAL", 0), errors="coerce").fillna(0.0)
    df_exposicoes["PD_FINAL"] = pd.to_numeric(df_exposicoes.get("PD_FINAL", 0), errors="coerce").fillna(0.0)

    for idx, row in df_exposicoes.iterrows():
        cnpj = row.get("CNPJ")
        mtm_positivo = row.get("MTM_POSITIVO_TOTAL")
        notional = row.get("NOTIONAL_TOTAL")
        segmento = row.get("SEGMENTO_METODOLOGICO", "CGRUPO")
        pd_final = row.get("PD_FINAL")

        cobertura_aplicada = 0.0
        # CORREÇÃO: Aplica a garantia se ela estiver VIGENTE
        if not df_garantias.empty and "CNPJ_CONTRAPARTE" in df_garantias.columns:
            filtro = (df_garantias["CNPJ_CONTRAPARTE"] == cnpj) & (df_garantias.get("STATUS", "") == "VIGENTE")
            if filtro.any():
                cobertura_calculada = df_garantias.loc[filtro, "PERCENTUAL_COBERTURA"].sum()
                cobertura_aplicada = min(float(cobertura_calculada), 1.0)

        res_ead = calcular_ead(mtm_positivo_total=mtm_positivo, fator_conversao=fator_conversao_ead)
        res_lgd = calcular_lgd(segmento=segmento, cobertura_garantias=cobertura_aplicada, config=config_lgd)
        res_pe = calcular_perda_esperada(
            ead=res_ead.get("ead_valor"), 
            lgd_liquida=res_lgd.get("lgd_liquida"), 
            pd_final=pd_final, 
            notional=notional
        )

        pe_val = res_pe.get("pe_reais", 0.0)
        if pe_val is not None: pe_total_carteira += float(pe_val)
        if notional is not None: notional_total_carteira += float(notional)

        fato = {
            "RUN_ID": run_id, "CNPJ": cnpj, "SEGMENTO": segmento,
            "DT_CALCULO": res_pe.get("dt_calculo"),
            "CALCULO_ID_EAD": res_ead.get("calculo_id"), "EAD_VALOR": res_ead.get("ead_valor", 0.0),
            "FATOR_CONVERSAO_EAD": res_ead.get("fator_conversao"), "CONFIG_SNAPSHOT_EAD": res_ead.get("config_snapshot_id"),
            "CALCULO_ID_LGD": res_lgd.get("calculo_id"), "LGD_BRUTA": res_lgd.get("lgd_bruta"),
            "LGD_LIQUIDA": res_lgd.get("lgd_liquida", 0.0), "COBERTURA_GARANTIAS": res_lgd.get("cobertura_garantias"),
            "CONFIG_SNAPSHOT_LGD": res_lgd.get("config_snapshot_id"),
            "PD_UTILIZADA": pd_final,
            "CALCULO_ID_PE": res_pe.get("calculo_id"), "PE_REAIS": res_pe.get("pe_reais", 0.0),
            "PE_PERCENTUAL": res_pe.get("pe_percentual", 0.0),
        }
        resultados_fatos.append(fato)

    res_taxa = calcular_taxa_risco(pe_total=pe_total_carteira, notional_total=notional_total_carteira)
    taxa_val = res_taxa.get("taxa_risco")
    taxa_print = f"{taxa_val*100:.4f}%" if taxa_val is not None else "0.00% (Notional Zerado na Origem)"
    
    if res_taxa.get("alertas"): alertas.extend(res_taxa["alertas"])

    if alertas:
        df_alertas = pd.DataFrame(alertas)
        df_alertas["RUN_ID"] = run_id
        df_alertas["DATA_DETECCAO"] = datetime.now().isoformat(timespec="seconds")
        df_alertas["STATUS_ALERTA"] = "ABERTO"
        write_silver_dataset(records=df_alertas.to_dict(orient="records"), output_dir=context.path("silver") / "alertas_credito", filename=f"alertas_risco_{run_id}")

    if resultados_fatos:
        df_fatos = pd.DataFrame(resultados_fatos)
        relational_dir = context.path("relational_facts")
        relational_dir.mkdir(parents=True, exist_ok=True)
        
        write_silver_dataset(records=df_fatos.to_dict(orient="records"), output_dir=relational_dir, filename=f"fato_exposicao_risco_{run_id}")
        write_silver_dataset(records=df_fatos.to_dict(orient="records"), output_dir=relational_dir, filename="fato_exposicao_risco_LATEST")
        
    logger.info("Pipeline de Risco concluído. Taxa Carteira: %s", taxa_print)

    return {
        "run_id": run_id, "linhas_processadas": len(resultados_fatos),
        "taxa_risco_carteira": taxa_val, "pe_total_carteira": pe_total_carteira,
        "notional_total_carteira": notional_total_carteira, "calculo_id_taxa": res_taxa.get("calculo_id")
    }