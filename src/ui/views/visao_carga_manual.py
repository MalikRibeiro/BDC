import streamlit as st
import pandas as pd
from pathlib import Path
import os
import sys
import json

# Adiciona o diretório src ao PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from domain.diagnostico.servico_diagnostico import gerar_diagnostico
from domain.diagnostico.servico_exportacao import exportar_carga_manual
from common.identificadores import normalizar_cnpj
from common.datas import normalizar_data

BASE_DIR = Path(".")
DIAGNOSTICO_DIR = BASE_DIR / "ENTRADAS" / "atualizacoes_manuais" / "diagnostico"
FILA_PATH = DIAGNOSTICO_DIR / "fila_pendencias.csv"
RASCUNHO_PATH = DIAGNOSTICO_DIR / "rascunho_carga_manual.csv"
SCHEMA_PATH = BASE_DIR / "ENTRADAS" / "control" / "schemas" / "schema_carga_manual.json"

# Carrega opções do JSON Schema obrigatoriamente (Governança Estrita)
try:
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = json.load(f)
    MOTIVOS_PERMITIDOS = schema.get("properties", {}).get("MOTIVO", {}).get("enum", [])
    SOLICITANTES_PERMITIDOS = schema.get("properties", {}).get("SOLICITANTE", {}).get("enum", [])
except Exception:
    MOTIVOS_PERMITIDOS = []
    SOLICITANTES_PERMITIDOS = []

def formatar_cnpj_canonico(val: str) -> str:
    res = normalizar_cnpj(val)
    return res.cnpj if res.cnpj else str(val or "").strip()

def formatar_data_canonica(val: str) -> str:
    res = normalizar_data(val)
    return res if res else str(val or "").strip()[:10]

def montar_chave_pendencia(row) -> str:
    c = formatar_cnpj_canonico(row.get("CNPJ", ""))
    d = formatar_data_canonica(row.get("DATA_DEMONSTRACAO_FINANCEIRA", ""))
    f = str(row.get("CAMPO_FALTANTE", "")).strip().upper()
    return f"{c}_{d}_{f}"

def carregar_dados():
    if FILA_PATH.exists():
        df_fila = pd.read_csv(FILA_PATH, sep=";", dtype=str).fillna("")
        df_fila.columns = df_fila.columns.str.strip()
        for col in df_fila.columns:
            df_fila[col] = df_fila[col].astype(str).str.strip()
    else:
        df_fila = pd.DataFrame(columns=["CNPJ", "DATA_DEMONSTRACAO_FINANCEIRA", "EMPRESA", "CAMPO_FALTANTE", "STATUS", "VALOR_RECUPERADO"])

    if RASCUNHO_PATH.exists():
        df_rascunho = pd.read_csv(RASCUNHO_PATH, sep=";", dtype=str).fillna("")
        df_rascunho.columns = df_rascunho.columns.str.strip()
        for col in df_rascunho.columns:
            df_rascunho[col] = df_rascunho[col].astype(str).str.strip()
    else:
        df_rascunho = pd.DataFrame(columns=["CNPJ", "DATA_DEMONSTRACAO_FINANCEIRA", "EMPRESA", "CAMPO_FALTANTE", "VALOR_NOVO", "FONTE", "MOTIVO", "SOLICITANTE", "TIPO_EVENTO"])
        
    return df_fila, df_rascunho

def salvar_form_rascunho(cnpj, data_df, empresa, campos):
    df_fila, df_rascunho = carregar_dados()
    novas_linhas = []
    
    for campo in campos:
        key_prefix = f"{cnpj}_{data_df}_{empresa}_{campo}"
        valor = st.session_state.get(f"{key_prefix}_valor", "")
        fonte = st.session_state.get(f"{key_prefix}_fonte", "FICHA")
        motivo = st.session_state.get(f"{key_prefix}_motivo", "")
        solicitante = st.session_state.get(f"{key_prefix}_solicitante", "")
        
        if str(valor).strip() != "":
            cnpj_canonico = formatar_cnpj_canonico(cnpj)
            data_canonica = formatar_data_canonica(data_df)
            novas_linhas.append({
                "CNPJ": cnpj_canonico,
                "DATA_DEMONSTRACAO_FINANCEIRA": str(data_df).strip(),
                "EMPRESA": str(empresa).strip(),
                "CAMPO_FALTANTE": str(campo).strip(),
                "VALOR_NOVO": str(valor).strip(),
                "FONTE": str(fonte).strip(),
                "MOTIVO": str(motivo).strip(),
                "SOLICITANTE": str(solicitante).strip(),
                "TIPO_EVENTO": "COMPLEMENTACAO"
            })
            
            # Remove se já existir para dar update
            if not df_rascunho.empty:
                df_rascunho = df_rascunho[~(
                    (df_rascunho["CNPJ"].apply(formatar_cnpj_canonico) == cnpj_canonico) & 
                    (df_rascunho["DATA_DEMONSTRACAO_FINANCEIRA"].apply(formatar_data_canonica) == data_canonica) & 
                    (df_rascunho["CAMPO_FALTANTE"].astype(str).str.strip().str.upper() == str(campo).strip().upper())
                )]
                                        
    if novas_linhas:
        df_rascunho = pd.concat([df_rascunho, pd.DataFrame(novas_linhas)], ignore_index=True)
        DIAGNOSTICO_DIR.mkdir(parents=True, exist_ok=True)
        df_rascunho.to_csv(RASCUNHO_PATH, index=False, sep=";")

def limpar_rascunho():
    if RASCUNHO_PATH.exists():
        RASCUNHO_PATH.unlink()

def render_visao_carga_manual():
    st.header("Carga Manual")
    
    if st.session_state.pop("sucesso_salvamento", False):
        st.success("Resoluções salvas com sucesso! Os campos foram transferidos para a aba 'Resoluções Salvas'.")
        
    df_fila, df_rascunho = carregar_dados()
    
    with st.sidebar:
        st.header("Operações de Diagnóstico")
        if st.button("Gerar Diagnóstico Atualizado", use_container_width=True):
            with st.spinner("Lendo Silver e gerando fila de pendências..."):
                gerar_diagnostico()
            st.success("Diagnóstico concluído!")
            st.rerun()
            
        if st.button("Exportar Carga Manual", use_container_width=True, type="primary"):
            with st.spinner("Exportando..."):
                sucesso = exportar_carga_manual()
                if sucesso:
                    st.success("Carga exportada com sucesso!")
                    st.rerun()
                else:
                    st.warning("Nada para exportar (Rascunho vazio).")
                    
        st.markdown("---")
        st.subheader("Configurações de Exibição")
        itens_por_pagina = st.selectbox("Fichas por página:", [5, 10, 20, 50], index=1)

    # Filtra as pendências que já estão resolvidas no rascunho
    if not df_rascunho.empty and not df_fila.empty:
        chaves_resolvidas = set(df_rascunho.apply(montar_chave_pendencia, axis=1))
        chaves_fila = df_fila.apply(montar_chave_pendencia, axis=1)
        df_fila_pendente = df_fila[~chaves_fila.isin(chaves_resolvidas)].copy()
    else:
        df_fila_pendente = df_fila.copy()

    # Métricas gerais no topo
    grupos_totais = list(df_fila_pendente.groupby(["CNPJ", "DATA_DEMONSTRACAO_FINANCEIRA", "EMPRESA"])) if not df_fila_pendente.empty else []
    
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Campos Pendentes", len(df_fila_pendente))
    col_m2.metric("Fichas a Resolver", len(grupos_totais))
    col_m3.metric("Campos Resolvidos", len(df_rascunho) if not df_rascunho.empty else 0)

    st.markdown("---")

    # Abas para separar Pendências de Resoluções Salvas
    tab_pendencias, tab_rascunho = st.tabs([
        f"Pendências ({len(df_fila_pendente)})", 
        f"Resoluções Salvas ({len(df_rascunho)})"
    ])

    # ---------------- ABA 1: PENDÊNCIAS ----------------
    with tab_pendencias:
        if df_fila_pendente.empty:
            if not df_rascunho.empty:
                st.success("🎉 Todas as pendências foram preenchidas e estão salvas no rascunho! Vá para a aba 'Resoluções Salvas' para conferir e exportar a carga.")
            else:
                st.info("Nenhuma pendência na fila. Clique em 'Gerar Diagnóstico Atualizado' para varrer a camada Silver.")
        else:
            # Corrige bug visual do Pandas que oculta registros com chaves nulas no groupby
            df_fila_pendente["CNPJ"] = df_fila_pendente["CNPJ"].replace("", "CNPJ_DESCONHECIDO")
            df_fila_pendente["DATA_DEMONSTRACAO_FINANCEIRA"] = df_fila_pendente["DATA_DEMONSTRACAO_FINANCEIRA"].replace("", "DATA_DESCONHECIDA")
            df_fila_pendente["EMPRESA"] = df_fila_pendente["EMPRESA"].replace("", "EMPRESA_DESCONHECIDA")

            # Barra de busca rápida
            busca = st.text_input("Filtrar por Empresa, CNPJ ou Campo:", placeholder="Digite o nome da empresa, CNPJ ou campo para filtrar...", key="busca_pendencias")
            
            if busca.strip():
                termo = busca.strip().lower()
                df_filtrado = df_fila_pendente[
                    df_fila_pendente["EMPRESA"].astype(str).str.lower().str.contains(termo) |
                    df_fila_pendente["CNPJ"].astype(str).str.lower().str.contains(termo) |
                    df_fila_pendente["CAMPO_FALTANTE"].astype(str).str.lower().str.contains(termo)
                ]
            else:
                df_filtrado = df_fila_pendente

            if df_filtrado.empty:
                st.warning(f"Nenhum registro encontrado para a busca '{busca}'.")
            else:
                grupos = list(df_filtrado.groupby(["CNPJ", "DATA_DEMONSTRACAO_FINANCEIRA", "EMPRESA"]))
                total_fichas = len(grupos)
                total_paginas = max(1, (total_fichas + itens_por_pagina - 1) // itens_por_pagina)
                
                if "pagina_carga" not in st.session_state:
                    st.session_state["pagina_carga"] = 1
                if st.session_state["pagina_carga"] > total_paginas:
                    st.session_state["pagina_carga"] = total_paginas
                    
                pagina_atual = st.session_state["pagina_carga"]
                inicio = (pagina_atual - 1) * itens_por_pagina
                fim = min(inicio + itens_por_pagina, total_fichas)
                
                st.caption(f"Exibindo fichas **{inicio + 1}** até **{fim}** de **{total_fichas}** fichas ({len(df_filtrado)} campos pendentes nesta visão).")
                
                grupos_pagina = grupos[inicio:fim]

                for (cnpj, data_df, empresa), grupo in grupos_pagina:
                    try:
                        data_df_exibicao = pd.to_datetime(data_df).strftime("%d/%m/%Y")
                    except Exception:
                        data_df_exibicao = str(data_df).split(" ")[0]
                        
                    with st.expander(f"🏢 {empresa} | CNPJ: {cnpj} | DF: {data_df_exibicao} ({len(grupo)} campos pendentes)", expanded=True):
                        arquivo_origem = grupo.iloc[0].get("ARQUIVO_ORIGEM", "Desconhecido")
                        st.info(f"Ficha mapeada: {arquivo_origem}")
                        st.markdown("---")
                        
                        with st.form(key=f"form_{cnpj}_{data_df}_{empresa}"):
                            campos_do_grupo = []
                            for _, row in grupo.iterrows():
                                campo = row["CAMPO_FALTANTE"]
                                status = row["STATUS"]
                                campos_do_grupo.append(campo)
                                
                                col1, col2, col3, col4, col5 = st.columns([1.2, 1.2, 1.2, 1.5, 1.5])
                                
                                key_prefix = f"{cnpj}_{data_df}_{empresa}_{campo}"
                                
                                with col1:
                                    st.text_input(
                                        "Campo Faltante", 
                                        value=campo, 
                                        disabled=True, 
                                        key=f"{key_prefix}_nome"
                                    )
                                
                                with col2:
                                    st.text_input(
                                        "Novo Valor", 
                                        key=f"{key_prefix}_valor"
                                    )
                                with col3:
                                    st.selectbox(
                                        "Fonte", 
                                        ["FICHA", "DEMONSTRACAO_FINANCEIRA", "CONSULTA_PUBLICA"], 
                                        key=f"{key_prefix}_fonte"
                                    )
                                with col4:
                                    st.selectbox(
                                        "Motivo", 
                                        MOTIVOS_PERMITIDOS,
                                        key=f"{key_prefix}_motivo"
                                    )
                                with col5:
                                    st.selectbox(
                                        "Solicitante", 
                                        SOLICITANTES_PERMITIDOS,
                                        key=f"{key_prefix}_solicitante"
                                    )
                                    
                            submit = st.form_submit_button("Salvar Resoluções")
                            if submit:
                                salvar_form_rascunho(cnpj, data_df, empresa, campos_do_grupo)
                                st.session_state["sucesso_salvamento"] = True
                                st.rerun()
                                
                # Renderização dos botões de paginação no final
                st.markdown("<br>", unsafe_allow_html=True)
                col_p1, col_p2, col_p3 = st.columns([1, 3, 1])
                with col_p1:
                    if st.button("Anterior", disabled=st.session_state["pagina_carga"] <= 1, use_container_width=True, key="btn_prev_pend"):
                        st.session_state["pagina_carga"] -= 1
                        st.rerun()
                with col_p2:
                    st.markdown(f"<div style='text-align: center; margin-top: 5px; font-size: 16px;'>Página <b>{st.session_state['pagina_carga']}</b> de {total_paginas}</div>", unsafe_allow_html=True)
                with col_p3:
                    if st.button("Próxima", disabled=st.session_state["pagina_carga"] >= total_paginas, use_container_width=True, key="btn_next_pend"):
                        st.session_state["pagina_carga"] += 1
                        st.rerun()

    # ---------------- ABA 2: RESOLUÇÕES SALVAS (RASCUNHO) ----------------
    with tab_rascunho:
        if df_rascunho.empty:
            st.info("Nenhuma resolução salva no rascunho ainda. Preencha os valores na aba 'Pendências' e clique em 'Salvar Resoluções'.")
        else:
            st.success(f"Você possui **{len(df_rascunho)}** campos resolvidos prontos para exportação.")
            
            col_b1, col_b2 = st.columns([1, 4])
            with col_b1:
                if st.button("Exportar Carga Manual", key="btn_exportar_tab", type="primary", use_container_width=True):
                    with st.spinner("Exportando..."):
                        sucesso = exportar_carga_manual()
                        if sucesso:
                            st.success("Carga exportada com sucesso!")
                            st.rerun()
            with col_b2:
                if st.button("Limpar Rascunho", key="btn_limpar_tab"):
                    limpar_rascunho()
                    st.warning("Rascunho limpo com sucesso!")
                    st.rerun()
                    
            st.markdown("---")
            colunas_exibir = [c for c in ["EMPRESA", "CNPJ", "DATA_DEMONSTRACAO_FINANCEIRA", "CAMPO_FALTANTE", "VALOR_NOVO", "FONTE", "MOTIVO", "SOLICITANTE", "TIPO_EVENTO"] if c in df_rascunho.columns]
            st.dataframe(
                df_rascunho[colunas_exibir],
                use_container_width=True,
                hide_index=True
            )
