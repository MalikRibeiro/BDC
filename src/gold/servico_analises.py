import pandas as pd
from typing import Any
from common.dados import validar_coluna_cnpj_canonica
from gold.regras_gold import checar_contrato_obrigatorio
from datetime import datetime

def integrar_analises_gold(df_gold: pd.DataFrame, df_analises: pd.DataFrame, hoje: datetime) -> pd.DataFrame:
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
            
        if "SCORE_TOTAL" not in df_analises.columns and "SCORE" in df_analises.columns:
            df_analises["SCORE_TOTAL"] = df_analises["SCORE"]

        cols_analise_payload = [
            c for c in [
                "SITUACAO_ANALISE", "SITUACAO_DF", "RATING_FINAL", "PD_FINAL", 
                "MODELO_METODOLOGICO", "PATRIMONIO_LIQUIDO", "DATA_ANALISE", "DATA_BALANCO_USADO", "TEM_ANALISE",
                "MOTIVO_AUSENCIA_DF", "TIPO_EVENTO_MANUAL", "ORIGEM_REGISTRO", "VALIDADE_EXCECAO", "STATUS_CALCULO_PD",
                "FCO", "LUCRO_LIQUIDO", "ROA", "QUANTIDADE_RESTRITIVOS", "SCORE_BUREAU",
                "SCORE_TOTAL", "RESTRITIVOS", "TIPO_ANALISE", "ANALISE_HERDADA", "ORIGEM_ANALISE"
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
    
    return df_gold


def integrar_bureau_gold(df_gold: pd.DataFrame, df_bureau: pd.DataFrame) -> pd.DataFrame:
    if not df_bureau.empty and "CNPJ" in df_bureau.columns:
        df_b_unique = df_bureau.drop_duplicates("CNPJ", keep="last").copy()
        
        colunas_bureau = ["CNPJ"]
        for col in ["RATING_BUREAU", "PD_BUREAU", "SCORE_BUREAU", "RESTRITIVOS", "DATA_CONSULTA"]:
            if col in df_b_unique.columns:
                colunas_bureau.append(col)
                
        # Handle overlapping columns by renaming them before merge
        bureau_rename_map = {}
        for col in colunas_bureau:
            if col != "CNPJ" and col in df_gold.columns:
                bureau_rename_map[col] = f"{col}_BUREAU_MERGE"
                
        df_b_unique = df_b_unique[colunas_bureau].rename(columns=bureau_rename_map)
        df_gold = pd.merge(df_gold, df_b_unique, on="CNPJ", how="left")
        
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
        
        # Merge Restritivos from Bureau
        col_res_bureau = bureau_rename_map.get("RESTRITIVOS", "RESTRITIVOS")
        if col_res_bureau in df_gold.columns:
            if "RESTRITIVOS" not in df_gold.columns:
                df_gold["RESTRITIVOS"] = df_gold[col_res_bureau]
            else:
                # Se for herança, preferir restritivos locais do bureau
                mask_herdada = df_gold["ORIGEM_ANALISE"].astype(str).str.startswith("HERDADA")
                df_gold.loc[mask_herdada, "RESTRITIVOS"] = df_gold.loc[mask_herdada, col_res_bureau]
                # Fallback genérico
                df_gold["RESTRITIVOS"] = df_gold["RESTRITIVOS"].combine_first(df_gold[col_res_bureau])
            if col_res_bureau != "RESTRITIVOS":
                df_gold = df_gold.drop(columns=[col_res_bureau])
        else:
            if "RESTRITIVOS" not in df_gold.columns: df_gold["RESTRITIVOS"] = pd.NA
            
        # Hybrid logic for SCORE_TOTAL
        if "SCORE_TOTAL" in df_gold.columns and "SCORE_BUREAU" in df_gold.columns:
            mask_herdada = df_gold["ORIGEM_ANALISE"].astype(str).str.startswith("HERDADA")
            df_gold.loc[mask_herdada, "SCORE_TOTAL"] = df_gold.loc[mask_herdada, "SCORE_TOTAL"].combine_first(df_gold.loc[mask_herdada, "SCORE_BUREAU"])
            
    else:
        df_gold["SCORE_BUREAU"] = pd.NA
        if "RESTRITIVOS" not in df_gold.columns: df_gold["RESTRITIVOS"] = pd.NA
        
    return df_gold
