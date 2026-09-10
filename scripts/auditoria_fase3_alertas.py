import pandas as pd
from pathlib import Path

def auditar_alertas():
    path = Path(r"SAIDAS/relational/facts/alertas/fato_alerta_credito.parquet")
    if not path.exists():
        print(f"Base de alertas não encontrada: {path}")
        return
        
    df = pd.read_parquet(path)
    
    print("="*80)
    print(f"AUDITORIA DE ALERTAS DE NEGÓCIO - FASE 3")
    print(f"Total de alertas disparados: {len(df)}")
    print("="*80)
    
    print("\n[A] DISTRIBUIÇÃO DE ALERTAS IMPLEMENTADOS:")
    if 'CODIGO_ALERTA' in df.columns:
        print(df['CODIGO_ALERTA'].value_counts(dropna=False))
    else:
        print("Coluna CODIGO_ALERTA ausente!")
        
    print("\n[B] STATUS DOS ALERTAS CRÍTICOS PARA CARGA MANUAL:")
    alertas_criticos = ['DF_001', 'MAN_001', 'MAN_002', 'MAN_003', 'MAN_004', 'EXC_001']
    encontrados = df[df['CODIGO_ALERTA'].isin(alertas_criticos)]
    if encontrados.empty:
        print(">>> Nenhum alerta da esteira de Carga Manual/Exceção foi disparado. CONFIRMADO: GAP FUNCIONAL.")
    else:
        print(encontrados['CODIGO_ALERTA'].value_counts())
        
    print("\n[C] AMOSTRAGEM PARA VALIDAÇÃO DE FALSOS POSITIVOS:")
    if not df.empty:
        amostra = df.sample(min(15, len(df)))
        colunas_exibicao = ['CODIGO_ALERTA', 'CNPJ', 'MENSAGEM_DESCRITIVA', 'CAMPO_AFETADO', 'VALOR_OBSERVADO']
        colunas_presentes = [c for c in colunas_exibicao if c in df.columns]
        
        for _, row in amostra[colunas_presentes].iterrows():
            print("-" * 50)
            for col in colunas_presentes:
                print(f"{col}: {row[col]}")

if __name__ == "__main__":
    auditar_alertas()
