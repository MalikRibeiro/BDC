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
        
    # Remove a trava para permitir exibir todos (Com Contrato, Sem Contrato)
    pass
        
    linhas_carteira = []
    
    for _, row in df_gold.iterrows():
        cnpj_c = str(row.get("CNPJ", "")).strip()
        
        nome_val = str(row.get("NOME", "")).strip()
        sigla_val = str(row.get("SIGLA", "")).strip()
        
        if nome_val.lower() == "nan" or not nome_val:
            nome_val = ""
        if sigla_val.lower() == "nan" or not sigla_val:
            sigla_val = ""
            
        contraparte = nome_val or sigla_val or f"CNPJ {cnpj_c}"
        
        # Mapeamentos De -> Para diretos da Gold
        rating = str(row.get("RATING_FINAL", "")).strip()
        
        pd_raw = row.get("PD_FINAL")
        if pd.notna(pd_raw) and str(pd_raw).strip() not in ["", "nan", "None", "<NA>"]:
            try:
                pd_val = float(str(pd_raw).replace(',', '.'))
                pd_val = pd_val * 100.0  # Converte decimal 0.9999 para 99.99 para exibição
            except Exception:
                pd_val = None
        else:
            pd_val = None
            
        score = str(row.get("SCORE_BUREAU", "")).strip()
        restritivos = str(row.get("RESTRITIVOS", "")).strip()
        
        data_df_raw = row.get("DATA_DA_ANALISE")
        data_df = ""
        ano_df = 0
        if pd.notna(data_df_raw) and str(data_df_raw).strip() not in ["", "nan", "None", "NaT"]:
            try:
                dt_obj = pd.to_datetime(data_df_raw)
                data_df = dt_obj.strftime("%d/%m/%Y")
                ano_df = dt_obj.year
            except Exception:
                data_df = str(data_df_raw).split(" ")[0]
                try:
                    if "/" in data_df: ano_df = int(data_df.split("/")[-1])
                    elif "-" in data_df: ano_df = int(data_df.split("-")[0])
                except:
                    ano_df = 0
                
        # Status de Fornecimento derivado da Gold
        status_ctr = str(row.get("STATUS_CONTRATUAL", "")).strip()
        qtd_contratos = int(row.get("QUANTIDADE_CONTRATOS", 0)) if pd.notna(row.get("QUANTIDADE_CONTRATOS")) else 0

        if status_ctr == "CONTRATO_VIGENTE":
            status_fornecimento = "Em Fornecimento"
        elif status_ctr == "CONTRATO_FUTURO":
            status_fornecimento = "A Fornecer"
        elif qtd_contratos > 0:
            status_fornecimento = "Contrato Vencido"
        else:
            status_fornecimento = "Sem Contrato"
            
        # Tipo de Análise direto da Metodologia Exigida da Gold
        metodologia = str(row.get("METODOLOGIA_EXIGIDA", "")).strip().upper()
        is_herdada = row.get("ANALISE_HERDADA") == True or str(row.get("TIPO_ANALISE", "")) == "Análise Herdada"
        
        if is_herdada:
            tipo_analise = "Análise Herdada"
        elif metodologia == "DF_DETALHADA":
            tipo_analise = "Análise DF"
        elif metodologia == "BUREAU":
            tipo_analise = "Análise Bureau"
        else:
            tipo_analise = "Sem Análise"
            
        # Datas de vigência formatadas
        dt_inicio = row.get("PROXIMO_INICIO")
        dt_fim = row.get("PROXIMO_FIM")
        
        vigencia_inicio = pd.to_datetime(dt_inicio).strftime("%d/%m/%Y") if pd.notna(dt_inicio) else None
        vigencia_fim = pd.to_datetime(dt_fim).strftime("%d/%m/%Y") if pd.notna(dt_fim) else None
        
        posicao_mtm = float(row.get("POSICAO_MTM", 0.0)) if pd.notna(row.get("POSICAO_MTM")) else 0.0
        
        # Filtro de ruído: Ocultar contrapartes puramente sem histórico
        if status_fornecimento == "Sem Contrato" and tipo_analise in ["Dispensada", "Sem Análise"] and posicao_mtm == 0.0:
            continue
            
        data_analise_exibicao = data_df if data_df and data_df.lower() != "nat" else None
        is_rating_empty = not rating or rating.lower() == "nan"
        is_score_empty = not score or score.lower() == "nan"
        
        if is_rating_empty and is_score_empty and tipo_analise != "Sem Análise":
            tipo_analise = f"{tipo_analise} (Não Encontrada)"
            if not data_analise_exibicao:
                # Usa a data de hoje como a data da última verificação do sistema
                data_analise_exibicao = pd.Timestamp.now().strftime("%d/%m/%Y")
            
        linhas_carteira.append({
            "CNPJ": cnpj_c,
            "Contraparte": contraparte,
            "Quantidade de contratos": qtd_contratos,
            "Numero do contrato": str(row.get("NUMERACAO_CONTRATOS", "")).strip() or None,
            "Rating": rating if not is_rating_empty else None,
            "Probabilidade de default": pd_val,
            "Score": score if not is_score_empty else None,
            "Restritivos": restritivos if restritivos and restritivos.lower() != "nan" else None,
            "Data da Analise": data_analise_exibicao,
            "Tipo de analise": tipo_analise,
            "Status_Fornecimento": status_fornecimento,
            "Posicao_MtM": posicao_mtm,
            "Status_Conciliacao": str(row.get("STATUS_CONCILIACAO", "DIVERGENTE")).strip(),
            "Ano_Inicio": row.get("ANO_INICIO_CONTRATO", 0),
            "Ano_DF": ano_df,
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
    f1, f2, f3, f4, f5 = st.columns([2, 1, 1, 1, 1])
    
    anos_disponiveis = sorted([int(a) for a in df_carteira["Ano_Inicio"].unique() if a > 0])
    with f1:
        busca = st.text_input("Buscar por Contraparte/CNPJ:", placeholder="Filtrar...", key="filtro_busca_carteira")
        
    tipos_analise_disponiveis = ["Todos"] + sorted(list(df_carteira["Tipo de analise"].unique()))
    with f2:
        anos_sel = st.multiselect("Ano Início:", anos_disponiveis, default=[], key="filtro_ano_carteira")
        
    with f3:
        tipo_sel = st.multiselect("Tipo de Análise:", tipos_analise_disponiveis, key="filtro_tipo_analise_carteira")
        
    with f4:
        opcoes_base = ["Em Fornecimento", "A Fornecer", "Contrato Vencido", "Sem Contrato"]
        fornecimentos_ativos = set(df_carteira["Status_Fornecimento"].dropna().unique())
        fornecimento_opcoes = ["Todos"] + [opt for opt in opcoes_base if opt in fornecimentos_ativos]
        for opt in fornecimentos_ativos:
            if opt not in fornecimento_opcoes:
                fornecimento_opcoes.append(opt)
        status_sel = st.multiselect("Fornecimento:", fornecimento_opcoes, key="filtro_fornecimento_carteira")
        
    with f5:
        mtm_sel = st.selectbox("Status MtM:", ["Todos", "Com MtM", "Sem MtM"], key="filtro_mtm_carteira")

    # Aplicação dos Filtros
    df_filtrado = df_carteira.copy()
    
    if anos_sel:
        df_filtrado = df_filtrado[df_filtrado["Ano_Inicio"].isin(anos_sel)]
        
    if tipo_sel and "Todos" not in tipo_sel:
        df_filtrado = df_filtrado[df_filtrado["Tipo de analise"].isin(tipo_sel)]
        
    if status_sel and "Todos" not in status_sel:
        df_filtrado = df_filtrado[df_filtrado["Status_Fornecimento"].isin(status_sel)]
        
    if mtm_sel and "Todos" not in mtm_sel:
        masks = []
        if "Com MtM" in mtm_sel:
            masks.append(df_filtrado["Posicao_MtM"] > 0)
        if "Sem MtM" in mtm_sel:
            masks.append(df_filtrado["Posicao_MtM"] == 0)
        if masks:
            import functools, operator
            df_filtrado = df_filtrado[functools.reduce(operator.or_, masks)]
        
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
    if not df_filtrado.empty and "Numero do contrato" in df_filtrado.columns:
        series_contratos = df_filtrado["Numero do contrato"].dropna().astype(str)
        lista_contratos = series_contratos.str.split(",").explode().str.strip()
        lista_contratos = lista_contratos[lista_contratos != ""]
        total_contratos_reais = lista_contratos.nunique()
    else:
        total_contratos_reais = 0
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
        "Posicao_MtM",
        "Status_Conciliacao",
        "Vigencia_Inicio",
        "Vigencia_Fim"
    ]
    
    st.dataframe(
        df_filtrado[colunas_exibicao],
        width="stretch",
        hide_index=True,
        column_config={
            "Probabilidade de default": st.column_config.NumberColumn(
                "PD (%)",
                format="%.4f%%"
            ),
            "Posicao_MtM": st.column_config.NumberColumn(
                "MtM (R$)",
                format="%.2f"
            )
        }
    )
