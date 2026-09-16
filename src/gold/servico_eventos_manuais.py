import pandas as pd

def integrar_eventos_manuais_gold(df_gold: pd.DataFrame, df_eventos: pd.DataFrame) -> pd.DataFrame:
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
        
    return df_gold
