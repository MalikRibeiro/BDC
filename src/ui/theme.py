"""Módulo utilitário de integração visual para o Streamlit (BDC).

Centraliza a injeção do CSS corporativo lendo diretamente de
`src/ui/assets/style.css` (único arquivo CSS do projeto) e fornece
funções Python para renderizar blocos HTML sem quebras de indentação CommonMark.
"""

from __future__ import annotations

from pathlib import Path
import streamlit as st

THEME_DIR = Path(__file__).resolve().parent
STYLE_CSS_PATH = THEME_DIR / "assets" / "style.css"


def inject_theme() -> None:
    """Lê diretamente o style.css central de assets e o injeta no Streamlit."""
    css_path = THEME_DIR / "assets" / "style.css"
    if css_path.exists():
        try:
            with open(css_path, "r", encoding="utf-8", errors="replace") as f:
                css_content = f.read()
            if hasattr(st, "html"):
                st.html(f"<style>\n{css_content}\n</style>")
            else:
                st.markdown(f"<style>\n{css_content}\n</style>", unsafe_allow_html=True)
        except Exception:
            pass


def render_header(
    titulo: str,
    subtitulo: str,
    badge_texto: str = "Banco de Dados de Crédito",
    status_online: bool = True
) -> None:
    """Renderiza cabeçalho executivo no topo da view com identidade Copel e Medallion."""
    dot_class = "bdc-status-dot" if status_online else ""
    html = (
        f'<div class="bdc-view-header">'
        f'<div class="bdc-view-header-top">'
        f'<h1 class="bdc-view-title">{titulo}</h1>'
        f'<div class="bdc-status-chip"><span class="{dot_class}"></span><span>{badge_texto}</span></div>'
        f'</div>'
        f'<p class="bdc-view-subtitle">{subtitulo}</p>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_kpis(kpis: list[dict]) -> None:
    """Renderiza uma grade de cards de KPI com classes do style.css central.

    Gera HTML estritamente minificado (sem recuo de 4 espaços) para evitar que o
    parser CommonMark do Streamlit interprete o HTML como bloco de código indentado.
    """
    cards_html = []
    for kpi in kpis:
        label = kpi.get("label", "")
        valor = kpi.get("valor", "-")
        subtexto = kpi.get("subtexto", "")
        layer = kpi.get("layer", "copel")

        subtexto_html = f'<div class="bdc-kpi-subtext">{subtexto}</div>' if subtexto else ""

        card = (
            f'<div class="bdc-kpi-card kpi-{layer}">'
            f'<div class="bdc-kpi-top"><span class="bdc-kpi-label">{label}</span></div>'
            f'<div class="bdc-kpi-value">{valor}</div>'
            f'{subtexto_html}'
            f'</div>'
        )
        cards_html.append(card)

    grid_html = f'<div class="bdc-kpi-grid">{"".join(cards_html)}</div>'
    st.markdown(grid_html, unsafe_allow_html=True)


def render_badge(texto: str, tipo: str = "neutral") -> str:
    """Retorna uma tag de badge HTML no estilo executivo."""
    return f'<span class="bdc-badge-pill {tipo}">{texto}</span>'
