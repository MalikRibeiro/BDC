"""Auditoria e Validação Pós-Pipeline da Camada Gold e Relacional do BDC.

Segmentação de Governança (conforme Planejamento Operacional v1.2 e NT v7):
1. Segmento Fichas com DF (Comercializadoras e Geradoras): Exige 100% de DRE e conciliação de PD.
2. Segmento Consumidores & Carteira Geral: Avaliação por Bureau (Risk3) ou pendência documental controlada.
"""
from __future__ import annotations

import sys
from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SAIDAS_DIR = PROJECT_ROOT / "SAIDAS"


def carregar_gold() -> pd.DataFrame:
    gold_dir = SAIDAS_DIR / "gold" / "visao_operacional_negocio"
    parquet_path = gold_dir / "Visao_Operacional_BDC_LATEST.parquet"
    csv_path = gold_dir / "Visao_Operacional_BDC_LATEST.csv"

    if parquet_path.exists():
        return pd.read_parquet(parquet_path)
    if csv_path.exists():
        return pd.read_csv(csv_path, sep=";", decimal=",")
    return pd.DataFrame()


def carregar_fatos() -> dict[str, pd.DataFrame]:
    rel_dir = SAIDAS_DIR / "relational" / "facts"
    res = {}

    f_analise = rel_dir / "credito" / "fato_analise_credito.parquet"
    res["analise"] = pd.read_parquet(f_analise) if f_analise.exists() else pd.DataFrame()

    f_score = rel_dir / "credito" / "fato_score_rating_pd.parquet"
    res["score"] = pd.read_parquet(f_score) if f_score.exists() else pd.DataFrame()

    f_risco = rel_dir / "risco" / "fato_exposicao_risco_LATEST.parquet"
    res["risco"] = pd.read_parquet(f_risco) if f_risco.exists() else pd.DataFrame()

    return res


def auditar_gold():
    print("\n" + "=" * 105)
    print("🔬 BDC — AUDITORIA INTEGRADA DA CAMADA GOLD & RELACIONAL (PÓS-PIPELINE)")
    print("=" * 105)

    df_gold = carregar_gold()
    if df_gold.empty:
        print("[-] Arquivo Gold não encontrado em SAIDAS/gold/visao_operacional_negocio/.")
        print("    Certifique-se de executar 'python main.py' antes de rodar esta auditoria.")
        return 1

    fatos = carregar_fatos()
    df_analise = fatos["analise"]
    df_score = fatos["score"]
    df_risco = fatos["risco"]

    total_carteira = len(df_gold)
    print(f"\n[+] Total Geral de Contrapartes na Carteira Gold: {total_carteira}")

    # Separar os dois universos conforme diretriz do projeto:
    # 1. Contrapartes com Ficha Cadastral / Demonstração Financeira (Comercializadoras e Geradoras)
    # 2. Contrapartes Consumidores / Bureau / Sem DF
    seg_upper = df_gold["SEGMENTO_METODOLOGICO"].astype(str).str.upper() if "SEGMENTO_METODOLOGICO" in df_gold.columns else pd.Series("", index=df_gold.index)
    tipo_upper = df_gold["TIPO_FICHA"].astype(str).str.upper() if "TIPO_FICHA" in df_gold.columns else pd.Series("", index=df_gold.index)
    modelo_str = df_gold["MODELO_METODOLOGICO"].astype(str) if "MODELO_METODOLOGICO" in df_gold.columns else pd.Series("", index=df_gold.index)
    tem_anl = (df_gold["TEM_ANALISE"].astype(str) == "SIM") if "TEM_ANALISE" in df_gold.columns else pd.Series(False, index=df_gold.index)
    tipo_anl = df_gold["TIPO_ANALISE"].astype(str) if "TIPO_ANALISE" in df_gold.columns else pd.Series("", index=df_gold.index)

    mask_df = (
        seg_upper.isin(["CPURA", "CGRUPO", "GERADORA"]) |
        tipo_upper.isin(["COMERCIALIZADORA", "GERADORA"]) |
        modelo_str.str.startswith("padrao_") |
        (tem_anl & tipo_anl.str.contains("DF", case=False) & (~tipo_anl.str.contains("Bureau", case=False)))
    )
    df_fichas_df = df_gold[mask_df].copy()
    df_outros = df_gold[~mask_df].copy()

    total_fichas = len(df_fichas_df)
    print(f"[+] Subconjunto com Ficha/DF (Comercializadoras & Geradoras): {total_fichas} contrapartes")
    print(f"[+] Subconjunto Carteira Consumidores / Bureau / Sem DF:       {len(df_outros)} contrapartes")

    # ==============================================================================
    # SEÇÃO 1: AUDITORIA DAS FICHAS CADASTRAIS COM DF (COMERCIALIZADORAS & GERADORAS)
    # ==============================================================================
    print("\n" + "=" * 105)
    print(f"📊 [SEÇÃO 1] FICHAS COM DEMONSTRAÇÃO FINANCEIRA (TOTAL: {total_fichas})")
    print("=" * 105)

    # 1.1 Validação Paralela da PD
    print("\n>>> 1.1 VALIDAÇÃO PARALELA DA PD (AUDITORIA SOMBRA)")
    if "STATUS_AUDITORIA_PD" in df_fichas_df.columns:
        st_dist = df_fichas_df["STATUS_AUDITORIA_PD"].value_counts(dropna=False)
        for st, c in st_dist.items():
            pct = (c / total_fichas) * 100 if total_fichas else 0
            print(f"  - Status '{str(st)}': {c:>4} ({pct:>5.1f}%)")
    else:
        print("  [-] Coluna 'STATUS_AUDITORIA_PD' ausente na visão Gold.")

    if not df_score.empty and "STATUS_AUDITORIA_PD" in df_score.columns:
        print("\n  [Fato Relacional fato_score_rating_pd]:")
        st_rel = df_score["STATUS_AUDITORIA_PD"].value_counts(dropna=False)
        for st, c in st_rel.items():
            print(f"    * {str(st):<28}: {c:>4} ({c/len(df_score)*100:>5.1f}%)")
        if "DELTA_PD" in df_score.columns:
            deltas = pd.to_numeric(df_score["DELTA_PD"], errors="coerce").dropna()
            if not deltas.empty:
                exatos = (deltas <= 1e-6).sum()
                print(f"    * Reconciliação Exata (delta < 1e-6): {exatos} de {len(deltas)} ({exatos/len(deltas)*100:.1f}%)")
                print(f"    * Delta Médio Absoluto: {deltas.mean():.8f}")

    # 1.2 Integridade das Demonstrações Financeiras (DRE)
    print("\n>>> 1.2 INTEGRIDADE DAS DEMONSTRAÇÕES FINANCEIRAS (DRE)")
    dre_cols = [
        ("VENDAS_LIQUIDAS", "Vendas Líquidas / ROL"),
        ("LUCRO_LIQUIDO", "Lucro Líquido"),
        ("FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS", "Fluxo de Caixa Operacional (FCO)")
    ]
    for col_key, label in dre_cols:
        if col_key in df_fichas_df.columns:
            s_num = pd.to_numeric(df_fichas_df[col_key], errors="coerce")
            preenchidos = s_num.notna().sum()
            positivos = (s_num > 0).sum()
            pct = (preenchidos / total_fichas) * 100 if total_fichas else 0
            print(f"  - {label:<35} ({col_key}): {preenchidos:>4} de {total_fichas} preenchidos ({pct:>5.1f}%) | Positivos: {positivos}")
        else:
            print(f"  - {label:<35} ({col_key}): AUSENTE NA VISÃO GOLD")

    # 1.3 Ratings e Métricas de Crédito das Fichas
    print("\n>>> 1.3 DISTRIBUIÇÃO DE RATING COPEL & PD FINAL")
    if "RATING_FINAL" in df_fichas_df.columns:
        r_dist = df_fichas_df["RATING_FINAL"].value_counts(dropna=False)
        print("  Ratings Copel (Fichas):")
        for r, c in r_dist.items():
            print(f"    * Rating {str(r):<6}: {c:>4} ({c/total_fichas*100:>5.1f}%)")

    # ==============================================================================
    # SEÇÃO 2: AUDITORIA DA CARTEIRA GERAL & CONSUMIDORES (SEM DF)
    # ==============================================================================
    print("\n" + "=" * 105)
    print(f"📊 [SEÇÃO 2] CARTEIRA GERAL DE CONSUMIDORES & MERCADO LIVRE (TOTAL: {len(df_outros)})")
    print("=" * 105)

    if not df_outros.empty:
        if "SITUACAO_DF" in df_outros.columns:
            sit_df = df_outros["SITUACAO_DF"].value_counts(dropna=False)
            print("Situação Documental (DF):")
            for s, c in sit_df.items():
                print(f"  - {str(s):<30}: {c:>5} ({c/len(df_outros)*100:>5.1f}%)")

        if "METODOLOGIA_EXIGIDA" in df_outros.columns:
            met_dist = df_outros["METODOLOGIA_EXIGIDA"].value_counts(dropna=False)
            print("\nMetodologia Exigida por Volume/Contrato:")
            for m, c in met_dist.items():
                print(f"  - {str(m):<30}: {c:>5} ({c/len(df_outros)*100:>5.1f}%)")

        if "STATUS_CONTRATUAL" in df_outros.columns:
            ctr_dist = df_outros["STATUS_CONTRATUAL"].value_counts(dropna=False)
            print("\nStatus Contratual (Denodo):")
            for st, c in ctr_dist.items():
                print(f"  - {str(st):<30}: {c:>5} ({c/len(df_outros)*100:>5.1f}%)")

    # ==============================================================================
    # SEÇÃO 3: MÉTRICAS CONSOLIDADAS DE RISCO DA CARTEIRA TOTAL
    # ==============================================================================
    print("\n" + "=" * 105)
    print("📊 [SEÇÃO 3] MÉTRICAS CONSOLIDADAS DE RISCO DA CARTEIRA TOTAL (R$ & EXPOSIÇÃO)")
    print("=" * 105)

    if "EAD_VALOR" in df_gold.columns:
        ead_series = pd.to_numeric(df_gold["EAD_VALOR"], errors="coerce").dropna()
        print(f"Exposição Total (EAD):          R$ {ead_series.sum():>18,.2f} ({len(ead_series)} contrapartes com exposição)")

    if "PE_REAIS" in df_gold.columns:
        pe_series = pd.to_numeric(df_gold["PE_REAIS"], errors="coerce").dropna()
        print(f"Perda Esperada Total (PE):      R$ {pe_series.sum():>18,.2f}")

    # ==============================================================================
    # SEÇÃO 4: AMOSTRA ANALÍTICA DAS FICHAS RECENTES CONCILIADAS
    # ==============================================================================
    print("\n" + "=" * 105)
    print("🔍 [SEÇÃO 4] AMOSTRA ANALÍTICA DAS FICHAS DE COMERCIALIZADORAS & GERADORAS RECENTES (TOP 10)")
    print("=" * 105)

    cols_amostra = [
        c for c in [
            "CNPJ", "SIGLA", "RATING_FINAL", "PD_OFICIAL_FICHA", "PD_RECALCULADA_PYTHON",
            "STATUS_AUDITORIA_PD", "VENDAS_LIQUIDAS", "LUCRO_LIQUIDO"
        ] if c in df_gold.columns
    ]

    df_amostra = df_fichas_df if not df_fichas_df.empty else df_gold
    print(df_amostra[cols_amostra].head(10).to_string(index=False))

    print("\n" + "=" * 105)
    print("✅ AUDITORIA CONCLUÍDA")
    print("=" * 105)
    return 0


if __name__ == "__main__":
    sys.exit(auditar_gold())
