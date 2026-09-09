import os
import json
import requests
import urllib3
import time

# Desabilita avisos SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

RISK3_API_URL = os.getenv("RISK3_API_URL", "https://express-api.risk3.live")
RISK3_USER = os.getenv("RISK3_USER", "apirisk3@copel.com.br")
RISK3_PWD = os.getenv("RISK3_PWD", "APIr!sk3C0Pe|")
    
CNPJ_TESTE = "00056633000111" 

def executar_teste_post():
    print("--- 1. AUTENTICANDO NA RISK3 ---")
    login_url = f"{RISK3_API_URL.rstrip('/')}/api/v0/login"
    
    resp_login = requests.post(
        login_url, 
        json={"username": RISK3_USER, "password": RISK3_PWD}, 
        verify=False
    )
    
    if resp_login.status_code != 200:
        print(f"FALHA NO LOGIN! HTTP {resp_login.status_code}")
        return
        
    token = resp_login.json().get("data")
    if isinstance(token, dict):
        token = token.get("token")
        
    headers = {
        "Venidera-AuthToken": str(token),
        "Content-Type": "application/json"
    }
    
    print(f"\n--- 2. SOLICITANDO NOVA ANÁLISE (POST) PARA O CNPJ: {CNPJ_TESTE} ---")
    url_post = f"{RISK3_API_URL.rstrip('/')}/api/v0/analises"
    
    # Payload padrão para criação de análise em APIs de Bureau
    payload = {"cnpj": CNPJ_TESTE}
    
    resp_post = requests.post(url_post, headers=headers, json=payload, verify=False)
    
    print(f"STATUS CODE POST: {resp_post.status_code}")
    print("\n--- JSON DE RESPOSTA (RAW) ---")
    try:
        print(json.dumps(resp_post.json(), indent=2, ensure_ascii=False))
    except Exception:
        print("Retorno não é JSON:")
        print(resp_post.text)

if __name__ == "__main__":
    executar_teste_post()