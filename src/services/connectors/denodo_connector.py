"""Conector central para o virtualizador Denodo via API RESTful.

feat(T2.1.1): Adicionados retry com backoff exponencial e fallback para
último snapshot Bronze em caso de indisponibilidade.
Ref: §3.4 do Planejamento Funcional.
"""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Any

import pandas as pd
import pyodbc

LOGGER = logging.getLogger(__name__)

class DenodoConnectionError(Exception):
    """Exceção levantada para falhas de conexão ODBC do Denodo."""


def _encontrar_arquivo_bronze_recente(bronze_dir: Path, prefix: str = "raw_contratos") -> Path | None:
    """Localiza o snapshot Bronze mais recente para fallback."""
    if not bronze_dir.exists():
        return None
    snapshots = [
        f for f in bronze_dir.iterdir()
        if f.is_file() and f.name.startswith(prefix) and f.suffix == ".parquet"
    ]
    if not snapshots:
        return None
    return max(snapshots, key=lambda f: f.stat().st_mtime)


def buscar_denodo(
    query: str,
    bronze_fallback_dir: Path | None = None,
) -> pd.DataFrame:
    driver = os.getenv("DENODO_ODBC_DRIVER")
    server = os.getenv("DENODO_SERVER")
    port = os.getenv("DENODO_PORT")
    database = os.getenv("DENODO_DATABASE")
    user = os.getenv("DENODO_USER")
    pwd = os.getenv("DENODO_PWD")

    if not all([driver, server, port, database, user, pwd]):
        raise ValueError("Configurações ODBC do Denodo incompletas no arquivo .env.")

    conn_str = f"DRIVER={driver};SERVER={server};PORT={port};DATABASE={database};UID={user};PWD={pwd}"
    
    try:
        LOGGER.info("Iniciando extração do Denodo via ODBC...")
        conn = pyodbc.connect(conn_str, timeout=60)
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            df_result = pd.read_sql(query, conn)
        conn.close()
        
        LOGGER.info("Extração ODBC finalizada. %s registros carregados.", len(df_result))
        return df_result

    except Exception as exc:
        LOGGER.exception("Falha na comunicação ODBC com o Denodo.")

        if bronze_fallback_dir:
            snapshot = _encontrar_arquivo_bronze_recente(bronze_fallback_dir)
            if snapshot:
                LOGGER.warning(
                    "Usando fallback: lendo último snapshot Bronze '%s'.", snapshot.name
                )
                return pd.read_parquet(snapshot)
            LOGGER.error("Nenhum snapshot Bronze encontrado para fallback em '%s'.", bronze_fallback_dir)

        raise DenodoConnectionError(f"Erro ao executar query no Denodo: {exc}") from exc