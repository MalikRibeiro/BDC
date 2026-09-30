import pandas as pd
from pathlib import Path

# 1. Verificar Visao_Carteira_Contratos
p_gold = Path("SAIDAS/gold/visao_operacional_negocio/Visao_Carteira_Contratos.parquet")
if p_gold.exists():
    df_gold = pd.read_parquet(p_gold)
    btg_gold = df_gold[df_gold["CONTRAPARTE"].astype(str).str.contains("BTG", case=False, na=False)]
    print("--- BTG na Gold (Visão Carteira) ---")
    print(btg_gold[["NUMERO_REFERENCIA_CONTRATO", "CONTRAPARTE", "CNPJ", "STATUS_VIGENCIA_ANALISE", "TIPO_ANALISE", "RATING", "PD_PERCENTUAL"]].head(10))

# 2. Verificar Fato Analise Credito
p_fato = Path("SAIDAS/relational/facts/credito/fato_analise_credito.parquet")
if p_fato.exists():
    df_fato = pd.read_parquet(p_fato)
    # Busca por CNPJ raiz do BTG ou nome se tiver
    # BTG Pactual CNPJ raiz geralmente é 30.306.294 ou similar
    btg_cnpjs = btg_gold["CNPJ"].unique() if p_gold.exists() else []
    print("CNPJs do BTG na Carteira:", btg_cnpjs)
    for c in btg_cnpjs:
        c_str = str(c).zfill(14)
        r = c_str[:8]
        fato_match = df_fato[df_fato["CNPJ"].astype(str).str.startswith(r)]
        print(f"Match na Fato para raiz {r}:")
        print(fato_match[["CNPJ", "DATA_ANALISE", "RATING", "PD_PERCENTUAL", "TIPO_ANALISE", "ANALISE_HERDADA", "ORIGEM_ANALISE"]])
