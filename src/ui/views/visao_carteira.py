import streamlit as st
import pandas as pd
from pathlib import Path
import os
import sys

# Adiciona o diretório src ao PYTHONPATH
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
        # Normaliza cabeçalhos em maiúsculo e remove colunas duplicadas
        df.columns = [str(c).replace("\ufeff", "").strip().upper() for c in df.columns]
        df = df.loc[:, ~df.columns.duplicated()].copy()
        
    return df

def carregar_dados_carteira() -> pd.DataFrame:
    # Lê exclusivamente da Camada Gold (Visão Consolidada Final)
    gold_dir = BASE_DIR / "SAIDAS" / "gold" / "visao_operacional_negocio"
    df_gold = ler_parquet_ou_csv(gold_dir, "Visao_Operacional_BDC_LATEST")
    
    if df_gold.empty:
        raise FileNotFoundError("Base Gold consolidada não encontrada em SAIDAS/gold/visao_operacional_negocio.")
        
    # Filtra apenas quem tem contrato (Ativo ou Futuro) validado pelo Master Join
    if "STATUS_CONTRATUAL" in df_gold.columns:
        df_gold = df_gold[df_gold["STATUS_CONTRATUAL"].isin(["CONTRATO_VIGENTE", "CONTRATO_FUTURO"])]
        
    linhas_carteira = []
    
    for _, row in df_gold.iterrows():
        cnpj_c = str(row.get("CNPJ", "")).strip()
        contraparte = str(row.get("NOME") or row.get("SIGLA") or f"CNPJ {cnpj_c}").strip()
        
        # Mapeamentos De -> Para diretos da Gold
        rating = str(row.get("RATING_FINAL", "")).strip()
        
        pd_raw = row.get("PD_FINAL")
        if pd.notna(pd_raw) and str(pd_raw).strip() not in ["", "nan", "None", "<NA>"]:
            try:
                pd_val = float(str(pd_raw).replace(',', '.'))
            except Exception:
                pd_val = None
        else:
            pd_val = None
            
        score = str(row.get("SCORE_BUREAU", "")).strip()
        restritivos = str(row.get("RESTRITIVOS", "")).strip()
        
        data_df_raw = row.get("DATA_DA_ANALISE")
        data_df = ""
        if pd.notna(data_df_raw) and str(data_df_raw).strip() not in ["", "nan", "None", "NaT"]:
            try:
                data_df = pd.to_datetime(data_df_raw).strftime("%d/%m/%Y")
            except Exception:
                data_df = str(data_df_raw).split(" ")[0]
                
        # Status de Fornecimento derivado da Gold
        status_ctr = str(row.get("STATUS_CONTRATUAL", "")).strip()
        if status_ctr == "CONTRATO_VIGENTE":
            status_fornecimento = "Em Fornecimento"
        elif status_ctr == "CONTRATO_FUTURO":
            status_fornecimento = "A Fornecer"
        else:
            status_fornecimento = "Desconhecido"
            
        # Tipo de Análise direto da Metodologia Exigida da Gold
        metodologia = str(row.get("METODOLOGIA_EXIGIDA", "")).strip().upper()
        if metodologia == "DF_DETALHADA":
            tipo_analise = "Análise DF"
        elif metodologia == "BUREAU":
            tipo_analise = "Análise Bureau"
        elif metodologia == "DISPENSADA":
            tipo_analise = "Dispensada"
        else:
            tipo_analise = "Sem Análise"
            
        # Datas de vigência formatadas
        dt_inicio = row.get("PROXIMO_INICIO")
        dt_fim = row.get("PROXIMO_FIM")
        
        vigencia_inicio = pd.to_datetime(dt_inicio).strftime("%d/%m/%Y") if pd.notna(dt_inicio) else None
        vigencia_fim = pd.to_datetime(dt_fim).strftime("%d/%m/%Y") if pd.notna(dt_fim) else None
        
        linhas_carteira.append({
            "CNPJ": cnpj_c,
            "Contraparte": contraparte,
            "Quantidade de contratos": int(row.get("QUANTIDADE_CONTRATOS", 0)) if pd.notna(row.get("QUANTIDADE_CONTRATOS")) else 0,
            "Numero do contrato": str(row.get("NUMERACAO_CONTRATOS", "")).strip() or None,
            "Rating": rating if rating and rating.lower() != "nan" else None,
            "Probabilidade de default": pd_val,
            "Score": score if score and score.lower() != "nan" else None,
            "Restritivos": restritivos if restritivos and restritivos.lower() != "nan" else None,
            "Data da Analise": data_df if data_df and data_df.lower() != "nat" else None,
            "Tipo de analise": tipo_analise,
            "Status_Fornecimento": status_fornecimento,
            "Ano_Inicio": row.get("ANO_INICIO_CONTRATO", 0),
            "Vigencia_Inicio": vigencia_inicio,
            "Vigencia_Fim": vigencia_fim
        })
        
    return pd.DataFrame(linhas_carteira)

def render_visao_carteira():
    st.title("Visão das Carteiras")

    with st.expander("Dicionário de Dados da Visão Carteira", expanded=False):
        st.markdown("""
        ### Bloco 1: Identificação da Contraparte
        * **Contraparte:** Origem: Denodo Contratos -> Metadado: `CONTRAPARTE_APELIDO`. Nome Fantasia ou Razão Social consolidada.
        * **CNPJ:** Origem: Denodo Contratos -> Metadado: `CNPJ`. Chave de integração unificada e normalizada.

        ### Bloco 2: Posição Contratual
        * **Status de Fornecimento:** Origem: Denodo Contratos -> Transformação: Mapeado via lógica temporal (`EH_VIGENTE`, `EH_FUTURO`) em `servico_gold.py`.
        * **Quantidade de Contratos:** Origem: Denodo Contratos -> Transformação: `nunique()` da coluna `col_id` por CNPJ em `servico_gold.py`.
        * **Número do Contrato:** Origem: Denodo Contratos -> Transformação: Junção textual de todos os IDs de contratos associados na Gold.
        * **Vigência (Início / Fim):** Origem: Denodo Contratos -> Transformação: Extremos temporais (`min` e `max` de vigência) extraídos em `servico_gold.py`.
        * **Volume de Enquadramento (MWm):** Origem: Denodo Contratos -> Transformação: Agregação sumária na dimensão de contraparte. Define a Metodologia (DF vs Bureau).

        ### Bloco 3: Metodologia e Governança
        * **Tipo de Análise (Metodologia Exigida):** Origem: `fato_exposicao_risco` e `servico_gold.py` -> Regra de Destino: `DF_DETALHADA` (Volume >= 5 MWm) ou `BUREAU` (Volume < 5 MWm).

        ### Bloco 4: Indicadores de Risco de Crédito
        * **Rating Final:** Origem: Fichas (DF) ou RISK3 (Bureau) -> Filtro: Passa pela validação de domínio estrito `{A, B, C, D, E, F, NAO_ENQUADRADO}` no motor (`fato_analise_credito.py`). Respeita exclusividade mútua via `servico_gold.py`.
        * **Probabilidade de Default (PD):** Origem: Motor de Cálculo (Fato) ou RISK3 -> Regra de Destino: Float representando a (%) de risco de inadimplência associada ao Rating Final.
        * **Score Bureau:** Origem: RISK3 -> Regra de Destino: Pontuação quantitativa consumida independentemente do volume contratado (Fallback opcional).
        * **Restritivos:** Origem: RISK3 -> Regra de Destino: Marcador booleano/textual sobre alertas legais detectados.

        ### Bloco 5: Rastreabilidade
        * **Data da Análise:** Origem: Master Join (`servico_gold.py`) -> Regra de Destino: Herda a `DATA_BALANCO_USADO` (se DF) ou `DATA_CONSULTA` (se Bureau).
        """)

    try:
        df_carteira = carregar_dados_carteira()
    except FileNotFoundError as e:
        st.warning(f"⚠️ {e} Por favor, execute o ETL principal para gerar a camada Silver.")
        return
    except Exception as e:
        st.error(f"Erro ao processar visão da carteira: {e}")
        return

    if df_carteira.empty:
        st.info("Nenhum contrato ativo ou futuro encontrado na base do Denodo.")
        return

    # ---------------- FILTROS SUPERIORES ----------------
    st.markdown("Filtros de Carteira")
    f1, f2, f3, f4 = st.columns([1.5, 1.5, 1.5, 2.5])
    
    anos_disponiveis = sorted([int(a) for a in df_carteira["Ano_Inicio"].unique() if a > 0])
    with f1:
        anos_sel = st.multiselect("Ano Início Suprimento:", anos_disponiveis, default=[])
        
    tipos_analise_disponiveis = ["Todos"] + sorted(list(df_carteira["Tipo de analise"].unique()))
    with f2:
        tipo_sel = st.selectbox("Tipo de Análise:", tipos_analise_disponiveis)
        
    with f3:
        status_sel = st.selectbox("Status Fornecimento:", ["Todos", "Em Fornecimento", "A Fornecer"])
        
    with f4:
        busca = st.text_input("Buscar por Contraparte, CNPJ ou Contrato:", placeholder="Digite para filtrar...")

    # Aplicação dos Filtros
    df_filtrado = df_carteira.copy()
    
    if anos_sel:
        df_filtrado = df_filtrado[df_filtrado["Ano_Inicio"].isin(anos_sel)]
        
    if tipo_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Tipo de analise"] == tipo_sel]
        
    if status_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Status_Fornecimento"] == status_sel]
        
    if busca.strip():
        termo = busca.strip().lower()
        df_filtrado = df_filtrado[
            df_filtrado["Contraparte"].astype(str).str.lower().str.contains(termo) |
            df_filtrado["CNPJ"].astype(str).str.lower().str.contains(termo) |
            df_filtrado["Numero do contrato"].astype(str).str.lower().str.contains(termo)
        ]

    st.markdown("---")

    # ---------------- INSIGHTS / KPIS ----------------
    total_contrapartes = len(df_filtrado)
    total_contratos_reais = int(df_filtrado["Quantidade de contratos"].sum()) if not df_filtrado.empty and "Quantidade de contratos" in df_filtrado.columns else 0
    total_ativos = sum(df_filtrado["Status_Fornecimento"] == "Em Fornecimento")
    total_futuros = sum(df_filtrado["Status_Fornecimento"] == "A Fornecer")
    
    com_rating = sum(df_filtrado["Rating"].notna())
    pct_rating = (com_rating / total_contrapartes * 100) if total_contrapartes > 0 else 0
    
    com_score = sum(df_filtrado["Score"].notna() & (df_filtrado["Score"] != ""))
    pct_score = (com_score / total_contrapartes * 100) if total_contrapartes > 0 else 0

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total de Contratos", f"{total_contratos_reais:,}".replace(",", "."))
    k2.metric("Contrapartes em Fornecimento", f"{total_ativos:,}".replace(",", "."))
    k3.metric("Contrapartes a Fornecer", f"{total_futuros:,}".replace(",", "."))
    k4.metric("Cobertura Rating (DF)", f"{pct_rating:.1f}%", f"{com_rating} clientes", delta_color="normal")
    k5.metric("Cobertura RISK3", f"{pct_score:.1f}%", f"{com_score} clientes", delta_color="normal")

    st.markdown("---")

    # ---------------- TABELA DE DADOS EXIGIDA ----------------
    st.subheader(f"Contrapartes da Carteira ({total_contrapartes} contrapartes)")
    
    colunas_exibicao = [
        "Contraparte",
        "CNPJ",
        "Quantidade de contratos",
        "Numero do contrato",
        "Rating",
        "Probabilidade de default",
        "Score",
        "Restritivos",
        "Data da Analise",
        "Tipo de analise",
        "Status_Fornecimento",
        "Vigencia_Inicio",
        "Vigencia_Fim"
    ]
    
    st.dataframe(
        df_filtrado[colunas_exibicao],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Probabilidade de default": st.column_config.NumberColumn(
                "PD (%)",
                format="%.4f%%"
            )
        }
    )
