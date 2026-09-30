"""Visão Streamlit: Garantias e Matriz de Transição de Rating.

Conforme Seção 7.2 (Itens 5 e 7) do Planejamento do Sistema BD Crédito.

Esta view NÃO define escalas nem regras de classificação; ela apenas consome
o que o pipeline já produz:
- Status de garantia .... domain.enums.StatusGarantia (gerado em fato_garantia.py)
- Migração de rating .... colunas de fato_migracao_rating.py
                          (variacao_em_graus > 0 = piora, < 0 = melhora, 0 = estável)
- Ordem dos ratings ..... ENTRADAS/control/configs/pd_faixas.json
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import streamlit as st

from common.json import ler_json
from domain.enums import StatusGarantia
from ui.theme import render_header, render_kpis

BASE_DIR = Path(".")
PD_FAIXAS_PATH = BASE_DIR / "ENTRADAS" / "control" / "configs" / "pd_faixas.json"
SEM_RATING = "N/D"  # rótulo de exibição para rating ausente


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _ler_base(caminho_dir: Path, nome_base: str) -> pd.DataFrame:
    parquet_path = caminho_dir / f"{nome_base}.parquet"
    csv_path = caminho_dir / f"{nome_base}.csv"

    if parquet_path.exists():
        try:
            return pd.read_parquet(parquet_path)
        except Exception:
            pass

    if csv_path.exists():
        for sep in (";", ","):
            try:
                return pd.read_csv(csv_path, sep=sep, encoding="utf-8-sig")
            except Exception:
                continue

    return pd.DataFrame()


def _col(df: pd.DataFrame, *nomes: str) -> str | None:
    """Resolve o nome real de uma coluna, ignorando maiúsculas/minúsculas."""
    mapa = {c.lower(): c for c in df.columns}
    for nome in nomes:
        if nome.lower() in mapa:
            return mapa[nome.lower()]
    return None


@st.cache_data(show_spinner=False)
def _ordem_ratings_config(caminho: str) -> list[str]:
    """Ordem dos ratings (melhor -> pior) derivada do pd_faixas.json.

    Ordena cada rating pela média do limite inferior de PD entre os segmentos.
    Se o arquivo não existir ou vier fora do formato, devolve lista vazia
    (a matriz cai para ordem alfabética, sem quebrar).
    """
    try:
        faixas = ler_json(caminho)
    except (OSError, ValueError):
        return []

    pd_min: dict[str, list[float]] = {}
    for segmento in faixas.values():
        if not isinstance(segmento, dict):
            continue
        for rating, faixa in segmento.items():
            try:
                pd_min.setdefault(str(rating), []).append(float(faixa["min"]))
            except (KeyError, TypeError, ValueError):
                continue

    return sorted(pd_min, key=lambda r: sum(pd_min[r]) / len(pd_min[r]))


def _ordenar_ratings(valores, ordem_config: list[str]) -> list[str]:
    """Ratings conhecidos na ordem da config; os demais vão ao final."""
    presentes = set(valores)
    conhecidos = [r for r in ordem_config if r in presentes]
    return conhecidos + sorted(presentes - set(conhecidos))


def _filtrar_busca(df: pd.DataFrame, termo: str) -> pd.DataFrame:
    """Busca literal (sem regex) por nome e por CNPJ (com ou sem pontuação)."""
    termo = termo.strip()
    if not termo:
        return df

    mask = pd.Series(False, index=df.index)

    col_nome = _col(df, "NOME")
    if col_nome:
        mask |= df[col_nome].astype(str).str.contains(termo, case=False, na=False, regex=False)

    col_cnpj = _col(df, "CNPJ")
    digitos = re.sub(r"\D", "", termo)
    if col_cnpj and digitos:
        cnpj_limpo = df[col_cnpj].astype(str).str.replace(r"\D", "", regex=True)
        mask |= cnpj_limpo.str.contains(digitos, na=False, regex=False)

    return df[mask]


# ---------------------------------------------------------------------------
# View
# ---------------------------------------------------------------------------
def render_visao_garantias_migracao():
    render_header(
        titulo="Garantias e Matriz de Transição de Rating",
        subtitulo="Visões consolidadas das Fatos de Crédito: controle de mitigadores de risco e migração histórica de ratings.",
        badge_texto="Mitigação & Migração",
        status_online=True,
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
            status_col = _col(df_gar, "STATUS", "STATUS_GARANTIA")
            total_gar = len(df_gar)

            if status_col:
                status = df_gar[status_col].astype(str).str.strip().str.upper()
                gar_vigentes = int((status == StatusGarantia.VIGENTE.value).sum())
                gar_prox = int((status == StatusGarantia.PROXIMA_VENCIMENTO.value).sum())
                gar_vencidas = int((status == StatusGarantia.VENCIDA.value).sum())
            else:
                gar_vigentes = gar_prox = gar_vencidas = 0
                st.warning("Coluna de status da garantia não encontrada; KPIs de status zerados.")

            render_kpis([
                {"label": "Total de Garantias", "valor": str(total_gar),
                 "subtexto": "Mitigadores cadastrados", "layer": "silver"},
                {"label": "Garantias Vigentes", "valor": str(gar_vigentes),
                 "subtexto": "Válidas e ativas", "layer": "copel"},
                {"label": "Próximas do Vencimento", "valor": str(gar_prox),
                 "subtexto": "Atenção ao vencimento", "layer": "warning"},
                {"label": "Garantias Vencidas", "valor": str(gar_vencidas),
                 "subtexto": "Alerta de mitigador expirado", "layer": "warning"},
            ])

            st.markdown("---")

            col_f1, col_f2 = st.columns(2)
            with col_f1:
                opcoes = ["TODOS"]
                if status_col:
                    opcoes += sorted(df_gar[status_col].dropna().astype(str).unique())
                filtro_status = st.selectbox("Filtrar por Status da Garantia:", opcoes)
            with col_f2:
                filtro_busca = st.text_input("Buscar por CNPJ ou Nome da Contraparte:")

            df_exibir = df_gar
            if filtro_status != "TODOS" and status_col:
                df_exibir = df_exibir[df_exibir[status_col].astype(str) == filtro_status]
            df_exibir = _filtrar_busca(df_exibir, filtro_busca)

            st.caption(f"{len(df_exibir)} de {total_gar} garantias exibidas")
            st.dataframe(df_exibir, width="stretch")

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
            return

        col_ant = _col(df_migr, "rating_anterior")
        col_atu = _col(df_migr, "rating_atual")
        col_var = _col(df_migr, "variacao_em_graus")
        col_dir = _col(df_migr, "direcao_migracao")

        if not (col_ant and col_atu and col_var):
            st.error(
                "A base de migração não possui as colunas esperadas "
                "(rating_anterior, rating_atual, variacao_em_graus). "
                f"Colunas encontradas: {list(df_migr.columns)}. "
                "Reexecute a fato_migracao_rating."
            )
            return

        # KPIs: a classificação vem da fato (variação em graus: + piora, - melhora)
        variacao = pd.to_numeric(df_migr[col_var], errors="coerce")
        total_transicoes = len(df_migr)
        melhoras = int((variacao < 0).sum())
        estaveis = int((variacao == 0).sum())
        pioras = int((variacao > 0).sum())

        render_kpis([
            {"label": "Total de Transições", "valor": str(total_transicoes),
             "subtexto": "Reavaliações históricas", "layer": "silver"},
            {"label": "Upgrades (Melhora)", "valor": str(melhoras),
             "subtexto": "Evolução positiva de risco", "layer": "copel"},
            {"label": "Estáveis (Sem Mudança)", "valor": str(estaveis),
             "subtexto": "Rating mantido", "layer": "silver"},
            {"label": "Downgrades (Piora)", "valor": str(pioras),
             "subtexto": "Deterioração de crédito", "layer": "warning"},
        ])

        sem_variacao = total_transicoes - (melhoras + estaveis + pioras)
        if sem_variacao:
            st.caption(f"{sem_variacao} transição(ões) sem variação calculada — fora dos três grupos acima.")

        st.markdown("---")

        # Matriz de Transição (ordem dos ratings vinda do pd_faixas.json)
        st.markdown("### Matriz de Transição (Rating Anterior x Rating Atual)")
        ant = df_migr[col_ant].fillna(SEM_RATING).astype(str).str.strip()
        atu = df_migr[col_atu].fillna(SEM_RATING).astype(str).str.strip()
        ordem = _ordenar_ratings(pd.concat([ant, atu]).unique(), _ordem_ratings_config(str(PD_FAIXAS_PATH)))

        matriz = (
            pd.crosstab(ant, atu, rownames=["Rating De"], colnames=["Rating Para"])
            .reindex(index=ordem, columns=ordem, fill_value=0)
        )
        matriz["Total"] = matriz.sum(axis=1)
        matriz.loc["Total"] = matriz.sum()
        st.dataframe(matriz, width="stretch")

        # Detalhamento
        st.markdown("### Detalhamento das Transições")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            opcoes = ["TODAS"]
            if col_dir:
                opcoes += sorted(df_migr[col_dir].dropna().astype(str).unique())
            filtro_dir = st.selectbox("Filtrar por direção da migração:", opcoes)
        with col_f2:
            filtro_busca = st.text_input("Buscar transição por CNPJ ou Nome:", key="busca_migracao")

        df_exibir = df_migr
        if filtro_dir != "TODAS" and col_dir:
            df_exibir = df_exibir[df_exibir[col_dir].astype(str) == filtro_dir]
        df_exibir = _filtrar_busca(df_exibir, filtro_busca)

        st.caption(f"{len(df_exibir)} de {total_transicoes} transições exibidas")
        st.dataframe(df_exibir, width="stretch")