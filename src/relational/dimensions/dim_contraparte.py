"""Serviço de consolidação da Dimensão de Contraparte."""
from __future__ import annotations
import logging
from datetime import datetime
from typing import Any
import pandas as pd

from app.context import AppContext
from storage.escrever_dados import escrever_conjunto_de_dados_silver

def processar_dim_contraparte(context: AppContext) -> dict[str, Any]:
    """Orquestra a leitura de dependências e construção da Dimensão de Contraparte."""
    logger = logging.getLogger("bdc.gold.dim_contraparte")
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
    
    df_fichas = pd.DataFrame()
    for segmento_dir in ["fichas_comercializadoras_extraidas", "fichas_consumidores_extraidas"]:
        seg_path = context.path("silver") / segmento_dir
        if seg_path.exists():
            parquets = list(seg_path.glob("*.parquet"))
            if parquets:
                df_seg_fichas = pd.read_parquet(max(parquets, key=lambda f: f.stat().st_mtime))
                df_fichas = pd.concat([df_fichas, df_seg_fichas], ignore_index=True)

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
    logger = logging.getLogger("bdc.gold.dim_contraparte")

    if df_silver_receita.empty:
        df_silver_receita = pd.DataFrame(columns=["CNPJ", "SITUACAO_CADASTRAL", "NATUREZA_JURIDICA", "CNAE_PRINCIPAL"])
    if df_silver_segmentacao.empty:
        df_silver_segmentacao = pd.DataFrame(columns=["CNPJ", "VOLUME_ENQUADRAMENTO_MWM", "POSSUI_PELO_MENOS_5_MWM", "SEGMENTO_METODOLOGICO"])

    from common.identificadores import normalizar_cnpj
    df_silver_receita["CNPJ"] = df_silver_receita["CNPJ"].apply(lambda x: normalizar_cnpj(x).cnpj if normalizar_cnpj(x).valido else None)
    df_silver_segmentacao["CNPJ"] = df_silver_segmentacao["CNPJ"].apply(lambda x: normalizar_cnpj(x).cnpj if normalizar_cnpj(x).valido else None)

    df_dim = pd.merge(df_silver_receita, df_silver_segmentacao, on="CNPJ", how="outer")

    if df_silver_fichas is not None and not df_silver_fichas.empty:
        df_fichas = df_silver_fichas.copy()
        df_fichas["CNPJ"] = df_fichas["CNPJ"].apply(lambda x: normalizar_cnpj(x).cnpj if normalizar_cnpj(x).valido else None)
        df_fichas["NOME_FICHA"] = df_fichas.get("EMPRESA", None)
        df_fichas["SIGLA_FICHA"] = df_fichas.get("SIGLA", None)
        
        col_sort = "DT_PROCESSAMENTO" if "DT_PROCESSAMENTO" in df_fichas.columns else "CNPJ"
        df_id_fichas = df_fichas.sort_values(col_sort).drop_duplicates("CNPJ", keep="last")[["CNPJ", "NOME_FICHA", "SIGLA_FICHA"]]
        df_dim = pd.merge(df_dim, df_id_fichas, on="CNPJ", how="outer")
    else:
        df_dim["NOME_FICHA"] = None
        df_dim["SIGLA_FICHA"] = None

    if df_silver_salesforce_account is not None and not df_silver_salesforce_account.empty:
        df_sf = df_silver_salesforce_account.copy()
        df_sf["CNPJ"] = df_sf["CNPJ"].apply(lambda x: normalizar_cnpj(x).cnpj if normalizar_cnpj(x).valido else None)
        sf_cols = {"CNPJ": "CNPJ", "Name": "NOME_SF", "Sigla__c": "SIGLA_SF"}
        df_sf_id = df_sf[[c for c in sf_cols.keys() if c in df_sf.columns]].rename(columns=sf_cols)
        df_sf_id = df_sf_id.drop_duplicates(subset=["CNPJ"], keep="last")
        df_dim = pd.merge(df_dim, df_sf_id, on="CNPJ", how="outer")
    else:
        df_dim["NOME_SF"] = None
        df_dim["SIGLA_SF"] = None

    for col_safe in ["NOME_SF", "SIGLA_SF", "NOME_FICHA", "SIGLA_FICHA"]:
        if col_safe not in df_dim.columns:
            df_dim[col_safe] = None

    df_dim["NOME"] = df_dim["NOME_SF"].combine_first(df_dim["NOME_FICHA"])
    df_dim["SIGLA"] = df_dim["SIGLA_SF"].combine_first(df_dim["SIGLA_FICHA"])

    # --- Enriquecimento com Grupo Econômico (Controladoras) ---
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

    df_dim["GRUPO_ECONOMICO"] = df_dim["NOME_CONTROLADORA"].combine_first(df_dim["NOME"])
    # --------------------------------------------------------

    df_dim = df_dim.dropna(subset=["CNPJ"])
    df_dim["CNPJ_RAIZ"] = df_dim["CNPJ"].str[:8]
    
    # Garante a existência das colunas para evitar KeyError
    for col in ["SITUACAO_CADASTRAL", "SEGMENTO_METODOLOGICO", "CNAE_PRINCIPAL"]:
        if col not in df_dim.columns:
            df_dim[col] = None
            
    df_dim["SITUACAO_CADASTRAL"] = df_dim["SITUACAO_CADASTRAL"].fillna("NAO_INFORMADO")
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