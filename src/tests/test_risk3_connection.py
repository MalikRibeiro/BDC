from __future__ import annotations

import time
import json
import os
import sys
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from dotenv import load_dotenv, find_dotenv

_dotenv_path = find_dotenv(usecwd=True)
if _dotenv_path:
    load_dotenv(_dotenv_path)
    print(f"[.env carregado de: {_dotenv_path}]")
else:
    print("[AVISO: nenhum arquivo .env encontrado a partir do diretório atual]")

PROXIES = {"http": None, "https": None}
PRODUCT = "express"  
CNPJ_TESTE = "00038166000105"  


def testar_login() -> str | None:
    base_url = os.getenv("RISK3_API_URL") 
    user = os.getenv("RISK3_USER") 
    pwd = os.getenv("RISK3_PWD")

    print("== 1. LOGIN ==")
    if not all([base_url, user, pwd]):
        print("FALHA: RISK3_API_URL, RISK3_USER ou RISK3_PWD não definidos no ambiente.")
        return None

    url = f"{base_url.rstrip('/')}/api/v0/login"
    try:
        resp = requests.post(
            url,
            json={"username": user, "password": pwd},
            timeout=15,
            verify=False,
            proxies=PROXIES,
        )
    except Exception as e:
        print(f"FALHA DE CONEXÃO: {e}")
        return None

    print(f"HTTP {resp.status_code}")
    if "Netskope" in resp.text or "Acesso Bloqueado" in resp.text:
        print("BLOQUEIO: resposta interceptada por proxy/firewall corporativo (Netskope).")
        print(resp.text[:500])
        return None

    try:
        body = resp.json()
    except Exception:
        print("FALHA: resposta não é JSON.")
        print(resp.text[:500])
        return None

    print(f"Corpo: status={body.get('status')!r} message={body.get('message')!r}")

    if resp.status_code != 200:
        print("FALHA: HTTP diferente de 200.")
        return None

    data = body.get("data")
    if not isinstance(data, dict):
        print(f"AVISO: campo 'data' em formato inesperado: {data!r}")
        return None

    token = data.get("token")
    if not token or not isinstance(token, str):
        print(f"AVISO: 'data.token' vazio ou em formato inesperado: {token!r}")
        return None

    preview = f"{token[:8]}...{token[-4:]}" if len(token) > 12 else token
    print(f"OK: token obtido ({preview})")
    return token


def testar_solicitar_analise(token: str, cnpj: str) -> None:
    base_url = os.getenv("RISK3_API_URL", "").rstrip("/")
    url = f"{base_url}/api/v0/analises"
    headers = {"Venidera-AuthToken": token}
    params = {"product": PRODUCT}
    payload = {"cnpjs": [cnpj], "analysis_cache": 1}

    print(f"\n== 2. SOLICITAR ANÁLISE (POST) CNPJ {cnpj} (product={PRODUCT}) ==")
    try:
        resp = requests.post(
            url, headers=headers, params=params, json=payload,
            timeout=30, verify=False, proxies=PROXIES,
        )
    except Exception as e:
        print(f"FALHA DE CONEXÃO: {e}")
        return

    print(f"HTTP {resp.status_code}")
    if "Netskope" in resp.text or "Acesso Bloqueado" in resp.text:
        print("BLOQUEIO: resposta interceptada por proxy/firewall corporativo (Netskope).")
        return

    try:
        body = resp.json()
    except Exception:
        print("FALHA: resposta não é JSON.")
        print(resp.text[:500])
        return

    print(f"status={body.get('status')!r} message={body.get('message')!r} batch_id={body.get('batch_id')!r}")
    data = body.get("data")
    print("data retornado no POST:")
    print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])


def testar_consulta_segura(token: str, cnpj: str) -> None:
    base_url = os.getenv("RISK3_API_URL", "").rstrip("/")
    url_busca = f"{base_url}/api/v0/analises"
    headers = {"Venidera-AuthToken": token}
    params = {"cnpj": cnpj}

    print(f"\n== 2. LISTAGEM DE ANÁLISES (GET) CNPJ {cnpj} ==")
    try:
        resp_busca = requests.get(url_busca, headers=headers, params=params, timeout=20, verify=False, proxies=PROXIES)
    except Exception as e:
        print(f"FALHA DE CONEXÃO: {e}")
        return

    print(f"HTTP {resp_busca.status_code}")
    if "Netskope" in resp_busca.text or "Acesso Bloqueado" in resp_busca.text:
        print("BLOQUEIO: resposta interceptada por proxy/firewall corporativo (Netskope).")
        return

    try:
        body_busca = resp_busca.json()
    except Exception:
        print("FALHA: resposta não é JSON.")
        print(resp_busca.text[:500])
        return

    print(f"status={body_busca.get('status')!r} message={body_busca.get('message')!r}")
    print("\n[DEBUG] JSON Bruto retornado pela API:")
    print(json.dumps(body_busca, indent=2, ensure_ascii=False)[:3000])

    data_busca = body_busca.get("data", [])
    lista = data_busca.get("data", []) if isinstance(data_busca, dict) and "data" in data_busca else data_busca
    if isinstance(lista, dict):
        lista = lista.get("solicitações") or lista.get("solicitacoes") or lista.get("analises") or []

    if not lista or not isinstance(lista, list):
        print("\nAVISO: Nenhuma análise encontrada na listagem (retorno vazio).")
        return

    print(f"\nEncontradas {len(lista)} análises gerais na conta. Procurando pelo CNPJ {cnpj}...")
    
    analise_id = None
    item_encontrado = None
    
    for item in lista:
        doc_item = str(item.get("cnpj") or item.get("documento") or item.get("document") or item.get("cpf_cnpj") or "")
        doc_limpo = ''.join(filter(str.isdigit, doc_item))
        if doc_limpo == cnpj:
            analise_id = item.get("id") or item.get("analise_id")
            item_encontrado = item
            break
    
    if not analise_id:
        print(f"AVISO: O CNPJ {cnpj} NÃO foi encontrado entre as {len(lista)} solicitações recentes.")
        print("Amostra do primeiro item da lista para debug:")
        print(json.dumps(lista[0], indent=2, ensure_ascii=False))
        return
        
    print(f"CNPJ encontrado! ID da análise: {analise_id}")
    print(f"\n== 3. DETALHE DA ANÁLISE (GET) ID {analise_id} ==")
    url_detalhe = f"{base_url}/api/v0/analises/id/{analise_id}"
    
    try:
        resp_det = requests.get(url_detalhe, headers=headers, timeout=20, verify=False, proxies=PROXIES)
    except Exception as e:
        print(f"FALHA DE CONEXÃO: {e}")
        return

    print(f"HTTP {resp_det.status_code}")
    try:
        body_det = resp_det.json()
    except Exception:
        print("FALHA: resposta não é JSON.")
        return

    data = body_det.get("data")
    print("\n== 4. ESTRUTURA DO PAYLOAD DETALHADO (data) ==")
    print(json.dumps(data, indent=2, ensure_ascii=False)[:4000])

    if isinstance(data, dict):
        print("\n== 5. CHAVES DE TOPO ENCONTRADAS (confira contra o mapeamento esperado) ==")
        for k in data.keys():
            print(f"  - {k}")
    else:
        print(f"\nAVISO: 'data' não é um dict (tipo={type(data)}).")


if __name__ == "__main__":
    cnpj = sys.argv[1] if len(sys.argv) > 1 else CNPJ_TESTE
    tok = testar_login()
    if tok:
        testar_consulta_segura(tok, cnpj)
    else:
        print("\nAbortado: sem token válido, não é possível testar a consulta.")