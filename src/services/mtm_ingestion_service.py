"""Serviço de ingestão e agregação da base de MtM para as camadas Bronze e Silver.

fix(T2.2.2): Removida lógica duplicada (leitura antiga via MTM_NETWORK_PATH
que salvava Bronze duas vezes). Mantido apenas o fluxo via mtm_connector.
Ref: §3.5, §11.6 do Planejamento Funcional.
"""

from __future__ import annotations

import shutil
from datetime import datetime
from typing import Any

import pandas as pd

from app.context import AppContext
from common.logging_utils import get_logger
from services.mtm_connector import fetch_mtm_consolidado, _encontrar_arquivo_mtm_recente
from storage.silver_store import write_silver_dataset


class MtmReconciliationError(Exception):
    """Exceção para falhas na reconciliação de totais entre Bronze e Silver."""


def ingest_mtm_data(context: AppContext) -> dict[str, Any]:
    """Orquestra a ingestão MtM: Bronze snapshot → Conector → Agregação → Reconciliação → Silver."""
    run_id = f"MTM_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    log_file = context.path("log_runner") / f"{run_id}__ingestao_mtm.log"
    logger = get_logger("bdc.mtm", log_file)

    try:
        logger.info("Iniciando processo de ingestão e agregação da base de MtM.")

        input_dir = context.path("entradas") / "mtm"
        arquivo_bruto = _encontrar_arquivo_mtm_recente(input_dir)

        # 1. Copia o snapshot bruto intacto para a Bronze (DoD T2.2.2 — §11.5)
        bronze_dir = context.path("bronze") / "snapshots_fontes" / "mtm"
        bronze_dir.mkdir(parents=True, exist_ok=True)

        nome_bronze = f"raw_mtm_{datetime.now().strftime('%Y%m%d')}_{arquivo_bruto.name}"
        caminho_bronze = bronze_dir / nome_bronze
        shutil.copy2(arquivo_bruto, caminho_bronze)
        logger.info("Snapshot bruto salvo na Bronze em: %s", caminho_bronze)

        # 2. Leitura via Conector (T2.2.1)
        df_mtm = fetch_mtm_consolidado(input_dir=input_dir, logger=logger)

        if df_mtm.empty:
            logger.warning("Nenhum registro encontrado na base de MtM.")
            return {"run_id": run_id, "contrapartes_consolidadas": 0, "status": "SEM_DADOS"}

        # Captura totais originais para controle de reconciliação
        soma_pos_orig = float(df_mtm["MTM_POSITIVO"].sum())
        soma_neg_orig = float(df_mtm["MTM_NEGATIVO"].sum())
        soma_not_orig = float(df_mtm["NOTIONAL"].sum())

        # 3. Agregação por contraparte (CNPJ) e DATA_BASE para a Silver
        if "DATA_BASE" not in df_mtm.columns:
            df_mtm["DATA_BASE"] = datetime.now().strftime("%Y-%m-%d")

        df_agregado = (
            df_mtm.groupby(["CNPJ", "DATA_BASE"], as_index=False)
            .agg({
                "MTM_POSITIVO": "sum",
                "MTM_NEGATIVO": "sum",
                "NOTIONAL": "sum"
            })
            .rename(columns={
                "MTM_POSITIVO": "MTM_POSITIVO_TOTAL",
                "MTM_NEGATIVO": "MTM_NEGATIVO_TOTAL",
                "NOTIONAL": "NOTIONAL_TOTAL"
            })
        )

        # 4. Reconciliação de integridade entre Bronze e Silver (§11.6)
        reconciliation_config = context.config.get("reconciliacao_mtm", {})
        tolerancia = reconciliation_config.get("tolerancia_absoluta", 0.01)

        soma_pos_silver = float(df_agregado["MTM_POSITIVO_TOTAL"].sum())
        soma_neg_silver = float(df_agregado["MTM_NEGATIVO_TOTAL"].sum())
        soma_not_silver = float(df_agregado["NOTIONAL_TOTAL"].sum())

        checks = [
            ("MTM Positivo Total", soma_pos_orig, soma_pos_silver),
            ("MTM Negativo Total", soma_neg_orig, soma_neg_silver),
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

        # 5. Persistência na Silver (CSV + Parquet) — versionado por run_id (§1.5)
        silver_output_dir = context.path("silver") / "mtm_consolidado_silver"
        csv_path, parquet_path = write_silver_dataset(
            records=records,
            output_dir=silver_output_dir,
            filename=f"mtm_agregado_contraparte_{run_id}"
        )

        # Ponteiro LATEST para consumo downstream (preserva versão anterior)
        latest_path = silver_output_dir / "mtm_agregado_contraparte.parquet"
        if latest_path.exists():
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy2(latest_path, silver_output_dir / f"mtm_agregado_contraparte_HIST_{ts}.parquet")
        shutil.copy2(parquet_path, latest_path)

        return {
            "run_id": run_id,
            "linhas_processadas": len(df_mtm),
            "contrapartes_consolidadas": len(records),
            "soma_mtm_positivo_total": soma_pos_silver,
            "soma_mtm_negativo_total": soma_neg_silver,
            "soma_notional_total": soma_not_silver,
            "status": "SUCESSO"
        }

    except Exception as exc:
        logger.exception("Falha crítica na ingestão/reconciliação do MtM.")
        raise