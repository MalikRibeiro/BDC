"""Serviço de ingestão e agregação da base de MtM para as camadas Bronze e Silver.

fix(T2.2.2): Removida lógica duplicada (leitura antiga via MTM_NETWORK_PATH
que salvava Bronze duas vezes). Mantido apenas o fluxo via mtm_connector.
Ref: §3.5, §11.6 do Planejamento Funcional.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from datetime import datetime
from typing import Any

import pandas as pd

from app.context import AppContext
from control.logger import obter_logger
from services.connectors.mtm_connector import buscar_mtm_consolidado, _encontrar_arquivo_mtm_recente
from storage.escrever_dados import escrever_conjunto_de_dados_silver


class MtmReconciliationError(Exception):
    """Exceção para falhas na reconciliação de totais entre Bronze e Silver."""


def inserir_dados_mtm(context: AppContext) -> dict[str, Any]:
    """Orquestra a ingestão MtM: Bronze snapshot → Conector → Agregação → Reconciliação → Silver."""
    run_id = f"MTM_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    log_file = Path("LOGS/ingestao") / f"{run_id}__ingestao_mtm.log"
    logger = obter_logger("bdc.mtm", log_file)

    try:
        logger.info("Iniciando processo de ingestão e agregação da base de MtM.")

        input_dir = context.path("entradas") / "mtm"
        arquivo_bruto = _encontrar_arquivo_mtm_recente(input_dir)

        bronze_dir = context.path("bronze") / "snapshots_fontes" / "mtm"
        bronze_dir.mkdir(parents=True, exist_ok=True)

        nome_bronze = f"raw_mtm_{datetime.now().strftime('%Y%m%d')}_{arquivo_bruto.name}"
        caminho_bronze = bronze_dir / nome_bronze
        shutil.copy2(arquivo_bruto, caminho_bronze)
        logger.info("Snapshot bruto salvo na Bronze em: %s", caminho_bronze)

        df_mtm = buscar_mtm_consolidado(input_dir=input_dir, logger=logger)

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