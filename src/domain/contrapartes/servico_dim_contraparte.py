"""Serviço de consolidação da Dimensão de Contraparte."""
from __future__ import annotations
import logging
from datetime import datetime
from typing import Any
import pandas as pd

from app.context import AppContext
from storage.escrever_dados import escrever_conjunto_de_dados_silver

def criar_dim_contraparte(
    context: AppContext, 
    df_silver_receita: pd.DataFrame, 
    df_silver_segmentacao: pd.DataFrame,
    df_silver_salesforce_account: pd.DataFrame = None,
    df_silver_fichas: pd.DataFrame = None
) -> dict[str, Any]:
    run_id = f"DIM_CTR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = logging.getLogger("bdc.gold.dim_contraparte")

    if df_silver_receita.empty:
        df_silver_receita = pd.DataFrame(columns=["CNPJ", "SITUACAO_CADASTRAL", "NATUREZA_JURIDICA", "CNAE_PRINCIPAL"])
    if df_silver_segmentacao.empty:
        df_silver_segmentacao = pd.DataFrame(columns=["CNPJ", "VOLUME_ENQUADRAMENTO_MWM", "POSSUI_PELO_MENOS_5_MWM", "SEGMENTO_METODOLOGICO"])

    df_silver_receita["CNPJ"] = df_silver_receita["CNPJ"].astype(str).str.replace(r"\D", "", regex=True).str.zfill(14)
    df_silver_segmentacao["CNPJ"] = df_silver_segmentacao["CNPJ"].astype(str).str.replace(r"\D", "", regex=True).str.zfill(14)

    # 1. Junta Receita + Segmentação
    df_dim = pd.merge(df_silver_receita, df_silver_segmentacao, on="CNPJ", how="outer")

    # 2. Resgata Identidade das Fichas
    if df_silver_fichas is not None and not df_silver_fichas.empty:
        df_fichas = df_silver_fichas.copy()
        df_fichas["CNPJ"] = df_fichas["CNPJ"].astype(str).str.replace(r"\D", "", regex=True).str.zfill(14)
        df_fichas["NOME_FICHA"] = df_fichas.get("EMPRESA", None)
        df_fichas["SIGLA_FICHA"] = df_fichas.get("SIGLA", None)
        
        # Pega o nome mais recente caso haja múltiplas fichas
        col_sort = "DT_PROCESSAMENTO" if "DT_PROCESSAMENTO" in df_fichas.columns else "CNPJ"
        df_id_fichas = df_fichas.sort_values(col_sort).drop_duplicates("CNPJ", keep="last")[["CNPJ", "NOME_FICHA", "SIGLA_FICHA"]]
        df_dim = pd.merge(df_dim, df_id_fichas, on="CNPJ", how="outer")
    else:
        df_dim["NOME_FICHA"] = None
        df_dim["SIGLA_FICHA"] = None

    # 3. Integra Salesforce (NOME e SIGLA)
    if df_silver_salesforce_account is not None and not df_silver_salesforce_account.empty:
        df_sf = df_silver_salesforce_account.copy()
        df_sf["CNPJ"] = df_sf["CNPJ"].astype(str).str.replace(r"\D", "", regex=True).str.zfill(14)
        sf_cols = {"CNPJ": "CNPJ", "Name": "NOME_SF", "Sigla__c": "SIGLA_SF"}
        df_sf_id = df_sf[[c for c in sf_cols.keys() if c in df_sf.columns]].rename(columns=sf_cols)
        df_sf_id = df_sf_id.drop_duplicates(subset=["CNPJ"], keep="last")
        df_dim = pd.merge(df_dim, df_sf_id, on="CNPJ", how="outer")
    else:
        df_dim["NOME_SF"] = None
        df_dim["SIGLA_SF"] = None

    # Garante que as colunas existam mesmo se as bases originais não as tiverem
    for col_safe in ["NOME_SF", "SIGLA_SF", "NOME_FICHA", "SIGLA_FICHA"]:
        if col_safe not in df_dim.columns:
            df_dim[col_safe] = None

    # 4. COALESCE (Salesforce tem prioridade, Ficha é o Fallback)
    df_dim["NOME"] = df_dim["NOME_SF"].combine_first(df_dim["NOME_FICHA"])
    df_dim["SIGLA"] = df_dim["SIGLA_SF"].combine_first(df_dim["SIGLA_FICHA"])

    df_dim = df_dim.dropna(subset=["CNPJ"])
    df_dim["CNPJ_RAIZ"] = df_dim["CNPJ"].str[:8]
    df_dim["SITUACAO_CADASTRAL"] = df_dim["SITUACAO_CADASTRAL"].fillna("NAO_INFORMADO")
    df_dim["SEGMENTO_METODOLOGICO"] = df_dim["SEGMENTO_METODOLOGICO"].fillna("NAO_ENQUADRADO")

    schema_dim = {
        "CNPJ": "CNPJ", "NOME": "NOME", "SIGLA": "SIGLA", "CNPJ_RAIZ": "CNPJ_RAIZ", 
        "SITUACAO_CADASTRAL": "SITUACAO_CADASTRAL", "CNAE_PRINCIPAL": "SETOR", 
        "SEGMENTO_METODOLOGICO": "SEGMENTO_METODOLOGICO"
    }
    
    df_final = df_dim[list(schema_dim.keys())].rename(columns=schema_dim).copy()
    
    relational_dir = context.path("relational_dimensions")
    relational_dir.mkdir(parents=True, exist_ok=True)
    escrever_conjunto_de_dados_silver(df_final.to_dict(orient="records"), relational_dir, f"dim_contraparte_{run_id}")
    df_final.to_parquet(relational_dir / "dim_contraparte.parquet", index=False)

    logger.info("Dimensão Contraparte construída com COALESCE. Registros: %d", len(df_final))
    return {"run_id": run_id, "linhas": len(df_final), "status": "SUCESSO"}