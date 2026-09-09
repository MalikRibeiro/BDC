import pandas as pd
from pathlib import Path

def testar_hipotese_cluster():
    silver_path = Path("SAIDAS/silver/fichas_comercializadoras_extraidas/fichas_comercializadoras_extraidas.parquet")
    if not silver_path.exists():
        silver_path = Path("SAIDAS/silver/fichas_comercializadoras_extraidas/fichas_comercializadoras_extraidas.csv")
        if not silver_path.exists():
            print("Base Silver não encontrada.")
            return
            
    if silver_path.suffix == ".parquet":
        df = pd.read_parquet(silver_path)
    else:
        df = pd.read_csv(silver_path, sep=";")
        
    print("="*60)
    print("1. TESTE DA HIPÓTESE DO CLUSTER (Agrupamento por versao_ficha)")
    print("="*60)
    
    campos_alvo = [
        "TIPO_COMERCIALIZADORA", "FCO", "ROA", "ROE",
        "LUCRO_LIQUIDO", "FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS",
        "NOTA_BOARD", "NOTA_BUREAU"
    ]
    
    total_por_versao = df["versao_ficha"].value_counts().to_dict()
    print("Total de registros por versao_ficha na base:")
    for v, t in total_por_versao.items():
        print(f"  - {v}: {t} registros")
    print("-" * 40)
    
    for campo in campos_alvo:
        if campo not in df.columns:
            print(f"Campo {campo} não existe na base.")
            continue
            
        nulos_mask = df[campo].isna()
        total_nulos = nulos_mask.sum()
        
        if total_nulos == 0:
            print(f"Campo {campo}: 0 nulos.")
            continue
            
        df_nulos = df[nulos_mask]
        contagem = df_nulos["versao_ficha"].value_counts()
        
        print(f"\nCampo: {campo} ({total_nulos} nulos no total)")
        for versao, qtd in contagem.items():
            pct_do_campo = (qtd / total_nulos) * 100
            pct_da_versao = (qtd / total_por_versao.get(versao, 1)) * 100
            print(f"  -> {versao}: {qtd} nulos ({pct_do_campo:.1f}% dos nulos, afeta {pct_da_versao:.1f}% desta versão)")
            
    print("\n" + "="*60)
    print("2. SANITY CHECK GLOBAL DE DATA (Impacto Atual na Silver)")
    print("="*60)
    
    campos_data = ["DATA_DEMONSTRACAO_FINANCEIRA", "DATA_ADESAO_CCEE", "DATA_CALCULO", "DATA_RATING_AGENCIA"]
    
    for campo in campos_data:
        if campo not in df.columns: continue
        
        s = pd.to_datetime(df[campo], errors="coerce")
        
        fora_da_faixa = s.dropna()[~s.dropna().dt.year.between(1990, 2035)]
        qtd = len(fora_da_faixa)
        
        print(f"Campo: {campo}")
        print(f"  - Registros fora da faixa (serão barrados pela nova regra): {qtd}")
        if qtd > 0:
            print("  - Amostra das datas absurdas encontradas:")
            print(fora_da_faixa.head(5).dt.strftime("%Y-%m-%d").to_string(index=False))
        print("-" * 20)

if __name__ == "__main__":
    testar_hipotese_cluster()
