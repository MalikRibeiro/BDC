import pandas as pd
from pathlib import Path

p_gold = Path("SAIDAS/gold/visao_operacional_negocio/Visao_Carteira_Contratos.parquet")
if p_gold.exists():
    df = pd.read_parquet(p_gold)
    
    # Filtros do usuário
    mask_status_contrato = df["STATUS_CONTRATO"].isin(["A_FORNECER", "EM_FORNECIMENTO"])
    mask_status_analise = df["STATUS_VIGENCIA_ANALISE"].isin(["SEM_ANALISE", "VENCIDA"])
    
    df_f = df[mask_status_contrato & mask_status_analise].copy()
    print(f"Total contratos filtrados: {len(df_f)}")
    print(f"Total contrapartes distintas: {df_f['CONTRAPARTE_CNPJ'].nunique()}")
    
    # Agrupa por contraparte e soma MtM
    agg = df_f.groupby(["CONTRAPARTE_CNPJ", "CONTRAPARTE_NOME_FANTASIA", "STATUS_VIGENCIA_ANALISE", "TIPO_ANALISE"]).agg(
        qtd_contratos=("NUMERO_REFERENCIA_CONTRATO", "count"),
        mtm_total=("MTM_TOTAL_R$", "sum"),
        data_analise=("DATA_ANALISE", "first"),
        fim_vigencia=("FIM_VIGENCIA_ANALISE", "first")
    ).reset_index()
    
    agg = agg.sort_values(by="mtm_total", ascending=False)
    print("\n--- TOP 15 CONTRAPARTES POR EXPOSIÇÃO MTM ---")
    for idx, row in agg.head(15).iterrows():
        print(f"CNPJ: {row['CONTRAPARTE_CNPJ']} | Nome: {str(row['CONTRAPARTE_NOME_FANTASIA'])[:30]} | Status: {row['STATUS_VIGENCIA_ANALISE']} | Tipo: {row['TIPO_ANALISE']} | Ctr: {row['qtd_contratos']} | MtM: R$ {row['mtm_total']:,.2f}")
