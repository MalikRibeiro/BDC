import streamlit as st
from pathlib import Path
import sys

# Garante o src no PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent))

from ui.views.visao_orquestrador import render_visao_orquestrador
from ui.views.visao_carga_manual import render_visao_carga_manual
from ui.views.visao_carteira import render_visao_carteira
from ui.views.visao_silver import render_visao_silver

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    with st.sidebar:
        st.title("BDC")
        st.markdown("---")

        menu = st.radio(
            "Navegação:",
            [
                "Orquestrador",
                "Visão da Carteira",
                "Carga Manual",
                "Visão Silver",
            ],
            index=1
        )
        st.markdown("---")

    if menu == "Orquestrador":
        render_visao_orquestrador()
    elif menu == "Visão da Carteira":
        render_visao_carteira()
    elif menu == "Carga Manual":
        render_visao_carga_manual()
    elif menu == "Visão Silver":
        render_visao_silver()

if __name__ == "__main__":
    main()