import pandas as pd
from typing import Any
from app.context import AppContext

def construir_fato_score_rating_pd(context: AppContext, df_fato_analise: pd.DataFrame) -> dict[str, Any]:
    if df_fato_analise.empty:
        return {"status": "SEM_DADOS"}

    colunas = [
        "ANALISE_ID", "CNPJ", "DATA_ANALISE", "FIM_VIGENCIA_ANALISE", "RATING", 
        "PD_PERCENTUAL", "SCORE", "CLASSE", "MODELO", "CONFIG_SNAPSHOT_PD",
        "PD_OFICIAL_FICHA", "PD_RECALCULADA_PYTHON", "STATUS_AUDITORIA_PD", 
        "DELTA_PD", "STATUS_AUDITORIA_RATING"
    ]
    disponiveis = [c for c in colunas if c in df_fato_analise.columns]
    df_score = df_fato_analise[disponiveis].copy()
    
    out_dir = context.path("relational_facts") / "credito"
    out_dir.mkdir(parents=True, exist_ok=True)
    df_score.to_parquet(out_dir / "fato_score_rating_pd.parquet", index=False)
    
    return {"status": "SUCESSO", "linhas": len(df_score)}

def processar_fato_score_rating_pd(context: AppContext) -> dict[str, Any]:
    fato_path = context.path("relational_facts") / "credito" / "fato_analise_credito.parquet"
    df_fato = pd.read_parquet(fato_path) if fato_path.exists() else pd.DataFrame()
    return construir_fato_score_rating_pd(context, df_fato)
