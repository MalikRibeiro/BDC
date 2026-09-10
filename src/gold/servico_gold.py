import logging
from pathlib import Path
from typing import Any
import pandas as pd
from datetime import datetime

from common.dados import validar_coluna_cnpj_canonica
from control.logger import obter_logger
from gold.regras_gold import (
    resolver_situacao_df,
    resolver_situacao_analise,
    classificar_exigencia,
    status_metodologia,
    checar_contrato_obrigatorio
)

def carregar_entradas_gold(context: Any, logger: logging.Logger) -> dict[str, pd.DataFrame]:
    silver_dir = context.path("silver")
    rel_dim_dir = context.path("relational_dimensions")
    rel_fact_dir = context.path("relational_facts")
    
    path_contraparte = rel_dim_dir / "contrapartes" / "dim_contraparte.parquet"
    path_contratos = silver_dir / "denodo_contratos_silver" / "contratos_correntes.parquet"
    if not path_contratos.exists():
        path_contratos = silver_dir / "denodo_contratos_padronizados" / "contratos_correntes.parquet"
        
    path_risco = rel_fact_dir / "risco" / "fato_exposicao_risco_LATEST.parquet"
    if not path_risco.exists():
        path_risco = silver_dir / "mtm_consolidado_silver" / "mtm_agregado_contraparte.parquet"

    path_analises = rel_fact_dir / "credito" / "fato_analise_credito.parquet"
    path_eventos_manuais = silver_dir / "governanca_carga_manual" / "eventos_manuais_consolidados.parquet"

    if not path_contraparte.exists():
        logger.error(f"Fonte obrigatória ausente: {path_contraparte}")
        raise FileNotFoundError(f"Fonte obrigatória ausente: {path_contraparte}. A dimensão de contraparte deve existir.")
    df_contraparte = pd.read_parquet(path_contraparte)

    if path_contratos.exists():
        df_contratos = pd.read_parquet(path_contratos)
    else:
        logger.warning(f"Base opcional de contratos ausente: {path_contratos}. Prosseguindo sem contratos.")
        df_contratos = pd.DataFrame()

    if path_analises.exists():
        df_analises = pd.read_parquet(path_analises)
    else:
        logger.warning(f"Base opcional de análises ausente: {path_analises}. Prosseguindo sem análises.")
        df_analises = pd.DataFrame()

    if path_risco.exists():
        df_risco = pd.read_parquet(path_risco)
    else:
        logger.warning(f"Base opcional de risco ausente: {path_risco}. Prosseguindo sem risco.")
        df_risco = pd.DataFrame()

    path_reconciliacao = rel_fact_dir / "reconciliacao" / "fato_reconciliacao_contrato_mtm.parquet"
    if path_reconciliacao.exists():
        df_reconciliacao = pd.read_parquet(path_reconciliacao)
    else:
        logger.warning(f"Base de reconciliação ausente: {path_reconciliacao}. Prosseguindo sem reconciliação.")
        df_reconciliacao = pd.DataFrame()

    if path_eventos_manuais.exists():
        df_eventos = pd.read_parquet(path_eventos_manuais)
    else:
        df_eventos = pd.DataFrame()

    path_bureau = silver_dir / "fato_bureau_silver" / "fato_bureau_silver.parquet"
    if path_bureau.exists():
        df_bureau = pd.read_parquet(path_bureau)
    else:
        df_bureau = pd.DataFrame()

    return {
        "contraparte": df_contraparte,
        "contratos": df_contratos,
        "analises": df_analises,
        "risco": df_risco,
        "eventos": df_eventos,
        "bureau": df_bureau,
        "reconciliacao": df_reconciliacao
    }

def salvar_visao_gold(context: Any, df_gold: pd.DataFrame, hoje: datetime, run_id: str, logger: logging.Logger):
    gold_dir = context.path("saidas") / "gold" / "visao_operacional_negocio"
    gold_dir.mkdir(parents=True, exist_ok=True)
    
    out_parquet = gold_dir / f"Visao_Operacional_BDC_{hoje.strftime('%Y%m%d')}.parquet"
    out_latest = gold_dir / "Visao_Operacional_BDC_LATEST.parquet"
    out_csv = gold_dir / f"Visao_Operacional_BDC_{hoje.strftime('%Y%m%d')}.csv"
    out_latest_csv = gold_dir / "Visao_Operacional_BDC_LATEST.csv"
    
    df_gold.to_parquet(out_parquet, index=False)
    df_gold.to_parquet(out_latest, index=False)
    df_gold.to_csv(out_csv, index=False, sep=";", decimal=",", encoding="utf-8-sig")
    df_gold.to_csv(out_latest_csv, index=False, sep=";", decimal=",", encoding="utf-8-sig")

    logger.info("Visão Gold gerada. Total Contrapartes consolidadas: %d", len(df_gold))

def construir_visao_consolidada(dfs: dict[str, pd.DataFrame], run_id: str, hoje: datetime) -> pd.DataFrame:
    df_contraparte = dfs["contraparte"]
    df_contratos = dfs["contratos"]
    df_analises = dfs["analises"]
    df_risco = dfs["risco"]
    df_eventos = dfs.get("eventos", pd.DataFrame())
    df_bureau = dfs.get("bureau", pd.DataFrame())
    df_reconciliacao = dfs.get("reconciliacao", pd.DataFrame())

    if df_contraparte.empty:
        raise ValueError("O DataFrame obrigatório 'contraparte' não pode estar vazio.")

    erros = validar_coluna_cnpj_canonica(df_contraparte)
    if erros:
        raise ValueError("Dataset Silver fora do contrato (contraparte): " + "; ".join(erros))
    
    checar_contrato_obrigatorio(df_contraparte, ["CNPJ"], "contraparte")
    
    cols_contra = [c for c in ["CNPJ", "CNPJ_RAIZ", "SIGLA", "NOME", "SEGMENTO_METODOLOGICO", "SITUACAO_CADASTRAL"] if c in df_contraparte.columns]
    df_gold = df_contraparte[cols_contra].copy()

    # Garante que todo CNPJ com contrato sobreviva na Gold (mesmo sem contraparte mapeada)
    if not df_contratos.empty:
        cnpjs_contratos = set(df_contratos["CNPJ"].dropna().unique())
        cnpjs_gold = set(df_gold["CNPJ"].dropna().unique())
        cnpjs_faltantes = cnpjs_contratos - cnpjs_gold
        if cnpjs_faltantes:
            df_missing = pd.DataFrame({"CNPJ": list(cnpjs_faltantes)})
            df_missing["CNPJ_RAIZ"] = df_missing["CNPJ"].str[:8]
            df_gold = pd.concat([df_gold, df_missing], ignore_index=True)

    if not df_analises.empty:
        erros = validar_coluna_cnpj_canonica(df_analises)
        if erros:
            raise ValueError("Dataset Silver fora do contrato (analises): " + "; ".join(erros))
        checar_contrato_obrigatorio(df_analises, ["CNPJ"], "analises")
        
        if "DATA_CALCULO" in df_analises.columns and "DATA_ANALISE" not in df_analises.columns:
            df_analises["DATA_ANALISE"] = df_analises["DATA_CALCULO"]
        if "DATA_DEMONSTRACAO_FINANCEIRA" in df_analises.columns and "DATA_BALANCO_USADO" not in df_analises.columns:
            df_analises["DATA_BALANCO_USADO"] = df_analises["DATA_DEMONSTRACAO_FINANCEIRA"]
        if "DATA_DF" in df_analises.columns and "DATA_BALANCO_USADO" not in df_analises.columns:
            df_analises["DATA_BALANCO_USADO"] = df_analises["DATA_DF"]
            
        def extrair_rating_valido(row):
            from common.nulos import is_nulo_textual
            for col in ["RATING_COPEL", "NOTA_CREDITO", "NOTA_BOARD", "RATING"]:
                val = row.get(col)
                if pd.notna(val) and not is_nulo_textual(val):
                    return str(val).strip().upper()
            return pd.NA

        def extrair_pd_valido(row):
            from common.nulos import is_nulo_textual
            for col in ["PROBABILIDADE_DEFAULT", "PD_PERCENTUAL", "PD"]:
                val = row.get(col)
                if pd.notna(val) and not is_nulo_textual(val):
                    return val
            return pd.NA

        if "RATING_FINAL" not in df_analises.columns:
            df_analises["RATING_FINAL"] = df_analises.apply(extrair_rating_valido, axis=1)
            
        if "PD_FINAL" not in df_analises.columns:
            df_analises["PD_FINAL"] = df_analises.apply(extrair_pd_valido, axis=1)
            
        if "MODELO" in df_analises.columns and "MODELO_METODOLOGICO" not in df_analises.columns:
            df_analises["MODELO_METODOLOGICO"] = df_analises["MODELO"]
        if "versao_ficha" in df_analises.columns and "MODELO_METODOLOGICO" not in df_analises.columns:
            df_analises["MODELO_METODOLOGICO"] = df_analises["versao_ficha"]

        col_sort = "DATA_ANALISE" if "DATA_ANALISE" in df_analises.columns else ("DATA_BALANCO_USADO" if "DATA_BALANCO_USADO" in df_analises.columns else "CNPJ")
        if col_sort in df_analises.columns and col_sort != "CNPJ":
            df_analises["_DT_SORT"] = pd.to_datetime(df_analises[col_sort], errors="coerce")
            df_analises = df_analises.sort_values("_DT_SORT", na_position="first").drop_duplicates("CNPJ", keep="last")
        else:
            df_analises = df_analises.drop_duplicates("CNPJ", keep="last")

        dt_balanco = pd.to_datetime(df_analises.get("DATA_BALANCO_USADO"), errors="coerce")
        dt_analise = pd.to_datetime(df_analises.get("DATA_ANALISE"), errors="coerce")
        
        mask_balanco = (dt_balanco.dt.year > 1900) & (dt_balanco.notna())
        mask_analise = (dt_analise.dt.year > 1900) & (dt_analise.notna())
        
        df_analises["VALIDADE_DT"] = pd.NaT
        df_analises.loc[mask_balanco, "VALIDADE_DT"] = dt_balanco.loc[mask_balanco] + pd.DateOffset(years=1, months=4)
        df_analises.loc[~mask_balanco & mask_analise, "VALIDADE_DT"] = dt_analise.loc[~mask_balanco & mask_analise] + pd.DateOffset(years=1)

        if "SITUACAO_ANALISE" not in df_analises.columns:
            df_analises["SITUACAO_ANALISE"] = df_analises["VALIDADE_DT"].apply(
                lambda dt: "VIGENTE" if pd.notnull(dt) and dt >= hoje else ("VENCIDA" if pd.notnull(dt) else "VENCIDA")
            )
        else:
            mask_null = df_analises["SITUACAO_ANALISE"].isna() | (df_analises["SITUACAO_ANALISE"].astype(str).str.strip().isin(["", "None", "nan", "<NA>"]))
            df_analises.loc[mask_null, "SITUACAO_ANALISE"] = df_analises.loc[mask_null, "VALIDADE_DT"].apply(
                lambda dt: "VIGENTE" if pd.notnull(dt) and dt >= hoje else ("VENCIDA" if pd.notnull(dt) else "VENCIDA")
            )

        if "SITUACAO_DF" not in df_analises.columns:
            df_analises["SITUACAO_DF"] = "RECEBIDA"
        else:
            df_analises["SITUACAO_DF"] = df_analises["SITUACAO_DF"].fillna("RECEBIDA")


        df_analises["TEM_ANALISE"] = "SIM"
            
        cols_analise_payload = [
            c for c in [
                "SITUACAO_ANALISE", "SITUACAO_DF", "RATING_FINAL", "PD_FINAL", 
                "MODELO_METODOLOGICO", "PATRIMONIO_LIQUIDO", "DATA_ANALISE", "DATA_BALANCO_USADO", "TEM_ANALISE",
                "MOTIVO_AUSENCIA_DF", "TIPO_EVENTO_MANUAL", "ORIGEM_REGISTRO", "VALIDADE_EXCECAO", "STATUS_CALCULO_PD"
            ] if c in df_analises.columns
        ]

        df_gold = pd.merge(
            df_gold, 
            df_analises[["CNPJ"] + cols_analise_payload], 
            on="CNPJ", 
            how="left"
        )

        df_analises["_EH_MATRIZ"] = df_analises["CNPJ"].str[8:12] == "0001"
        sort_raiz = ["_EH_MATRIZ"]
        if "_DT_SORT" in df_analises.columns:
            sort_raiz.append("_DT_SORT")
            
        df_analises_raiz = (
            df_analises.sort_values(sort_raiz, ascending=[True] * len(sort_raiz))
            .drop_duplicates(subset=["CNPJ_RAIZ"], keep="last")
        )
        
        df_fallback = df_analises_raiz[["CNPJ_RAIZ"] + cols_analise_payload].copy()
        df_fallback.columns = ["CNPJ_RAIZ"] + [f"{c}_RAIZ" for c in cols_analise_payload]

        if "CNPJ_RAIZ" in df_gold.columns:
            df_gold = pd.merge(df_gold, df_fallback, on="CNPJ_RAIZ", how="left")
            for col in cols_analise_payload:
                col_raiz = f"{col}_RAIZ"
                if col_raiz in df_gold.columns:
                    df_gold[col] = df_gold[col].combine_first(df_gold[col_raiz])
                    df_gold = df_gold.drop(columns=[col_raiz])
    
    if "TEM_ANALISE" not in df_gold.columns:
        df_gold["TEM_ANALISE"] = "NÃO"
    df_gold["TEM_ANALISE"] = df_gold["TEM_ANALISE"].fillna("NÃO")

    if not df_contratos.empty:
        erros = validar_coluna_cnpj_canonica(df_contratos)
        if erros:
            raise ValueError("Dataset Silver fora do contrato (contratos): " + "; ".join(erros))
        checar_contrato_obrigatorio(df_contratos, ["CNPJ_RAIZ"], "contratos")

        col_vol = "VOLUME_CONTRATADO_MENSAL_MWM" if "VOLUME_CONTRATADO_MENSAL_MWM" in df_contratos.columns else "VOLUME_MWM"
        if col_vol in df_contratos.columns:
            df_contratos["VOLUME_MWM"] = pd.to_numeric(df_contratos[col_vol], errors="coerce").fillna(0.0)
        else:
            df_contratos["VOLUME_MWM"] = 0.0
        
        if "ano" in df_contratos.columns and "mes" in df_contratos.columns:
            df_mensal = df_contratos.groupby(["CNPJ_RAIZ", "ano", "mes"], as_index=False)["VOLUME_MWM"].sum()
            df_vol_enquadramento = df_mensal.groupby("CNPJ_RAIZ", as_index=False)["VOLUME_MWM"].max()
        else:
            df_vol_enquadramento = df_contratos.groupby("CNPJ_RAIZ", as_index=False)["VOLUME_MWM"].max()

        col_id = "NUMERO_REFERENCIA_CONTRATO"
        col_in = "SUPRIMENTO_INICIO"
        if col_in not in df_contratos.columns:
            col_in = "VIGENCIA_INICIO" if "VIGENCIA_INICIO" in df_contratos.columns else "inicio_suprimento"
            
        col_out = "SUPRIMENTO_TERMINO"
        if col_out not in df_contratos.columns:
            col_out = "VIGENCIA_FIM" if "VIGENCIA_FIM" in df_contratos.columns else "fim_suprimento"

        df_contratos["DT_INICIO"] = pd.to_datetime(df_contratos.get(col_in), errors="coerce")
        df_contratos["DT_FIM"] = pd.to_datetime(df_contratos.get(col_out), errors="coerce")
        
        df_contratos["EH_VIGENTE"] = (
            (df_contratos.get("STATUS", df_contratos.get("id_status", "")).astype(str).str.upper().str.contains("ATIVO|EM SUPRIMENTO|2")) &
            (df_contratos["DT_INICIO"] <= hoje) &
            (df_contratos["DT_FIM"] >= hoje)
        )
        df_contratos["EH_FUTURO"] = (df_contratos["DT_INICIO"] > hoje)

        resumo_contratos = df_contratos.groupby("CNPJ").agg(
            QUANTIDADE_CONTRATOS=(col_id, "nunique") if col_id in df_contratos.columns else ("CNPJ", "count"),
            NUMERACAO_CONTRATOS=(col_id, lambda x: ", ".join(x.dropna().astype(str).unique())) if col_id in df_contratos.columns else ("CNPJ", lambda x: ""),
            STATUS_CONTRATUAL=("EH_VIGENTE", lambda x: "CONTRATO_VIGENTE" if x.any() else ("CONTRATO_FUTURO" if df_contratos.loc[x.index, "EH_FUTURO"].any() else "SEM_CONTRATO")),
            PROXIMO_INICIO=("DT_INICIO", "min"),
            PROXIMO_FIM=("DT_FIM", "max")
        ).reset_index()

        resumo_contratos["ANO_INICIO_CONTRATO"] = resumo_contratos["PROXIMO_INICIO"].dt.year.fillna(0).astype(int)

        resumo_contratos["CNPJ_RAIZ"] = resumo_contratos["CNPJ"].str[:8]
        df_contratos_gold = pd.merge(resumo_contratos, df_vol_enquadramento[["CNPJ_RAIZ", "VOLUME_MWM"]], on="CNPJ_RAIZ", how="left")
        df_gold = pd.merge(df_gold, df_contratos_gold, on="CNPJ", how="left")
    else:
        df_gold["STATUS_CONTRATUAL"] = "SEM_CONTRATO"
        df_gold["VOLUME_MWM"] = 0.0
        df_gold["NUMERACAO_CONTRATOS"] = ""
        df_gold["QUANTIDADE_CONTRATOS"] = 0
        df_gold["ANO_INICIO_CONTRATO"] = 0
        df_gold["PROXIMO_INICIO"] = pd.NaT
        df_gold["PROXIMO_FIM"] = pd.NaT
        
    df_gold["TEM_CONTRATO"] = df_gold["STATUS_CONTRATUAL"].apply(lambda x: "SIM" if x in ["CONTRATO_VIGENTE", "CONTRATO_FUTURO"] else "NÃO")

    if not df_risco.empty:
        erros = validar_coluna_cnpj_canonica(df_risco)
        if erros:
            raise ValueError("Dataset Silver fora do contrato (risco): " + "; ".join(erros))
        checar_contrato_obrigatorio(df_risco, ["CNPJ"], "risco")
        df_risco = df_risco.drop_duplicates(subset=["CNPJ"], keep="last")
        
        if "PE_REAIS" in df_risco.columns:
            cols_risco = [c for c in ["CNPJ", "EAD_VALOR", "LGD_LIQUIDA", "PE_REAIS"] if c in df_risco.columns]
            df_gold = pd.merge(df_gold, df_risco[cols_risco], on="CNPJ", how="left")
        else:
            col_mtm = "FINANCEIRO_MTM" if "FINANCEIRO_MTM" in df_risco.columns else ("MTM" if "MTM" in df_risco.columns else None)
            if col_mtm:
                df_gold = pd.merge(df_gold, df_risco[["CNPJ", col_mtm]].rename(columns={col_mtm: "EAD_VALOR"}), on="CNPJ", how="left")
                df_gold["PE_REAIS"] = 0.0

    if not df_reconciliacao.empty:
        erros = validar_coluna_cnpj_canonica(df_reconciliacao)
        if erros:
            raise ValueError("Dataset Silver fora do contrato (reconciliacao): " + "; ".join(erros))
        checar_contrato_obrigatorio(df_reconciliacao, ["CNPJ"], "reconciliacao")
        df_reconciliacao = df_reconciliacao.drop_duplicates(subset=["CNPJ"], keep="last")
        
        cols_recon = [c for c in ["CNPJ", "STATUS_CONCILIACAO", "MTM_POSITIVO_TOTAL"] if c in df_reconciliacao.columns]
        df_gold = pd.merge(df_gold, df_reconciliacao[cols_recon], on="CNPJ", how="left")
        
        if "MTM_POSITIVO_TOTAL" in df_gold.columns:
            df_gold["POSICAO_MTM_MW"] = pd.to_numeric(df_gold["MTM_POSITIVO_TOTAL"], errors="coerce").fillna(0.0)
            df_gold = df_gold.drop(columns=["MTM_POSITIVO_TOTAL"])
        else:
            df_gold["POSICAO_MTM_MW"] = 0.0
            
        if "STATUS_CONCILIACAO" not in df_gold.columns:
            df_gold["STATUS_CONCILIACAO"] = "DIVERGENTE"
    else:
        df_gold["POSICAO_MTM_MW"] = 0.0
        df_gold["STATUS_CONCILIACAO"] = "DIVERGENTE"

    colunas_esperadas = [
        "VOLUME_MWM", "EAD_VALOR", "PE_REAIS", "PATRIMONIO_LIQUIDO", "QUANTIDADE_CONTRATOS", 
        "STATUS_CONTRATUAL", "SITUACAO_ANALISE", "SITUACAO_DF", "SITUACAO_CADASTRAL"
    ]
    for col in colunas_esperadas:
        if col not in df_gold.columns:
            logging.warning("Coluna esperada '%s' ausente no DataFrame Gold. Preenchida com fallback pd.NA.", col)
            df_gold[col] = pd.NA

    df_gold["STATUS_CONTRATUAL"] = df_gold["STATUS_CONTRATUAL"].fillna("SEM_CONTRATO")
    df_gold["SITUACAO_CADASTRAL"] = df_gold["SITUACAO_CADASTRAL"].fillna("NAO_INFORMADA")

    df_gold["SITUACAO_DF"] = df_gold.apply(resolver_situacao_df, axis=1)
    df_gold["SITUACAO_ANALISE"] = df_gold.apply(resolver_situacao_analise, axis=1)
    df_gold["METODOLOGIA_EXIGIDA"] = df_gold.apply(classificar_exigencia, axis=1)
    df_gold["STATUS_METODOLOGIA"] = df_gold.apply(status_metodologia, axis=1)

    df_gold["CONTRAPARTE_ID"] = df_gold["CNPJ"].apply(lambda x: f"CPT_{x}")
    df_gold["ANALISE_ID"] = df_gold.apply(
        lambda row: f"ANA_{row['CNPJ']}_{str(row.get('DATA_ANALISE', '')).replace('-','')}" if row.get("TEM_ANALISE") == "SIM" and pd.notna(row.get("DATA_ANALISE")) else pd.NA, axis=1
    )
    df_gold["RUN_ID"] = run_id
    df_gold["REVISAO_LIMITE"] = (df_gold["STATUS_METODOLOGIA"] != "COMPLIANT")
    df_gold["DATA_GERACAO"] = hoje
    df_gold["VERSAO_LAYOUT_LIMITE"] = "v1.2"
    df_gold["FONTE_VOLUME"] = "DENODO_CONTRATOS"
    df_gold["DATA_REFERENCIA_VOLUME"] = hoje

    if "MOTIVO_AUSENCIA_DF" not in df_gold.columns:
        df_gold["MOTIVO_AUSENCIA_DF"] = df_gold["SITUACAO_DF"].apply(lambda x: "NAO_ENVIADA_PELA_CONTRAPARTE" if x == "NAO_RECEBIDA" else pd.NA)

    if not df_eventos.empty and "CNPJ" in df_eventos.columns:
        from common.identificadores import normalizar_cnpj
        
        df_ev_vigentes = df_eventos[df_eventos["STATUS_EVENTO"] == "VIGENTE"].copy() if "STATUS_EVENTO" in df_eventos.columns else df_eventos.copy()
        df_ev_vigentes["CNPJ"] = df_ev_vigentes["CNPJ"].apply(lambda x: normalizar_cnpj(x).cnpj if normalizar_cnpj(x).valido else None)
        df_ev_vigentes = df_ev_vigentes.dropna(subset=["CNPJ"])
        
        cnpjs_manuais = set(df_ev_vigentes["CNPJ"].unique())
        df_gold["INDICADOR_DADO_MANUAL"] = df_gold["CNPJ"].apply(lambda x: "SIM" if x in cnpjs_manuais else "NÃO")
        
        if not df_ev_vigentes.empty and "CAMPO_AFETADO" in df_ev_vigentes.columns and "VALOR_NOVO" in df_ev_vigentes.columns:
            df_ev_vigentes["CAMPO_AFETADO"] = df_ev_vigentes["CAMPO_AFETADO"].replace({
                "NOTA_CREDITO": "RATING_FINAL",
                "RATING": "RATING_FINAL",
                "NOTA_BOARD": "RATING_FINAL",
                "NOTA_BUREAU": "RATING_FINAL",
                "PD": "PD_FINAL",
                "PROBABILIDADE_DEFAULT": "PD_FINAL"
            })
            
            df_ev_dedup = df_ev_vigentes.drop_duplicates(subset=["CNPJ", "CAMPO_AFETADO"], keep="last")
            df_ev_pivot = df_ev_dedup.pivot(index="CNPJ", columns="CAMPO_AFETADO", values="VALOR_NOVO").reset_index()
            
            for col in df_ev_pivot.columns:
                if col != "CNPJ" and col in df_gold.columns:
                    df_gold = pd.merge(df_gold, df_ev_pivot[["CNPJ", col]], on="CNPJ", how="left", suffixes=("", "_MANUAL"))
                    
                    col_manual = f"{col}_MANUAL"
                    if col_manual in df_gold.columns:
                        mask_manual = df_gold[col_manual].notna() & (df_gold[col_manual].astype(str).str.strip().str.upper() != "NONE")
                        mask_none = df_gold[col_manual].astype(str).str.strip().str.upper() == "NONE"
                        
                        if mask_manual.any():
                            if pd.api.types.is_numeric_dtype(df_gold[col]):
                                valores_convertidos = pd.to_numeric(df_gold.loc[mask_manual, col_manual], errors="coerce")
                                df_gold.loc[mask_manual, col] = valores_convertidos.astype(df_gold[col].dtype)
                            else:
                                df_gold.loc[mask_manual, col] = df_gold.loc[mask_manual, col_manual]
                        if mask_none.any():
                            df_gold.loc[mask_none, col] = pd.NA
                            
                        df_gold = df_gold.drop(columns=[col_manual])
    else:
        df_gold["INDICADOR_DADO_MANUAL"] = "NÃO"

    if "ORIGEM_REGISTRO" in df_gold.columns:
        df_gold["ORIGEM_ANALISE"] = df_gold["ORIGEM_REGISTRO"].fillna("FICHA")
    else:
        df_gold["ORIGEM_ANALISE"] = "FICHA"

    if "VALIDADE_EXCECAO" not in df_gold.columns:
        df_gold["VALIDADE_EXCECAO"] = pd.NaT

    if "PATRIMONIO_LIQUIDO" in df_gold.columns:
        df_gold["PATRIMONIO_LIQUIDO_AJUSTADO"] = df_gold["PATRIMONIO_LIQUIDO"]
    else:
        df_gold["PATRIMONIO_LIQUIDO_AJUSTADO"] = pd.NA

    if not df_bureau.empty and "CNPJ" in df_bureau.columns:
        df_b_unique = df_bureau.drop_duplicates("CNPJ", keep="last").copy()
        
        colunas_bureau = ["CNPJ"]
        for col in ["RATING_BUREAU", "PD_BUREAU", "SCORE_BUREAU", "RESTRITIVOS", "DATA_CONSULTA"]:
            if col in df_b_unique.columns:
                colunas_bureau.append(col)
                
        df_gold = pd.merge(df_gold, df_b_unique[colunas_bureau], on="CNPJ", how="left")
        
        if "METODOLOGIA_EXIGIDA" in df_gold.columns:
            mask_bureau = df_gold["METODOLOGIA_EXIGIDA"] == "BUREAU"
            
            if "RATING_BUREAU" in df_gold.columns:
                if "RATING_FINAL" not in df_gold.columns:
                    df_gold["RATING_FINAL"] = pd.NA
                df_gold.loc[mask_bureau, "RATING_FINAL"] = df_gold.loc[mask_bureau, "RATING_BUREAU"]
                    
            if "PD_BUREAU" in df_gold.columns:
                df_gold["PD_BUREAU"] = pd.to_numeric(df_gold["PD_BUREAU"], errors="coerce")
                if "PD_FINAL" not in df_gold.columns:
                    df_gold["PD_FINAL"] = pd.NA
                df_gold["PD_FINAL"] = pd.to_numeric(df_gold["PD_FINAL"], errors="coerce")
                df_gold.loc[mask_bureau, "PD_FINAL"] = df_gold.loc[mask_bureau, "PD_BUREAU"]

        if "SCORE_BUREAU" not in df_gold.columns: df_gold["SCORE_BUREAU"] = pd.NA
        if "RESTRITIVOS" not in df_gold.columns: df_gold["RESTRITIVOS"] = pd.NA
    else:
        df_gold["SCORE_BUREAU"] = pd.NA
        df_gold["RESTRITIVOS"] = pd.NA
        
    df_gold["DATA_DA_ANALISE"] = pd.NA
    if "DATA_BALANCO_USADO" in df_gold.columns:
        df_gold["DATA_DA_ANALISE"] = df_gold["DATA_BALANCO_USADO"]
        
    if "METODOLOGIA_EXIGIDA" in df_gold.columns and "DATA_CONSULTA" in df_gold.columns:
        mask_bureau = df_gold["METODOLOGIA_EXIGIDA"] == "BUREAU"
        df_gold.loc[mask_bureau, "DATA_DA_ANALISE"] = df_gold.loc[mask_bureau, "DATA_CONSULTA"]

    return df_gold

def exportar_visao_consolidada_gold(context: Any) -> dict[str, Any]:
    run_id = f"GOLD_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = obter_logger("bdc.gold", Path("LOGS/gold") / f"{run_id}__service_gold.log")
    logger.info("Construindo Visão Consolidada Gold (Master Join)...")
    hoje = pd.Timestamp("today").normalize()

    dfs = carregar_entradas_gold(context, logger)
    df_gold = construir_visao_consolidada(dfs, run_id, hoje)
    
    salvar_visao_gold(context, df_gold, hoje, run_id, logger)

    sit_analise = df_gold["SITUACAO_ANALISE"].fillna("").astype(str)
    met_exigida  = df_gold["METODOLOGIA_EXIGIDA"].fillna("").astype(str)
    stat_ctr     = df_gold["STATUS_CONTRATUAL"].fillna("").astype(str)

    mask_descoberto     = (stat_ctr == "CONTRATO_VIGENTE") & (sit_analise != "VIGENTE")
    mask_irregular      = (stat_ctr == "CONTRATO_VIGENTE") & (met_exigida == "DF_DETALHADA") & (sit_analise != "VIGENTE")
    mask_pendente_bureau = (stat_ctr == "CONTRATO_VIGENTE") & (met_exigida == "BUREAU")      & (sit_analise != "VIGENTE")

    return {
        "status": "SUCESSO",
        "total_contrapartes": len(df_gold),
        "contrato_vigente": int((df_gold["STATUS_CONTRATUAL"] == "CONTRATO_VIGENTE").sum()),
        "contrato_futuro": int((df_gold["STATUS_CONTRATUAL"] == "CONTRATO_FUTURO").sum()),
        "analise_vigente": int((df_gold["SITUACAO_ANALISE"].fillna("").astype(str) == "VIGENTE").sum()),
        "analise_vencida": int((df_gold["SITUACAO_ANALISE"].fillna("").astype(str) == "VENCIDA").sum()),
        "contrato_vig_sem_analise_vig": int(mask_descoberto.sum()),
        "contrato_irregular_sem_df": int(mask_irregular.sum()),
        "contrato_pendente_bureau": int(mask_pendente_bureau.sum()),
        "ficha_sem_contrato": int(((df_gold["TEM_ANALISE"] == "SIM") & (df_gold["STATUS_CONTRATUAL"] == "SEM_CONTRATO")).sum()),
        "contrato_sem_ficha": int(((df_gold["STATUS_CONTRATUAL"].isin(["CONTRATO_VIGENTE", "CONTRATO_FUTURO"])) & (df_gold["TEM_ANALISE"] == "NÃO")).sum()),
        "dados_incompletos": int((df_gold["SITUACAO_CADASTRAL"].isin(["NAO_INFORMADA", "PENDENTE"])).sum()),
        "ead_descoberto": float(df_gold.loc[mask_irregular, "EAD_VALOR"].sum(skipna=True)) if "EAD_VALOR" in df_gold.columns else 0.0,
    }