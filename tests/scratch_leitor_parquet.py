"""Script utilitário para conversão e inspeção de arquivos Parquet em CSV para auditoria no Excel.

Lê fato_analise_credito.parquet e Visao_Carteira_Contratos.parquet e exporta para a pasta SAIDAS/.
Formatação: delimitador ponto-e-vírgula (;), decimal com vírgula (,) e encoding utf-8-sig para abertura direta no Excel.
"""

from __future__ import annotations

import sys
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def localizar_arquivo(nome_arquivo: str, pastas_busca: list[Path]) -> Path | None:
    for pasta in pastas_busca:
        if not pasta.exists():
            continue
        candidatos = list(pasta.rglob(nome_arquivo))
        if candidatos:
            # Retorna o arquivo mais recentemente modificado
            candidatos.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            return candidatos[0]
    return None


def exportar_parquet_para_csv() -> None:
    saidas_dir = PROJECT_ROOT / "SAIDAS"
    saidas_dir.mkdir(parents=True, exist_ok=True)

    pastas_busca = [
        PROJECT_ROOT / "SAIDAS",
        PROJECT_ROOT / "DADOS",
        PROJECT_ROOT / "ENTRADAS",
    ]

    alvos = [
        {
            "nome_parquet": "fato_analise_credito.parquet",
            "nome_csv": "fato_analise_credito_export.csv",
            "descricao": "Fato Análise de Crédito (Relacional)"
        },
        {
            "nome_parquet": "Visao_Carteira_Contratos.parquet",
            "nome_csv": "Visao_Carteira_Contratos_export.csv",
            "descricao": "Visão Carteira Contratos (Gold)"
        },
        {
            "nome_parquet": "dim_contraparte.parquet",
            "nome_csv": "dim_contraparte_export.csv",
            "descricao": "Dimensão Contraparte (Relacional)"
        },
        {
            "nome_parquet": "fato_bureau_silver.parquet",
            "nome_csv": "fato_bureau_silver_export.csv",
            "descricao": "Fato Bureau Silver (Silver)"
        },
    ]

    print("=" * 80)
    print("LEITOR E EXPORTADOR DE ARQUIVOS PARQUET PARA AUDITORIA (CSV / EXCEL)")
    print("=" * 80)

    for item in alvos:
        nome_arq = item["nome_parquet"]
        nome_csv = item["nome_csv"]
        desc = item["descricao"]

        caminho_parquet = localizar_arquivo(nome_arq, pastas_busca)
        caminho_csv = saidas_dir / nome_csv

        if caminho_parquet and caminho_parquet.exists():
            print(f"\n[ENCONTRADO] {desc}")
            print(f"  Origem : {caminho_parquet}")
            df = pd.read_parquet(caminho_parquet)
            print(f"  Dimensões: {df.shape[0]} linhas x {df.shape[1]} colunas")
            
            # Exporta com delimitador ; e decimal , para Excel em Português
            df.to_csv(
                caminho_csv,
                sep=";",
                decimal=",",
                index=False,
                encoding="utf-8-sig"
            )
            print(f"  Destino: {caminho_csv}")
            print("  Status : Exportação concluída com sucesso.")
        else:
            print(f"\n[NÃO ENCONTRADO] {desc} ({nome_arq})")
            print("  Dica: Execute o pipeline (main.py) para gerar os arquivos antes de auditar.")

    print("\n" + "=" * 80)
    print(f"Arquivos CSV salvos na pasta: {saidas_dir}")
    print("Prontos para abertura direta no Microsoft Excel.")
    print("=" * 80)

    # Auditoria dos CNPJs críticos mencionados pelo usuário
    caminho_carteira = localizar_arquivo("Visao_Carteira_Contratos.parquet", pastas_busca)
    if caminho_carteira and caminho_carteira.exists():
        df_cart = pd.read_parquet(caminho_carteira)
        cnpjs_teste = ["19572597000258", "09316105001877", "68457727000136"]
        print("\n" + "=" * 80)
        print("AUDITORIA PONTUAL NA VISÃO CARTEIRA CONTRATOS (GOLD):")
        print("=" * 80)
        colunas_exibir = [
            c for c in [
                "CNPJ", "CONTRAPARTE", "STATUS_VIGENCIA_ANALISE", "TIPO_ANALISE",
                "FONTE_ANALISE", "RATING", "DATA_ANALISE", "FIM_VIGENCIA_ANALISE"
            ] if c in df_cart.columns
        ]
        col_cnpj = "CNPJ" if "CNPJ" in df_cart.columns else ("CONTRAPARTE_CNPJ" if "CONTRAPARTE_CNPJ" in df_cart.columns else None)
        if col_cnpj:
            df_sub = df_cart[df_cart[col_cnpj].astype(str).str.zfill(14).isin(cnpjs_teste)]
            if not df_sub.empty:
                df_unique = df_sub.drop_duplicates(subset=[col_cnpj])[colunas_exibir]
                print(df_unique.to_string(index=False))
            else:
                print("Nenhum contrato ativo encontrado para os 3 CNPJs na carteira.")
        print("=" * 80)


if __name__ == "__main__":
    exportar_parquet_para_csv()

