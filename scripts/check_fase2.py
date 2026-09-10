import pandas as pd
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

def rodar_auditoria(caminho, segmento):
    pasta = Path(caminho)
    if not pasta.exists():
        return
    
    arquivos = list(pasta.glob("*.parquet"))
    if not arquivos:
        return
        
    df = pd.concat([pd.read_parquet(f) for f in arquivos], ignore_index=True)
    print(f"\n{'='*60}\nAUDITORIA SILVER: {segmento} | Total: {len(df)} registros\n{'='*60}")
    
    col_v = None
    for c in ["VERSAO_FICHA", "LAYOUT", "NOME_LAYOUT", "LAYOUT_NAME", "VERSAO", "TIPO_LAYOUT", "LAYOUT_UTILIZADO", "PADRAO_LAYOUT"]:
        if c in df.columns:
            col_v = c
            break
    
    if col_v:
        for v in df[col_v].unique():
            df_v = df[df[col_v] == v]
            print(f"\n--- Layout/Versão: {v} ({len(df_v)} registros) ---")
            nulos = (df_v.isnull().sum() / len(df_v)) * 100
            for campo, pct in nulos[nulos > 0].sort_values(ascending=False).head(10).items():
                print(f"  {campo}: {pct:.1f}% nulo")
    else:
        print("\n[AVISO] Coluna de versão não encontrada. Colunas disponíveis no arquivo:")
        print(df.columns.tolist())
        # Imprime os nulos globais como fallback
        print("\n--- % Nulos Geral ---")
        nulos = (df.isnull().sum() / len(df)) * 100
        for campo, pct in nulos[nulos > 0].sort_values(ascending=False).head(10).items():
            print(f"  {campo}: {pct:.1f}% nulo")
        
    # --- TESTE DA REGRA CRÍTICA: AUSÊNCIA DE DF NÃO VIRA ZERO ---
    print(f"\n--- Validação: Regra de Ouro (DF ausente != Zero) ---")
    campos_fin = ["ATIVO_TOTAL", "LUCRO_LIQUIDO", "PATRIMONIO_LIQUIDO", "PASSIVO_CIRCULANTE"]
    campos_fin = [c for c in campos_fin if c in df.columns]
    
    if "DATA_DEMONSTRACAO_FINANCEIRA" in df.columns:
        mask_df_ausente = df["DATA_DEMONSTRACAO_FINANCEIRA"].isnull() | (df["DATA_DEMONSTRACAO_FINANCEIRA"].astype(str).str.upper() == "NAO_APLICAVEL")
        df_ausentes = df[mask_df_ausente]
        
        violacoes = 0
        if not df_ausentes.empty:
            for c in campos_fin:
                zeros = df_ausentes[df_ausentes[c] == 0.0]
                if not zeros.empty:
                    print(f"[FALHA CRÍTICA] Campo {c} virou '0.0' indevidamente em {len(zeros)} fichas sem DF! Ex: CNPJs {zeros['CNPJ'].head(3).tolist()}")
                    violacoes += len(zeros)
                    
        if violacoes == 0:
            print("[OK] Nenhum indicador financeiro avaliado foi convertido para zero incorretamente.")
    else:
        print("[AVISO] DATA_DEMONSTRACAO_FINANCEIRA ausente no parquet.")

if __name__ == "__main__":
    rodar_auditoria(r"SAIDAS\silver\fichas_comercializadoras_extraidas", "Comercializadoras")
    rodar_auditoria(r"SAIDAS\silver\fichas_consumidores_extraidas", "Consumidores")
