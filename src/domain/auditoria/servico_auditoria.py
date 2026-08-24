"""Serviços de Auditoria do Pipeline (§11.5 — Tabelas de Controle).

Registra cada execução do pipeline (ctl_run_pipeline) e cada documento
processado (ctl_documento) em tabelas persistentes.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from storage.escrever_dados import escrever_conjunto_de_dados_silver


LOGGER = logging.getLogger("bdc.auditoria")


# ==============================================================================
# ctl_run_pipeline — Uma linha por execução do pipeline
# ==============================================================================
def registrar_inicio_pipeline(
    run_id: str,
    etapas_planejadas: int,
    control_dir: Path,
) -> dict[str, Any]:
    """Registra o início de uma execução do pipeline."""
    registro = {
        "RUN_ID": run_id,
        "DT_INICIO": datetime.now().isoformat(timespec="seconds"),
        "DT_FIM": None,
        "STATUS_GERAL": "EM_EXECUCAO",
        "TOTAL_ETAPAS": etapas_planejadas,
        "ETAPAS_OK": 0,
        "ETAPAS_FALHA": 0,
        "VERSAO_SISTEMA": "BDC_v06",
    }
    LOGGER.info("Pipeline iniciado (run_id=%s).", run_id)
    return registro


def registrar_fim_pipeline(
    registro_inicio: dict[str, Any],
    etapas_ok: int,
    etapas_falha: int,
    control_dir: Path,
) -> dict[str, Any]:
    """Registra o fim de uma execução do pipeline e persiste em ctl_run_pipeline."""
    registro = registro_inicio.copy()
    registro["DT_FIM"] = datetime.now().isoformat(timespec="seconds")
    registro["STATUS_GERAL"] = "SUCESSO" if etapas_falha == 0 else "PARCIAL"
    registro["ETAPAS_OK"] = etapas_ok
    registro["ETAPAS_FALHA"] = etapas_falha

    control_dir.mkdir(parents=True, exist_ok=True)

    # Append-only: cada execução é uma nova linha no arquivo de controle
    ctl_path = control_dir / "ctl_run_pipeline.parquet"
    if ctl_path.exists():
        df_existing = pd.read_parquet(ctl_path)
        df_combined = pd.concat([df_existing, pd.DataFrame([registro])], ignore_index=True)
    else:
        df_combined = pd.DataFrame([registro])

    df_combined.to_parquet(ctl_path, index=False)

    csv_path = control_dir / "ctl_run_pipeline.csv"
    df_combined.to_csv(csv_path, index=False, encoding="utf-8-sig", sep=";")

    LOGGER.info(
        "Pipeline finalizado (run_id=%s). Status=%s. OK=%d, Falha=%d.",
        registro["RUN_ID"], registro["STATUS_GERAL"],
        etapas_ok, etapas_falha,
    )
    return registro


# ==============================================================================
# ctl_documento — Uma linha por documento processado
# ==============================================================================
def registrar_documento(
    documento_id: str,
    run_id: str,
    arquivo_origem: str,
    hash_arquivo: str | None,
    tipo_ficha: str,
    status_classificacao: str,
    status_extracao: str,
    control_dir: Path,
) -> dict[str, Any]:
    """Registra um documento processado na tabela ctl_documento (append-only)."""
    registro = {
        "DOCUMENTO_ID": documento_id,
        "RUN_ID": run_id,
        "ARQUIVO_ORIGEM": arquivo_origem,
        "HASH_ARQUIVO": hash_arquivo,
        "TIPO_FICHA": tipo_ficha,
        "STATUS_CLASSIFICACAO": status_classificacao,
        "STATUS_EXTRACAO": status_extracao,
        "DT_PROCESSAMENTO": datetime.now().isoformat(timespec="seconds"),
    }

    control_dir.mkdir(parents=True, exist_ok=True)

    ctl_path = control_dir / "ctl_documento.parquet"
    if ctl_path.exists():
        df_existing = pd.read_parquet(ctl_path)
        df_combined = pd.concat([df_existing, pd.DataFrame([registro])], ignore_index=True)
    else:
        df_combined = pd.DataFrame([registro])

    df_combined.to_parquet(ctl_path, index=False)

    LOGGER.info(
        "Documento registrado: %s (tipo=%s, status=%s).",
        documento_id, tipo_ficha, status_extracao,
    )
    return registro


# ==============================================================================
# ctl_campo_origem — Uma linha por campo extraído (Linhagem)
# ==============================================================================
def registrar_linhagem_campos(
    documento_id: str,
    run_id: str,
    campos_metadata: list[dict[str, Any]],
    control_dir: Path,
) -> None:
    """Registra a linhagem (aba, célula, método) de cada campo extraído."""
    if not campos_metadata:
        return

    registros = []
    dt_proc = datetime.now().isoformat(timespec="seconds")
    for cm in campos_metadata:
        registros.append({
            "DOCUMENTO_ID": documento_id,
            "RUN_ID": run_id,
            "CAMPO": cm.get("campo"),
            "ABA_ORIGEM": cm.get("aba_origem"),
            "CELULA_ORIGEM": cm.get("celula_origem"),
            "METODO_EXTRACAO": cm.get("metodo"),
            "VALOR_EXTRAIDO": str(cm.get("valor"))[:255] if cm.get("valor") is not None else None,
            "DT_PROCESSAMENTO": dt_proc,
        })

    control_dir.mkdir(parents=True, exist_ok=True)
    ctl_path = control_dir / "ctl_campo_origem.parquet"
    
    df_new = pd.DataFrame(registros)
    if ctl_path.exists():
        df_existing = pd.read_parquet(ctl_path)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new

    df_combined.to_parquet(ctl_path, index=False)
    LOGGER.debug("Registrada linhagem de %d campos para documento %s.", len(registros), documento_id)
