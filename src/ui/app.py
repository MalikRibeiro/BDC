import streamlit as st
from pathlib import Path
import sys

# Garante o src no PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent))

from ui.views.visao_orquestrador import render_visao_orquestrador
from ui.views.visao_carga_manual import render_visao_carga_manual
from ui.views.visao_carteira import render_visao_carteira
from ui.views.visao_silver import render_visao_silver
from ui.views.visao_governanca import render_visao_governanca
from ui.views.visao_garantias_migracao import render_visao_garantias_migracao
from ui.theme import inject_theme

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
    page_title="Banco de Dados de Crédito"
)

inject_theme()

def main():
    inject_theme()
    with st.sidebar:
        logo_path = Path(__file__).resolve().parent / "assets" / "logo-copel-horizontal-laranja.png"
        if logo_path.exists():
            st.image(str(logo_path), width="stretch")
        else:
            st.title("BDC")

        st.markdown(
            """
            <div style="padding: 4px 0 12px 0;">
                <span style="font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.8px; color: var(--bdc-text-subtle, #9fa1a4); font-weight: 700;">
                    RISCO DE CRÉDITO
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("---")

        menu = st.radio(
            "Navegação:",
            [
                "Orquestrador",
                "Visão da Carteira",
                "Garantias e Rating",
                "Visão Silver",
                "Auditoria",
                "Carga Manual",
            ],
            index=0
        )
        st.markdown("---")
        st.markdown(
            """
            <div style="padding: 10px 4px; font-size: 0.75rem; color: var(--bdc-text-subtle, #9fa1a4);">
                <p style="margin: 2px 0 0 0;">Versão 1.0 • Homologação</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    if menu == "Orquestrador":
        render_visao_orquestrador()
    elif menu == "Visão da Carteira":
        render_visao_carteira()
    elif menu == "Garantias e Rating":
        render_visao_garantias_migracao()
    elif menu == "Visão Silver":
        render_visao_silver()
    elif menu == "Carga Manual":
        render_visao_carga_manual()
    elif menu == "Auditoria":
        render_visao_governanca()

if __name__ == "__main__":
    main()