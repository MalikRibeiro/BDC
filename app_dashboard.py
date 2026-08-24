import streamlit as st
import pandas as pd
from pathlib import Path

# ==================================================
# CONFIGURAÇÕES
# ==================================================
st.set_page_config(page_title="BDC | Dashboard de Extração", layout="wide", page_icon="📄")

st.title("BD CRÉDITO | Dashboard de Extração de Fichas")

# Definição de caminhos
BASE_DIR = Path(r"C:\Users\C807951\Desktop\BDC")
BRONZE_DIR = BASE_DIR / "SAIDAS" / "bronze" / "fichas_comercializadoras_raw"
SILVER_DIR = BASE_DIR / "SAIDAS" / "silver" / "fichas_comercializadoras_extraidas"

# ==================================================
# 1. CAMADA BRONZE (Quantidade de Fichas Lidas)
# ==================================================
st.header("🗂️ Camada Bronze")
st.caption(f"Caminho: `{BRONZE_DIR}`")

qtd_fichas_bronze = 0
if BRONZE_DIR.exists():
    qtd_fichas_bronze = len([f for f in BRONZE_DIR.rglob("*") if f.is_file()])

st.metric(label="Quantidade de Fichas Lidas (Raw)", value=f"{qtd_fichas_bronze} arquivos")

st.divider()

# ==================================================
# 2. CAMADA SILVER (Tabela Extraída e Dados por Campo)
# ==================================================
st.header("⚙️ Camada Silver")
st.caption(f"Caminho: `{SILVER_DIR}`")

df_silver = pd.DataFrame()

if SILVER_DIR.exists():
    csv_files = list(SILVER_DIR.glob("*.csv"))
    if csv_files:
        df_list = []
        for p in csv_files:
            try:
                df = pd.read_csv(p, sep=';', on_bad_lines='skip', low_memory=False)
                df_list.append(df)
            except Exception as e:
                st.error(f"Erro ao ler {p.name}: {e}")
        
        if df_list:
            df_silver = pd.concat(df_list, ignore_index=True)

if not df_silver.empty:
    st.success(f"Foram extraídos {len(df_silver)} registros no total.")
    
    # 2.1 Tabela Completa (Fichas Extraídas)
    st.subheader("1. Tabela de Fichas Extraídas (fichas_comercializadoras_extraidas)")
    st.dataframe(df_silver, use_container_width=True)

    # 2.2 Dados Lidos para Cada Campo (Estatísticas de Preenchimento)
    st.subheader("2. Resumo de Dados Lidos para Cada Campo")
    
    # Montando a tabela de estatísticas dos campos
    resumo_campos = pd.DataFrame({
        "Campo Extraído": df_silver.columns,
        "Tipo de Dado": df_silver.dtypes.astype(str),
        "Total de Registros": len(df_silver),
        "Valores Preenchidos": df_silver.notna().sum().values,
        "% de Preenchimento": (df_silver.notna().mean().values * 100).round(2).astype(str) + "%"
    })
    
    st.dataframe(resumo_campos.reset_index(drop=True), use_container_width=True)

else:
    st.warning(f"Nenhum arquivo .csv encontrado no diretório Silver ({SILVER_DIR}).")