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
import requests
from requests.auth import HTTPBasicAuth
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LOGGER = logging.getLogger(__name__)

MAX_RETRIES = 3
BACKOFF_BASE_SECONDS = 2.0


class DenodoConnectionError(Exception):
    """Exceção levantada para falhas de conexão na API do Denodo."""


def _solicitacao_com_tentativa(url: str, params, auth, max_retries: int = MAX_RETRIES) -> requests.Response:
    """Executa GET com retry e backoff exponencial."""
    last_exc = None
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(
                url,
                params=params,
                auth=auth,
                verify=False,
                timeout=300,
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as exc:
            last_exc = exc
            if attempt < max_retries:
                wait = BACKOFF_BASE_SECONDS ** attempt
                LOGGER.warning(
                    "Tentativa %s/%s falhou para '%s'. Retry em %.1fs. Erro: %s",
                    attempt, max_retries, url, wait, exc,
                )
                time.sleep(wait)
            else:
                LOGGER.error("Todas as %s tentativas falharam para '%s'.", max_retries, url)
    raise last_exc


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
    view_name: str,
    params: dict[str, Any] | None = None,
    bronze_fallback_dir: Path | None = None,
) -> pd.DataFrame:
    base_url = os.getenv("DENODO_REST_BASE_URL", "https://vidgcpprd.copel.nt:9443/denodo-restfulws/com/views")
    url = f"{base_url}/{view_name}"

    user = os.getenv("DENODO_USER")
    pwd = os.getenv("DENODO_PWD")

    if not all([user, pwd]):
        raise ValueError("Credenciais DENODO_USER ou DENODO_PWD não encontradas no arquivo .env.")

    req_params: dict[str, Any] | None = {"$format": "json"}
    if params:
        req_params.update(params)

    auth = HTTPBasicAuth(user, pwd)
    all_elements: list[dict[str, Any]] = []

    try:
        LOGGER.info("Iniciando extração da view '%s' via REST API...", view_name)

        while url:
            response = _solicitacao_com_tentativa(url, params=req_params, auth=auth)

            data = response.json()
            elements = data.get("elements", [])

            if not elements:
                break

            all_elements.extend(elements)

            links = data.get("links", [])
            next_link = next((link["href"] for link in links if link.get("rel") == "next"), None)

            if next_link:
                url = next_link
                req_params = None
            else:
                url = None

        LOGGER.info("Extração via REST finalizada. %s registros carregados.", len(all_elements))
        return pd.DataFrame(all_elements)

    except (requests.exceptions.RequestException, DenodoConnectionError) as exc:
        LOGGER.exception("Falha na comunicação com a API REST do Denodo.")

        if bronze_fallback_dir:
            snapshot = _encontrar_arquivo_bronze_recente(bronze_fallback_dir)
            if snapshot:
                LOGGER.warning(
                    "Usando fallback: lendo último snapshot Bronze '%s'.", snapshot.name
                )
                return pd.read_parquet(snapshot)
            LOGGER.error("Nenhum snapshot Bronze encontrado para fallback em '%s'.", bronze_fallback_dir)

        raise DenodoConnectionError(f"Erro ao acessar endpoint '{view_name}': {exc}") from exc