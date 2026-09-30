"""Serviço de consolidação da Dimensão de Contraparte."""
from __future__ import annotations
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from app.context import AppContext
from control.logger import obter_logger
from storage.escrever_dados import escrever_conjunto_de_dados_silver

def processar_dim_contraparte(context: AppContext) -> dict[str, Any]:
    """Orquestra a leitura de dependências e construção da Dimensão de Contraparte."""
    run_id = f"DIM_CTR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = obter_logger("bdc.dim_contraparte", Path("LOGS/relational") / f"{run_id}__dim_contraparte.log")
    logger.info("Iniciando processamento da Dimensão de Contraparte...")
    
    receita_path = context.path("silver") / "receita_silver" / "receita_cadastral_silver.parquet"
    enquadra_path = context.path("relational_configs") / f"enquadramento_consumidores_{datetime.now().strftime('%Y%m')}.csv"
    salesforce_path = context.path("silver") / "salesforce_silver" / "account" / "salesforce_account.parquet"
    
    df_receita = pd.read_parquet(receita_path) if receita_path.exists() else pd.DataFrame()
    df_seg = pd.read_csv(enquadra_path) if enquadra_path.exists() else pd.DataFrame()
    df_sf_account = pd.read_parquet(salesforce_path) if salesforce_path.exists() else pd.DataFrame()
    
    ctrl_path = context.path("silver") / "mapeamento_controladoras" / "mapeamento_controladoras.parquet"
    df_ctrl = pd.read_parquet(ctrl_path) if ctrl_path.exists() else pd.DataFrame()
    if not df_ctrl.empty and "_STATUS_REGISTRO" in df_ctrl.columns:
        df_ctrl = df_ctrl[df_ctrl["_STATUS_REGISTRO"] == "VIGENTE"]
    
    from common.dados import carregar_fichas_silver_consolidadas
    df_fichas = carregar_fichas_silver_consolidadas(context.path("silver"))

    return criar_dim_contraparte(
        context, 
        df_silver_receita=df_receita, 
        df_silver_segmentacao=df_seg,
        df_silver_salesforce_account=df_sf_account,
        df_silver_fichas=df_fichas,
        df_controladoras=df_ctrl
    )


def criar_dim_contraparte(
    context: AppContext, 
    df_silver_receita: pd.DataFrame, 
    df_silver_segmentacao: pd.DataFrame,
    df_silver_salesforce_account: pd.DataFrame = None,
    df_silver_fichas: pd.DataFrame = None,
    df_controladoras: pd.DataFrame = None
) -> dict[str, Any]:
    run_id = f"DIM_CTR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = obter_logger("bdc.dim_contraparte", Path("LOGS/relational") / f"{run_id}__dim_contraparte.log")

    if df_silver_receita.empty:
        df_silver_receita = pd.DataFrame(columns=["CNPJ", "SITUACAO_CADASTRAL", "NATUREZA_JURIDICA", "CNAE_PRINCIPAL"])
    if df_silver_segmentacao.empty:
        df_silver_segmentacao = pd.DataFrame(columns=["CNPJ", "VOLUME_ENQUADRAMENTO_MWM", "POSSUI_PELO_MENOS_5_MWM", "SEGMENTO_METODOLOGICO"])

    from common.identificadores import normalizar_cnpj_coluna
    df_silver_receita["CNPJ"] = df_silver_receita["CNPJ"].apply(normalizar_cnpj_coluna)
    df_silver_segmentacao["CNPJ"] = df_silver_segmentacao["CNPJ"].apply(normalizar_cnpj_coluna)

    df_dim = pd.merge(df_silver_receita, df_silver_segmentacao, on="CNPJ", how="outer")

    if df_silver_fichas is not None and not df_silver_fichas.empty:
        df_fichas = df_silver_fichas.copy()
        df_fichas["CNPJ"] = df_fichas["CNPJ"].apply(normalizar_cnpj_coluna)
        df_fichas["NOME_FICHA"] = df_fichas.get("RAZAO_SOCIAL", None)
        df_fichas["SIGLA_FICHA"] = df_fichas.get("SIGLA", None)
        
        col_sort = "DT_PROCESSAMENTO" if "DT_PROCESSAMENTO" in df_fichas.columns else "CNPJ"
        df_id_fichas = df_fichas.sort_values(col_sort).drop_duplicates("CNPJ", keep="last")[["CNPJ", "NOME_FICHA", "SIGLA_FICHA"]]
        df_dim = pd.merge(df_dim, df_id_fichas, on="CNPJ", how="outer")
    else:
        df_dim["NOME_FICHA"] = None
        df_dim["SIGLA_FICHA"] = None

    if df_silver_salesforce_account is not None and not df_silver_salesforce_account.empty:
        df_sf = df_silver_salesforce_account.copy()
        df_sf["CNPJ"] = df_sf["CNPJ"].apply(normalizar_cnpj_coluna)
        sf_cols = {
            "CNPJ": "CNPJ",
            "Name": "NOME_SF",
            "Sigla__c": "SIGLA_SF",
            "Grupo_economico__c": "GRUPO_ECONOMICO_SF"
        }
        df_sf_id = df_sf[[c for c in sf_cols.keys() if c in df_sf.columns]].rename(columns=sf_cols)
        df_sf_id = df_sf_id.drop_duplicates(subset=["CNPJ"], keep="last")
        df_dim = pd.merge(df_dim, df_sf_id, on="CNPJ", how="outer")
    else:
        df_dim["NOME_SF"] = None
        df_dim["SIGLA_SF"] = None
        df_dim["GRUPO_ECONOMICO_SF"] = None

    for col_safe in ["NOME_SF", "SIGLA_SF", "NOME_FICHA", "SIGLA_FICHA", "GRUPO_ECONOMICO_SF"]:
        if col_safe not in df_dim.columns:
            df_dim[col_safe] = None

    df_dim["NOME"] = df_dim["NOME_SF"].combine_first(df_dim["NOME_FICHA"])
    df_dim["SIGLA"] = df_dim["SIGLA_SF"].combine_first(df_dim["SIGLA_FICHA"])

    # --- Enriquecimento com Grupo Econômico (Controladoras + Salesforce) ---
    if df_controladoras is not None and not df_controladoras.empty:
        df_ctrl_sub = df_controladoras[["CNPJ_SUBSIDIARIA", "CNPJ_CONTA_ATRELADA", "CONTA_ATRELADA"]].rename(columns={
            "CNPJ_SUBSIDIARIA": "CNPJ",
            "CNPJ_CONTA_ATRELADA": "CNPJ_CONTROLADORA",
            "CONTA_ATRELADA": "NOME_CONTROLADORA"
        }).drop_duplicates(subset=["CNPJ"], keep="last")
        df_dim = pd.merge(df_dim, df_ctrl_sub, on="CNPJ", how="left")
    else:
        df_dim["CNPJ_CONTROLADORA"] = None
        df_dim["NOME_CONTROLADORA"] = None

    df_dim["NOME_CONTROLADORA"] = df_dim["NOME_CONTROLADORA"].replace({"": None, "None": None, "nan": None, "<NA>": None})
    df_dim["GRUPO_ECONOMICO_SF"] = df_dim["GRUPO_ECONOMICO_SF"].replace({"": None, "None": None, "nan": None, "<NA>": None})

    df_dim["GRUPO_ECONOMICO"] = (
        df_dim["NOME_CONTROLADORA"]
        .combine_first(df_dim["GRUPO_ECONOMICO_SF"])
        .combine_first(df_dim["NOME"])
    )

    # BUG 1 FIX: Quando o CSV estático não mapeou a controladora mas o Salesforce
    # preencheu o grupo econômico, tentar casamento de nome com correspondência unívoca.
    mask_ctrl_nulo = df_dim["CNPJ_CONTROLADORA"].isna() & df_dim["GRUPO_ECONOMICO_SF"].notna()
    if mask_ctrl_nulo.any():
        from common.texto import normalizar_chave_textual
        # Base de busca: contrapartes conhecidas com nome e CNPJ
        candidatos_base = df_dim[["CNPJ", "NOME"]].dropna().copy()
        candidatos_base["NOME_NORM"] = candidatos_base["NOME"].apply(normalizar_chave_textual)
        candidatos_base = candidatos_base[candidatos_base["NOME_NORM"].notna()]
        candidatos_base["CNPJ_RAIZ"] = candidatos_base["CNPJ"].str[:8]
        candidatos_base["IS_SEDE"] = candidatos_base["CNPJ"].str[8:12] == "0001"

        mapa_nome_cnpj: dict[str, str] = {}
        for nome_norm, grp in candidatos_base.groupby("NOME_NORM"):
            raizes_unicas = grp["CNPJ_RAIZ"].unique()
            # Apenas se houver correspondência unívoca (uma única raiz corporativa)
            if len(raizes_unicas) == 1:
                # Preferir a sede (0001) se disponível
                sede = grp.sort_values("IS_SEDE", ascending=False).iloc[0]["CNPJ"]
                mapa_nome_cnpj[nome_norm] = sede

        for idx in df_dim[mask_ctrl_nulo].index:
            grupo_nome_norm = normalizar_chave_textual(df_dim.at[idx, "GRUPO_ECONOMICO_SF"])
            if grupo_nome_norm and grupo_nome_norm in mapa_nome_cnpj:
                cnpj_encontrado = mapa_nome_cnpj[grupo_nome_norm]
                # A empresa não pode ser controladora de si mesma
                if cnpj_encontrado != df_dim.at[idx, "CNPJ"]:
                    df_dim.at[idx, "CNPJ_CONTROLADORA"] = cnpj_encontrado

    df_dim = df_dim.dropna(subset=["CNPJ"])
    df_dim["CNPJ_RAIZ"] = df_dim["CNPJ"].str[:8]
    
    # Garante a existência das colunas para evitar KeyError
    for col in ["SITUACAO_CADASTRAL", "CNAE_PRINCIPAL"]:
        if col not in df_dim.columns:
            df_dim[col] = None
            
    df_dim["SITUACAO_CADASTRAL"] = df_dim["SITUACAO_CADASTRAL"].fillna("NAO_INFORMADO")

    # BUG 2 FIX: Enquadramento Metodológico Canônico
    if "SEGMENTO_METODOLOGICO" not in df_dim.columns:
        df_dim["SEGMENTO_METODOLOGICO"] = None

    # 1. Comercializadoras têm precedência absoluta (CPURA / CGRUPO)
    if df_silver_fichas is not None and not df_silver_fichas.empty:
        df_fichas_seg = df_silver_fichas.copy()
        df_fichas_seg["CNPJ"] = df_fichas_seg["CNPJ"].apply(normalizar_cnpj_coluna)
        if "TIPO_FICHA" in df_fichas_seg.columns:
            mask_com = df_fichas_seg["TIPO_FICHA"].astype(str).str.upper() == "COMERCIALIZADORA"
            tipo_com_col = "TIPO_COMERCIALIZADORA" if "TIPO_COMERCIALIZADORA" in df_fichas_seg.columns else None
            df_fichas_seg["_SEG"] = None
            if tipo_com_col:
                df_fichas_seg.loc[mask_com & (df_fichas_seg[tipo_com_col].astype(str).str.upper() == "CPURA"), "_SEG"] = "CPURA"
                df_fichas_seg.loc[mask_com & (df_fichas_seg[tipo_com_col].astype(str).str.upper() == "CGRUPO"), "_SEG"] = "CGRUPO"
            df_fichas_seg.loc[mask_com & df_fichas_seg["_SEG"].isna(), "_SEG"] = "CGRUPO"
            
            mask_cons_ficha = df_fichas_seg["TIPO_FICHA"].astype(str).str.upper() == "CONSUMIDOR"
            df_fichas_seg.loc[mask_cons_ficha & df_fichas_seg["_SEG"].isna(), "_SEG"] = "CONSUMIDOR"

            df_com_map = df_fichas_seg.dropna(subset=["_SEG"]).drop_duplicates("CNPJ", keep="last")[["CNPJ", "_SEG"]]
            df_dim = pd.merge(df_dim, df_com_map, on="CNPJ", how="left")
            df_dim.loc[df_dim["_SEG"].isin(["CPURA", "CGRUPO"]), "SEGMENTO_METODOLOGICO"] = df_dim["_SEG"]
            df_dim.drop(columns=["_SEG"], inplace=True)

    # 2. Consumidores e Enquadramento por Volume (regra dos 5 MWm)
    vol_num = pd.to_numeric(df_dim.get("VOLUME_ENQUADRAMENTO_MWM"), errors="coerce")
    possui_5 = df_dim.get("POSSUI_PELO_MENOS_5_MWM")

    mask_nao_definido = df_dim["SEGMENTO_METODOLOGICO"].isna() | df_dim["SEGMENTO_METODOLOGICO"].isin(["NAO_ENQUADRADO", "CONSUMIDOR", ""])

    cond_gt5 = mask_nao_definido & ((possui_5 == True) | (vol_num >= 5.0))
    cond_le5 = mask_nao_definido & ((possui_5 == False) | ((vol_num < 5.0) & vol_num.notna()))

    df_dim.loc[cond_gt5, "SEGMENTO_METODOLOGICO"] = "CONSUMIDOR_GT_5"
    df_dim.loc[cond_le5, "SEGMENTO_METODOLOGICO"] = "CONSUMIDOR_LE_5"

    # Se ainda estiver sem enquadramento:
    df_dim["SEGMENTO_METODOLOGICO"] = df_dim["SEGMENTO_METODOLOGICO"].fillna("NAO_ENQUADRADO")

    schema_dim = {
        "CNPJ": "CNPJ", "NOME": "NOME", "SIGLA": "SIGLA", "CNPJ_RAIZ": "CNPJ_RAIZ", 
        "SITUACAO_CADASTRAL": "SITUACAO_CADASTRAL", "CNAE_PRINCIPAL": "SETOR", 
        "SEGMENTO_METODOLOGICO": "SEGMENTO_METODOLOGICO",
        "GRUPO_ECONOMICO": "GRUPO_ECONOMICO", "CNPJ_CONTROLADORA": "CNPJ_CONTROLADORA"
    }
    
    df_final = df_dim[list(schema_dim.keys())].rename(columns=schema_dim).copy()
    
    relational_dir = context.path("relational_dimensions") / "contrapartes"
    relational_dir.mkdir(parents=True, exist_ok=True)
    escrever_conjunto_de_dados_silver(df_final.to_dict(orient="records"), relational_dir, f"dim_contraparte_{run_id}")
    df_final.to_parquet(relational_dir / "dim_contraparte.parquet", index=False)

    logger.info("Dimensão Contraparte construída com COALESCE. Registros: %d", len(df_final))
    return {"run_id": run_id, "linhas": len(df_final), "status": "SUCESSO"}