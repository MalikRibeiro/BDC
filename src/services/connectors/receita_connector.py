from __future__ import annotations
from common.identificadores import normalizar_cnpj

import json
import logging
import time
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from app.context import AppContext

LOGGER = logging.getLogger(__name__)
BRASIL_API_BASE_URL = "https://brasilapi.com.br/api/cnpj/v1"

def _cache_path(context: AppContext) -> Path:
    return context.path("entradas") / "receita" / "cache" / "receita_cache.json"

def _load_cache(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists(): return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError): return {}
    if not isinstance(payload, dict): return {}
    
    cache: dict[str, dict[str, Any]] = {}
    for cnpj, record in payload.items():
        if record.get("STATUS") == "OK_BYPASS" or "Simulacao" in str(record.get("NATUREZA_JURIDICA", "")):
            continue
        resultado = normalizar_cnpj(cnpj)
        if resultado.valido and isinstance(record, dict):
            cache[resultado.cnpj] = record
    return cache

def _save_cache(path: Path, cache: dict[str, dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ordered = {cnpj: cache[cnpj] for cnpj in sorted(cache)}
    path.write_text(json.dumps(ordered, ensure_ascii=False, indent=2), encoding="utf-8")

def _is_cache_valido(record: dict[str, Any], dias_validade: int = 30) -> bool:
    """Retorna True se o registro de cache foi consultado dentro do período de validade."""
    quando = record.get("DATA_CONSULTA")
    if not quando: return False
    try:
        dt_consulta = datetime.fromisoformat(str(quando)[:19])
        return (datetime.now() - dt_consulta).days < dias_validade
    except Exception: return False

def _consultar_cnpj_brasilapi(cnpj: str, session: requests.Session) -> dict[str, Any]:
    url = f"{BRASIL_API_BASE_URL}/{cnpj}"
    resultado = {
        "CNPJ": cnpj, "SITUACAO_CADASTRAL": "ERRO_API", "DATA_ABERTURA": "N/D",
        "CNAE_PRINCIPAL": "N/D", "NATUREZA_JURIDICA": "N/D",
        "DATA_CONSULTA": datetime.now().isoformat(timespec="seconds"),
        "STATUS": "FALHA", "MENSAGEM": ""
    }
    
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) BDC_Pipeline/1.0",
    }
    
    tentativas_maximas = 4
    espera_base = 3.0

    for tentativa in range(1, tentativas_maximas + 1):
        try:
            resp = session.get(url, headers=headers, timeout=15, verify=False)
            
            if resp.status_code == 200:
                data = resp.json()
                resultado["SITUACAO_CADASTRAL"] = str(data.get("descricao_situacao_cadastral", "N/D")).strip().upper()
                resultado["DATA_ABERTURA"] = str(data.get("data_inicio_atividade", "N/D")).strip()
                resultado["CNAE_PRINCIPAL"] = str(data.get("cnae_fiscal", "N/D")).strip()
                resultado["NATUREZA_JURIDICA"] = str(data.get("natureza_juridica", "N/D")).strip()
                resultado["STATUS"] = "SUCESSO"
                resultado["MENSAGEM"] = "Consulta via BrasilAPI com sucesso"
                return resultado
                
            if resp.status_code in (404, 400):
                resultado["SITUACAO_CADASTRAL"] = "NAO_ENCONTRADO"
                resultado["MENSAGEM"] = f"CNPJ inexistente (HTTP {resp.status_code})"
                return resultado
                
            if resp.status_code == 429 or resp.status_code >= 500:
                if tentativa < tentativas_maximas:
                    tempo_espera = espera_base * (2 ** (tentativa - 1))
                    LOGGER.warning("API bloqueou - HTTP %s. Pausando %ss...", resp.status_code, tempo_espera)
                    time.sleep(tempo_espera)
                    continue
                else:
                    resultado["SITUACAO_CADASTRAL"] = "RATE_LIMIT"
                    resultado["MENSAGEM"] = "Bloqueio persistente após múltiplas tentativas."
                    return resultado

            resultado["SITUACAO_CADASTRAL"] = f"ERRO_HTTP_{resp.status_code}"
            return resultado

        except requests.exceptions.Timeout:
            if tentativa < tentativas_maximas:
                time.sleep(espera_base * tentativa)
                continue
            resultado["SITUACAO_CADASTRAL"] = "TIMEOUT"
            return resultado
            
        except requests.exceptions.RequestException as e:
            if tentativa < tentativas_maximas:
                time.sleep(espera_base * tentativa)
                continue
            resultado["SITUACAO_CADASTRAL"] = "ERRO_CONEXAO"
            return resultado

    return resultado

def buscar_receita_dados_lote(cnpjs: list[str], context: AppContext, logger: logging.Logger = LOGGER) -> pd.DataFrame:
    cache_path = _cache_path(context)
    cache = _load_cache(cache_path)
    
    list_normalizada = []
    seen = set()
    for cnpj in cnpjs or []:
        resultado = normalizar_cnpj(cnpj)
        if resultado.valido and resultado.cnpj not in seen:
            seen.add(resultado.cnpj)
            list_normalizada.append(resultado.cnpj)

    results = []
    total = len(list_normalizada)
    qtd_cache = 0
    qtd_api = 0
    qtd_erro = 0
    
    logger.info("[RECEITA FEDERAL] Processando %d CNPJs...", total)
    logger.info("--- INICIANDO CONSULTA RECEITA FEDERAL (%d CNPJs) ---", total)

    with requests.Session() as sessao:
        for index, cnpj in enumerate(list_normalizada):
            cached = cache.get(cnpj)
            
            if cached and _is_cache_valido(cached):
                if cached.get("SITUACAO_CADASTRAL") not in ["TIMEOUT", "RATE_LIMIT", "ERRO_CONEXAO", "ERRO_API"]:
                    logger.info("[%d/%d] CNPJ %s -> CACHE (%s)", index + 1, total, cnpj, cached.get('SITUACAO_CADASTRAL'))
                    results.append(cached)
                    qtd_cache += 1
                    continue

            logger.info("[%d/%d] CNPJ %s -> Consultando API...", index + 1, total, cnpj)
            api_result = _consultar_cnpj_brasilapi(cnpj, sessao)
            status_obtido = api_result.get("SITUACAO_CADASTRAL")
            logger.info("Resultado: %s", status_obtido)
            
            qtd_api += 1
            if api_result.get("STATUS") == "FALHA":
                qtd_erro += 1
                
            if status_obtido not in ["TIMEOUT", "RATE_LIMIT", "ERRO_CONEXAO"]:
                cache[cnpj] = api_result
                
            results.append(api_result)
            
            time.sleep(0.8)

            if qtd_api > 0 and qtd_api % 50 == 0:
                _save_cache(cache_path, cache)

    if qtd_api > 0:
        _save_cache(cache_path, cache)

    logger.info("--- RESUMO RECEITA: %d Cache | %d API | %d Erros ---", qtd_cache, qtd_api, qtd_erro)

    df = pd.DataFrame(results)
    return df.drop_duplicates(subset=["CNPJ"], keep="last").reset_index(drop=True)