import pandas as pd
from pathlib import Path

# Paths
silver_dir = Path("SAIDAS/silver")
fato_credito_path = Path("SAIDAS/relational/facts/credito/fato_analise_credito.parquet")
if not fato_credito_path.exists():
    fato_credito_path = Path("SAIDAS/relational/facts/fato_analise_credito.parquet")

risk3_path = silver_dir / "fato_bureau_silver" / "fato_bureau_silver.parquet"

com_path = silver_dir / "fichas_comercializadoras_extraidas"
con_path = silver_dir / "fichas_consumidores_extraidas"

# 1. Carregar Bureau (Risk3)
df_risk3 = pd.DataFrame()
if risk3_path.exists():
    df_risk3 = pd.read_parquet(risk3_path)
    print(f"Risk3 lido: {len(df_risk3)} linhas. Colunas: {list(df_risk3.columns)}")
else:
    print(f"Risk3 não encontrado em {risk3_path}")

# 2. Carregar Fichas
dfs_fichas = []
for p in [com_path, con_path]:
    if p.exists():
        for f in p.glob("*.parquet"):
            try:
                dfs_fichas.append(pd.read_parquet(f))
            except:
                pass
df_fichas = pd.concat(dfs_fichas, ignore_index=True) if dfs_fichas else pd.DataFrame()
print(f"Fichas lidas: {len(df_fichas)} linhas. Colunas base: {['CNPJ'] + [c for c in df_fichas.columns if 'SCORE' in c.upper() or 'RESTRITI' in c.upper()]}")

# 3. Carregar Fato Analise de Credito
df_fato = pd.DataFrame()
if fato_credito_path.exists():
    df_fato = pd.read_parquet(fato_credito_path)
    print(f"Fato Analise lida: {len(df_fato)} linhas. Colunas SCORE/RESTRITIVOS: {[c for c in df_fato.columns if 'SCORE' in c.upper() or 'RESTRITI' in c.upper()]}")

print("\n" + "="*50)
print("BUSCANDO CNPJS PARA AMOSTRA (COM SCORE OU RESTRITIVOS)...")

cnpjs_amostra = set()

# Procurar no Risk3
col_score_risk = next((c for c in df_risk3.columns if 'SCORE' in c.upper()), None)
col_rest_risk = next((c for c in df_risk3.columns if 'RESTRIT' in c.upper()), None)

if not df_risk3.empty:
    mask = pd.Series(False, index=df_risk3.index)
    if col_score_risk: mask = mask | df_risk3[col_score_risk].notna()
    if col_rest_risk: mask = mask | df_risk3[col_rest_risk].notna()
    cnpjs_risk = df_risk3[mask]['CNPJ'].dropna().unique()[:3]
    cnpjs_amostra.update(cnpjs_risk)

# Procurar nas Fichas
col_score_ficha = next((c for c in df_fichas.columns if 'SCORE_BUREAU' in c.upper() or 'SCORE' in c.upper()), None)
col_rest_ficha = next((c for c in df_fichas.columns if 'RESTRIT' in c.upper()), None)

if not df_fichas.empty and len(cnpjs_amostra) < 5:
    mask = pd.Series(False, index=df_fichas.index)
    if col_score_ficha: mask = mask | df_fichas[col_score_ficha].notna()
    if col_rest_ficha: mask = mask | df_fichas[col_rest_ficha].notna()
    cnpjs_ficha = df_fichas[mask]['CNPJ'].dropna().unique()[:(5 - len(cnpjs_amostra))]
    cnpjs_amostra.update(cnpjs_ficha)

cnpjs_amostra = list(cnpjs_amostra)
print(f"CNPJs selecionados para rastreio: {cnpjs_amostra}")

print("\n" + "="*50)
print("RASTREAMENTO NAS CAMADAS:")

for cnpj in cnpjs_amostra:
    print(f"\n--- CNPJ: {cnpj} ---")
    
    # Risk3
    if not df_risk3.empty:
        df_r = df_risk3[df_risk3['CNPJ'] == cnpj]
        if not df_r.empty:
            print(f"  [RISK3] SCORE: {df_r[col_score_risk].iloc[0] if col_score_risk else 'N/A'}, RESTRITIVOS: {df_r[col_rest_risk].iloc[0] if col_rest_risk else 'N/A'}")
        else:
            print("  [RISK3] Não encontrado")
            
    # Fichas
    if not df_fichas.empty:
        df_f = df_fichas[df_fichas['CNPJ'] == cnpj]
        if not df_f.empty:
            sc = df_f[col_score_ficha].iloc[0] if col_score_ficha and col_score_ficha in df_f.columns else 'N/A'
            rs = df_f[col_rest_ficha].iloc[0] if col_rest_ficha and col_rest_ficha in df_f.columns else 'N/A'
            print(f"  [FICHA] TIPO: {df_f['TIPO_FICHA'].iloc[0] if 'TIPO_FICHA' in df_f.columns else 'N/A'}, SCORE: {sc}, RESTRITIVOS: {rs}")
        else:
            print("  [FICHA] Não encontrado")
            
    # Fato Analise
    if not df_fato.empty:
        df_fa = df_fato[df_fato['CNPJ'] == cnpj]
        if not df_fa.empty:
            print(f"  [FATO_ANALISE_CREDITO]")
            for _, row in df_fa.iterrows():
                print(f"    -> TIPO_ANALISE: {row.get('TIPO_ANALISE', 'N/A')}, RATING: {row.get('RATING', 'N/A')}, SCORE: {row.get('SCORE', 'N/A')}, RESTRITIVOS: {row.get('RESTRITIVOS', 'N/A')}")
        else:
            print("  [FATO_ANALISE_CREDITO] Não encontrado")
