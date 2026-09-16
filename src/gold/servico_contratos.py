import pandas as pd
from typing import Any
from common.dados import validar_coluna_cnpj_canonica
from gold.regras_gold import checar_contrato_obrigatorio
from datetime import datetime

def integrar_contratos_gold(df_gold: pd.DataFrame, df_contratos: pd.DataFrame, hoje: datetime) -> pd.DataFrame:
    # 1. Garante que todo CNPJ com contrato sobreviva na Gold (mesmo sem contraparte mapeada)
    if not df_contratos.empty:
        cnpjs_contratos = set(df_contratos["CNPJ"].dropna().unique())
        cnpjs_gold = set(df_gold["CNPJ"].dropna().unique())
        cnpjs_faltantes = cnpjs_contratos - cnpjs_gold
        if cnpjs_faltantes:
            df_missing = pd.DataFrame({"CNPJ": list(cnpjs_faltantes)})
            df_missing["CNPJ_RAIZ"] = df_missing["CNPJ"].str[:8]
            df_gold = pd.concat([df_gold, df_missing], ignore_index=True)

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

        col_nome_contrato = "CONTRAPARTE_APELIDO" if "CONTRAPARTE_APELIDO" in df_contratos.columns else "CNPJ"
        
        resumo_contratos = df_contratos.groupby("CNPJ").agg(
            QUANTIDADE_CONTRATOS=(col_id, "nunique") if col_id in df_contratos.columns else ("CNPJ", "count"),
            NUMERACAO_CONTRATOS=(col_id, lambda x: ", ".join(x.dropna().astype(str).unique())) if col_id in df_contratos.columns else ("CNPJ", lambda x: ""),
            STATUS_CONTRATUAL=("EH_VIGENTE", lambda x: "CONTRATO_VIGENTE" if x.any() else ("CONTRATO_FUTURO" if df_contratos.loc[x.index, "EH_FUTURO"].any() else "SEM_CONTRATO")),
            PROXIMO_INICIO=("DT_INICIO", "min"),
            PROXIMO_FIM=("DT_FIM", "max"),
            NOME_CONTRATO_FALLBACK=(col_nome_contrato, lambda x: next((v for v in x.dropna() if str(v).strip() != ""), ""))
        ).reset_index()

        resumo_contratos["ANO_INICIO_CONTRATO"] = resumo_contratos["PROXIMO_INICIO"].dt.year.fillna(0).astype(int)

        resumo_contratos["CNPJ_RAIZ"] = resumo_contratos["CNPJ"].str[:8]
        df_contratos_gold = pd.merge(resumo_contratos, df_vol_enquadramento[["CNPJ_RAIZ", "VOLUME_MWM"]], on="CNPJ_RAIZ", how="left")
        df_gold = pd.merge(df_gold, df_contratos_gold, on="CNPJ", how="left")
        
        # Fallback de NOME com base no CONTRAPARTE_APELIDO do contrato
        if "NOME_CONTRATO_FALLBACK" in df_gold.columns:
            mask_nome_vazio = df_gold["NOME"].isna() | (df_gold["NOME"].astype(str).str.strip() == "") | (df_gold["NOME"].astype(str).str.lower() == "nan")
            df_gold.loc[mask_nome_vazio, "NOME"] = df_gold.loc[mask_nome_vazio, "NOME_CONTRATO_FALLBACK"]
            df_gold = df_gold.drop(columns=["NOME_CONTRATO_FALLBACK"])
    else:
        df_gold["STATUS_CONTRATUAL"] = "SEM_CONTRATO"
        df_gold["VOLUME_MWM"] = 0.0
        df_gold["NUMERACAO_CONTRATOS"] = ""
        df_gold["QUANTIDADE_CONTRATOS"] = 0
        df_gold["ANO_INICIO_CONTRATO"] = 0
        df_gold["PROXIMO_INICIO"] = pd.NaT
        df_gold["PROXIMO_FIM"] = pd.NaT
        
    df_gold["TEM_CONTRATO"] = df_gold["STATUS_CONTRATUAL"].apply(lambda x: "SIM" if x in ["CONTRATO_VIGENTE", "CONTRATO_FUTURO"] else "NÃO")

    return df_gold
