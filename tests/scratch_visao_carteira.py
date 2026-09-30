import pandas as pd
from pathlib import Path

# Verificar colunas dos Silver de Contratos e MTM
silver_dir = Path("SAIDAS/silver")

# 1. Denodo Contratos Silver
denodo_path = silver_dir / "denodo_contratos_silver" / "contratos_correntes.parquet"
if denodo_path.exists():
    df = pd.read_parquet(denodo_path)
    print("--- DENODO CONTRATOS SILVER ---")
    print(f"Linhas: {len(df)}")
    print(f"Colunas ({len(df.columns)}): {list(df.columns)}")
    for col in ["SUPRIMENTO_INICIO", "SUPRIMENTO_FIM", "SUPRIMENTO_TERMINO", "CONTRAPARTE_NOME_FANTASIA", "CONTRAPARTE_APELIDO", "MOVIMENTACAO", "DATA_FECHAMENTO", "CONTRAPARTE_CNPJ", "NUMERO_REFERENCIA_CONTRATO", "STATUS"]:
        presente = col in df.columns
        if presente:
            nulos = df[col].isna().sum()
            print(f"  {col}: PRESENTE (nulos: {nulos}/{len(df)})")
        else:
            print(f"  {col}: AUSENTE")
else:
    print(f"Arquivo não encontrado: {denodo_path}")

# 2. MTM Contratos Silver
mtm_path = silver_dir / "mtm_contratos_silver" / "mtm_contratos.parquet"
if mtm_path.exists():
    df_mtm = pd.read_parquet(mtm_path)
    print("\n--- MTM CONTRATOS SILVER ---")
    print(f"Linhas: {len(df_mtm)}")
    print(f"Colunas ({len(df_mtm.columns)}): {list(df_mtm.columns)}")
    for col in ["DATA_FECHAMENTO", "PORTFOLIO", "MTM_TOTAL", "MTM_VPL", "CONTRATO", "MTM_TOTAL_R$", "MTM_VPL_R$"]:
        presente = col in df_mtm.columns
        if presente:
            nulos = df_mtm[col].isna().sum()
            print(f"  {col}: PRESENTE (nulos: {nulos}/{len(df_mtm)})")
        else:
            print(f"  {col}: AUSENTE")
else:
    print(f"Arquivo não encontrado: {mtm_path}")

# 3. Fato Análise Crédito (checar TIPO_ANALISE)
fato_path = Path("SAIDAS/relational/facts/credito/fato_analise_credito.parquet")
if not fato_path.exists():
    fato_path = Path("SAIDAS/relational/facts/fato_analise_credito.parquet")
if fato_path.exists():
    df_f = pd.read_parquet(fato_path)
    print("\n--- FATO ANALISE CREDITO ---")
    print(f"Linhas: {len(df_f)}")
    for col in ["TIPO_ANALISE", "ANALISE_HERDADA", "ORIGEM_ANALISE", "RATING", "PD_PERCENTUAL", "SCORE", "RESTRITIVOS", "DATA_ANALISE"]:
        if col in df_f.columns:
            nulos = df_f[col].isna().sum()
            vals = df_f[col].dropna().unique()[:5].tolist()
            print(f"  {col}: PRESENTE (nulos: {nulos}/{len(df_f)}, amostra: {vals})")
        else:
            print(f"  {col}: AUSENTE")
