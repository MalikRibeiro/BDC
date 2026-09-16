"""Serviço de construção da tabela Fato Exposição de Risco."""
from __future__ import annotations
import logging
import math
from datetime import datetime
from typing import Any
import pandas as pd
from pathlib import Path

from app.context import AppContext
from control.logger import obter_logger
from storage.escrever_dados import escrever_conjunto_de_dados_silver

from domain.credito.motor_ead import calcular_ead
from domain.credito.motor_lgd import calcular_lgd
from domain.credito.motor_pe import calcular_perda_esperada
from domain.credito.motor_taxa_risco import calcular_taxa_risco

def processar_fato_exposicao_risco(context: AppContext) -> dict[str, Any] | None:
    """Orquestra a leitura do MtM e Fato de Crédito para gerar a Exposição de Risco."""
    mtm_path = context.path("silver") / "mtm_consolidado_silver" / "mtm_agregado_contraparte.parquet"
    df_mtm = pd.read_parquet(mtm_path) if mtm_path.exists() else pd.DataFrame()
    if df_mtm.empty: 
        return None
        
    fato_path = context.path("relational_facts") / "credito" / "fato_analise_credito.parquet"
    if not fato_path.exists():
        fato_path = context.path("relational_facts") / "fato_analise_credito.parquet" # fallback antigo
        
    df_fichas = pd.read_parquet(fato_path) if fato_path.exists() else pd.DataFrame()

    df_mtm["CNPJ"] = df_mtm["CNPJ"].astype(str).str.zfill(14)
    df_exposicoes = df_mtm.copy()
    
    if not df_fichas.empty and "CNPJ" in df_fichas.columns:
        df_fichas["CNPJ"] = df_fichas["CNPJ"].astype(str).str.zfill(14)
        if "DATA_ANALISE" in df_fichas.columns:
            df_fichas = df_fichas.sort_values("DATA_ANALISE").drop_duplicates("CNPJ", keep="last")
            
        cols_ficha = ["CNPJ"]
        
        if "PD_PERCENTUAL" in df_fichas.columns: cols_ficha.append("PD_PERCENTUAL")
        if "SEGMENTO_METODOLOGICO_FICHA" in df_fichas.columns: cols_ficha.append("SEGMENTO_METODOLOGICO_FICHA")
        
        df_fichas = df_fichas[cols_ficha]
        df_exposicoes = pd.merge(df_exposicoes, df_fichas, on="CNPJ", how="left")
        
        if "PD_PERCENTUAL" in df_exposicoes.columns:
            df_exposicoes["PD_FINAL"] = df_exposicoes["PD_PERCENTUAL"]
        if "SEGMENTO_METODOLOGICO_FICHA" in df_exposicoes.columns:
            df_exposicoes["SEGMENTO_METODOLOGICO"] = df_exposicoes["SEGMENTO_METODOLOGICO_FICHA"]
            
    if "PD_FINAL" not in df_exposicoes.columns: df_exposicoes["PD_FINAL"] = None
    if "SEGMENTO_METODOLOGICO" not in df_exposicoes.columns: df_exposicoes["SEGMENTO_METODOLOGICO"] = "NAO_ENQUADRADO"
    
    return construir_fato_exposicao_risco(context, df_exposicoes=df_exposicoes)


def construir_fato_exposicao_risco(
    context: AppContext,
    df_exposicoes: pd.DataFrame,
    fator_conversao_ead: float = 1.0,
    config_lgd: dict[str, Any] | None = None
) -> dict[str, Any]:
    run_id = f"RSK_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = obter_logger("bdc.fato_risco", Path("LOGS/relacional") / f"{run_id}__fato_risco.log")
    logger.info("Iniciando Fato Exposição de Risco (run_id=%s)", run_id)
    
    garantias_path = context.path("silver") / "garantias_silver" / "fato_garantia.parquet"
    df_garantias = pd.read_parquet(garantias_path) if garantias_path.exists() else pd.DataFrame()

    resultados_fatos = []
    pe_total_carteira = 0.0
    notional_total_carteira = 0.0
    alertas = []

    df_exposicoes["MTM_POSITIVO_TOTAL"] = pd.to_numeric(df_exposicoes.get("MTM_POSITIVO_TOTAL", 0), errors="coerce").fillna(0.0)
    df_exposicoes["NOTIONAL_TOTAL"]     = pd.to_numeric(df_exposicoes.get("NOTIONAL_TOTAL", 0), errors="coerce").fillna(0.0)
    df_exposicoes["PD_FINAL"] = pd.to_numeric(df_exposicoes.get("PD_FINAL"), errors="coerce")

    if "CNPJ_RAIZ" not in df_exposicoes.columns:
        from common.identificadores import normalizar_cnpj
        df_exposicoes["CNPJ_RAIZ"] = df_exposicoes["CNPJ"].apply(lambda x: normalizar_cnpj(x).raiz if normalizar_cnpj(x).valido else None)

    for idx, row in df_exposicoes.iterrows():
        cnpj      = row.get("CNPJ")
        cnpj_raiz = str(row.get("CNPJ_RAIZ", str(cnpj)[:8]))
        mtm_positivo = row.get("MTM_POSITIVO_TOTAL")
        notional     = row.get("NOTIONAL_TOTAL")
        segmento     = row.get("SEGMENTO_METODOLOGICO", "CGRUPO")
        pd_final     = row.get("PD_FINAL")

        cobertura_aplicada = 0.0
        if not df_garantias.empty and "CNPJ_CONTRAPARTE" in df_garantias.columns:
            filtro = (
                df_garantias["CNPJ_CONTRAPARTE"].astype(str).str[:8] == cnpj_raiz
            ) & (
                df_garantias["STATUS"].astype(str).str.strip().str.upper() == "VIGENTE"
                if "STATUS" in df_garantias.columns
                else True
            )
            if filtro.any():
                cobertura_calculada = df_garantias.loc[filtro, "PERCENTUAL_COBERTURA"].sum()
                cobertura_aplicada  = min(float(cobertura_calculada), 1.0)

        res_ead = calcular_ead(mtm_positivo_total=mtm_positivo, fator_conversao=fator_conversao_ead)
        res_lgd = calcular_lgd(segmento=segmento, cobertura_garantias=cobertura_aplicada, config=config_lgd)
        res_pe = calcular_perda_esperada(
            ead=res_ead.get("ead_valor"), 
            lgd_liquida=res_lgd.get("lgd_liquida"), 
            pd_final=pd_final, 
            notional=notional
        )

        pe_val = res_pe.get("pe_reais", 0.0)
        if pe_val is not None and not (isinstance(pe_val, float) and math.isnan(pe_val)):
            pe_total_carteira += float(pe_val)
        if notional is not None and not (isinstance(notional, float) and math.isnan(notional)):
            notional_total_carteira += float(notional)

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

    res_taxa = calcular_taxa_risco(pe_total=pe_total_carteira, notional_total=notional_total_carteira, run_id=run_id, context=context)
    taxa_val = res_taxa.get("taxa_risco")
    taxa_print = f"{taxa_val*100:.4f}%" if taxa_val is not None else "0.00% (Notional Zerado na Origem)"
    
    if res_taxa.get("alertas"): alertas.extend(res_taxa["alertas"])

    if alertas:
        df_alertas = pd.DataFrame(alertas)
        df_alertas["RUN_ID"] = run_id
        df_alertas["DATA_DETECCAO"] = datetime.now().isoformat(timespec="seconds")
        df_alertas["STATUS_ALERTA"] = "ABERTO"
        escrever_conjunto_de_dados_silver(records=df_alertas.to_dict(orient="records"), output_dir=context.path("silver") / "alertas_credito", filename=f"alertas_risco_{run_id}")

    if resultados_fatos:
        df_fatos = pd.DataFrame(resultados_fatos)
        relational_dir = context.path("relational_facts") / "risco"
        relational_dir.mkdir(parents=True, exist_ok=True)
        
        escrever_conjunto_de_dados_silver(records=df_fatos.to_dict(orient="records"), output_dir=relational_dir, filename=f"fato_exposicao_risco_{run_id}")
        escrever_conjunto_de_dados_silver(records=df_fatos.to_dict(orient="records"), output_dir=relational_dir, filename="fato_exposicao_risco_LATEST")
        
    logger.info("Fato Exposição de Risco concluída. Taxa Carteira: %s", taxa_print)

    return {
        "run_id": run_id, "linhas_processadas": len(resultados_fatos),
        "taxa_risco_carteira": taxa_val, "pe_total_carteira": pe_total_carteira,
        "notional_total_carteira": notional_total_carteira, "calculo_id_taxa": res_taxa.get("calculo_id")
    }
