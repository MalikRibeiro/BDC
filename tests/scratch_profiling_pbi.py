"""Script de profiling e diagnóstico dos dados Parquet para o Power BI.
Investiga:
1. STATUS_AUDITORIA_PD e colunas de fato_analise_credito.
2. Integridade e cobertura de NOME_GRUPO em dim_grupo_economico (0 nulos / 0 vazios).
3. Integridade referencial GRUPO_ID e CONTRAPARTE_ID na Visao_Carteira_Contratos.
4. Identificação dos contratos ISENTO_INTERCOMPANY vs Carteira de Mercado.
5. Verificação da exportação SAIDAS/exportacoes/CNPJs_Descobertos_Acao_Imediata.csv.
"""
from pathlib import Path
import pandas as pd

def main():
    print("=" * 80)
    print("🔍 BDC — PROFILING DE DADOS PARQUET PARA POWER BI (GOVERNANÇA & INTERCOMPANY)")
    print("=" * 80)

    # 1. FATO ANALISE CREDITO
    p_fato = Path("SAIDAS/relational/facts/credito/fato_analise_credito.parquet")
    if p_fato.exists():
        df_fato = pd.read_parquet(p_fato)
        print(f"\n📌 1. FATO ANALISE CREDITO (Total linhas: {len(df_fato)})")
        
        if "RATING" in df_fato.columns:
            print("\nDistribuição de RATING na Fato:")
            print(df_fato["RATING"].value_counts(dropna=False))

        if "STATUS_AUDITORIA_PD" in df_fato.columns:
            print("\nDistribuição de STATUS_AUDITORIA_PD:")
            print(df_fato["STATUS_AUDITORIA_PD"].value_counts(dropna=False))
            
        if "STATUS_AUDITORIA_RATING" in df_fato.columns:
            print("\nDistribuição de STATUS_AUDITORIA_RATING:")
            print(df_fato["STATUS_AUDITORIA_RATING"].value_counts(dropna=False))

    # 2. DIMENSAO GRUPO ECONOMICO vs CONTRAPARTE
    p_grp = Path("SAIDAS/relational/dimensions/grupos_economicos/dim_grupo_economico.parquet")
    p_cpt = Path("SAIDAS/relational/dimensions/contrapartes/dim_contraparte.parquet")
    if p_grp.exists() and p_cpt.exists():
        df_grp = pd.read_parquet(p_grp)
        df_cpt = pd.read_parquet(p_cpt)
        print(f"\n📌 2. GRUPOS ECONOMICOS vs CONTRAPARTES")
        print(f"Total grupos em dim_grupo_economico: {len(df_grp)}")
        print(f"Total contrapartes em dim_contraparte: {len(df_cpt)}")
        
        # Teste de integridade de NOME_GRUPO
        mask_grp_vazio = (
            df_grp["NOME_GRUPO"].isna() | 
            df_grp["NOME_GRUPO"].astype(str).str.strip().isin(["", "None", "nan", "<NA>", "NULL"])
        )
        print(f"Grupos com NOME_GRUPO nulo ou vazio: {mask_grp_vazio.sum()} (Esperado: 0)")
        
        set_grp_ids = set(df_grp["GRUPO_ID"].dropna().unique())
        set_cpt_grp_ids = set(df_cpt["GRUPO_ID"].dropna().unique())
        
        casados = set_cpt_grp_ids.intersection(set_grp_ids)
        nao_casados = set_cpt_grp_ids - set_grp_ids
        print(f"Contrapartes com GRUPO_ID encontrado na dim_grupo_economico: {len(df_cpt[df_cpt['GRUPO_ID'].isin(casados)])}")
        print(f"Contrapartes com GRUPO_ID NÃO encontrado (órfãos de dimensão): {len(df_cpt[df_cpt['GRUPO_ID'].isin(nao_casados)])}")

    # 3. VISAO CARTEIRA CONTRATOS
    p_ctr = Path("SAIDAS/gold/visao_operacional_negocio/Visao_Carteira_Contratos.parquet")
    if p_ctr.exists():
        df_ctr = pd.read_parquet(p_ctr)
        print(f"\n📌 3. VISAO CARTEIRA CONTRATOS (Total contratos: {len(df_ctr)})")
        
        # Integridade de NOME_GRUPO na Gold
        if "NOME_GRUPO" in df_ctr.columns:
            mask_ctr_grp_vazio = (
                df_ctr["NOME_GRUPO"].isna() | 
                df_ctr["NOME_GRUPO"].astype(str).str.strip().isin(["", "None", "nan", "<NA>", "NULL"])
            )
            print(f"Contratos com NOME_GRUPO em branco / nulo: {mask_ctr_grp_vazio.sum()} (Esperado: 0)")
            print(f"Top 5 Grupos por EAD (MtM positivo):")
            df_pos = df_ctr[df_ctr["MTM_TOTAL_R$"] > 0]
            top_grps = df_pos.groupby("NOME_GRUPO")["MTM_TOTAL_R$"].sum().sort_values(ascending=False).head(5)
            print(top_grps)

        print("\nDistribuição de RATING:")
        print(df_ctr["RATING"].value_counts(dropna=False))
        
        print("\nDistribuição de STATUS_VIGENCIA_ANALISE:")
        print(df_ctr["STATUS_VIGENCIA_ANALISE"].value_counts(dropna=False))

        print("\nDistribuição de FONTE_ANALISE:")
        print(df_ctr["FONTE_ANALISE"].value_counts(dropna=False))
        
        # Análise de Intercompany
        intercompany = df_ctr[df_ctr["RATING"] == "ISENTO_INTERCOMPANY"]
        print(f"\nContratos com RATING = 'ISENTO_INTERCOMPANY' (Total: {len(intercompany)}):")
        if not intercompany.empty:
            print(intercompany[["CONTRAPARTE_CNPJ", "CONTRAPARTE_NOME_FANTASIA", "MTM_TOTAL_R$"]].groupby(["CONTRAPARTE_CNPJ", "CONTRAPARTE_NOME_FANTASIA"]).agg({"MTM_TOTAL_R$": ["count", "sum"]}))

        # Contratos a mercado sem análise (Realmente Descobertos)
        mask_sem = (
            (df_ctr["RATING"].isna() | df_ctr["RATING"].astype(str).str.strip().isin(["", "None", "nan", "<NA>", "SEM_ANALISE"])) &
            (df_ctr["FONTE_ANALISE"].astype(str) != "Intercompany") &
            (df_ctr["STATUS_VIGENCIA_ANALISE"] != "ISENTO_INTERCOMPANY") &
            (df_ctr["RATING"].astype(str) != "ISENTO_INTERCOMPANY")
        )
        sem_analise = df_ctr[mask_sem]
        print(f"\nContratos A MERCADO realmente sem análise / vencidos (Total: {len(sem_analise)}):")
        print(f"CNPJs únicos sem análise: {sem_analise['CONTRAPARTE_CNPJ'].nunique()}")
        print(f"Total MtM Descoberto: R$ {sem_analise['MTM_TOTAL_R$'].sum():,.2f}")
        print(f"Top 5 CNPJs sem análise por MtM:")
        print(sem_analise[["CONTRAPARTE_CNPJ", "CONTRAPARTE_NOME_FANTASIA", "MTM_TOTAL_R$"]].groupby(["CONTRAPARTE_CNPJ", "CONTRAPARTE_NOME_FANTASIA"]).agg({"MTM_TOTAL_R$": ["count", "sum"]}).sort_values(("MTM_TOTAL_R$", "sum"), ascending=False).head(5))

    # 4. RELATORIO EXPORTADO
    p_exp = Path("SAIDAS/exportacoes/CNPJs_Descobertos_Acao_Imediata.csv")
    if p_exp.exists():
        df_exp = pd.read_csv(p_exp, sep=";", encoding="utf-8-sig")
        print(f"\n📌 4. RELATÓRIO DE AÇÃO IMEDIATA GERADO ({p_exp})")
        print(f"Total de CNPJs listados para ação da mesa: {len(df_exp)}")
        print(f"Top 5 registros:")
        print(df_exp.head(5))
    else:
        print(f"\n📌 4. RELATÓRIO DE AÇÃO IMEDIATA: Não encontrado em {p_exp} (será gerado na próxima execução do pipeline)")

    print("\n" + "=" * 80)
    print("🏁 PROFILING CONCLUÍDO")
    print("=" * 80)

if __name__ == "__main__":
    main()
