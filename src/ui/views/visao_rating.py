import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import plotly.express as px

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

BASE_DIR = Path(".")

def ler_parquet_ou_csv(caminho_dir: Path, nome_base: str) -> pd.DataFrame:
    parquet_path = caminho_dir / f"{nome_base}.parquet"
    csv_path = caminho_dir / f"{nome_base}.csv"
    
    df = pd.DataFrame()
    if parquet_path.exists():
        try:
            df = pd.read_parquet(parquet_path)
        except Exception:
            pass
            
    if df.empty and csv_path.exists():
        try:
            df = pd.read_csv(csv_path, sep=";", encoding="utf-8-sig", dtype=str)
        except Exception:
            try:
                df = pd.read_csv(csv_path, sep=",", encoding="utf-8-sig", dtype=str)
            except Exception:
                pass
                
    if not df.empty:
        df.columns = [str(c).replace("\ufeff", "").strip().upper() for c in df.columns]
        df = df.loc[:, ~df.columns.duplicated()].copy()
        
    return df

def carregar_dados_degradacao() -> pd.DataFrame:
    gold_dir = BASE_DIR / "SAIDAS" / "gold" / "visao_operacional_negocio"
    df_gold = ler_parquet_ou_csv(gold_dir, "Visao_Operacional_BDC_LATEST")
    
    if df_gold.empty:
        raise FileNotFoundError("Base Gold consolidada não encontrada.")
        
    # Filtrar apenas clientes com rating D e E
    mask_rating = df_gold["RATING_FINAL"].astype(str).str.strip().str.upper().isin(["D", "E"])
    df_degradados = df_gold[mask_rating].copy()
    
    if df_degradados.empty:
        return pd.DataFrame()
        
    linhas = []
    for _, row in df_degradados.iterrows():
        cnpj_c = str(row.get("CNPJ", "")).strip()
        
        # Tratamento seguro contra strings "nan" do Pandas
        nome_val = str(row.get("NOME", "")).strip()
        sigla_val = str(row.get("SIGLA", "")).strip()

        if nome_val.lower() == "nan" or not nome_val:
            nome_val = ""
        if sigla_val.lower() == "nan" or not sigla_val:
            sigla_val = ""            
        contraparte = nome_val or sigla_val or f"CNPJ {cnpj_c}"
        
        pd_raw = row.get("PD_FINAL")
        try:
            pd_val = float(str(pd_raw).replace(',', '.')) if pd.notna(pd_raw) else 0.0
        except Exception:
            pd_val = 0.0
            
        try:
            mtm = float(row.get("POSICAO_MTM", 0.0)) if pd.notna(row.get("POSICAO_MTM")) else 0.0
        except Exception:
            mtm = 0.0
            
        data_df_raw = row.get("DATA_DA_ANALISE") or row.get("DATA_ANALISE") or row.get("DATA_BALANCO_USADO")
        data_df = ""
        if pd.notna(data_df_raw) and str(data_df_raw).strip() not in ["", "nan", "None", "NaT"]:
            try:
                data_df = pd.to_datetime(data_df_raw).strftime("%d/%m/%Y")
            except Exception:
                data_df = str(data_df_raw).split(" ")[0]
    
        metodologia = str(row.get("METODOLOGIA_EXIGIDA", "")).strip().upper()
        if metodologia == "BUREAU":
            fco_val = None
            lucro_val = None
            
        try:
            qtd_rest = float(row.get("RESTRITIVOS", 0.0)) if pd.notna(row.get("RESTRITIVOS")) and str(row.get("RESTRITIVOS")).strip() != "" else 0.0
        except Exception:
            qtd_rest = 0.0
                    
        linhas.append({
            "Contraparte": contraparte,
            "CNPJ": cnpj_c,
            "Rating": str(row.get("RATING_FINAL", "")).strip().upper(),
            "PD": pd_val,
            "Posicao_MtM": mtm,
            "Restritivos": int(qtd_rest),
            "Última Data da Análise": data_df
        })
        
    return pd.DataFrame(linhas)


def render_visao_rating():
    st.title("Visão de Degradação de Rating")
    st.markdown("Monitoramento de contrapartes em faixas de alto risco (Rating D e E).")
    
    with st.expander("Resumão de Linha de Montagem: Como essa tela é criada e de onde vem o Rating?", expanded=False):
        st.markdown("""
    A tela não recalcula ratings, ela consome a "verdade" consolidada! O processo inteiro é:

    1. O orquestrador roda as extrações de Fichas (Risk3/Bureau/DREs). Isso gera a camada Silver.
    2. O script src/gold/servico_gold.py junta tudo (Contratos + Fichas + MtM + Salesforce).
    3. Dentro do script Gold existe uma regra para a coluna RATING_FINAL: ele procura os campos RATING_COPEL ou NOTA_CREDITO e adota a nota encontrada.
    4. O arquivo final Visao_Operacional_BDC_LATEST.parquet é gerado.
    5. Nossa tela lê esse arquivo final, e faz um filtro simples na coluna RATING_FINAL, pegando os dados que são D ou E.
    """)

    try:
        df = carregar_dados_degradacao()
    except FileNotFoundError as e:
        st.warning(f"⚠️ {e}")
        return
    except Exception as e:
        st.error(f"Erro ao processar visão: {e}")
        return
        
    if df.empty:
        st.success("Nenhuma contraparte classificada com Rating D ou E. Carteira saudável.")
        return
        
    # Filtros
    c_filtros = st.columns(1)
    
        
    with c_filtros[0]:
        busca_texto = st.text_input("Buscar por CNPJ ou Contraparte:", placeholder="Digite o nome ou CNPJ...")
    
    if busca_texto.strip():
        termo = busca_texto.strip().lower()
        mask_busca = (
            df["CNPJ"].astype(str).str.lower().str.contains(termo, regex=False, na=False) |
            df["Contraparte"].astype(str).str.lower().str.contains(termo, regex=False, na=False)
        )
        df = df[mask_busca]
        
    if df.empty:
        st.info("Nenhuma contraparte no segmento selecionado.")
        return
        
    # KPIs
    st.markdown("### Indicadores de Estresse")
    c1, c2, c3 = st.columns(3)
    
    total_degradados = len(df)
    total_degradados = len(df)
    
    c1.metric("Total de Contrapartes (D/E)", total_degradados)
    
    st.markdown("---")
    
    # Gráficos
    g1 = st.columns(1)
        
    with g1[0]:
        st.markdown("#### Exposição (MtM) vs. Probabilidade de Default (PD)")
        fig_scatter = px.scatter(
            df, x="Posicao_MtM", y="PD", 
            color="Rating",
            hover_data=["Contraparte", "CNPJ"],
            color_discrete_map={"D": "orange", "E": "red"}
        )
        st.plotly_chart(fig_scatter, height=600)
        
    st.markdown("---")
    st.markdown("### Detalhamento da Watchlist")
    st.dataframe(
        df, 
        use_container_width=True,
        hide_index=True,
        column_config={
            "FCO": st.column_config.NumberColumn("FCO", format="R$ %.2f"),
            "Lucro Liquido": st.column_config.NumberColumn("Lucro Líquido", format="R$ %.2f"),
            "Posicao_MtM": st.column_config.NumberColumn("MtM (R$)", format="%.2f"),
            "PD": st.column_config.NumberColumn("PD", format="%.4f")
        }
    )
