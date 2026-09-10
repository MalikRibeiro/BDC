import pandas as pd
from pathlib import Path

def debug_zeros():
    caminho = Path(r"SAIDAS\silver\fichas_consumidores_extraidas")
    arquivos = list(caminho.glob("*.parquet"))
    
    if not arquivos:
        print("Arquivos parquet não encontrados.")
        return
        
    df = pd.concat([pd.read_parquet(f) for f in arquivos], ignore_index=True)
    cnpjs_problema = ['00529188000160', '38246958000130', '41501877000143']
    alvos = df[df["CNPJ"].isin(cnpjs_problema)]
    
    colunas = [
        "CNPJ", "arquivo_nome", "tipo_analise_exigida", "DATA_DEMONSTRACAO_FINANCEIRA", 
        "LUCRO_LIQUIDO", "PATRIMONIO_LIQUIDO", "ATIVO_TOTAL"
    ]
    cols = [c for c in colunas if c in alvos.columns]
    
    print("\n" + "="*80 + "\nDIAGNÓSTICO DOS 'FALSOS ZEROS'\n" + "="*80)
    for _, row in alvos[cols].iterrows():
        print("\n--------------------------------------------------")
        for col in cols:
            print(f"{col}: {row[col]}")

if __name__ == "__main__":
    debug_zeros()
