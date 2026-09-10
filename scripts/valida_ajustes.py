import pandas as pd
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

def validar_ajustes():
    caminho = Path(r"SAIDAS\silver\fichas_consumidores_extraidas")
    arquivos = list(caminho.glob("*.parquet"))
    
    if not arquivos:
        print("Arquivos parquet não encontrados em SAIDAS\\silver\\fichas_consumidores_extraidas.")
        return
        
    df = pd.concat([pd.read_parquet(f) for f in arquivos], ignore_index=True)
    
    print("\n" + "="*80)
    print(f"VALIDAÇÃO DE AJUSTES - CONSUMIDORES (Total: {len(df)} registros)")
    print("="*80)
    
    # 1. Validação do Padrão de Versão
    print("\n1. Distribuição da versão do layout:")
    col_v = "versao_ficha" if "versao_ficha" in df.columns else "versao_layout" if "versao_layout" in df.columns else None
    if col_v:
        print(df[col_v].value_counts(dropna=False))
    else:
        print(" [AVISO] Coluna de versão não encontrada.")

    # 2. Validação do Volume de Datas Extraídas
    if 'DATA_DEMONSTRACAO_FINANCEIRA' in df.columns:
        # Conta as datas válidas (excluindo nulos e 'NAO_APLICAVEL')
        mask_valida = df['DATA_DEMONSTRACAO_FINANCEIRA'].notnull() & (df['DATA_DEMONSTRACAO_FINANCEIRA'].astype(str).str.upper() != 'NAO_APLICAVEL')
        qtd_com_df = mask_valida.sum()
        print(f"\n2. Datas de DF Extraídas com Sucesso: {qtd_com_df} (Antes do ajuste era ~294)")
    else:
        print("\n2. [ERRO] Coluna DATA_DEMONSTRACAO_FINANCEIRA não encontrada!")

    # 3. Validação dos Falsos Zeros (Regra 14.8)
    print("\n3. Checagem de Falsos Zeros (Regra 14.8):")
    if 'DATA_DEMONSTRACAO_FINANCEIRA' in df.columns and 'LUCRO_LIQUIDO' in df.columns:
        sem_df = df[df['DATA_DEMONSTRACAO_FINANCEIRA'].isnull() | (df['DATA_DEMONSTRACAO_FINANCEIRA'].astype(str).str.upper() == 'NAO_APLICAVEL')]
        
        if sem_df.empty:
            print("  Nenhuma ficha sem DF encontrada para validar.")
        else:
            zeros_falsos = sem_df[sem_df['LUCRO_LIQUIDO'] == 0.0]
            if zeros_falsos.empty:
                print(f"  [SUCESSO] ZERO vazamentos encontrados. Todos os 0.0 falsos entre as {len(sem_df)} fichas sem DF foram anulados corretamente.")
            else:
                print(f"  [FALHA] Ainda vazaram {len(zeros_falsos)} falsos zeros! Ex CNPJs: {zeros_falsos['CNPJ'].head(3).tolist()}")
    else:
        print("  Colunas necessárias ausentes para validação da Regra 14.8.")

    print("\n" + "="*80)

if __name__ == "__main__":
    validar_ajustes()
