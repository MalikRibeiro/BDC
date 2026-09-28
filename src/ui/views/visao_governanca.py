import streamlit as st
import pandas as pd
from pathlib import Path
import sys
from datetime import datetime, timedelta
from ui.theme import render_header, render_kpis

BASE_DIR = Path(".").resolve()

def ler_parquet_ou_csv(caminho_dir: Path, nome_base: str) -> pd.DataFrame:
    parquet_path = caminho_dir / f"{nome_base}.parquet"
    csv_path = caminho_dir / f"{nome_base}.csv"
    
    df = pd.DataFrame()
    if parquet_path.exists():
        try:
            df = pd.read_parquet(parquet_path)
        except Exception: pass
            
    if df.empty and csv_path.exists():
        try:
            df = pd.read_csv(csv_path, sep=";", encoding="utf-8-sig", dtype=str)
        except Exception: pass
                
    if not df.empty:
        df.columns = [str(c).replace("\ufeff", "").strip().upper() for c in df.columns]
        df = df.loc[:, ~df.columns.duplicated()].copy()
        
    return df

def render_visao_governanca():
    render_header(
        titulo="Governança, Auditoria e Alertas",
        subtitulo="Monitoramento de conformidade de crédito, integridade de tabelas de controle e vigência de análises.",
        badge_texto="Controle & Auditoria",
        status_online=True
    )
    
    tab_alertas, tab_auditoria, tab_vencimentos = st.tabs(["Alertas de Crédito", "Tabelas de Controle (Auditoria)", "Controle de Vencimentos"])

    with tab_alertas:
        dir_alertas = BASE_DIR / "SAIDAS" / "gold" / "alertas"
        df_alertas = ler_parquet_ou_csv(dir_alertas, "alertas_consolidados")
        
        if df_alertas.empty:
            st.info("Nenhum alerta crítico encontrado no pipeline atual.")
        else:
            total_alertas = len(df_alertas)
            total_criticos = len(df_alertas[df_alertas.get("SEVERIDADE", "") == "CRITICO"]) if "SEVERIDADE" in df_alertas.columns else 0
            total_risco = len(df_alertas[df_alertas.get("CODIGO", "").astype(str).str.contains("RAT|EXP")]) if "CODIGO" in df_alertas.columns else 0

            render_kpis([
                {
                    "label": "Total de Apontamentos",
                    "valor": str(total_alertas),
                    "subtexto": "Todos os alertas consolidados",
                    "layer": "silver"
                },
                {
                    "label": "Alertas Críticos",
                    "valor": str(total_criticos),
                    "subtexto": "Exigem ação imediata da mesa",
                    "layer": "warning"
                },
                {
                    "label": "Risco de Rating/Exposição",
                    "valor": str(total_risco),
                    "subtexto": "Códigos RAT / EXP acionados",
                    "layer": "copel"
                }
            ])

            if "filtro_alerta" not in st.session_state:
                st.session_state["filtro_alerta"] = "Todos"

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"Exibir Todos ({total_alertas})", width="stretch"):
                    st.session_state["filtro_alerta"] = "Todos"
            with col2:
                if st.button(f"Apenas Críticos ({total_criticos})", width="stretch"):
                    st.session_state["filtro_alerta"] = "Criticos"
            with col3:
                if st.button(f"Apenas RAT/EXP ({total_risco})", width="stretch"):
                    st.session_state["filtro_alerta"] = "Risco"
            
            st.markdown(f"<p style='color: var(--primary); font-weight: bold;'>Filtro Aplicado: {st.session_state['filtro_alerta']}</p>", unsafe_allow_html=True)
            
            df_mostrar = df_alertas
            if st.session_state["filtro_alerta"] == "Criticos" and "SEVERIDADE" in df_alertas.columns:
                df_mostrar = df_alertas[df_alertas["SEVERIDADE"] == "CRITICO"]
            elif st.session_state["filtro_alerta"] == "Risco" and "CODIGO" in df_alertas.columns:
                df_mostrar = df_alertas[df_alertas["CODIGO"].astype(str).str.contains("RAT|EXP")]

            st.dataframe(
                df_mostrar,
                width="stretch",
                height=400
            )

    with tab_auditoria:
        st.subheader("Tabelas de Controle do Sistema (Aprovadas pela Auditoria)")
        
        ctrl_dir = BASE_DIR / "ENTRADAS" / "control" / "relational_control"
        tabelas_disponiveis = [
            "ctl_run_pipeline", "ctl_evento_processamento", "ctl_documento",
            "ctl_mudanca_config", "ctl_override", "ctl_reconciliacao"
        ]
        
        selecao_tabela = st.selectbox("Selecione a Tabela de Controle:", tabelas_disponiveis)
        
        if selecao_tabela:
            df_ctrl = ler_parquet_ou_csv(ctrl_dir, selecao_tabela)
            if not df_ctrl.empty:
                st.dataframe(df_ctrl.sort_values(by=df_ctrl.columns[0], ascending=False) if len(df_ctrl.columns) > 0 else df_ctrl, width="stretch")
            else:
                st.warning(f"Tabela {selecao_tabela} ainda vazia ou não inicializada nesta rodada.")

    with tab_vencimentos:
        st.subheader("Controle de Vencimentos de Análises")

        # ---------------- FILTROS SUPERIORES ----------------
        st.markdown("Filtros de Vencimento")
        filtro_faixa = st.selectbox("Selecione a Faixa de Vencimento:", ["Todos", "Vencida", "Vence em até 15 dias", "Entre 16 e 30 dias", "Entre 31 e 60 dias", "Entre 61 e 90 dias", "Acima de 90 dias"])
    
        
        gold_dir = BASE_DIR / "SAIDAS" / "gold" / "visao_operacional_negocio"
        df_gold = ler_parquet_ou_csv(gold_dir, "Visao_Operacional_BDC_LATEST")
        
        if df_gold.empty:
            st.error("Base Gold não encontrada.")
        else:
            # Lógica de agrupamento por Faixa de Vencimento
            agora = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            vencimentos = []
            
            for _, row in df_gold.iterrows():
                cnpj = row.get("CNPJ", "")
                nome = row.get("NOME", row.get("SIGLA", cnpj))
                
                # Definir a data da análise e calcular validade (18 meses por default na NT)
                data_base_str = row.get("DATA_BALANCO_USADO", row.get("DATA_ANALISE", ""))
                try:
                    dt_base = pd.to_datetime(data_base_str)
                    if pd.isna(dt_base): raise ValueError()
                    
                    dt_vencimento = dt_base + timedelta(days=540) # Default 18 meses
                    dias_restantes = (dt_vencimento - agora).days
                    
                    if dias_restantes < 0:
                        faixa = "Vencida"
                    elif dias_restantes <= 15:
                        faixa = "Vence em até 15 dias"
                    elif dias_restantes <= 30:
                        faixa = "Entre 16 e 30 dias"
                    elif dias_restantes <= 60:
                        faixa = "Entre 31 e 60 dias"
                    elif dias_restantes <= 90:
                        faixa = "Entre 61 e 90 dias"
                    else:
                        faixa = "Acima de 90 dias"
                        
                    vencimentos.append({
                        "CNPJ": cnpj,
                        "CONTRAPARTE": nome,
                        "DATA_REFERENCIA": dt_base.strftime("%Y-%m-%d"),
                        "DATA_VENCIMENTO": dt_vencimento.strftime("%Y-%m-%d"),
                        "DIAS_RESTANTES": dias_restantes,
                        "FAIXA_VENCIMENTO": faixa,
                        "STATUS_ANALISE": row.get("SITUACAO_ANALISE", "")
                    })
                except Exception:
                    pass
            
            df_venc = pd.DataFrame(vencimentos)
            if not df_venc.empty:
                # Ordena para mostrar as piores faixas primeiro
                ordem = ["Vencida", "Vence em até 15 dias", "Entre 16 e 30 dias", "Entre 31 e 60 dias", "Entre 61 e 90 dias", "Acima de 90 dias"]
                df_venc["FAIXA_ORDEM"] = pd.Categorical(df_venc["FAIXA_VENCIMENTO"], categories=ordem, ordered=True)
                df_venc = df_venc.sort_values(["FAIXA_ORDEM", "DIAS_RESTANTES"])
                
                # Resumo
                st.write("**Resumo por Faixa de Vencimento:**")
                resumo = df_venc["FAIXA_VENCIMENTO"].value_counts().reindex(ordem).fillna(0).astype(int)
                
                cols = st.columns(len(ordem))
                for idx, (faixa, count) in enumerate(resumo.items()):
                    cor = "#f5821e" if ("Vencida" in faixa or "15" in faixa or "30" in faixa) else "#9fa1a4"
                    cols[idx].markdown(f"<div style='text-align: center; padding: 10px; border-radius: 8px; border: 1px solid var(--bdc-surface-border);'><h4 style='color: {cor}; margin:0;'>{count}</h4><small>{faixa}</small></div>", unsafe_allow_html=True)
                
                st.markdown("---")
                df_exibir = df_venc.drop(columns=["FAIXA_ORDEM"])
                if filtro_faixa != "Todos":
                    df_exibir = df_exibir[df_exibir["FAIXA_VENCIMENTO"] == filtro_faixa]
                st.dataframe(df_exibir, width="stretch")
            else:
                st.info("Nenhuma análise ativa para calcular vencimentos.")
