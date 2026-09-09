import pandas as pd
from pathlib import Path

def main():
    print("="*100)
    print("COMPARAÇÃO DE BASES TRILATERAL: REGRA ANTIGA vs OMNI-LAYOUT vs MODELO HÍBRIDO")
    print("="*100)

    base_dir = Path(r"c:\Users\C807951\Desktop\BDC")
    
    path_antiga = base_dir / "tests" / "fichas_comercializadoras_extraidas_versao_7layouts.csv"
    path_omni = base_dir / "tests" / "fichas_comercializadoras_extraidas_versao_omni_layout.csv"
    path_hibrida = base_dir / "SAIDAS" / "silver" / "fichas_comercializadoras_extraidas" / "fichas_comercializadoras_extraidas.csv"

    dfs = {}
    for nome, path in [("Antiga (7 s/ Semântica)", path_antiga), ("Omni (Só Padrão 7)", path_omni), ("Híbrida (7 c/ Semântica)", path_hibrida)]:
        if not path.exists():
            print(f"ERRO: Base {nome} não encontrada em {path}")
            return
        try:
            dfs[nome] = pd.read_csv(path, sep=";")
        except:
            dfs[nome] = pd.read_csv(path)
            
    print("\n--- TOTAL DE REGISTROS EXTRAÍDOS ---")
    for nome, df in dfs.items():
        print(f"  - {nome}: {len(df)} registros")

    print("\n--- COMPARATIVO DE NULOS (Menos nulos = Melhor) ---")
    
    campos_criticos = [
        "TIPO_COMERCIALIZADORA", "FCO", "ROA", "ROE",
        "LUCRO_LIQUIDO", "FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS",
        "NOTA_BOARD", "NOTA_BUREAU", "PATRIMONIO_LIQUIDO"
    ]
    
    resultados = []
    
    for col in campos_criticos:
        nulos_antiga = dfs["Antiga (7 s/ Semântica)"][col].isna().sum() if col in dfs["Antiga (7 s/ Semântica)"].columns else "N/A"
        nulos_omni = dfs["Omni (Só Padrão 7)"][col].isna().sum() if col in dfs["Omni (Só Padrão 7)"].columns else "N/A"
        nulos_hibrida = dfs["Híbrida (7 c/ Semântica)"][col].isna().sum() if col in dfs["Híbrida (7 c/ Semântica)"].columns else "N/A"
        
        resultados.append({
            "Campo": col,
            "Nulos Antiga": nulos_antiga,
            "Nulos Omni": nulos_omni,
            "Nulos Híbrida": nulos_hibrida
        })
            
    df_res = pd.DataFrame(resultados)
    print(df_res.to_string(index=False))

if __name__ == "__main__":
    main()
