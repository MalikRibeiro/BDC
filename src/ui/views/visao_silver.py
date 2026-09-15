import streamlit as st
import pandas as pd
from pathlib import Path
import os
import sys
import json

# Adiciona o diretório src ao PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from common.identificadores import normalizar_cnpj
from common.datas import normalizar_data

BASE_DIR = Path(".")
DIAGNOSTICO_DIR = BASE_DIR / "ENTRADAS" / "atualizacoes_manuais" / "diagnostico"
RASCUNHO_PATH = DIAGNOSTICO_DIR / "rascunho_carga_manual.csv"
SCHEMA_PATH = BASE_DIR / "ENTRADAS" / "control" / "schemas" / "schema_carga_manual.json"

try:
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = json.load(f)
    MOTIVOS_PERMITIDOS = schema.get("properties", {}).get("MOTIVO", {}).get("enum", ["Outro"])
    SOLICITANTES_PERMITIDOS = schema.get("properties", {}).get("SOLICITANTE", {}).get("enum", ["Outro..."])
except Exception:
    MOTIVOS_PERMITIDOS = ["Correção de Falhas na Origem", "Atualização Histórica", "Intervenção de Alçada (Override)", "Outro"]
    SOLICITANTES_PERMITIDOS = ["Malik Ribeiro Mourad", "Eduardo Suzuki Yamauti"]

def ler_arquivo_silver(caminho_base: Path, nome_arquivo_opcional: str = None) -> pd.DataFrame | None:
    if not caminho_base.exists():
        return None

    arquivos = list(caminho_base.glob("*.parquet")) + list(caminho_base.glob("*.csv"))
    
    for arquivo in arquivos:
        if arquivo.suffix == ".parquet":
            try:
                return pd.read_parquet(arquivo)
            except Exception:
                continue
        elif arquivo.suffix == ".csv":
            try:
                return pd.read_csv(arquivo, sep=";", encoding="utf-8-sig", dtype=str)
            except Exception:
                try:
                    return pd.read_csv(arquivo, sep=",", encoding="utf-8-sig", dtype=str)
                except Exception:
                    continue
                    
    return None

def registrar_correcao_rascunho(cnpj: str, data_df: str, empresa: str, campo: str, valor_novo: str, motivo: str, solicitante: str):
    res_cnpj = normalizar_cnpj(cnpj)
    cnpj_norm = res_cnpj.cnpj if res_cnpj.cnpj else cnpj.strip()
    data_norm = normalizar_data(data_df) or data_df.strip()
    
    if RASCUNHO_PATH.exists():
        try:
            df_rascunho = pd.read_csv(RASCUNHO_PATH, sep=";", dtype=str).fillna("")
        except Exception:
            df_rascunho = pd.DataFrame()
    else:
        df_rascunho = pd.DataFrame(columns=["CNPJ", "DATA_DEMONSTRACAO_FINANCEIRA", "EMPRESA", "CAMPO_FALTANTE", "VALOR_NOVO", "FONTE", "MOTIVO", "SOLICITANTE", "TIPO_EVENTO"])

    nova_linha = {
        "CNPJ": cnpj_norm,
        "DATA_DEMONSTRACAO_FINANCEIRA": data_norm,
        "EMPRESA": empresa.strip(),
        "CAMPO_FALTANTE": campo.strip(),
        "VALOR_NOVO": str(valor_novo).strip(),
        "FONTE": "OVERRIDE_MANUAL_SILVER",
        "MOTIVO": motivo,
        "SOLICITANTE": solicitante,
        "TIPO_EVENTO": "CORRECAO"
    }

    if not df_rascunho.empty:
        df_rascunho = df_rascunho[~(
            (df_rascunho["CNPJ"].astype(str).str.strip() == cnpj_norm) & 
            (df_rascunho["DATA_DEMONSTRACAO_FINANCEIRA"].astype(str).str.strip() == data_norm) & 
            (df_rascunho["CAMPO_FALTANTE"].astype(str).str.strip().str.upper() == campo.strip().upper())
        )]

    df_rascunho = pd.concat([df_rascunho, pd.DataFrame([nova_linha])], ignore_index=True)
    DIAGNOSTICO_DIR.mkdir(parents=True, exist_ok=True)
    df_rascunho.to_csv(RASCUNHO_PATH, index=False, sep=";")

def render_visao_silver():
    st.header("Visão da Camada Silver")

    # Formulário de Correção / Override
    with st.expander("Criar Correção de Dado Incorreto", expanded=False):
        st.markdown("Utilize este formulário para solicitar a **correção de um dado incorreto** já extraído na Silver. A correção será gravada como evento `CORRECAO` e aplicada na próxima execução.")
        
        with st.form("form_correcao_silver"):
            c1, c2, c3 = st.columns(3)
            with c1:
                cnpj_input = st.text_input("CNPJ da Empresa:", placeholder="Ex: 00.001.180/0001-26")
            with c2:
                data_input = st.text_input("Data da DF (YYYY-MM-DD ou DD/MM/YYYY):", placeholder="Ex: 2024-12-31")
            with c3:
                empresa_input = st.text_input("Nome da Empresa / Sigla:", placeholder="Ex: ELETROBRAS")

            c4, c5, c6 = st.columns(3)
            with c4:
                campo_input = st.text_input("Nome da Coluna / Campo Afetado:", placeholder="Ex: PATRIMONIO_LIQUIDO")
            with c5:
                valor_antigo_input = st.text_input("Valor Anterior (Referência):", placeholder="Ex: 1000000")
            with c6:
                valor_novo_input = st.text_input("Novo Valor Correto:", placeholder="Ex: 1250000")

            c7, c8 = st.columns(2)
            with c7:
                motivo_sel = st.selectbox("Motivo da Correção:", MOTIVOS_PERMITIDOS)
            with c8:
                solicitante_sel = st.selectbox("Solicitante:", SOLICITANTES_PERMITIDOS)

            submit_correcao = st.form_submit_button("Salvar Correção no Rascunho", type="primary")
            if submit_correcao:
                if not cnpj_input.strip() or not campo_input.strip() or not valor_novo_input.strip():
                    st.error("CNPJ, Campo Afetado e Novo Valor são obrigatórios.")
                else:
                    registrar_correcao_rascunho(
                        cnpj=cnpj_input,
                        data_df=data_input,
                        empresa=empresa_input,
                        campo=campo_input,
                        valor_novo=valor_novo_input,
                        motivo=motivo_sel,
                        solicitante=solicitante_sel
                    )
                    st.success(f"Correção para o campo '{campo_input}' registrada com sucesso no rascunho de carga manual!")

    st.markdown("---")
    
    busca = st.text_input("Buscar por Contraparte, CNPJ ou Contrato:", placeholder="Digite um termo para filtrar em todas as bases...")

    # Abas de Consulta dos Datasets
    tab_com, tab_cons, tab_denodo, tab_sf, tab_rec, tab_mtm, tab_bureau, tab_garantias = st.tabs([
        "Comercializadoras",
        "Consumidores",
        "Denodo (Contratos)",
        "Salesforce (Accounts)",
        "Receita Federal",
        "MTM",
        "Bureau (Risk3)",
        "Garantias"
    ])

    silver_base = BASE_DIR / "SAIDAS" / "silver"

    def aplicar_filtro(df):
        if not busca.strip() or df is None or df.empty:
            return df
        termo = busca.strip().lower()
        
        colunas_alvo = [
            "CNPJ", "CONTRAPARTE_CNPJ", 
            "EMPRESA", "SIGLA", "CONTRAPARTE_NOME_FANTASIA", "NAME", "NOME_EMPRESARIAL", 
            "CONTRATO", "NUMERO_REFERENCIA_CONTRATO"
        ]
        
        colunas_busca = [col for col in df.columns if col.upper() in colunas_alvo]
        
        if not colunas_busca:
            colunas_busca = df.columns
            
        mask = pd.Series(False, index=df.index)
        for col in colunas_busca:
            mask = mask | df[col].astype(str).str.lower().str.contains(termo, regex=False, na=False)
            
        return df[mask]

    with tab_com:
        df = ler_arquivo_silver(silver_base / "fichas_comercializadoras_extraidas", "fichas_comercializadoras_extraidas")
        if df is not None and not df.empty:
            df_filtrado = aplicar_filtro(df)
            st.metric("Total de Registros", len(df_filtrado))
            st.dataframe(df_filtrado, use_container_width=True)
        else:
            st.warning("Base de Comercializadoras não encontrada em SAIDAS/silver/fichas_comercializadoras_extraidas. Execute o pipeline primeiro.")

    with tab_cons:
        df = ler_arquivo_silver(silver_base / "fichas_consumidores_extraidas", "fichas_consumidores_extraidas")
        if df is not None and not df.empty:
            df_filtrado = aplicar_filtro(df)
            st.metric("Total de Registros", len(df_filtrado))
            st.dataframe(df_filtrado, use_container_width=True)
        else:
            st.warning("Base de Consumidores não encontrada em SAIDAS/silver/fichas_consumidores_extraidas. Execute o pipeline primeiro.")

    with tab_denodo:
        df = ler_arquivo_silver(silver_base / "denodo_contratos_silver", "contratos_correntes")
        if df is not None and not df.empty:
            df_filtrado = aplicar_filtro(df)
            st.metric("Total de Contratos", len(df_filtrado))
            st.dataframe(df_filtrado, use_container_width=True)
        else:
            st.warning("Base do Denodo não encontrada em SAIDAS/silver/denodo_contratos_silver. Execute o pipeline primeiro.")

    with tab_sf:
        df = ler_arquivo_silver(silver_base / "salesforce_silver" / "account", "salesforce_account")
        if df is not None and not df.empty:
            df_filtrado = aplicar_filtro(df)
            st.metric("Total de Contas Salesforce", len(df_filtrado))
            st.dataframe(df_filtrado, use_container_width=True)
        else:
            st.warning("Base do Salesforce não encontrada em SAIDAS/silver/salesforce_silver/account. Execute o pipeline primeiro.")

    with tab_rec:
        df = ler_arquivo_silver(silver_base / "receita_silver", "receita_cadastral_silver")
        if df is not None and not df.empty:
            df_filtrado = aplicar_filtro(df)
            st.metric("Total de Registros Cadastrais", len(df_filtrado))
            st.dataframe(df_filtrado, use_container_width=True)
        else:
            st.warning("Base da Receita Federal não encontrada em SAIDAS/silver/receita_silver. Execute o pipeline primeiro.")

    with tab_mtm:
        df = ler_arquivo_silver(silver_base / "mtm_consolidado_silver", "mtm_consolidado")
        if df is not None and not df.empty:
            df_filtrado = aplicar_filtro(df)
            st.metric("Total de Registros MTM", len(df_filtrado))
            st.dataframe(df_filtrado, use_container_width=True)
        else:
            st.warning("Base de MTM não encontrada em SAIDAS/silver/mtm_consolidado_silver. Execute o pipeline primeiro.")

    with tab_bureau:
        df = ler_arquivo_silver(silver_base / "fato_bureau_silver", "fato_bureau")
        if df is not None and not df.empty:
            df_filtrado = aplicar_filtro(df)
            st.metric("Total de Registros Bureau", len(df_filtrado))
            st.dataframe(df_filtrado, use_container_width=True)
        else:
            st.warning("Base de Bureau não encontrada em SAIDAS/silver/fato_bureau_silver. Execute o pipeline primeiro.")

    with tab_garantias:
        df = ler_arquivo_silver(silver_base / "garantias_silver", "garantias")
        if df is not None and not df.empty:
            df_filtrado = aplicar_filtro(df)
            st.metric("Total de Registros de Garantias", len(df_filtrado))
            st.dataframe(df_filtrado, use_container_width=True)
        else:
            st.warning("Base de Garantias não encontrada em SAIDAS/silver/garantias_silver. Execute o pipeline primeiro.")
