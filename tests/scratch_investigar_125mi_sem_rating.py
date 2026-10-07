import pandas as pd
from pathlib import Path

gold_path = Path("SAIDAS/gold/visao_operacional_negocio/Visao_Carteira_Contratos.parquet")
if not gold_path.exists():
    print("❌ Arquivo Gold Visao_Carteira_Contratos não encontrado!")
    exit(1)

df = pd.read_parquet(gold_path)
print(f"Total registros na Gold: {len(df)}")
print(f"Colunas disponíveis: {list(df.columns)}")

col_mtm = "MTM_TOTAL_R$" if "MTM_TOTAL_R$" in df.columns else "MTM_TOTAL"
print(f"Coluna de valor usada: {col_mtm}")

# 1. Identificar contratos onde RATING está em branco / nulo / nan
mask_sem_rating = df["RATING"].isna() | df["RATING"].astype(str).str.strip().isin(["", "None", "nan", "<NA>", "SEM_RATING"])

df_sem_rating = df[mask_sem_rating].copy()
print(f"\nTotal contratos SEM RATING: {len(df_sem_rating)}")

# Converter MTM para numérico
df_sem_rating["MTM_NUM"] = pd.to_numeric(df_sem_rating[col_mtm], errors="coerce").fillna(0)

mtm_total_sem_rating = df_sem_rating["MTM_NUM"].sum()
mtm_positivo_sem_rating = df_sem_rating[df_sem_rating["MTM_NUM"] > 0]["MTM_NUM"].sum()
mtm_negativo_sem_rating = df_sem_rating[df_sem_rating["MTM_NUM"] < 0]["MTM_NUM"].sum()

print(f"Soma MTM Líquido (com negativos) SEM RATING: R$ {mtm_total_sem_rating:,.2f}")
print(f"Soma MTM Positivo (EAD clássica > 0) SEM RATING: R$ {mtm_positivo_sem_rating:,.2f}")
print(f"Soma MTM Negativo (Passivo < 0) SEM RATING: R$ {mtm_negativo_sem_rating:,.2f}")

# 2. Agrupar por Contraparte / CNPJ
col_cnpj = "CONTRAPARTE_CNPJ" if "CONTRAPARTE_CNPJ" in df.columns else "CNPJ"
col_nome = "CONTRAPARTE_NOME_FANTASIA" if "CONTRAPARTE_NOME_FANTASIA" in df.columns else "CONTRAPARTE"

resumo = df_sem_rating.groupby([col_cnpj, col_nome, "STATUS_VIGENCIA_ANALISE", "TIPO_ANALISE", "FONTE_ANALISE"], dropna=False)["MTM_NUM"].agg(
    qtd_contratos="count",
    mtm_liquido="sum"
).reset_index()

resumo = resumo.sort_values("mtm_liquido", ascending=False)
print("\n" + "="*110)
print("TOP 25 CONTRAPARTES SEM RATING (ORDENADAS POR MTM LÍQUIDO):")
print("="*110)
for idx, r in resumo.head(25).iterrows():
    print(f"• CNPJ: {r[col_cnpj]} | Nome: {r[col_nome]}")
    print(f"  MtM Líquido: R$ {r['mtm_liquido']:,.2f} | Contratos: {r['qtd_contratos']}")
    print(f"  Status: {r['STATUS_VIGENCIA_ANALISE']} | Tipo: {r['TIPO_ANALISE']} | Fonte: {r['FONTE_ANALISE']}\n")

# 3. Analisar contratos da AXIA
print("="*110)
print("AUDITORIA DA AXIA ENERGIA NA GOLD:")
print("="*110)
df_axia = df[df[col_cnpj].astype(str).str.contains("02016507") | df[col_nome].astype(str).str.contains("AXIA", case=False, na=False)]
if not df_axia.empty:
    cols_ax = [c for c in [col_cnpj, col_nome, "RATING", "PD", col_mtm, "STATUS_VIGENCIA_ANALISE", "FONTE_ANALISE"] if c in df_axia.columns]
    print(df_axia[cols_ax].to_string())
else:
    print("AXIA não encontrada na Gold.")
