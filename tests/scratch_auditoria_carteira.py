import pandas as pd
from pathlib import Path

def auditar_visao_carteira():
    print("=" * 60)
    print("AUDITORIA FORENSE - VISÃO CARTEIRA")
    print("=" * 60)
    
    # 1. Carregar Bases
    gold_path = Path("SAIDAS/gold/visao_operacional_negocio/Visao_Carteira_Contratos.parquet")
    fato_path = Path("SAIDAS/relational/facts/credito/fato_analise_credito.parquet")
    if not fato_path.exists():
        fato_path = Path("SAIDAS/relational/credito/fato_analise_credito.parquet")
    
    if not gold_path.exists():
        print(f"❌ ERRO: Base Gold não encontrada em {gold_path}")
        return
        
    df_gold = pd.read_parquet(gold_path)
    df_fato = pd.read_parquet(fato_path) if fato_path.exists() else pd.DataFrame()
    
    # FRENTE 1: Explosão Cartesiana (Tamanho)
    print("\n[1] ANÁLISE DE VOLUMETRIA E CARTESIANO")
    print(f"Linhas na Gold: {len(df_gold)}")
    
    col_contrato = "NUMERO_REFERENCIA_CONTRATO"
    if col_contrato in df_gold.columns:
        duplicatas_contrato = df_gold.duplicated(subset=[col_contrato]).sum()
        print(f"Duplicatas exatas de Contrato (se houver): {duplicatas_contrato}")
        if duplicatas_contrato > 0:
            dup_ex = df_gold[df_gold.duplicated(subset=[col_contrato], keep=False)].sort_values(col_contrato).head(4)
            print("Exemplo de duplicatas na Gold:")
            print(dup_ex[[col_contrato, "CONTRAPARTE_CNPJ", "DATA_FECHAMENTO"]])
    
    # FRENTE 2: Apagão de Crédito
    print("\n[2] ANÁLISE DE DADOS NULOS (RISCO)")
    for col in ["PD", "RATING", "SCORE", "RESTRITIVOS", "STATUS_ANALISE_CREDITO"]:
        if col in df_gold.columns:
            nulos = df_gold[col].isna().sum()
            print(f"Coluna {col}: {nulos} nulos ({nulos/len(df_gold):.1%} da base)")
            
    print("\n[2.1] TIPAGEM DE DATAS (O Motivo do Merge falhar)")
    print("Tipos na Fato (DATA_ANALISE):")
    if "DATA_ANALISE" in df_fato.columns:
        print(df_fato["DATA_ANALISE"].dtype)
        if df_fato["DATA_ANALISE"].dropna().shape[0] > 0:
            print(f"Exemplo Fato: {df_fato['DATA_ANALISE'].dropna().iloc[0]} (Type: {type(df_fato['DATA_ANALISE'].dropna().iloc[0])})")
            
    print("\nTipos na Gold (DATA_FECHAMENTO):")
    if "DATA_FECHAMENTO" in df_gold.columns:
        print(df_gold["DATA_FECHAMENTO"].dtype)
        if df_gold["DATA_FECHAMENTO"].dropna().shape[0] > 0:
            print(f"Exemplo Gold: {df_gold['DATA_FECHAMENTO'].dropna().iloc[0]} (Type: {type(df_gold['DATA_FECHAMENTO'].dropna().iloc[0])})")
            
    # FRENTE 2.2: Rastreador de CNPJ (Tracer Bullet)
    print("\n[2.2] RASTREADOR DE CNPJ DA FATO PARA A GOLD")
    if not df_fato.empty and "RESTRITIVOS" in df_fato.columns:
        df_fato_com_risco = df_fato[df_fato["RESTRITIVOS"].notna()]
        if not df_fato_com_risco.empty:
            cnpj_teste = df_fato_com_risco["CNPJ"].iloc[0]
            print(f"CNPJ Selecionado para rastro: {cnpj_teste}")
            
            print(f"\nNa Fato, este CNPJ tem {len(df_fato[df_fato['CNPJ'] == cnpj_teste])} linhas:")
            cols_fato = ["CNPJ", "DATA_ANALISE", "RATING", "SCORE", "RESTRITIVOS"]
            print(df_fato[df_fato["CNPJ"] == cnpj_teste][cols_fato].head(2))
            
            print(f"\nNa Gold, este CNPJ tem {len(df_gold[df_gold['CONTRAPARTE_CNPJ'] == cnpj_teste])} linhas:")
            cols_gold = ["CONTRAPARTE_CNPJ", "DATA_FECHAMENTO", "STATUS_ANALISE_CREDITO", "RATING", "SCORE", "RESTRITIVOS"]
            print(df_gold[df_gold["CONTRAPARTE_CNPJ"] == cnpj_teste][cols_gold].head(5))
        else:
            print("Nenhum CNPJ com Restritivos na Fato para rastrear.")
            
    # FRENTE 3: Tipo Análise
    print("\n[3] ANÁLISE DE TIPOS DE ANÁLISE (REGRA DE 5MW)")
    if "TIPO_ANALISE" in df_gold.columns:
        print(df_gold["TIPO_ANALISE"].value_counts(dropna=False))

    print("\n" + "=" * 60)
    print("FIM DA AUDITORIA. COPIE ESTE OUTPUT.")
    print("=" * 60)

if __name__ == "__main__":
    auditar_visao_carteira()
