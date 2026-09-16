"""Serviço de ingestão e normalização da base do Salesforce."""

from __future__ import annotations

import shutil
import uuid
from pathlib import Path
from datetime import datetime
from typing import Any

import pandas as pd

from app.context import AppContext
from control.logger import obter_logger
from services.connectors.salesforce_connector import buscar_salesforce_dados
from storage.escrever_dados import escrever_conjunto_de_dados_silver
from common.hashing import arquivo_hash
from common.servico_desduplicacao import tem_hash_duplicado
from storage.armazenamento_manifest import historico_de_ingestao_de_carga, anexar_registro_de_manifesto

class SalesforceIngestionError(Exception):
    """Exceção para falhas na ingestão da base do Salesforce."""


def inserir_dados_salesforce(context: AppContext) -> dict[str, Any]:
    """
    Lê o arquivo do Salesforce (via conector), salva o snapshot na Bronze,
    deduplica os registros, enriquece as tabelas filhas com o CNPJ da Conta
    e persiste na camada Silver.
    """
    run_id = f"SF_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    log_file = Path("LOGS/ingestao") / f"{run_id}__ingestao_salesforce.log"
    logger = obter_logger("bdc.salesforce", log_file)

    try:
        logger.info("Iniciando processo de ingestão da base do Salesforce.")

        input_dir = context.path("entradas") / "salesforce"
        vigente_dir = input_dir / "vigente"
        processadas_dir = input_dir / "processadas"
        
        vigente_dir.mkdir(parents=True, exist_ok=True)
        processadas_dir.mkdir(parents=True, exist_ok=True)
        
        # Move arquivo legado solto
        arquivo_legado = input_dir / "salesforce.xlsx"
        if arquivo_legado.exists():
            shutil.move(str(arquivo_legado), str(vigente_dir / "salesforce.xlsx"))
            
        arquivos = list(vigente_dir.glob("*.xlsx"))

        if not arquivos:
            logger.warning("Nenhum arquivo Salesforce encontrado na entrada vigente.")
            return {"run_id": run_id, "status": "SEM_DADOS"}
            
        arquivo_bruto = max(arquivos, key=lambda f: f.stat().st_mtime)

        # Staging Proxy Pattern
        staging_dir = context.path("staging") / "salesforce"
        staging_dir.mkdir(parents=True, exist_ok=True)
        staging_file = staging_dir / arquivo_bruto.name
        shutil.copy2(arquivo_bruto, staging_file)

        ingestion_log_path = context.path("bronze_ingestion_log") / "salesforce_ingestion.jsonl"
        history = historico_de_ingestao_de_carga(ingestion_log_path)
        
        hash_arquivo = arquivo_hash(staging_file)
        
        if tem_hash_duplicado(history, hash_arquivo):
            logger.info("Hash de Salesforce duplicado (%s). Ignorando pipeline por idempotência.", hash_arquivo)
            shutil.move(str(arquivo_bruto), str(processadas_dir / arquivo_bruto.name))
            return {"run_id": run_id, "linhas_account": 0, "status": "IGNORADO_DUPLICADO"}

        manifest_record = {
            "documento_id": str(uuid.uuid4()),
            "run_id": run_id,
            "tipo_ficha": "SALESFORCE_EXCEL",
            "arquivo_nome": staging_file.name,
            "hash_arquivo": hash_arquivo,
            "data_processamento": datetime.now().isoformat(timespec="seconds"),
            "status_extracao": "SUCESSO"
        }

        bronze_dir = context.path("bronze") / "snapshots_fontes" / "salesforce"
        bronze_dir.mkdir(parents=True, exist_ok=True)

        nome_bronze = f"raw_salesforce_{run_id}_{staging_file.name}"
        caminho_bronze = bronze_dir / nome_bronze
        shutil.copy2(staging_file, caminho_bronze)
        logger.info("Snapshot bruto salvo na Bronze em: %s", caminho_bronze.name)
        
        anexar_registro_de_manifesto(str(ingestion_log_path), manifest_record)

        # Continuação com o Staging File (garantindo que se usa a cópia estável)
        dfs_sf = buscar_salesforce_dados(input_dir=staging_dir, logger=logger)
        
        df_account = dfs_sf.get("Account", pd.DataFrame())
        df_cotacao = dfs_sf.get("Cotacao", pd.DataFrame())
        df_chamado = dfs_sf.get("Chamado", pd.DataFrame())
        df_contrato = dfs_sf.get("Contrato", pd.DataFrame())

        df_account = df_account.drop_duplicates(subset=["Id"], keep="last") if not df_account.empty else df_account
        df_cotacao = df_cotacao.drop_duplicates(subset=["Id"], keep="last") if not df_cotacao.empty else df_cotacao
        df_chamado = df_chamado.drop_duplicates(subset=["Id"], keep="last") if not df_chamado.empty else df_chamado
        df_contrato = df_contrato.drop_duplicates(subset=["Id"], keep="last") if not df_contrato.empty else df_contrato

        if "CNPJ__c" in df_account.columns:
            df_account = df_account.rename(columns={"CNPJ__c": "CNPJ"})

        if not df_account.empty and "CNPJ" in df_account.columns:
            account_map = df_account[["Id", "CNPJ"]].rename(columns={"Id": "AccountId_Join"})
            
            def enriquecer_com_cnpj(df_filho: pd.DataFrame) -> pd.DataFrame:
                if df_filho.empty or "AccountId" not in df_filho.columns:
                    return df_filho
                
                df_merged = pd.merge(
                    df_filho, 
                    account_map, 
                    left_on="AccountId", 
                    right_on="AccountId_Join", 
                    how="left"
                )
                df_merged = df_merged.drop(columns=["AccountId_Join"])
                
                if "CNPJ" in df_merged.columns:
                    df_merged["CNPJ"] = df_merged["CNPJ"].fillna("00000000000000")
                return df_merged

            df_cotacao = enriquecer_com_cnpj(df_cotacao)
            df_chamado = enriquecer_com_cnpj(df_chamado)
            df_contrato = enriquecer_com_cnpj(df_contrato)

        for df in [df_account, df_cotacao, df_chamado, df_contrato]:
            if not df.empty:
                df["RUN_ID"] = run_id
                df["DT_PROCESSAMENTO"] = datetime.now().isoformat(timespec="seconds")

        silver_dir = context.path("silver") / "salesforce_silver"
        
        datasets = {
            "account": df_account,
            "cotacao": df_cotacao,
            "chamado": df_chamado,
            "contrato": df_contrato
        }

        arquivos_salvos = []
        for nome, df in datasets.items():
            if not df.empty:
                csv_p, pqt_p = escrever_conjunto_de_dados_silver(
                    records=df.to_dict(orient="records"),
                    output_dir=silver_dir / nome,
                    filename=f"salesforce_{nome}"
                )
                arquivos_salvos.append(nome)
                
        shutil.move(str(arquivo_bruto), str(processadas_dir / arquivo_bruto.name))

        logger.info("Ingestão do Salesforce concluída. Objetos salvos: %s", ", ".join(arquivos_salvos))

        return {
            "run_id": run_id,
            "linhas_account": len(df_account),
            "linhas_cotacao": len(df_cotacao),
            "linhas_chamado": len(df_chamado),
            "linhas_contrato": len(df_contrato),
            "status": "SUCESSO"
        }

    except Exception as exc:
        logger.exception("Falha crítica na ingestão do Salesforce.")
        raise SalesforceIngestionError(f"Erro ao ingerir base do Salesforce: {exc}") from exc