"""Serviço de Ingestão e Persistência do Bureau RISK3."""

from __future__ import annotations

from datetime import datetime
from typing import Any
import pandas as pd

from app.context import AppContext
from pathlib import Path
from control.logger import obter_logger
from storage.escrever_dados import escrever_conjunto_de_dados_silver

def inserir_dados_bureau(context: AppContext) -> dict[str, Any]:
    run_id = f"BUR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = obter_logger("bdc.bureau", Path("LOGS/ingestion") / f"{run_id}__ingestao_bureau.log")

    path_enq = context.path("relational_configs")
    arquivos = list(path_enq.glob("enquadramento_consumidores_*.csv"))
    if not arquivos:
        logger.warning("Nenhum enquadramento encontrado para guiar o Bureau.")
        _gravar_silver_vazia(context, run_id)
        return {"run_id": run_id, "status": "SEM_DADOS_ENQUADRAMENTO"}
        
    try:
        df_enq = pd.read_csv(max(arquivos, key=lambda f: f.stat().st_mtime), sep=",", dtype={"CNPJ": str})
    except Exception as e:
        logger.critical("Falha ao ler arquivo de enquadramento: %s. Prosseguindo com DataFrame vazio.", e)
        _gravar_silver_vazia(context, run_id)
        return {"run_id": run_id, "status": "FALHA_LEITURA_ENQUADRAMENTO"}
    
    cnpjs_enquadrados = df_enq["CNPJ"].dropna().unique().tolist()
    
    path_fichas_com = context.path("silver") / "fichas_comercializadoras_extraidas" / "fichas_comercializadoras_extraidas.parquet"
    path_fichas_cons = context.path("silver") / "fichas_consumidores_extraidas" / "fichas_consumidores_extraidas.parquet"
    path_controladoras = context.path("silver") / "mapeamento_controladoras" / "mapeamento_controladoras.parquet"
    path_controladoras_csv = Path("ENTRADAS/controlador/Controladora e Subsidiaria.csv")
    
    cnpjs_adicionais = set()
    for p in [path_fichas_com, path_fichas_cons]:
        if p.exists():
            df_f = pd.read_parquet(p)
            if "CNPJ" in df_f.columns:
                cnpjs_adicionais.update(df_f["CNPJ"].dropna().unique())
                
    if path_controladoras.exists():
        df_ctrl = pd.read_parquet(path_controladoras)
        if "CNPJ_SUBSIDIARIA" in df_ctrl.columns:
            cnpjs_adicionais.update(df_ctrl["CNPJ_SUBSIDIARIA"].dropna().unique())
        if "CNPJ_CONTA_ATRELADA" in df_ctrl.columns:
            cnpjs_adicionais.update(df_ctrl["CNPJ_CONTA_ATRELADA"].dropna().unique())
    elif path_controladoras_csv.exists():
        try:
            df_ctrl = pd.read_csv(path_controladoras_csv, sep=",")
            if len(df_ctrl.columns) <= 1:
                df_ctrl = pd.read_csv(path_controladoras_csv, sep=";")
            df_ctrl.columns = df_ctrl.columns.str.strip().str.upper()
            if "CNPJ_SUBSIDIARIA" in df_ctrl.columns:
                cnpjs_adicionais.update(df_ctrl["CNPJ_SUBSIDIARIA"].dropna().unique())
            if "CNPJ_CONTA_ATRELADA" in df_ctrl.columns:
                cnpjs_adicionais.update(df_ctrl["CNPJ_CONTA_ATRELADA"].dropna().unique())
        except Exception as e:
            logger.warning("Falha ao ler CSV de controladoras como fallback: %s", e)
    
    path_contratos = context.path("silver") / "denodo_contratos_silver" / "contratos_correntes.parquet"
    if not path_contratos.exists():
        path_contratos = context.path("silver") / "denodo_contratos_padronizados" / "contratos_correntes.parquet"
        
    cnpjs_matrizes_derivadas = set()
    from common.identificadores import calcular_cnpj_matriz, normalizar_cnpj_coluna
    if path_contratos.exists():
        df_contratos = pd.read_parquet(path_contratos)
        cnpjs_todos_contratos = set(df_contratos["CNPJ"].dropna().unique())
        for c in cnpjs_todos_contratos:
            c_norm = normalizar_cnpj_coluna(c)
            if c_norm and len(c_norm) == 14 and c_norm[8:12] != "0001":
                matriz = calcular_cnpj_matriz(c_norm)
                if matriz:
                    cnpjs_matrizes_derivadas.add(matriz)
        cnpjs_alvo = list(set(cnpjs_enquadrados).union(cnpjs_adicionais).union(cnpjs_todos_contratos).union(cnpjs_matrizes_derivadas))
    else:
        logger.warning("Base de contratos correntes não encontrada. Prosseguindo sem filtro de atividade.")
        cnpjs_alvo = list(set(cnpjs_enquadrados).union(cnpjs_adicionais))

    if cnpjs_matrizes_derivadas:
        logger.info("Adicionadas %d Matrizes (0001-XX) derivadas de filiais para busca no Bureau.", len(cnpjs_matrizes_derivadas))

    logger.info("Total de CNPJs elegíveis para consulta RISK3 (Enquadrados, Ativos e Matrizes): %d", len(cnpjs_alvo))
    
    if not cnpjs_alvo:
        _gravar_silver_vazia(context, run_id)
        return {"run_id": run_id, "status": "NENHUM_CLIENTE_ELEGIVEL"}

    try:
        from services.connectors.risk3_connector import buscar_bureau_risk3
        df_bureau = buscar_bureau_risk3(cnpjs_alvo, context)
    except Exception as e:
        logger.critical("API RISK3 indisponível ou falha de conexão: %s. Prosseguindo com Silver vazia.", e)
        _gravar_silver_vazia(context, run_id)
        return {"run_id": run_id, "status": "FALHA_API_RISK3"}

    if df_bureau.empty:
        logger.warning("Consulta RISK3 retornou DataFrame vazio.")
        _gravar_silver_vazia(context, run_id)
        return {"run_id": run_id, "status": "SEM_RETORNO_API"}

    bronze_dir = context.path("bronze") / "snapshots_fontes" / "bureau"
    bronze_dir.mkdir(parents=True, exist_ok=True)
    df_bureau.to_parquet(bronze_dir / f"raw_bureau_{run_id}.parquet", index=False)

    df_silver = df_bureau[df_bureau["STATUS"].isin(["SUCESSO", "NAO_ENCONTRADO"])].copy()
    
    if df_silver.empty:
        logger.warning("Nenhum registro com STATUS válido retornado pelo Bureau.")
        _gravar_silver_vazia(context, run_id)
        return {"run_id": run_id, "status": "FALHA_OU_BLOQUEIO_DE_REDE"}
        
    if "DATA_CONSULTA" in df_silver.columns and "DATA_VALIDADE" in df_silver.columns:
        mask_sem_data = df_silver["DATA_CONSULTA"].isna() | df_silver["DATA_CONSULTA"].astype(str).str.strip().isin(["", "None", "nan", "<NA>"])
        df_silver.loc[mask_sem_data, "DATA_CONSULTA"] = (
            pd.to_datetime(df_silver.loc[mask_sem_data, "DATA_VALIDADE"], errors="coerce") - pd.DateOffset(months=12)
        ).dt.strftime("%Y-%m-%d")

    df_silver["RUN_ID"] = run_id
    df_silver["DT_PROCESSAMENTO"] = datetime.now().isoformat(timespec="seconds")
    
    silver_dir = context.path("silver") / "fato_bureau_silver"
    escrever_conjunto_de_dados_silver(
        records=df_silver.to_dict(orient="records"), 
        output_dir=silver_dir, 
        filename="fato_bureau_silver"
    )

    logger.info("Ingestão do Bureau concluída. %d registros na Silver.", len(df_silver))
    return {"run_id": run_id, "status": "SUCESSO", "linhas": len(df_silver)}


def _gravar_silver_vazia(context: AppContext, run_id: str) -> None:
    silver_dir = context.path("silver") / "fato_bureau_silver"
    silver_dir.mkdir(parents=True, exist_ok=True)
    df_vazio = pd.DataFrame(columns=[
        "CNPJ", "SCORE_BUREAU", "RATING_BUREAU", "PD_BUREAU",
        "RESTRITIVOS", "DATA_CONSULTA", "DATA_VALIDADE",
        "STATUS", "RAW_DATA", "RUN_ID", "DT_PROCESSAMENTO"
    ])
    df_vazio.to_parquet(silver_dir / "fato_bureau_silver.parquet", index=False)