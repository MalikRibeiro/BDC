"""Conector oficial para a API Expresso RISK3 (Bureau de Crédito)."""

from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from app.context import AppContext
from silver.normalizadores import padronizar_cnpj

LOGGER = logging.getLogger(__name__)

def _obter_token_auth() -> str | None:
    """Autentica na API da RISK3 e obtém um token de sessão via POST."""
    base_url = os.getenv("RISK3_BASE_URL")
    user = os.getenv("RISK3_USER")
    pwd = os.getenv("RISK3_PWD")

    if not all([base_url, user, pwd]):
        LOGGER.warning("Credenciais RISK3_BASE_URL, RISK3_USER ou RISK3_PWD ausentes no .env")
        return None

    proxies = {"http": None, "https": None} # Tenta bypass de proxy local

    try:
        url = f"{base_url.rstrip('/')}/api/v0/login"
        resp = requests.post(url, json={"username": user, "password": pwd}, timeout=15, verify=False, proxies=proxies)
        
        # Bloqueio de rede detectado
        if "Acesso Bloqueado" in resp.text or "Netskope" in resp.text:
            LOGGER.error("Conexão interceptada pelo Netskope/Firewall da Copel.")
            return None

        if resp.status_code == 200:
            return resp.json().get("data")
            
        LOGGER.error("Falha na autenticação RISK3. HTTP %s", resp.status_code)
        return None
    except Exception as e:
        LOGGER.error("Falha de conexão na RISK3: %s", e)
        return None

def buscar_bureau_risk3(cnpjs: list[str], context: AppContext) -> pd.DataFrame:
    """Orquestra a consulta em lote na RISK3 utilizando cache local."""
    cache_path = context.path("entradas") / "bureau" / "cache" / "risk3_cache.json"
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    
    cache = {}
    if cache_path.exists():
        try:
            cache = json.loads(cache_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass

    token = _obter_token_auth()
    if not token:
        LOGGER.warning("Sem token da RISK3. Abortando consulta de Bureau.")
        return pd.DataFrame()

    base_url = os.getenv("RISK3_BASE_URL", "").rstrip('/')
    proxies = {"http": None, "https": None}
    
    cnpjs_unicos = sorted(list(set(padronizar_cnpj(c)[0] for c in cnpjs if padronizar_cnpj(c)[0] is not None)))
    results = []
    
    print(f"\n--- INICIANDO CONSULTA RISK3 BUREAU ({len(cnpjs_unicos)} CNPJs) ---")
    
    for i, cnpj in enumerate(cnpjs_unicos):
        # Validação de Cache (30 dias para não gastar chamadas do contrato)
        cached = cache.get(cnpj)
        if cached and cached.get("STATUS") == "SUCESSO":
            data_cons = cached.get("DATA_CONSULTA")
            if data_cons:
                if (datetime.now() - datetime.fromisoformat(data_cons)).days < 30:
                    print(f"[{i + 1}/{len(cnpjs_unicos)}] CNPJ {cnpj} -> CACHE (Válido)")
                    results.append(cached)
                    continue

        print(f"[{i + 1}/{len(cnpjs_unicos)}] CNPJ {cnpj} -> Consultando API...", end=" ", flush=True)
        
        url = f"{base_url}/api/v0/analises/cnpj/{cnpj}"
        headers = {"Venidera-AuthToken": token}
        
        resultado = {
            "CNPJ": cnpj,
            "DATA_CONSULTA": datetime.now().isoformat(timespec="seconds"),
            "STATUS": "FALHA"
        }

        try:
            resp = requests.get(url, headers=headers, timeout=20, verify=False, proxies=proxies)
            
            if "Netskope" in resp.text or "Acesso Bloqueado" in resp.text:
                resultado["STATUS"] = "BLOQUEIO_FIREWALL"
                print("BLOQUEIO_FIREWALL")
            elif resp.status_code == 200:
                data_obj = resp.json().get("data", {})
                resultado["RAW_DATA"] = json.dumps(data_obj, ensure_ascii=False)
                resultado["STATUS"] = "SUCESSO"
                print("SUCESSO")
            elif resp.status_code in (404, 422):
                resultado["STATUS"] = "NAO_ENCONTRADO"
                print("NAO_ENCONTRADO")
            else:
                resultado["STATUS"] = f"ERRO_HTTP_{resp.status_code}"
                print(f"ERRO_HTTP_{resp.status_code}")
        except Exception:
            resultado["STATUS"] = "ERRO_CONEXAO"
            print("ERRO_CONEXAO")

        if resultado["STATUS"] in ["SUCESSO", "NAO_ENCONTRADO"]:
            cache[cnpj] = resultado
            
        results.append(resultado)
        time.sleep(0.5)

    if results:
        cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")

    return pd.DataFrame(results)