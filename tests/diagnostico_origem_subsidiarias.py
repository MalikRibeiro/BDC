"""Diagnóstico da origem das linhas de subsidiárias em fato_analise_credito."""
import pandas as pd
from pathlib import Path

def main():
    base_dir = Path("SAIDAS")
    fato_path = base_dir / "relational" / "facts" / "credito" / "fato_analise_credito.parquet"
    df_fato = pd.read_parquet(fato_path) if fato_path.exists() else pd.DataFrame()

    # Amostra de SPE subsidiária
    cnpj_sub = "36205095000127"
    
    print(f"=== INVESTIGANDO CNPJ SUBSIDIÁRIA: {cnpj_sub} ===")
    sub_fato = df_fato[df_fato["CNPJ"] == cnpj_sub]
    print(f"Linhas na fato_analise_credito: {len(sub_fato)}")
    if not sub_fato.empty:
        cols = ["CNPJ", "RATING", "PD_PERCENTUAL", "TIPO_ANALISE", "FONTE_ANALISE", "ORIGEM_FONTE", "ORIGEM_ANALISE", "ANALISE_HERDADA", "_STATUS_REGISTRO", "_VERSAO_REGISTRO"]
        presentes = [c for c in cols if c in sub_fato.columns]
        print(sub_fato[presentes].to_dict(orient="records"))

    # Checar na Silver de Fichas Comercializadoras
    f_com = base_dir / "silver" / "fichas_comercializadoras_extraidas" / "fichas_comercializadoras_extraidas.parquet"
    if f_com.exists():
        df_c = pd.read_parquet(f_com)
        tem_com = cnpj_sub in df_c.get("CNPJ", pd.Series()).values
        print(f"Está em fichas_comercializadoras_extraidas? {tem_com}")

    # Checar na Silver de Fichas Consumidores
    f_cons = base_dir / "silver" / "fichas_consumidores_extraidas" / "fichas_consumidores_extraidas.parquet"
    if f_cons.exists():
        df_cons = pd.read_parquet(f_cons)
        tem_cons = cnpj_sub in df_cons.get("CNPJ", pd.Series()).values
        print(f"Está em fichas_consumidores_extraidas? {tem_cons}")

    # Checar no Bureau Silver
    f_bur = base_dir / "silver" / "fato_bureau_silver" / "fato_bureau_silver.parquet"
    if f_bur.exists():
        df_bur = pd.read_parquet(f_bur)
        tem_bur = cnpj_sub in df_bur.get("CNPJ", pd.Series()).values
        print(f"Está em fato_bureau_silver? {tem_bur}")
        if tem_bur:
            print("Dados do Bureau para a SPE:")
            bur_cols = [c for c in ["CNPJ", "SCORE_BUREAU", "RATING_BUREAU", "DATA_CONSULTA", "PD_BUREAU", "STATUS"] if c in df_bur.columns]
            print(df_bur[df_bur["CNPJ"] == cnpj_sub][bur_cols].to_dict(orient="records"))

    # Checar a Controladora (QAIR BRASIL: 39608949000104)
    cnpj_ctrl = "39608949000104"
    print(f"\n=== INVESTIGANDO CONTROLADORA: {cnpj_ctrl} ===")
    ctrl_fato = df_fato[df_fato["CNPJ"] == cnpj_ctrl]
    print(f"Linhas na fato_analise_credito: {len(ctrl_fato)}")
    if not ctrl_fato.empty:
        cols = ["CNPJ", "RATING", "PD_PERCENTUAL", "TIPO_ANALISE", "FONTE_ANALISE", "ORIGEM_FONTE", "ORIGEM_ANALISE", "ANALISE_HERDADA"]
        presentes = [c for c in cols if c in ctrl_fato.columns]
        print(ctrl_fato[presentes].to_dict(orient="records"))

if __name__ == "__main__":
    main()
