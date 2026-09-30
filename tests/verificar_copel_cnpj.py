import pandas as pd
from pathlib import Path

p_gold = Path("SAIDAS/gold/visao_operacional_negocio/Visao_Carteira_Contratos.parquet")
if p_gold.exists():
    df = pd.read_parquet(p_gold)
    copel_rows = df[df["CONTRAPARTE"].astype(str).str.contains("COPEL", case=False, na=False)]
    res = copel_rows[["CONTRAPARTE_CNPJ", "CONTRAPARTE", "NUMERO_REFERENCIA_CONTRATO"]].drop_duplicates(subset=["CONTRAPARTE_CNPJ", "CONTRAPARTE"])
    print("CNPJs Copel na base Gold:")
    print(res.to_string())
