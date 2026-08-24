# -*- coding: utf-8 -*-
"""Conector e cache da BrasilAPI para consulta cadastral de Receita Federal."""

from __future__ import annotations
from silver.normalizadores import padronizar_cnpj

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
        normalized = padronizar_cnpj(cnpj)
        if normalized and isinstance(record, dict):
            cache[normalized[0]] = record
    return cache

def _save_cache(path: Path, cache: dict[str, dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ordered = {cnpj: cache[cnpj] for cnpj in sorted(cache)}
    path.write_text(json.dumps(ordered, ensure_ascii=False, indent=2), encoding="utf-8")

def _is_same_day_cache(record: dict[str, Any]) -> bool:
    quando = record.get("DATA_CONSULTA")
    if not quando: return False
    try:
        return str(quando)[:10] == date.today().isoformat()
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
    espera_base = 3.0 # Segundos

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
                    tempo_espera = espera_base * (2 ** (tentativa - 1)) # Backoff Exponencial (3s, 6s, 12s...)
                    print(f" [API bloqueou - HTTP {resp.status_code}] Pausando {tempo_espera}s...", end="", flush=True)
                    time.sleep(tempo_espera)
                    continue
                else:
                    resultado["SITUACAO_CADASTRAL"] = "RATE_LIMIT"
                    resultado["MENSAGEM"] = "Bloqueio persistente após múltiplas tentativas."
                    return resultado

            # Outros erros HTTP (401, 403, etc)
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

def buscar_receita_dados_lote(cnpjs: list[str], context: AppContext) -> pd.DataFrame:
    cache_path = _cache_path(context)
    cache = _load_cache(cache_path)
    
    list_normalizada = []
    seen = set()
    for cnpj in cnpjs or []:
        normalized = padronizar_cnpj(cnpj)
        if normalized and normalized not in seen:
            seen.add(normalized)
            list_normalizada.append(normalized)

    results = []
    total = len(list_normalizada)
    qtd_cache = 0
    qtd_api = 0
    qtd_erro = 0
    
    LOGGER.info("[RECEITA FEDERAL] Processando %d CNPJs...", total)
    print(f"\n--- INICIANDO CONSULTA RECEITA FEDERAL ({total} CNPJs) ---")

    # Usando Session para otimizar conexões TCP
    with requests.Session() as sessao:
        for index, cnpj in enumerate(list_normalizada):
            cached = cache.get(cnpj)
            
            if cached and _is_same_day_cache(cached):
                if cached.get("SITUACAO_CADASTRAL") not in ["TIMEOUT", "RATE_LIMIT", "ERRO_CONEXAO", "ERRO_API"]:
                    print(f"[{index + 1}/{total}] CNPJ {cnpj} -> CACHE ({cached.get('SITUACAO_CADASTRAL')})")
                    results.append(cached)
                    qtd_cache += 1
                    continue

            print(f"[{index + 1}/{total}] CNPJ {cnpj} -> Consultando API...", end=" ", flush=True)
            api_result = _consultar_cnpj_brasilapi(cnpj, sessao)
            status_obtido = api_result.get("SITUACAO_CADASTRAL")
            print(f"Resultado: {status_obtido}")
            
            qtd_api += 1
            if api_result.get("STATUS") == "FALHA":
                qtd_erro += 1
                
            if status_obtido not in ["TIMEOUT", "RATE_LIMIT", "ERRO_CONEXAO"]:
                cache[cnpj] = api_result
                
            results.append(api_result)
            
            # Pausa padrão gentil de 0.8s entre requisições de sucesso para não irritar a BrasilAPI
            time.sleep(0.8)

            if qtd_api > 0 and qtd_api % 50 == 0:
                _save_cache(cache_path, cache)

    if qtd_api > 0:
        _save_cache(cache_path, cache)

    print(f"\n--- RESUMO RECEITA: {qtd_cache} Cache | {qtd_api} API | {qtd_erro} Erros ---")

    df = pd.DataFrame(results)
    return df.drop_duplicates(subset=["CNPJ"], keep="last").reset_index(drop=True)