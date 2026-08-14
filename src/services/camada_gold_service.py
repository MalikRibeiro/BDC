"""
Construtor da Visão Operacional Consolidada (Camada Gold) e Interface de Limites.
Atende às Prioridades de Governança de DF e Interface com Sistema Externo.
"""
from __future__ import annotations
import logging
from datetime import datetime
from typing import Any
import pandas as pd
from app.context import AppContext
from storage.silver_store import write_silver_dataset

def _classificar_matriz_operacional(row: pd.Series) -> str:
    c = row.get("STATUS_CONTRATUAL", "SEM_CONTRATO")
    a = row.get("SITUACAO_ANALISE", "SEM_ANALISE")
    if c == "CONTRATO_VIGENTE":
        if a == "VIGENTE": return "CONTRATO_VIGENTE_ANALISE_VIGENTE"
        if a == "VENCIDA": return "CONTRATO_VIGENTE_ANALISE_VENCIDA"
        return "CONTRATO_VIGENTE_SEM_ANALISE"
    if c == "CONTRATO_FUTURO":
        if a == "VIGENTE": return "CONTRATO_FUTURO_ANALISE_VIGENTE"
        if a == "VENCIDA": return "CONTRATO_FUTURO_ANALISE_VENCIDA"
        return "CONTRATO_FUTURO_SEM_ANALISE"
    if c == "SEM_CONTRATO":
        if a == "VIGENTE": return "SEM_CONTRATO_ANALISE_VIGENTE"
        if a == "VENCIDA": return "SEM_CONTRATO_ANALISE_VENCIDA"
        return "SEM_CONTRATO_SEM_ANALISE"
    return "OUTROS"

def exportar_visao_consolidada_gold(context: AppContext) -> dict[str, Any]:
    run_id = f"GLD_MVP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = logging.getLogger("bdc.gold.operacional")

    # 1. Carregamento de Todas as Bases do Cruzamento (Stitching)
    path_contratos = context.path("silver") / "denodo_contratos_silver" / "contratos_correntes.parquet"
    path_analises = context.path("relational_facts") / "fato_analise_credito.parquet"
    path_contraparte = context.path("relational_dimensions") / "dim_contraparte.parquet"
    path_risco = context.path("relational_facts") / "fato_exposicao_risco_LATEST.parquet"
    
    # Enquadramento Dinâmico
    relational_configs = context.path("relational_configs")
    enquadramento_files = list(relational_configs.glob("enquadramento_consumidores_*.parquet"))
    path_enquadramento = max(enquadramento_files, key=lambda f: f.stat().st_mtime) if enquadramento_files else None
    
    df_contratos = pd.read_parquet(path_contratos) if path_contratos.exists() else pd.DataFrame()
    df_analises = pd.read_parquet(path_analises) if path_analises.exists() else pd.DataFrame()
    df_contraparte = pd.read_parquet(path_contraparte) if path_contraparte.exists() else pd.DataFrame()
    df_risco = pd.read_parquet(path_risco) if path_risco.exists() else pd.DataFrame()
    df_enquadramento = pd.read_parquet(path_enquadramento) if path_enquadramento else pd.DataFrame(columns=["CNPJ", "POSSUI_PELO_MENOS_5_MWM"])

    hoje = pd.Timestamp(datetime.now().date())

    # 2. Consolidação Contratual
    df_contratos_agg = pd.DataFrame()
    if not df_contratos.empty:
        df_contratos["CNPJ"] = df_contratos["CNPJ"].astype(str).str.zfill(14)
        df_contratos["VOLUME_MWM"] = pd.to_numeric(df_contratos.get("VOLUME_CONTRATADO_MENSAL_MWM", 0), errors="coerce").fillna(0.0)
        df_contratos["INICIO"] = pd.to_datetime(df_contratos.get("VIGENCIA_INICIO"), errors="coerce")
        df_contratos["FIM"] = pd.to_datetime(df_contratos.get("VIGENCIA_FIM"), errors="coerce")
        df_contratos["EH_VIGENTE"] = (df_contratos["INICIO"] <= hoje) & (df_contratos["FIM"] >= hoje)
        df_contratos["EH_FUTURO"] = (df_contratos["INICIO"] > hoje)
        
        df_contratos_agg = df_contratos.groupby("CNPJ").agg(
            QTD_CONTRATOS=("CONTRATO", "nunique"), VOLUME_MWM=("VOLUME_MWM", "sum"),
            QTD_VIGENTES=("EH_VIGENTE", "sum"), QTD_FUTUROS=("EH_FUTURO", "sum"),
            PROXIMO_INICIO=("INICIO", "min"), PROXIMO_FIM=("FIM", "max")
        ).reset_index()
        
        df_contratos_agg["STATUS_CONTRATUAL"] = df_contratos_agg.apply(lambda r: "CONTRATO_VIGENTE" if r["QTD_VIGENTES"] > 0 else ("CONTRATO_FUTURO" if r["QTD_FUTUROS"] > 0 else "CONTRATO_VENCIDO"), axis=1)
        df_contratos_agg["TEM_CONTRATO"] = df_contratos_agg["STATUS_CONTRATUAL"].isin(["CONTRATO_VIGENTE", "CONTRATO_FUTURO"]).map({True:"SIM", False:"NÃO"})

    # 3. Consolidação de Análises e Fichas
    df_analises_agg = pd.DataFrame()
    if not df_analises.empty:
        df_analises["CNPJ"] = df_analises["CNPJ"].astype(str).str.zfill(14)
        df_analises = df_analises.dropna(subset=["CNPJ"]).copy()
        
        # Reconhecimento do Placeholder (0001-01-01) injetado na Silver
        df_analises["DATA_BALANCO_DT"] = pd.to_datetime(df_analises.get("DATA_BALANCO_USADO"), errors="coerce")
        mask_valida = (df_analises["DATA_BALANCO_DT"].dt.year > 1900) & (df_analises["DATA_BALANCO_DT"].notna())
        
        df_analises.loc[mask_valida, "VALIDADE_DT"] = df_analises.loc[mask_valida, "DATA_BALANCO_DT"] + pd.DateOffset(years=1, months=4)
        df_analises.loc[~mask_valida, "VALIDADE_DT"] = pd.NaT
        
        df_analises = df_analises.sort_values("DATA_BALANCO_DT").drop_duplicates("CNPJ", keep="last")
        df_analises["SITUACAO_ANALISE"] = df_analises["VALIDADE_DT"].apply(lambda x: "VIGENTE" if pd.notnull(x) and x >= hoje else ("VENCIDA" if pd.notnull(x) else "SEM_ANALISE"))
        
        # Reverte o fallback da data para exibir "-" nos relatórios em vez de data falsa
        df_analises.loc[~mask_valida, "DATA_BALANCO_USADO"] = "-"
        
        col_map = {
            "DATA_ANALISE": "DATA_ANALISE", "DATA_BALANCO_USADO": "DATA_DF", "RATING_FINAL": "RATING", 
            "PD_FINAL": "PD", "MODELO_METODOLOGICO": "MODELO_ANALISE", "PATRIMONIO_LIQUIDO": "PATRIMONIO_LIQUIDO", 
            "SITUACAO_DF": "SITUACAO_DF"
        }
        df_analises_agg = df_analises.rename(columns=col_map)
        df_analises_agg["VALIDADE_ANALISE"] = df_analises_agg["VALIDADE_DT"].dt.strftime("%d/%m/%Y")
        df_analises_agg["TEM_ANALISE"] = "SIM"

    # 4. Master Join: Onde a Governança Acontece
    if df_contratos_agg.empty and df_analises_agg.empty:
        return {"run_id": run_id, "status": "SEM_DADOS"}
    elif df_contratos_agg.empty:
        df_gold = df_analises_agg.copy()
    elif df_analises_agg.empty:
        df_gold = df_contratos_agg.copy()
    else:
        df_gold = pd.merge(df_contratos_agg, df_analises_agg, on="CNPJ", how="outer")

    # BLINDAGEM DE JOINS: Seleção dinâmica (evita KeyError)
    if not df_contraparte.empty:
        df_contraparte["CNPJ"] = df_contraparte["CNPJ"].astype(str).str.zfill(14)
        cols_contra = [c for c in ["CNPJ", "SEGMENTO_METODOLOGICO", "SITUACAO_CADASTRAL"] if c in df_contraparte.columns]
        df_gold = pd.merge(df_gold, df_contraparte[cols_contra], on="CNPJ", how="left")

    if not df_enquadramento.empty:
        df_enquadramento["CNPJ"] = df_enquadramento["CNPJ"].astype(str).str.zfill(14)
        cols_enq = [c for c in ["CNPJ", "POSSUI_PELO_MENOS_5_MWM"] if c in df_enquadramento.columns]
        df_gold = pd.merge(df_gold, df_enquadramento[cols_enq], on="CNPJ", how="left")

    if not df_risco.empty:
        df_risco["CNPJ"] = df_risco["CNPJ"].astype(str).str.zfill(14)
        df_risco = df_risco.drop_duplicates(subset=["CNPJ"], keep="last")
        cols_risco = [c for c in ["CNPJ", "EAD_VALOR", "LGD_LIQUIDA", "PE_REAIS"] if c in df_risco.columns]
        df_gold = pd.merge(df_gold, df_risco[cols_risco], on="CNPJ", how="left")

    # 5. PRIORIDADE 2: Tratamento de Governança de Ausência de DF (§14.2)
    def definir_situacao_df(row):
        seg = str(row.get("SEGMENTO_METODOLOGICO", "")).upper()
        tem_analise = row.get("TEM_ANALISE") == "SIM"
        is_gt5 = row.get("POSSUI_PELO_MENOS_5_MWM") == True
        
        if seg == "CONSUMIDOR_LE_5" or (seg == "CONSUMIDOR" and not is_gt5):
            return "NAO_APLICAVEL"
            
        if tem_analise and pd.notna(row.get("DATA_DF")):
            return "RECEBIDA"
            
        return "NAO_RECEBIDA"

    def ajustar_analise_df(row):
        if row["SITUACAO_DF"] == "NAO_RECEBIDA":
            return "IRREGULAR"
        return row.get("SITUACAO_ANALISE", "SEM_ANALISE")

    df_gold["SITUACAO_DF"] = df_gold.apply(definir_situacao_df, axis=1)
    df_gold["SITUACAO_ANALISE"] = df_gold.apply(ajustar_analise_df, axis=1)

    # Limpeza e Padronização
    colunas_finais = [
        "CNPJ", "SEGMENTO_METODOLOGICO", "SITUACAO_CADASTRAL", "STATUS_CONTRATUAL", "TEM_CONTRATO", 
        "QTD_CONTRATOS", "VOLUME_MWM", "PROXIMO_INICIO", "PROXIMO_FIM", "TEM_ANALISE", "SITUACAO_ANALISE", 
        "DATA_ANALISE", "DATA_DF", "SITUACAO_DF", "VALIDADE_ANALISE", "RATING", "PD", "PATRIMONIO_LIQUIDO", 
        "MODELO_ANALISE", "EAD_VALOR", "LGD_LIQUIDA", "PE_REAIS"
    ]
    
    # Preenche colunas ausentes no momento da geração para não dar erro
    for c in colunas_finais:
        if c not in df_gold.columns: df_gold[c] = None

    df_gold = df_gold.reindex(columns=colunas_finais)

    df_gold["STATUS_CONTRATUAL"] = df_gold["STATUS_CONTRATUAL"].fillna("SEM_CONTRATO").astype(str)
    df_gold["TEM_CONTRATO"] = df_gold["TEM_CONTRATO"].fillna("NÃO").astype(str)
    df_gold["TEM_ANALISE"] = df_gold["TEM_ANALISE"].fillna("NÃO").astype(str)
    df_gold["SITUACAO_ANALISE"] = df_gold["SITUACAO_ANALISE"].fillna("SEM_ANALISE").astype(str)
    df_gold["SEGMENTO_METODOLOGICO"] = df_gold["SEGMENTO_METODOLOGICO"].fillna("NAO_ENQUADRADO").astype(str)
    df_gold["SITUACAO_CADASTRAL"] = df_gold["SITUACAO_CADASTRAL"].fillna("NAO_INFORMADA").astype(str)
    df_gold["SITUACAO_DF"] = df_gold["SITUACAO_DF"].fillna("N/A").astype(str)
    
    for col_fin in ["EAD_VALOR", "LGD_LIQUIDA", "PE_REAIS", "PATRIMONIO_LIQUIDO", "PD", "VOLUME_MWM"]:
        df_gold[col_fin] = pd.to_numeric(df_gold[col_fin], errors="coerce").fillna(0.0).round(4)
    
    for col in ["PROXIMO_INICIO", "PROXIMO_FIM", "DATA_ANALISE", "DATA_DF", "VALIDADE_ANALISE", "RATING", "MODELO_ANALISE"]:
        df_gold[col] = df_gold[col].fillna("-").astype(str)

    df_gold["STATUS_OPERACIONAL"] = df_gold.apply(_classificar_matriz_operacional, axis=1)
    colunas_finais.append("STATUS_OPERACIONAL")
    
    df_export = df_gold[colunas_finais].copy()

    gold_dir = context.path("gold") / "visao_operacional_negocio"
    gold_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    df_export.to_csv(gold_dir / f"Visao_Operacional_BDC_{timestamp}.csv", index=False, encoding="utf-8-sig", sep=";", decimal=",")
    df_export.to_parquet(gold_dir / "Visao_Operacional_BDC_LATEST.parquet", index=False)

    # 6. PRIORIDADE 3: Exportação do Arquivo Oficial para Cálculo de Limites (§7.3)
    colunas_limites = ["CNPJ", "SEGMENTO_METODOLOGICO", "PATRIMONIO_LIQUIDO", "RATING", "PD", "DATA_DF", "TEM_CONTRATO", "VOLUME_MWM", "SITUACAO_DF", "SITUACAO_ANALISE", "STATUS_OPERACIONAL"]
    df_limites = df_export[[c for c in colunas_limites if c in df_export.columns]].copy()
    
    # Tratamento de Nulos para Exportação a sistemas legados em Excel
    df_limites["PATRIMONIO_LIQUIDO"] = df_limites["PATRIMONIO_LIQUIDO"].replace(0.0, None)
    
    df_limites.to_excel(gold_dir / f"Interface_Limites_BDC_{timestamp}.xlsx", index=False)
    df_limites.to_excel(gold_dir / "Interface_Limites_BDC_LATEST.xlsx", index=False)
    
    logger.info("Arquivos Gold gerados com sucesso: Visão Operacional e Interface de Limites.")

    mask_descoberto = (df_export["STATUS_CONTRATUAL"] == "CONTRATO_VIGENTE") & (df_export["SITUACAO_ANALISE"] != "VIGENTE")
    ead_descoberto = df_export.loc[mask_descoberto, "EAD_VALOR"].sum()

    metrics = {
        "run_id": run_id, "status": "SUCESSO", "total_contrapartes": len(df_export),
        "contrato_vigente": int((df_export["STATUS_CONTRATUAL"] == "CONTRATO_VIGENTE").sum()),
        "contrato_futuro": int((df_export["STATUS_CONTRATUAL"] == "CONTRATO_FUTURO").sum()),
        "analise_vigente": int((df_export["SITUACAO_ANALISE"] == "VIGENTE").sum()),
        "contrato_vig_sem_analise_vig": int(mask_descoberto.sum()),
        "analise_vencida": int((df_export["SITUACAO_ANALISE"] == "VENCIDA").sum()),
        "ficha_sem_contrato": int(((df_export["STATUS_CONTRATUAL"] == "SEM_CONTRATO") & (df_export["TEM_ANALISE"] == "SIM")).sum()),
        "contrato_sem_ficha": int(((df_export["STATUS_CONTRATUAL"].isin(["CONTRATO_VIGENTE", "CONTRATO_FUTURO"])) & (df_export["TEM_ANALISE"] == "NÃO")).sum()),
        "dados_incompletos": int((df_export["SITUACAO_CADASTRAL"] == "NAO_INFORMADA").sum()),
        "ead_descoberto": float(ead_descoberto)
    }
    return metrics