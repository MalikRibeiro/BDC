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
    logger = obter_logger("bdc.bureau", Path("LOGS/ingestao") / f"{run_id}__ingestao_bureau.log")

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
    
    path_contratos = context.path("silver") / "denodo_contratos_silver" / "contratos_correntes.parquet"
    if not path_contratos.exists():
        path_contratos = context.path("silver") / "denodo_contratos_padronizados" / "contratos_correntes.parquet"
        
    if path_contratos.exists():
        df_contratos = pd.read_parquet(path_contratos)
        status_excluidos = ["CANCELADO", "DISTRATADO", "ENCERRADO", "REJEITADO", "INATIVO"]
        if "STATUS" in df_contratos.columns:
            df_ativos = df_contratos[~df_contratos["STATUS"].astype(str).str.upper().isin(status_excluidos)]
        else:
            df_ativos = df_contratos
        cnpjs_ativos = set(df_ativos["CNPJ"].dropna().unique())
        cnpjs_alvo = list(set([c for c in cnpjs_enquadrados if c in cnpjs_ativos]).union(cnpjs_adicionais))
    else:
        logger.warning("Base de contratos correntes não encontrada. Prosseguindo sem filtro de atividade.")
        cnpjs_alvo = list(set(cnpjs_enquadrados).union(cnpjs_adicionais))

    logger.info("Total de CNPJs elegíveis para consulta RISK3 (Enquadrados e Ativos): %d", len(cnpjs_alvo))
    
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

    df_silver = df_bureau[df_bureau["STATUS"] == "SUCESSO"].copy()
    
    if df_silver.empty:
        logger.warning("Nenhum registro com STATUS=SUCESSO retornado pelo Bureau.")
        _gravar_silver_vazia(context, run_id)
        return {"run_id": run_id, "status": "FALHA_OU_BLOQUEIO_DE_REDE"}
        
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