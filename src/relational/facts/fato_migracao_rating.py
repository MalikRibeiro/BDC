import pandas as pd
from typing import Any
from app.context import AppContext

def construir_fato_migracao_rating(context: AppContext, df_fato_analise: pd.DataFrame, cfg_escala_rating: dict[str, int]) -> dict[str, Any]:
    """Constrói a Fato Migração de Rating com base no histórico de análises.
    Convenção: POSITIVO = PIORA (Rating maior/pior = downgrade)
    NEGATIVO = MELHORA (Rating menor/melhor = upgrade)
    """
    if df_fato_analise.empty or "CNPJ" not in df_fato_analise.columns:
        return {"status": "SEM_DADOS"}
        
    df_hist = df_fato_analise.sort_values(by=["CNPJ", "DATA_ANALISE"]).copy()
    
    # Criar colunas de anterior usando shift
    df_hist["rating_anterior"] = df_hist.groupby("CNPJ")["RATING"].shift(1)
    df_hist["pd_anterior"] = df_hist.groupby("CNPJ")["PD_PERCENTUAL"].shift(1)
    
    # Filtra apenas os que possuem avaliação anterior (migrações)
    df_migr = df_hist.dropna(subset=["rating_anterior"]).copy()
    if df_migr.empty:
        return {"status": "SEM_MIGRACAO", "linhas": 0}
        
    df_migr["rating_atual"] = df_migr["RATING"]
    df_migr["pd_atual"] = df_migr["PD_PERCENTUAL"]
    df_migr["data_alteracao"] = df_migr["DATA_ANALISE"]
    
    # Delta PD = Atual - Anterior (Positivo = Aumentou PD = Piorou)
    df_migr["delta_pd"] = df_migr["pd_atual"] - df_migr["pd_anterior"]
    
    def calc_variacao_graus(rating_atual, rating_ant):
        # Mapeamento do rating para ordem numérica
        ordem_atual = cfg_escala_rating.get(rating_atual, 0)
        ordem_ant = cfg_escala_rating.get(rating_ant, 0)
        return ordem_atual - ordem_ant
        
    df_migr["variacao_em_graus"] = df_migr.apply(
        lambda r: calc_variacao_graus(r["rating_atual"], r["rating_anterior"]), axis=1
    )
    
    def determinar_direcao(var):
        if var > 0: return "PIORA"
        elif var < 0: return "MELHORA"
        return "ESTÁVEL"
        
    df_migr["direcao_migracao"] = df_migr["variacao_em_graus"].apply(determinar_direcao)
    
    colunas_saida = ["CNPJ", "ANALISE_ID", "data_alteracao", "rating_anterior", "rating_atual", "variacao_em_graus", 
                     "pd_anterior", "pd_atual", "delta_pd", "direcao_migracao"]
    
    df_final = df_migr[colunas_saida]
    out_dir = context.path("relational_facts") / "credito"
    out_dir.mkdir(parents=True, exist_ok=True)
    df_final.to_parquet(out_dir / "fato_migracao_rating.parquet", index=False)
    
    return {"status": "SUCESSO", "linhas": len(df_final)}

def processar_fato_migracao_rating(context: AppContext) -> dict[str, Any]:
    fato_path = context.path("relational_facts") / "credito" / "fato_analise_credito.parquet"
    df_fato = pd.read_parquet(fato_path) if fato_path.exists() else pd.DataFrame()
    cfg_escala_rating = {"AAA": 1, "AA": 2, "A": 3, "BBB": 4, "BB": 5, "B": 6, "CCC": 7, "CC": 8, "C": 9, "D": 10, "E": 11}
    return construir_fato_migracao_rating(context, df_fato, cfg_escala_rating)
