import openpyxl
import pandas as pd
from pathlib import Path

print("="*80)
print("AUDITORIA DETALHADA DAS FICHAS DA EDF")
print("="*80)

fichas_paths = [
    Path("ENTRADAS/fichas/comercializadoras/processadas/EDF EN DO BRASIL 02102026.xlsx"),
    Path("ENTRADAS/fichas/comercializadoras/processadas/EDF EN DO BRASIL 26082026.xlsx"),
    Path("ENTRADAS/fichas/comercializadoras/processadas/EDF 30062026.xlsx"),
    Path("ENTRADAS/fichas/comercializadoras/processadas/EDF RENEWABLES VERDECOM 03082026.xlsx"),
]

for p in fichas_paths:
    print(f"\n--- Arquivo: {p.name} ---")
    if not p.exists():
        print("  ❌ Arquivo não encontrado no disco!")
        continue
    
    try:
        wb = openpyxl.load_workbook(p, data_only=True)
        sheet_names = wb.sheetnames
        print(f"  Abas disponíveis: {sheet_names}")
        
        # Inspecionar abas comuns
        for sheet_cand in ["Análise", "Analise", "Ficha Cadastral", "Cadastro", "Premissas", sheet_names[0]]:
            if sheet_cand in sheet_names:
                ws = wb[sheet_cand]
                # Buscar CNPJ, Razão Social, Data DF, etc. nas primeiras 30 linhas e 10 colunas
                achados = {}
                for r in range(1, 35):
                    for c in range(1, 12):
                        val = ws.cell(row=r, column=c).value
                        if val is not None:
                            val_str = str(val).strip()
                            if any(k in val_str.upper() for k in ["CNPJ", "RAZÃO", "RAZAO", "DATA", "DEMONSTR", "BALANÇO", "BALANCO", "RATING", "NOTA"]):
                                # pegar valor na célula ao lado ou abaixo
                                val_dir = ws.cell(row=r, column=c+1).value
                                val_dir2 = ws.cell(row=r, column=c+2).value
                                val_abaixo = ws.cell(row=r+1, column=c).value
                                achados[f"({sheet_cand}) {r}:{c} '{val_str}'"] = f"Dir1: {val_dir} | Dir2: {val_dir2} | Abaixo: {val_abaixo}"
                
                print(f"  Metadados encontrados na aba '{sheet_cand}':")
                for k, v in list(achados.items())[:12]:
                    print(f"    • {k} -> {v}")
                break
    except Exception as e:
        print(f"  Erro ao abrir workbook: {e}")

# Inspecionar a Camada Silver de Comercializadoras
print("\n" + "="*80)
print("INSPEÇÃO NA CAMADA SILVER: fichas_comercializadoras_extraidas")
print("="*80)
silver_com_path = Path("SAIDAS/silver/fichas_comercializadoras_extraidas/fichas_comercializadoras_extraidas.parquet")
if silver_com_path.exists():
    df_silver = pd.read_parquet(silver_com_path)
    print(f"Total registros na Silver Comercializadoras: {len(df_silver)}")
    mask_edf = df_silver["CNPJ"].astype(str).str.contains("21812954") | df_silver.get("RAZAO_SOCIAL", pd.Series("")).astype(str).str.contains("EDF", case=False)
    df_edf = df_silver[mask_edf]
    print(f"Registros encontrados para EDF: {len(df_edf)}")
    for idx, row in df_edf.iterrows():
        print(f"\n--- REGISTRO INDEX {idx} ---")
        for col, val in row.items():
            if pd.notna(val) and str(val).strip() != "":
                print(f"  {col}: {val}")
else:
    print("❌ Silver Comercializadoras não encontrada!")

# Inspecionar a Fato de Análise de Crédito
print("\n" + "="*80)
print("INSPEÇÃO NA FATO: fato_analise_credito")
print("="*80)
fato_path = Path("SAIDAS/relational/facts/credito/fato_analise_credito.parquet")
if fato_path.exists():
    df_fato = pd.read_parquet(fato_path)
    mask_edf_f = df_fato["CNPJ"].astype(str).str.contains("21812954") | df_fato.get("RAZAO_SOCIAL", pd.Series("")).astype(str).str.contains("EDF", case=False)
    df_edf_f = df_fato[mask_edf_f]
    print(f"Registros encontrados na Fato para EDF: {len(df_edf_f)}")
    for idx, row in df_edf_f.iterrows():
        print(f"\n--- REGISTRO FATO INDEX {idx} ---")
        for col, val in row.items():
            if pd.notna(val) and str(val).strip() != "":
                print(f"  {col}: {val}")
else:
    print(f"❌ Fato de Análise não encontrada em {fato_path}!")
