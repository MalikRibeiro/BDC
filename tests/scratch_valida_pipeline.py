import pandas as pd
from pathlib import Path

def validar_pipeline():
    print("=" * 60)
    print("VALIDAÇÃO END-TO-END DO PIPELINE (VISÃO CARTEIRA)")
    print("=" * 60)

    # 1. Validação Silver (Denodo)
    silver_path = Path("SAIDAS/silver/denodo_contratos_silver/contratos_correntes.parquet")
    if not silver_path.exists():
        silver_path = Path("SAIDAS/silver/denodo_contratos_padronizados/contratos_correntes.parquet")
        
    print("\n[1] CAMADA SILVER (Denodo)")
    if silver_path.exists():
        df_silver = pd.read_parquet(silver_path)
        colunas_desejadas = ["DATA_FECHAMENTO", "MOVIMENTACAO", "VIGENCIA_INICIO", "VIGENCIA_FIM"]
        print(f"Total de Registros: {len(df_silver)}")
        for col in colunas_desejadas:
            if col in df_silver.columns:
                nulos = df_silver[col].isna().sum()
                print(f"  ✓ Coluna '{col}' encontrada! (Nulos: {nulos})")
            else:
                print(f"  ❌ ERRO: Coluna '{col}' NÃO encontrada!")
    else:
        print("  ❌ ERRO: Arquivo Silver do Denodo não encontrado.")

    # 2. Validação Relacional (Fato de Crédito)
    fato_path = Path("SAIDAS/relational/facts/credito/fato_analise_credito.parquet")
    print("\n[2] CAMADA RELACIONAL (Fato Análise Crédito)")
    if fato_path.exists():
        df_fato = pd.read_parquet(fato_path)
        print(f"Total de Registros: {len(df_fato)}")
        
        # Verificar SCD2
        cols_scd2 = ["_VERSAO_REGISTRO", "_STATUS_REGISTRO"]
        for col in cols_scd2:
            if col in df_fato.columns:
                print(f"  ✓ Coluna SCD2 '{col}' encontrada!")
            else:
                print(f"  ❌ ERRO: Coluna SCD2 '{col}' NÃO encontrada!")
                
        if "_STATUS_REGISTRO" in df_fato.columns:
            print(f"    - Distribuição de Status: {df_fato['_STATUS_REGISTRO'].value_counts().to_dict()}")

        # Verificar SCORE e RESTRITIVOS (integração Risk3)
        cols_risk3 = ["SCORE", "RESTRITIVOS"]
        for col in cols_risk3:
            if col in df_fato.columns:
                preenchidos = df_fato[col].notna().sum()
                print(f"  ✓ Coluna '{col}' encontrada! (Preenchidos: {preenchidos} registros)")
            else:
                print(f"  ❌ ERRO: Coluna '{col}' NÃO encontrada!")
    else:
        print("  ❌ ERRO: Arquivo Fato de Crédito não encontrado.")

    # 3. Validação Gold (Visão Carteira)
    gold_path = Path("SAIDAS/gold/visao_operacional_negocio/Visao_Carteira_Contratos.parquet")
    print("\n[3] CAMADA GOLD (Visão Carteira)")
    if gold_path.exists():
        df_gold = pd.read_parquet(gold_path)
        print(f"Total de Registros: {len(df_gold)}")
        
        # Verificar Schema Exato
        colunas_esperadas = [
            "DATA_FECHAMENTO", "SUPRIMENTO_INICIO", "SUPRIMENTO_FIM", 
            "CONTRAPARTE_NOME_FANTASIA", "CONTRAPARTE_CNPJ", "NUMERO_REFERENCIA_CONTRATO", 
            "MOVIMENTACAO", "PORTFOLIO", "MTM_TOTAL_R$", "MTM_VPL_R$", 
            "PD", "RATING", "SCORE", "RESTRITIVOS", "DATA_ANALISE", 
            "TIPO_ANALISE", "STATUS_ANALISE_CREDITO"
        ]
        
        ausentes = set(colunas_esperadas) - set(df_gold.columns)
        extras = set(df_gold.columns) - set(colunas_esperadas)
        
        if not ausentes and not extras:
            print("  ✓ Schema Perfeito (17 colunas).")
        else:
            if ausentes: print(f"  ❌ ERRO: Colunas ausentes na Gold: {ausentes}")
            if extras: print(f"  ❌ ERRO: Colunas sobrando na Gold: {extras}")
            
        if "STATUS_ANALISE_CREDITO" in df_gold.columns:
            print(f"  ✓ Distribuição de Status de Análise (Master Join):")
            print(f"    {df_gold['STATUS_ANALISE_CREDITO'].value_counts().to_dict()}")
            
        if "RATING" in df_gold.columns:
            ratings = df_gold["RATING"].dropna().unique()
            print(f"  ✓ Valores de Rating encontrados: {list(ratings[:10])}...")
            
    else:
        print("  ❌ ERRO: Arquivo Gold não encontrado.")
        
    print("\n" + "=" * 60)

if __name__ == "__main__":
    validar_pipeline()
