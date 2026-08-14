"""Serviço de ingestão e normalização da base do Salesforce."""

from __future__ import annotations

import shutil
from datetime import datetime
from typing import Any

import pandas as pd

from app.context import AppContext
from common.logging_utils import get_logger
from services.salesforce_connector import fetch_salesforce_data
from storage.silver_store import write_silver_dataset


class SalesforceIngestionError(Exception):
    """Exceção para falhas na ingestão da base do Salesforce."""


def ingest_salesforce_data(context: AppContext) -> dict[str, Any]:
    """
    Lê o arquivo do Salesforce (via conector), salva o snapshot na Bronze,
    deduplica os registros, enriquece as tabelas filhas com o CNPJ da Conta
    e persiste na camada Silver.
    """
    run_id = f"SF_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    log_file = context.path("log_runner") / f"{run_id}__ingestao_salesforce.log"
    logger = get_logger("bdc.salesforce", log_file)

    try:
        logger.info("Iniciando processo de ingestão da base do Salesforce.")

        input_dir = context.path("entradas") / "salesforce"
        arquivo_bruto = input_dir / "salesforce.xlsx"

        if not arquivo_bruto.exists():
            logger.warning("Arquivo salesforce.xlsx não encontrado na entrada.")
            return {"run_id": run_id, "status": "SEM_DADOS"}

        # 1. Copia o snapshot bruto intacto para a Bronze
        bronze_dir = context.path("bronze") / "snapshots_fontes" / "salesforce"
        bronze_dir.mkdir(parents=True, exist_ok=True)

        nome_bronze = f"raw_salesforce_{datetime.now().strftime('%Y%m%d')}_{arquivo_bruto.name}"
        caminho_bronze = bronze_dir / nome_bronze
        shutil.copy2(arquivo_bruto, caminho_bronze)
        logger.info("Snapshot bruto salvo na Bronze em: %s", caminho_bronze.name)

        # 2. Extração via Conector
        dfs_sf = fetch_salesforce_data(input_dir=input_dir, logger=logger)
        
        df_account = dfs_sf.get("Account", pd.DataFrame())
        df_cotacao = dfs_sf.get("Cotacao", pd.DataFrame())
        df_chamado = dfs_sf.get("Chamado", pd.DataFrame())
        df_contrato = dfs_sf.get("Contrato", pd.DataFrame())

        # 3. Deduplicação (Mantém apenas o último registro de cada Id inserido pelo Power Query)
        df_account = df_account.drop_duplicates(subset=["Id"], keep="last") if not df_account.empty else df_account
        df_cotacao = df_cotacao.drop_duplicates(subset=["Id"], keep="last") if not df_cotacao.empty else df_cotacao
        df_chamado = df_chamado.drop_duplicates(subset=["Id"], keep="last") if not df_chamado.empty else df_chamado
        df_contrato = df_contrato.drop_duplicates(subset=["Id"], keep="last") if not df_contrato.empty else df_contrato

        # Padroniza nome da coluna CNPJ na Account para facilitar os cruzamentos
        if "CNPJ__c" in df_account.columns:
            df_account = df_account.rename(columns={"CNPJ__c": "CNPJ"})

        # 4. Enriquecimento: Traz o CNPJ da Conta (Account) para os objetos filhos
        if not df_account.empty and "CNPJ" in df_account.columns:
            account_map = df_account[["Id", "CNPJ"]].rename(columns={"Id": "AccountId_Join"})
            
            def enriquecer_com_cnpj(df_filho: pd.DataFrame) -> pd.DataFrame:
                if df_filho.empty or "AccountId" not in df_filho.columns:
                    return df_filho
                
                # Faz o Procv/Join: Filho[AccountId] == Conta[Id]
                df_merged = pd.merge(
                    df_filho, 
                    account_map, 
                    left_on="AccountId", 
                    right_on="AccountId_Join", 
                    how="left"
                )
                df_merged = df_merged.drop(columns=["AccountId_Join"])
                
                # Se não encontrou CNPJ (conta órfã), preenche com zeros para evitar quebra de contrato
                if "CNPJ" in df_merged.columns:
                    df_merged["CNPJ"] = df_merged["CNPJ"].fillna("00000000000000")
                return df_merged

            df_cotacao = enriquecer_com_cnpj(df_cotacao)
            df_chamado = enriquecer_com_cnpj(df_chamado)
            df_contrato = enriquecer_com_cnpj(df_contrato)

        # Adiciona metadados de rastreabilidade
        for df in [df_account, df_cotacao, df_chamado, df_contrato]:
            if not df.empty:
                df["RUN_ID"] = run_id
                df["DT_PROCESSAMENTO"] = datetime.now().isoformat(timespec="seconds")

        # 5. Persistência na Silver (CSV + Parquet) separada por objeto
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
                csv_p, pqt_p = write_silver_dataset(
                    records=df.to_dict(orient="records"),
                    output_dir=silver_dir / nome,
                    filename=f"salesforce_{nome}"
                )
                arquivos_salvos.append(nome)

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