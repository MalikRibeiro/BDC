"""Visão Streamlit: Garantias e Matriz de Transição de Rating.

Conforme Seção 7.2 (Itens 5 e 7) do Planejamento do Sistema BD Crédito.
"""

from __future__ import annotations

from pathlib import Path
import pandas as pd
import streamlit as st

from ui.theme import render_header, render_kpis

BASE_DIR = Path(".")


def _ler_base(caminho_dir: Path, nome_base: str) -> pd.DataFrame:
    parquet_path = caminho_dir / f"{nome_base}.parquet"
    csv_path = caminho_dir / f"{nome_base}.csv"

    if parquet_path.exists():
        try:
            return pd.read_parquet(parquet_path)
        except Exception:
            pass

    if csv_path.exists():
        try:
            return pd.read_csv(csv_path, sep=";", encoding="utf-8-sig")
        except Exception:
            try:
                return pd.read_csv(csv_path, sep=",", encoding="utf-8-sig")
            except Exception:
                pass

    return pd.DataFrame()


def render_visao_garantias_migracao():
    render_header(
        titulo="Garantias e Matriz de Transição de Rating",
        subtitulo="Visões consolidadas das Fatos de Crédito: controle de mitigadores de risco e migração histórica de ratings.",
        badge_texto="Mitigação & Migração",
        status_online=True
    )

    tab_garantias, tab_migracao = st.tabs(["Relatório de Garantias", "Matriz de Transição de Rating"])

    # =========================================================================
    # ABA 1: RELATÓRIO DE GARANTIAS
    # =========================================================================
    with tab_garantias:
        st.subheader("Garantias Vinculadas a Operações e Contratos")
        
        gold_gar_dir = BASE_DIR / "SAIDAS" / "gold" / "visao_garantias"
        df_gar = _ler_base(gold_gar_dir, "Visao_Garantias_LATEST")

        if df_gar.empty:
            # Fallback para Fato Relacional caso Gold ainda não tenha sido gerada
            rel_gar_dir = BASE_DIR / "SAIDAS" / "relational" / "facts" / "garantias"
            if not rel_gar_dir.exists():
                rel_gar_dir = BASE_DIR / "SAIDAS" / "relational" / "facts" / "credito"
            df_gar = _ler_base(rel_gar_dir, "fato_garantia")

        if df_gar.empty:
            st.info("Nenhuma garantia encontrada na base de dados. Execute o pipeline para popular a camada Gold/Relacional.")
        else:
            total_gar = len(df_gar)
            status_col = "STATUS" if "STATUS" in df_gar.columns else "STATUS_GARANTIA"
            gar_vigentes = int((df_gar[status_col] == "VIGENTE").sum()) if status_col in df_gar.columns else 0
            gar_vencidas = int((df_gar[status_col] == "VENCIDA").sum()) if status_col in df_gar.columns else 0
            gar_prox = int((df_gar[status_col] == "PROXIMA_VENCIMENTO").sum()) if status_col in df_gar.columns else 0

            render_kpis([
                {
                    "label": "Total de Garantias",
                    "valor": str(total_gar),
                    "subtexto": "Mitigadores cadastrados",
                    "layer": "silver"
                },
                {
                    "label": "Garantias Vigentes",
                    "valor": str(gar_vigentes),
                    "subtexto": "Válidas e ativas",
                    "layer": "copel"
                },
                {
                    "label": "Próximas do Vencimento",
                    "valor": str(gar_prox),
                    "subtexto": "Atenção em até 30 dias",
                    "layer": "warning"
                },
                {
                    "label": "Garantias Vencidas",
                    "valor": str(gar_vencidas),
                    "subtexto": "Alerta de mitigador expirado",
                    "layer": "warning"
                }
            ])

            st.markdown("---")

            # Filtros
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                status_opcoes = ["TODOS"] + sorted(list(df_gar[status_col].dropna().unique())) if status_col in df_gar.columns else ["TODOS"]
                filtro_status = st.selectbox("Filtrar por Status da Garantia:", status_opcoes)
            with col_f2:
                filtro_busca = st.text_input("Buscar por CNPJ ou Nome da Contraparte:")

            df_exibir_gar = df_gar.copy()
            if filtro_status != "TODOS" and status_col in df_exibir_gar.columns:
                df_exibir_gar = df_exibir_gar[df_exibir_gar[status_col] == filtro_status]
            if filtro_busca:
                mask_cnpj = df_exibir_gar["CNPJ"].astype(str).str.contains(filtro_busca, case=False, na=False) if "CNPJ" in df_exibir_gar.columns else False
                mask_nome = df_exibir_gar["NOME"].astype(str).str.contains(filtro_busca, case=False, na=False) if "NOME" in df_exibir_gar.columns else False
                df_exibir_gar = df_exibir_gar[mask_cnpj | mask_nome]

            st.dataframe(df_exibir_gar, width="stretch")

    # =========================================================================
    # ABA 2: MATRIZ DE TRANSIÇÃO DE RATING
    # =========================================================================
    with tab_migracao:
        st.subheader("Histórico e Matriz de Transição de Rating")

        gold_migr_dir = BASE_DIR / "SAIDAS" / "gold" / "visao_migracao_rating"
        df_migr = _ler_base(gold_migr_dir, "Visao_Migracao_Rating_LATEST")

        if df_migr.empty:
            # Fallback para Fato Relacional
            rel_migr_dir = BASE_DIR / "SAIDAS" / "relational" / "facts" / "credito"
            df_migr = _ler_base(rel_migr_dir, "fato_migracao_rating")

        if df_migr.empty:
            st.info("Nenhuma migração de rating registrada até o momento. As migrações surgem conforme reavaliações periódicas acontecem no histórico.")
        else:
            render_kpis([
                {
                    "label": "Total de Transições",
                    "valor": str(total_gar),
                    "subtexto": "Reavaliações históricas",
                    "layer": "silver"
                },
                {
                    "label": "Upgrades (Melhora)",
                    "valor": str(melhoras),
                    "subtexto": "Evolução positiva de risco",
                    "layer": "copel"
                },
                {
                    "label": "Estáveis (Sem Mudança)",
                    "valor": str(estaveis),
                    "subtexto": "Rating mantido",
                    "layer": "silver"
                },
                {
                    "label": "Downgrades (Piora)",
                    "valor": str(pioras),
                    "subtexto": "Deterioração de crédito",
                    "layer": "warning"
                }
            ])

            st.markdown("---")

            # Matriz de Transição Cruzada
            col_ant = "rating_anterior" if "rating_anterior" in df_migr.columns else "RATING_ANTERIOR"
            col_atu = "rating_atual" if "rating_atual" in df_migr.columns else "RATING_ATUAL"

            if col_ant in df_migr.columns and col_atu in df_migr.columns:
                st.markdown("### Matriz de Transição (Rating Anterior x Rating Atual)")
                matriz = pd.crosstab(
                    df_migr[col_ant],
                    df_migr[col_atu],
                    rownames=["Rating De"],
                    colnames=["Rating Para"],
                    margins=True,
                    margins_name="Total"
                )
                st.dataframe(matriz, width="stretch")

            st.markdown("### Detalhamento das Transições")
            st.dataframe(df_migr, width="stretch")
