"""Script de teste para validação de impacto: fato_alertas atual vs refatorada."""
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from app.bootstrap import carregar_contexto

def testar_comparacao():
    print("=" * 60)
    print("TESTE DE IMPACTO: FATO_ALERTAS ATUAL VS REFATORADA")
    print("=" * 60)

    context = carregar_contexto(ROOT / "ENTRADAS" / "configs")

    # 1. Carregar a Gold atual (para rodar a lógica atual)
    path_gold = context.path("saidas") / "gold" / "visao_operacional_negocio" / "Visao_Operacional_BDC_LATEST.parquet"
    if not path_gold.exists():
        print(f"❌ Gold LATEST não encontrada em {path_gold}")
        return

    df_gold = pd.read_parquet(path_gold)
    print(f"Colunas na Gold ({len(df_gold)} linhas):")
    print(list(df_gold.columns))

    # 2. Carregar Dimensões e Fatos Relacionais
    path_dim = context.path("relational_dimensions") / "contrapartes" / "dim_contraparte.parquet"
    if not path_dim.exists():
        path_dim = context.path("saidas") / "relational" / "dimensions" / "dim_contraparte.parquet"
    df_dim = pd.read_parquet(path_dim) if path_dim.exists() else pd.DataFrame()
    print(f"\nColunas na Dim Contraparte ({len(df_dim)} linhas):")
    print(list(df_dim.columns))

    path_anl = context.path("relational_facts") / "credito" / "fato_analise_credito.parquet"
    df_anl = pd.read_parquet(path_anl) if path_anl.exists() else pd.DataFrame()
    print(f"\nColunas na Fato Análise de Crédito ({len(df_anl)} linhas):")
    print(list(df_anl.columns))

    path_ctr = context.path("silver") / "denodo_contratos_silver" / "contratos_correntes.parquet"
    df_ctr = pd.read_parquet(path_ctr) if path_ctr.exists() else pd.DataFrame()
    print(f"\nColunas em Contratos Silver ({len(df_ctr)} linhas):")
    print(list(df_ctr.columns))

if __name__ == "__main__":
    testar_comparacao()
