import streamlit as st
import pandas as pd
from pathlib import Path
import os
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from ui.theme import render_header, render_kpis
from common.datas import formatar_data_br_serie

BASE_DIR = Path(".")

COL_MAP_CARTEIRA = {
    # Bloco 1: Contrato e Operação
    "NUMERO_REFERENCIA_CONTRATO": "Nº Contrato",
    "MOVIMENTACAO": "Operação",
    "STATUS_CONTRATO": "Status do Contrato",
    "DATA_FECHAMENTO": "Data Fechamento",
    "SUPRIMENTO_INICIO": "Início Suprimento",
    "SUPRIMENTO_FIM": "Fim Suprimento",
    
    # Bloco 2: Contraparte
    "CONTRAPARTE_NOME_FANTASIA": "Contraparte",
    "CONTRAPARTE_CNPJ": "CNPJ",
    
    # Bloco 3: Exposição Financeira (MtM)
    "MTM_TOTAL_R$": "MtM Total (R$)",
    "MTM_VPL_R$": "MtM VPL (R$)",
    "PORTFOLIO": "Portfólio",
    
    # Bloco 4: Risco de Crédito Vigente
    "STATUS_VIGENCIA_ANALISE": "Status Análise",
    "RATING": "Rating",
    "PD": "PD (%)",
    "SCORE": "Score Bureau",
    "RESTRITIVOS": "Restritivos",
    "DATA_ANALISE": "Data Análise",
    "FIM_VIGENCIA_ANALISE": "Fim Vigência",
    "TIPO_ANALISE": "Tipo de Análise",
    "FONTE_ANALISE": "Fonte dos Dados"
}

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

@st.cache_data(show_spinner="Carregando visão da carteira...")
def carregar_dados_carteira_preparados() -> pd.DataFrame:
    gold_dir = BASE_DIR / "SAIDAS" / "gold" / "visao_operacional_negocio"
    df_carteira = ler_parquet_ou_csv(gold_dir, "Visao_Carteira_Contratos")
    
    if df_carteira.empty:
        raise FileNotFoundError("Base Gold de contratos não encontrada em SAIDAS/gold/visao_operacional_negocio/Visao_Carteira_Contratos.parquet.")
        
    for col in COL_MAP_CARTEIRA.keys():
        if col not in df_carteira.columns:
            df_carteira[col] = pd.NA

    df_exibicao = df_carteira[list(COL_MAP_CARTEIRA.keys())].rename(columns=COL_MAP_CARTEIRA)
    s_fechamento_dt = pd.to_datetime(df_exibicao["Data Fechamento"], format="%d/%m/%Y", errors="coerce")
    mask_fech_iso = s_fechamento_dt.isna() & df_exibicao["Data Fechamento"].notna()
    if mask_fech_iso.any():
        s_fechamento_dt.loc[mask_fech_iso] = pd.to_datetime(df_exibicao.loc[mask_fech_iso, "Data Fechamento"], errors="coerce")
    df_exibicao["Ano_Fechamento"] = s_fechamento_dt.dt.year.fillna(0).astype(int)

    # Padronização canônica de datas para o formato corporativo DD/MM/AAAA
    cols_datas = ["Data Fechamento", "Início Suprimento", "Fim Suprimento", "Data Análise", "Fim Vigência"]
    for col_dt in cols_datas:
        if col_dt in df_exibicao.columns:
            df_exibicao[col_dt] = formatar_data_br_serie(df_exibicao[col_dt])

    # Ajuste de Escala da PD: converter decimal (0.1370) para base 100 (13.70%)
    if "PD (%)" in df_exibicao.columns:
        df_exibicao["PD (%)"] = pd.to_numeric(df_exibicao["PD (%)"], errors="coerce") * 100.0

    # Normalizar valores vazios/nulos nas colunas de texto para evitar overhead no filtro
    cols_traco = ["Rating", "Tipo de Análise", "Fonte dos Dados", "Status do Contrato", "Operação", "Data Análise", "Fim Vigência", "Portfólio", "Data Fechamento", "Início Suprimento", "Fim Suprimento"]
    for col_txt in cols_traco:
        if col_txt in df_exibicao.columns:
            df_exibicao[col_txt] = df_exibicao[col_txt].replace({"None": "-", "nan": "-", "<NA>": "-", "NaT": "-"}).fillna("-")

    # Identificação Declarativa de Contrapartes Intercompany (Grupo Econômico Próprio)
    cfg_intercompany_path = Path("ENTRADAS/control/configs/contrapartes_grupo_proprio.json")
    if cfg_intercompany_path.exists():
        try:
            import json
            with open(cfg_intercompany_path, "r", encoding="utf-8") as f:
                cfg_ic = json.load(f)
            raizes = tuple(cfg_ic.get("raizes_cnpj_isentas", []))
            cnpjs_exatos = set(cfg_ic.get("cnpjs_isentos", []))
            termos_nome = cfg_ic.get("termos_razao_social", [])

            s_cnpj = df_exibicao["CNPJ"].astype(str).str.zfill(14)
            cond_raiz = s_cnpj.str.startswith(raizes) if raizes else pd.Series(False, index=df_exibicao.index)
            cond_cnpj = s_cnpj.isin(cnpjs_exatos) if cnpjs_exatos else pd.Series(False, index=df_exibicao.index)

            s_nome = df_exibicao["Contraparte"].astype(str).str.upper()
            cond_nome = s_nome.apply(lambda x: any(t in x for t in termos_nome)) if termos_nome else pd.Series(False, index=df_exibicao.index)

            mask_ic = cond_raiz | cond_cnpj | cond_nome
            df_exibicao.loc[mask_ic, "Status Análise"] = "INTERCOMPANY"
            df_exibicao.loc[mask_ic, "Tipo de Análise"] = "Intercompany"
            df_exibicao.loc[mask_ic, "Rating"] = "N/A"
            df_exibicao.loc[mask_ic, "PD (%)"] = 0.0
            df_exibicao.loc[mask_ic, "Score Bureau"] = pd.NA
            df_exibicao.loc[mask_ic, "Restritivos"] = 0
        except Exception:
            pass

    # Corpus pré-indexado vetorizado para pesquisa textual instantânea
    df_exibicao["_BUSCA_CORPUS"] = (
        df_exibicao["Contraparte"].astype(str) + " " +
        df_exibicao["CNPJ"].astype(str) + " " +
        df_exibicao["Nº Contrato"].astype(str)
    ).str.lower()

    return df_exibicao


def render_visao_carteira():
    # Obter estado do pipeline
    esta_executando = False
    if "pipeline_proc" in st.session_state:
        proc = st.session_state.pipeline_proc
        if proc is not None:
            codigo_retorno = proc.poll()
            if codigo_retorno is None:
                esta_executando = True

    render_header(
        titulo="Visão da Carteira de Contratos",
        subtitulo="Monitoramento de exposição MtM, análise de crédito vigente (DF e Bureau).",
        badge_texto="EM EXECUÇÃO" if esta_executando else "SISTEMA PRONTO",
        status_online=esta_executando
    )

    with st.expander("Dicionário de Dados da Visão Carteira", expanded=False):
        st.markdown("""
        #### Bloco 1: Identificação do Contrato (Origem: Denodo Contratos)
        * **Nº Contrato (`NUMERO_REFERENCIA_CONTRATO`):** Identificador unívoco do contrato no sistema de comercialização.
        * **Operação (`MOVIMENTACAO`):** Sentido do fluxo comercial (COMPRA, VENDA, etc.).
        * **Status do Contrato (`STATUS_CONTRATO`):** Situação operacional temporal comparando a data-base com as vigências:
        - `A_FORNECER`: Data-base anterior ao início do suprimento.
        - `EM_FORNECIMENTO`: Contrato com suprimento em execução corrente.
        - `ENCERRADO`: Suprimento concluído.
        * **Data Fechamento (`DATA_FECHAMENTO`):** Data de celebração ou registro inicial da operação.
        * **Início Suprimento (`SUPRIMENTO_INICIO`):** Data inicial da entrega de energia.
        * **Fim Suprimento (`SUPRIMENTO_FIM`):** Data final da entrega de energia.
        * **Contraparte (`CONTRAPARTE_NOME_FANTASIA`):** Razão Social ou Nome Fantasia padronizado.
        * **CNPJ (`CONTRAPARTE_CNPJ`):** CNPJ canônico normalizado (14 dígitos).

        #### Bloco 2: Cruzamento de Risco Vigente (N:1)
        Cada contrato ativo é cruzado deterministicamente com o estado mais recente da análise de crédito da contraparte:
        * **Origem DF (Comercializadoras / Consumidor > 5 MWm):** Validade máxima de 18 meses a partir da competência da Demonstração Financeira.
        * **Origem Bureau (RISK3 / Consumidor ≤ 5 MWm):** Validade máxima de 12 meses a partir da consulta ao bureau de crédito.
        * **Status da Análise (`STATUS_VIGENCIA_ANALISE`):**
        - `VIGENTE`: Parecer de crédito ativo dentro do prazo de validade normativo.
        - `VENCIDA`: Prazo regulatório expirado.
        - `SEM_ANALISE`: Contraparte cadastrada sem parecer de crédito vigente (lacuna operacional).
        - `INTERCOMPANY`: Empresas do grupo societário próprio (Copel GeT, Copel Com, Elejor), isentas de risco de crédito de terceiros.
        * **Rating (`RATING`) & PD (`PD`):** Refletem estritamente a análise vigente. Em casos de `VENCIDA` ou `SEM_ANALISE`, os valores são convertidos para nulos (`pd.NA`) para não mascarar a exposição a mercado.
        * **Score Bureau (`SCORE`) & Restritivos (`RESTRITIVOS`):** Indicadores cadastrais e pontuação externa de bureau de crédito.
        * **Tipo de Análise (`TIPO_ANALISE`):** Metodologia aplicada (`Análise DF`, `Análise Bureau`, `Análise Herdada`, `Intercompany`).

        #### Bloco 3: Exposição Financeira (Origem: MtM)
        * **Portfólio (`PORTFOLIO`):** Classificação do book de negociação ou submercado.
        * **MtM Total (`MTM_TOTAL_R$`):** Marcação a mercado total acumulada do contrato (soma de parcelas líquidas).
        * **MtM VPL (`MTM_VPL_R$`):** Valor Presente Líquido da curva de exposição projetada.
        
        ### Valorados à MtM: Contratos com reconhecimento futuro
        * **Estratégia** (Aprovado em Comissão Estratégica com caráter de Trading) = Raro​
        * **Geradores NE** (Operações de LP com geradores em implantação) = Raro​
        * **Chamada 01/2020 Etapa 1** (Operações LP da CP já ocorrida em 01/2020) = não será utilizado de agora em diante​
        * **Trading** (operações de Trading para o portfólio da COPEL COM) 
        * **Direcional** (Operações de Trading para o Direcional)
        """)

    try:
        df_exibicao = carregar_dados_carteira_preparados()
    except FileNotFoundError as e:
        st.warning(f"{e} Por favor, execute o script de junção Gold.")
        return
    except Exception as e:
        st.error(f"Erro ao carregar a visão da carteira: {e}")
        return

    if df_exibicao.empty:
        st.info("Nenhum contrato encontrado na base.")
        return


    st.markdown("### Filtros de Carteira")
    f1, f2, f3, f4, f5, f6 = st.columns([2, 1, 1, 1, 1, 1])
    
    anos_disponiveis = sorted([a for a in df_exibicao["Ano_Fechamento"].unique() if a > 0])
    with f1:
        busca = st.text_input("Buscar por Contraparte/CNPJ/Contrato:", placeholder="Filtrar...", key="filtro_busca_carteira")
        
    with f2:
        anos_sel = st.multiselect("Ano Fechamento:", anos_disponiveis, default=[], key="filtro_ano_carteira")

    status_vig_disponiveis = ["Todos"] + sorted(list(df_exibicao["Status Análise"].dropna().astype(str).unique()))
    with f3:
        status_vig_sel = st.multiselect("Status Análise:", status_vig_disponiveis, key="filtro_vigencia_carteira")
        
    tipos_analise_disponiveis = ["Todos"] + sorted(list(df_exibicao["Tipo de Análise"].dropna().astype(str).unique()))
    with f4:
        tipo_sel = st.multiselect("Tipo de Análise:", tipos_analise_disponiveis, key="filtro_tipo_analise_carteira")
        
    portfolios_disponiveis = ["Todos"] + sorted([str(x) for x in df_exibicao["Portfólio"].dropna().unique() if str(x).strip()])
    with f5:
        portfolio_sel = st.multiselect("Portfólio:", portfolios_disponiveis, key="filtro_portfolio_carteira")

    status_disponiveis = ["Todos"] + sorted(list(df_exibicao["Status do Contrato"].dropna().astype(str).unique()))
    with f6:
        status_sel = st.multiselect("Status Contrato:", status_disponiveis, key="filtro_status_contrato_carteira")

    df_filtrado = df_exibicao.copy()
    
    if anos_sel:
        df_filtrado = df_filtrado[df_filtrado["Ano_Fechamento"].isin(anos_sel)]
        
    if status_vig_sel and "Todos" not in status_vig_sel:
        df_filtrado = df_filtrado[df_filtrado["Status Análise"].astype(str).isin(status_vig_sel)]

    if tipo_sel and "Todos" not in tipo_sel:
        df_filtrado = df_filtrado[df_filtrado["Tipo de Análise"].astype(str).isin(tipo_sel)]
            
    if portfolio_sel and "Todos" not in portfolio_sel:
        df_filtrado = df_filtrado[df_filtrado["Portfólio"].astype(str).isin(portfolio_sel)]

    if status_sel and "Todos" not in status_sel:
        df_filtrado = df_filtrado[df_filtrado["Status do Contrato"].astype(str).isin(status_sel)]
        
    if busca.strip():
        termo = busca.strip().lower()
        df_filtrado = df_filtrado[df_filtrado["_BUSCA_CORPUS"].str.contains(termo, regex=False, na=False)]

    st.markdown("---")

    # KPIs Executivos no Topo
    total_contratos = len(df_filtrado)
    total_contrapartes = df_filtrado["CNPJ"].nunique() if "CNPJ" in df_filtrado.columns else 0
    
    mtm_col = "MtM Total (R$)"
    mtm_total = pd.to_numeric(df_filtrado[mtm_col], errors="coerce").sum() if mtm_col in df_filtrado.columns else 0.0
    
    # Contratos com Análise Vigente vs Lacunas (Isolando Intercompany de risco de crédito de terceiros)
    vig_series = df_filtrado["Status Análise"].fillna("SEM_ANALISE").astype(str)
    
    mask_mercado = vig_series != "INTERCOMPANY"
    df_mercado = df_filtrado[mask_mercado]
    total_mercado = len(df_mercado)
    
    qtd_vigentes = sum(df_mercado["Status Análise"] == "VIGENTE")
    qtd_vencidas = sum(df_mercado["Status Análise"] == "VENCIDA")
    qtd_sem_analise = sum(df_mercado["Status Análise"] == "SEM_ANALISE")
    pct_cobertura = (qtd_vigentes / total_mercado * 100) if total_mercado > 0 else 100.0
    
    qtd_lacunas = qtd_vencidas + qtd_sem_analise
    mtm_lacunas = pd.to_numeric(df_mercado.loc[df_mercado["Status Análise"].isin(["VENCIDA", "SEM_ANALISE"]), mtm_col], errors="coerce").sum()
    
    qtd_intercompany = sum(vig_series == "INTERCOMPANY")
    mtm_intercompany = pd.to_numeric(df_filtrado.loc[vig_series == "INTERCOMPANY", mtm_col], errors="coerce").sum()

    subtexto_cobertura = f"{qtd_vigentes} de {total_mercado} contratos de mercado vigentes"
    if qtd_intercompany > 0:
        subtexto_cobertura += f" ({qtd_intercompany} intercompany isentos)"

    render_kpis([
        {
            "label": "Total de Contratos",
            "valor": f"{total_contratos:,}".replace(",", "."),
            "subtexto": f"{total_contrapartes} contrapartes distintas",
            "layer": "copel" if qtd_lacunas > 0 else "silver"
        },
        {
            "label": "Exposição Total MtM",
            "valor": f"R$ {mtm_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "subtexto": "Marcação a mercado acumulada",
            "layer": "copel" if qtd_lacunas > 0 else "silver"
        },
        {
            "label": "Cobertura de Mercado",
            "valor": f"{pct_cobertura:.1f}%",
            "subtexto": subtexto_cobertura,
            "layer": "copel" if qtd_lacunas > 0 else "silver"
        },
        {
            "label": "Lacunas de Terceiros",
            "valor": f"{qtd_lacunas} Descobertos",
            "subtexto": f"{qtd_vencidas} vencidas | {qtd_sem_analise} sem análise (R$ {mtm_lacunas:,.0f} MtM)",
            "layer": "copel" if qtd_lacunas > 0 else "silver"
        }
    ])

    st.markdown("---")

    colunas_finais = [v for k, v in COL_MAP_CARTEIRA.items() if v in df_filtrado.columns]

    st.dataframe(
        df_filtrado[colunas_finais],
        width="stretch",
        hide_index=True,
        column_config={
            "Nº Contrato": st.column_config.TextColumn("Nº Contrato", width="medium"),
            "Operação": st.column_config.TextColumn("Operação", width="small"),
            "Status do Contrato": st.column_config.TextColumn(
                "Status Contrato", 
                help="A_FORNECER, EM_FORNECIMENTO, ENCERRADO ou NAO_APLICAVEL",
                width="medium"
            ),
            "Data Fechamento": st.column_config.TextColumn("Fechamento", width="small"),
            "Início Suprimento": st.column_config.TextColumn("Início Supr.", width="small"),
            "Fim Suprimento": st.column_config.TextColumn("Fim Supr.", width="small"),
            "Contraparte": st.column_config.TextColumn("Contraparte", width="large"),
            "CNPJ": st.column_config.TextColumn("CNPJ", width="medium"),
            "MtM Total (R$)": st.column_config.NumberColumn("MtM Total (R$)", format="%.2f"),
            "MtM VPL (R$)": st.column_config.NumberColumn("MtM VPL (R$)", format="%.2f"),
            "Portfólio": st.column_config.TextColumn("Portfólio", width="small"),
            "Status Análise": st.column_config.TextColumn("Status Análise", width="small", help="VIGENTE, VENCIDA ou SEM_ANALISE"),
            "Rating": st.column_config.TextColumn("Rating", width="small"),
            "PD (%)": st.column_config.NumberColumn("PD (%)", format="%.2f%%", help="Probabilidade de Default anualizada (anulada se vencida/ausente)"),
            "Score Bureau": st.column_config.NumberColumn("Score Bureau", format="%.2f", help="Score quantitativo Risk3"),
            "Restritivos": st.column_config.NumberColumn("Restritivos", format="%.0f", help="Quantidade de apontamentos restritivos"),
            "Data Análise": st.column_config.TextColumn("Data Análise", width="small"),
            "Fim Vigência": st.column_config.TextColumn("Fim Vigência", width="small"),
            "Tipo de Análise": st.column_config.TextColumn("Tipo de Análise", width="medium")
        }
    )
