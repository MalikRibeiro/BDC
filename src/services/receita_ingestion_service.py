"""Serviço de ingestão e validação cadastral da Receita Federal."""

from __future__ import annotations

import json
import logging
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from app.context import AppContext
from domain.enums import StatusAlerta
from services.receita_connector import fetch_receita_data_batch
from storage.silver_store import write_silver_dataset

LOGGER = logging.getLogger(__name__)

class ReceitaIngestionError(Exception):
    """Exceção para falhas na ingestão da base da Receita Federal."""

def _listar_cnpjs_de_entrada(context: AppContext) -> list[str]:
    """Lê TODOS os CNPJs das Fichas e dos Contratos para garantir cobertura total."""
    cnpjs = set()
    silver_dir = context.path("silver")

    # 1. CNPJs das Fichas
    for segmento in ["fichas_comercializadoras_extraidas", "fichas_consumidores_extraidas"]:
        path = silver_dir / segmento / f"{segmento}.parquet"
        if path.exists():
            df = pd.read_parquet(path)
            if "CNPJ" in df.columns:
                cnpjs.update(df["CNPJ"].dropna().astype(str).str.strip().tolist())

    # 2. CNPJs dos Contratos (Base completa do MVP)
    path_contratos = silver_dir / "denodo_contratos_silver" / "contratos_correntes.parquet"
    if path_contratos.exists():
        df_contratos = pd.read_parquet(path_contratos)
        if "CNPJ" in df_contratos.columns:
            cnpjs.update(df_contratos["CNPJ"].dropna().astype(str).str.strip().tolist())

    # Limpeza e validação estrita dos 14 dígitos
    cnpjs_limpos = []
    for c in cnpjs:
        c_limpo = re.sub(r"\D", "", str(c)).zfill(14)
        if len(c_limpo) == 14 and c_limpo != "00000000000000":
            cnpjs_limpos.append(c_limpo)

    return list(set(cnpjs_limpos))

def _save_raw_snapshot(context: AppContext, payload: list[dict[str, Any]]) -> Path:
    bronze_dir = context.path("bronze") / "snapshots_fontes" / "receita"
    bronze_dir.mkdir(parents=True, exist_ok=True)
    filename = f"raw_receita_{date.today().strftime('%Y%m%d')}.json"
    target = bronze_dir / filename
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return target

def ingest_receita_data(context: AppContext) -> dict[str, Any]:
    run_id = f"REC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = logging.getLogger("bdc.receita")

    cnpjs = _listar_cnpjs_de_entrada(context)
    if not cnpjs:
        logger.warning("Nenhum CNPJ encontrado nas bases da Silver para consulta na Receita.")
        return {"run_id": run_id, "linhas_processadas": 0, "alertas_gerados_cad001": 0, "status": "SEM_DADOS"}

    logger.info("Iniciando consulta na BrasilAPI para %d CNPJ(s). Pode levar alguns minutos (Cache ativo)...", len(cnpjs))
    df_receita = fetch_receita_data_batch(cnpjs, context)
    
    if df_receita.empty:
        logger.warning("Consulta da Receita retornou DataFrame vazio.")
        return {"run_id": run_id, "linhas_processadas": 0, "alertas_gerados_cad001": 0, "status": "SEM_DADOS"}

    payload = df_receita.to_dict(orient="records")
    _save_raw_snapshot(context, payload)

    df_receita = df_receita.drop_duplicates(subset=["CNPJ"], keep="last").reset_index(drop=True)
    df_receita["RUN_ID"] = run_id
    df_receita["DT_PROCESSAMENTO"] = datetime.now().isoformat(timespec="seconds")

    alertas: list[dict[str, Any]] = []
    for _, row in df_receita.iterrows():
        situacao = str(row.get("SITUACAO_CADASTRAL") or "").strip().upper()
        if situacao and situacao != "ATIVA" and situacao != "NONE":
            alertas.append({
                "CODIGO": "CAD_001",
                "CNPJ": row.get("CNPJ"),
                "MENSAGEM": f"CNPJ com situação cadastral irregular: {situacao}.",
                "SEVERIDADE": "ALTA",
                "RUN_ID": run_id,
                "DT_DETECCAO": datetime.now().isoformat(timespec="seconds"),
                "STATUS_ALERTA": StatusAlerta.ABERTO.value,
            })

    if alertas:
        df_alertas = pd.DataFrame(alertas)
        write_silver_dataset(
            records=df_alertas.to_dict(orient="records"),
            output_dir=context.path("silver") / "alertas_credito",
            filename=f"alertas_cadastrais_receita_{run_id}",
        )

    silver_dir = context.path("silver") / "receita_silver"
    write_silver_dataset(
        records=df_receita.to_dict(orient="records"),
        output_dir=silver_dir,
        filename=f"receita_cadastral_silver_{run_id}",
    )

    # Ponteiro LATEST
    import shutil
    latest_path = silver_dir / "receita_cadastral_silver.parquet"
    versioned_path = silver_dir / f"receita_cadastral_silver_{run_id}.parquet"
    if latest_path.exists():
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(latest_path, silver_dir / f"receita_cadastral_silver_HIST_{ts}.parquet")
    if versioned_path.exists():
        shutil.copy2(versioned_path, latest_path)

    resumo = {
        "run_id": run_id,
        "linhas_processadas": int(len(df_receita)),
        "alertas_gerados_cad001": len(alertas),
        "status": "SUCESSO",
    }
    logger.info("Ingestão da Receita concluída: %s", resumo)
    return resumo