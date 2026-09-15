import pandas as pd
from pathlib import Path

def limpar_numero_br(valor):
    if pd.isna(valor):
        return pd.NA
    s = str(valor).strip().replace("R$", "").strip()
    if s == "" or s.lower() == "nan":
        return pd.NA
    if "," in s and "." in s:
        # Ambos presentes: assume ponto = milhar, vírgula = decimal
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        # Só vírgula: é o decimal
        s = s.replace(",", ".")
    return s

def auditar_rol_comercializadoras():
    base_dir = Path(r"c:\Users\C807951\Desktop\BDC\SAIDAS\silver\fichas_comercializadoras_extraidas")
    csv_file = base_dir / "fichas_comercializadoras_extraidas.csv"

    if not csv_file.exists():
        print(f"ERRO: Arquivo não encontrado em {csv_file}")
        return

    print("Carregando base Silver de Comercializadoras...")
    df = pd.read_csv(csv_file, sep=";", low_memory=False)

    if len(df.columns) == 1:
        df = pd.read_csv(csv_file, sep=",", low_memory=False)

    print(f"Total de registros carregados: {len(df)}")

    if "ROL" not in df.columns:
        print("ERRO: Coluna 'ROL' não existe neste CSV.")
        return

    # Debug: ver como os valores brutos realmente estão
    print("\n--- AMOSTRA BRUTA DA COLUNA ROL ---")
    print(df["ROL"].dropna().head(10).tolist())

    # 1. Limpeza e conversão
    df["ROL_LIMPO"] = df["ROL"].apply(limpar_numero_br)
    df["ROL_NUM"] = pd.to_numeric(df["ROL_LIMPO"], errors="coerce")
    rol_preenchido = df.dropna(subset=["ROL_NUM"])

    print(f"\n--- RESUMO DE PREENCHIMENTO ---")
    print(f"Registros COM ROL: {len(rol_preenchido)}")
    print(f"Registros SEM ROL: {len(df) - len(rol_preenchido)}")

    # 2. Top 5 ROLs mais repetidos
    print("\n--- TOP 5 VALORES DE ROL MAIS REPETIDOS ---")
    print(rol_preenchido["ROL_NUM"].value_counts().head(5))

    # 3. Auditoria do valor anômalo
    anomalia_val = 4134205523.4
    df["IS_ANOMALY"] = df["ROL_NUM"].apply(
        lambda x: pd.notna(x) and abs(x - anomalia_val) < 1
    )
    df_anomalia = df[df["IS_ANOMALY"]]

    print(f"\n--- AUDITORIA: EMPRESAS COM ROL = {anomalia_val} ---")
    print(f"Total de LINHAS com essa anomalia: {len(df_anomalia)}")

    if "CNPJ" in df.columns:
        print(f"Total de EMPRESAS ÚNICAS (por CNPJ): {df_anomalia['CNPJ'].nunique()}")
    elif "EMPRESA" in df.columns:
        print(f"Total de EMPRESAS ÚNICAS (por nome): {df_anomalia['EMPRESA'].nunique()}")

if __name__ == "__main__":
    auditar_rol_comercializadoras()