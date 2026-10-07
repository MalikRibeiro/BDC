import pandas as pd
from pathlib import Path

silver_cons_path = Path("SAIDAS/silver/fichas_consumidores_extraidas/fichas_consumidores_extraidas.parquet")
if silver_cons_path.exists():
    df_c = pd.read_parquet(silver_cons_path)
    mask_edf = df_c["CNPJ"].astype(str).str.contains("21812954") | df_c.get("RAZAO_SOCIAL", pd.Series("")).astype(str).str.contains("EDF", case=False)
    df_edf = df_c[mask_edf]
    print(f"Total registros para EDF na Silver de Consumidores: {len(df_edf)}")
    for idx, row in df_edf.iterrows():
        print(f"\n--- REGISTRO CONSUMIDOR INDEX {idx} ---")
        for col, val in row.items():
            if pd.notna(val) and str(val).strip() != "":
                print(f"  {col}: {val}")
else:
    print("Silver consumidores não encontrada.")
