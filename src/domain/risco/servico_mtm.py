"""Serviço de ingestão e agregação da base de MtM para as camadas Bronze e Silver.

fix(T2.2.2): Removida lógica duplicada (leitura antiga via MTM_NETWORK_PATH
que salvava Bronze duas vezes). Mantido apenas o fluxo via mtm_connector.
Ref: §3.5, §11.6 do Planejamento Funcional.
"""

from __future__ import annotations

import shutil
import uuid
from pathlib import Path
from datetime import datetime
from typing import Any

import pandas as pd

from app.context import AppContext
from control.logger import obter_logger
from services.connectors.mtm_connector import buscar_mtm_consolidado, _encontrar_arquivo_mtm_recente
from storage.escrever_dados import escrever_conjunto_de_dados_silver
from common.hashing import arquivo_hash
from common.servico_desduplicacao import tem_hash_duplicado
from storage.armazenamento_manifest import historico_de_ingestao_de_carga, anexar_registro_de_manifesto


class MtmReconciliationError(Exception):
    """Exceção para falhas na reconciliação de totais entre Bronze e Silver."""


def inserir_dados_mtm(context: AppContext) -> dict[str, Any]:
    """Orquestra a ingestão MtM: Bronze snapshot → Conector → Agregação → Reconciliação → Silver."""
    run_id = f"MTM_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    log_file = Path("LOGS/ingestao") / f"{run_id}__ingestao_mtm.log"
    logger = obter_logger("bdc.mtm", log_file)

    try:
        logger.info("Iniciando processo de ingestão e agregação da base de MtM.")

        import os
        input_dir = context.path("entradas") / "mtm"
        dir_vigente = input_dir / "vigente"
        dir_processadas = input_dir / "processadas"
        
        dir_vigente.mkdir(parents=True, exist_ok=True)
        dir_processadas.mkdir(parents=True, exist_ok=True)
        
        network_path_str = os.getenv("MTM_NETWORK_PATH")
        if network_path_str:
            network_path = Path(network_path_str)
            if network_path.exists() and network_path.is_file():
                try:
                    arq_vigente_local = _encontrar_arquivo_mtm_recente(dir_vigente)
                    local_mtime = arq_vigente_local.stat().st_mtime
                except FileNotFoundError:
                    local_mtime = 0
                    arq_vigente_local = None
                    
                net_mtime = network_path.stat().st_mtime
                if net_mtime > local_mtime:
                    logger.info("Arquivo de rede mais recente encontrado. Copiando e quebrando cache preguiçoso...")
                    hoje_str = datetime.now().strftime("%d%m%Y_%H%M%S")
                    
                    if arq_vigente_local:
                        arq_processado = dir_processadas / f"{arq_vigente_local.stem}_{hoje_str}{arq_vigente_local.suffix}"
                        shutil.move(str(arq_vigente_local), str(arq_processado))
                    
                    novo_local = dir_vigente / network_path.name
                    shutil.copy2(str(network_path), str(novo_local))
                    
        try:
            arquivo_bruto = _encontrar_arquivo_mtm_recente(dir_vigente)
        except FileNotFoundError:
            logger.warning("Nenhum arquivo de MtM encontrado em vigente.")
            return {"run_id": run_id, "contrapartes_consolidadas": 0, "status": "SEM_DADOS"}

        # Staging Proxy Pattern
        staging_dir = context.path("staging") / "mtm"
        staging_dir.mkdir(parents=True, exist_ok=True)
        staging_file = staging_dir / arquivo_bruto.name
        shutil.copy2(arquivo_bruto, staging_file)

        ingestion_log_path = context.path("bronze_ingestion_log") / "mtm_ingestion.jsonl"
        history = historico_de_ingestao_de_carga(ingestion_log_path)
        
        hash_arquivo = arquivo_hash(staging_file)
        
        silver_dir_check = context.path("silver") / "mtm_consolidado_silver"
        latest_path_check = silver_dir_check / "mtm_agregado_contraparte.parquet"

        if tem_hash_duplicado(history, hash_arquivo) and latest_path_check.exists():
            logger.info("Hash de MtM duplicado (%s). Ignorando pipeline por idempotência.", hash_arquivo)
            return {"run_id": run_id, "contrapartes_consolidadas": 0, "status": "IGNORADO_DUPLICADO"}

        manifest_record = {
            "documento_id": str(uuid.uuid4()),
            "run_id": run_id,
            "tipo_ficha": "MTM_ARQUIVO",
            "arquivo_nome": staging_file.name,
            "hash_arquivo": hash_arquivo,
            "data_processamento": datetime.now().isoformat(timespec="seconds"),
            "status_extracao": "SUCESSO"
        }

        bronze_dir = context.path("bronze") / "snapshots_fontes" / "mtm"
        bronze_dir.mkdir(parents=True, exist_ok=True)

        nome_bronze = f"raw_mtm_{datetime.now().strftime('%Y%m%d')}_{arquivo_bruto.name}"
        caminho_bronze = bronze_dir / nome_bronze
        shutil.copy2(staging_file, caminho_bronze)
        logger.info("Snapshot bruto salvo na Bronze em: %s", caminho_bronze)
        
        anexar_registro_de_manifesto(str(ingestion_log_path), manifest_record)

        df_mtm = buscar_mtm_consolidado(input_dir=dir_vigente, logger=logger)

        if df_mtm.empty:
            logger.warning("Nenhum registro encontrado na base de MtM.")
            return {"run_id": run_id, "contrapartes_consolidadas": 0, "status": "SEM_DADOS"}

        soma_mtm_orig = float(df_mtm["MTM_TOTAL"].sum())
        soma_not_orig = float(df_mtm["NOTIONAL"].sum())

        if "DATA_BASE" not in df_mtm.columns:
            df_mtm["DATA_BASE"] = datetime.now().strftime("%Y-%m-%d")

        df_agregado = (
            df_mtm.groupby(["CNPJ", "CNPJ_RAIZ", "DATA_BASE"], as_index=False)
            .agg({
                "MTM_TOTAL": "sum",
                "NOTIONAL": "sum"
            })
            .rename(columns={
                "MTM_TOTAL": "MTM_TOTAL_NETTED",
                "NOTIONAL": "NOTIONAL_TOTAL"
            })
        )

        df_agregado["MTM_POSITIVO_TOTAL"] = df_agregado["MTM_TOTAL_NETTED"].apply(
            lambda x: x if x > 0 else 0.0
        )
        df_agregado["MTM_NEGATIVO_TOTAL"] = df_agregado["MTM_TOTAL_NETTED"].apply(
            lambda x: abs(x) if x < 0 else 0.0
        )

        if "STATUS_CNPJ" in df_mtm.columns:
            status_map = df_mtm[["CNPJ", "STATUS_CNPJ"]].drop_duplicates(subset=["CNPJ"])
            df_agregado = pd.merge(df_agregado, status_map, on="CNPJ", how="left")

        reconciliation_config = context.config.get("reconciliacao_mtm", {})
        tolerancia = reconciliation_config.get("tolerancia_absoluta", 0.01)

        soma_mtm_silver = float(df_agregado["MTM_TOTAL_NETTED"].sum())
        soma_not_silver = float(df_agregado["NOTIONAL_TOTAL"].sum())

        checks = [
            ("MTM Total", soma_mtm_orig, soma_mtm_silver),
            ("Notional Total", soma_not_orig, soma_not_silver),
        ]
        for label, original, silver in checks:
            diff = abs(original - silver)
            if diff > tolerancia:
                raise MtmReconciliationError(
                    f"Divergência de reconciliação no {label}! "
                    f"Original: {original} vs Silver: {silver} (Diff: {diff} > Tolerância: {tolerancia})"
                )

        df_agregado["RUN_ID"] = run_id
        df_agregado["DT_PROCESSAMENTO"] = datetime.now().isoformat(timespec="seconds")

        records = df_agregado.to_dict(orient="records")

        silver_output_dir = context.path("silver") / "mtm_consolidado_silver"
        csv_path, parquet_path = escrever_conjunto_de_dados_silver(
            records=records,
            output_dir=silver_output_dir,
            filename=f"mtm_agregado_contraparte_{run_id}"
        )

        latest_path = silver_output_dir / "mtm_agregado_contraparte.parquet"
        if latest_path.exists():
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy2(latest_path, silver_output_dir / f"mtm_agregado_contraparte_HIST_{ts}.parquet")
        shutil.copy2(parquet_path, latest_path)

        return {
            "run_id": run_id,
            "linhas_processadas": len(df_mtm),
            "contrapartes_consolidadas": len(records),
            "soma_mtm_total_netted": soma_mtm_silver,
            "soma_mtm_positivo_total": float(df_agregado["MTM_POSITIVO_TOTAL"].sum()),
            "soma_mtm_negativo_total": float(df_agregado["MTM_NEGATIVO_TOTAL"].sum()),
            "soma_notional_total": soma_not_silver,
            "status": "SUCESSO"
        }

    except Exception as exc:
        logger.exception("Falha crítica na ingestão/reconciliação do MtM.")
        raise
