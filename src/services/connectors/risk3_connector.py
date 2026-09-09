"""Conector oficial para a API Expresso RISK3 (Bureau de Crédito)."""
from __future__ import annotations
import json
import logging
import math
import os
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pathlib import Path
from typing import Any
import pandas as pd
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from app.context import AppContext
from common.identificadores import normalizar_cnpj
from control.logger import obter_logger
logger = obter_logger(__name__)

def _obter_token_auth() -> str | None:
    """Autentica na API da RISK3 e obtém um token de sessão via POST."""
    base_url = os.getenv("RISK3_API_URL")
    user = os.getenv("RISK3_USER")
    pwd = os.getenv("RISK3_PWD")

    if not all([base_url, user, pwd]):
        logger.warning("Credenciais RISK3_API_URL, RISK3_USER ou RISK3_PWD ausentes no .env")
        return None
    proxies = {"http": None, "https": None}

    try:
        url = f"{base_url.rstrip('/')}/api/v0/login"
        resp = requests.post(url, json={"username": user, "password": pwd}, timeout=15, verify=False, proxies=proxies)
        
        if "Acesso Bloqueado" in resp.text or "Netskope" in resp.text:
            logger.error("Conexão interceptada pelo Netskope/Firewall da Copel.")
            return None

        if resp.status_code == 200:
            data = resp.json().get("data")
            if isinstance(data, dict):
                return data.get("token")
            return data
        logger.error("Falha na autenticação RISK3. HTTP %s", resp.status_code)
        return None
    except Exception as e:
        logger.error("Falha de conexão na RISK3: %s", e)
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
        logger.warning("Sem token da RISK3. Abortando consulta de Bureau.")
        return pd.DataFrame()
    api_url = os.getenv("RISK3_API_URL", "").rstrip('/')
    proxies = {"http": None, "https": None}
    cnpjs_unicos = sorted(list(set(normalizar_cnpj(c).cnpj for c in cnpjs if normalizar_cnpj(c).valido)))
    results = []
    
    logger.info("--- INICIANDO CONSULTA RISK3 BUREAU (%d CNPJs) ---", len(cnpjs_unicos))
    
    for i, cnpj in enumerate(cnpjs_unicos):
        cached = cache.get(cnpj)
        if cached:
            status_cache = cached.get("STATUS")
            data_cons = cached.get("DATA_CONSULTA")
            if data_cons and status_cache in ("SUCESSO", "NAO_ENCONTRADO"):
                dias_cache = (datetime.now() - datetime.fromisoformat(data_cons)).days
                ttl = 365 if status_cache == "SUCESSO" else 30
                if dias_cache < ttl:
                    logger.info("[%d/%d] CNPJ %s -> CACHE (%s, %dd/%dd)", i + 1, len(cnpjs_unicos), cnpj, status_cache, dias_cache, ttl)
                    results.append(cached)
                    continue

        logger.info("[%d/%d] CNPJ %s -> Consultando API (Endpoint detalhado por CNPJ)...", i + 1, len(cnpjs_unicos), cnpj)
        
        auth_value = json.dumps(token) if isinstance(token, dict) else str(token)
        headers = {"Venidera-AuthToken": auth_value}
        
        resultado = {
            "CNPJ": cnpj,
            "DATA_CONSULTA": datetime.now().isoformat(timespec="seconds"),
            "STATUS": "FALHA"
        }

        try:
            # Pelo Swagger oficial, o endpoint correto de consulta por CNPJ é:
            url_busca = f"{api_url}/api/v0/analises/cnpj/{cnpj}"
            resp_busca = requests.get(url_busca, headers=headers, timeout=20, verify=False, proxies=proxies)
            
            if "Netskope" in resp_busca.text or "Acesso Bloqueado" in resp_busca.text:
                resultado["STATUS"] = "BLOQUEIO_FIREWALL"
                logger.warning("BLOQUEIO_FIREWALL")
            elif resp_busca.status_code == 200:
                body_busca = resp_busca.json()
                data_obj = body_busca.get("data")
                
                if not data_obj:
                    resultado["STATUS"] = "NAO_ENCONTRADO"
                    logger.info("NAO_ENCONTRADO (Data vazio)")
                else:
                    # A resposta detalhada pode vir como uma lista de análises para aquele CNPJ ou um dicionário
                    analises = data_obj if isinstance(data_obj, list) else data_obj.get("analises", [])
                    if isinstance(data_obj, dict) and not analises:
                        analises = [data_obj]
                    
                    if not analises:
                        resultado["STATUS"] = "NAO_ENCONTRADO"
                        logger.warning("NAO_ENCONTRADO (Lista de análises vazia no retorno detalhado)")
                    else:
                        analise_item = analises[0]
                        bloco_analise = analise_item.get("analise", {}) if "analise" in analise_item else analise_item
                        bloco_calculos = bloco_analise.get("calculos", {})
                        bloco_custom = bloco_analise.get("custom_ratings", {}).get("rating", {})
                        
                        score_val = bloco_calculos.get("score_final")
                        restritivos_val = bloco_calculos.get("fator_de_alerta")
                        
                        resultado["SCORE_BUREAU"] = float(score_val) if score_val is not None else None
                        resultado["RATING_BUREAU"] = bloco_custom.get("grade") if bloco_custom.get("grade") is not None else None
                        resultado["RESTRITIVOS"] = float(restritivos_val) if restritivos_val is not None else None
                        
                        data_req = analise_item.get("data_da_solicitacao")
                        if data_req:
                            try:
                                dt_consulta = pd.to_datetime(data_req)
                                resultado["DATA_CONSULTA"] = dt_consulta.strftime("%Y-%m-%d")
                                resultado["DATA_VALIDADE"] = (dt_consulta + relativedelta(months=18)).strftime("%Y-%m-%d")
                            except Exception:
                                resultado["DATA_CONSULTA"] = data_req
                                resultado["DATA_VALIDADE"] = None
                        else:
                            resultado["DATA_CONSULTA"] = None
                            resultado["DATA_VALIDADE"] = None
                            
                        if resultado["SCORE_BUREAU"] is not None and resultado["RESTRITIVOS"] is not None:
                            try:
                                s = resultado["SCORE_BUREAU"]
                                r = resultado["RESTRITIVOS"]
                                pd_calc = 1.9 * math.exp(-0.5 * (0.11 * s - r / 3.0 + 1))
                                resultado["PD_BUREAU"] = min(pd_calc, 0.9999)
                            except Exception:
                                resultado["PD_BUREAU"] = None
                        else:
                            resultado["PD_BUREAU"] = None

                        resultado["RAW_DATA"] = json.dumps(data_obj, ensure_ascii=False)
                        resultado["STATUS"] = "SUCESSO"
                        logger.info("SUCESSO na extração dos detalhes!")
                        
                        # Salvar raw json na pasta risk3 (Auditoria/Física)
                        pasta_raw = context.path("bronze") / "risk3_raw"
                        pasta_raw.mkdir(parents=True, exist_ok=True)
                        arquivo_raw = pasta_raw / f"risk3_{cnpj}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        arquivo_raw.write_text(resultado["RAW_DATA"], encoding="utf-8")
                        
            elif resp_busca.status_code in (404, 422):
                resultado["STATUS"] = "NAO_ENCONTRADO"
                logger.info("NAO_ENCONTRADO (HTTP %s - A análise pode não existir ainda no Bureau)", resp_busca.status_code)
            else:
                resultado["STATUS"] = f"ERRO_HTTP_{resp_busca.status_code}"
                logger.warning("ERRO_HTTP_%s ao consultar CNPJ", resp_busca.status_code)
        except Exception as e:
            resultado["STATUS"] = "ERRO_CONEXAO"
            logger.exception("ERRO_CONEXAO: %s", e)
        if resultado["STATUS"] in ["SUCESSO", "NAO_ENCONTRADO"]:
            cache[cnpj] = resultado
        results.append(resultado)
        time.sleep(0.5)

    if results:
        cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    return pd.DataFrame(results)