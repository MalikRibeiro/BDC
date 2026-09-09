import os
import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

api_url = os.getenv("RISK3_API_URL", "").rstrip('/')
user = os.getenv("RISK3_USER")
pwd = os.getenv("RISK3_PWD")

print("1. Autenticando na RISK3...")
resp_login = requests.post(f"{api_url}/api/v0/login", json={"username": user, "password": pwd}, verify=False)
token = resp_login.json().get("data", {}).get("token")
headers = {"Venidera-AuthToken": str(token)}

cnpj_alvo = "00601731000192"
print(f"\n2. Solicitando NOVA análise (POST) para o CNPJ {cnpj_alvo}...")

# Conforme o Swagger: POST /api/v0/analises
url_post = f"{api_url}/api/v0/analises"

# Payload conforme schema RequestsCacheCNPJ
payload = {
    "cnpjs": [cnpj_alvo],
    # analysis_cache = 1 geralmente indica para a API não refazer do zero se já tiver feito hoje, economizando créditos.
    "analysis_cache": 1 
}

try:
    resp_post = requests.post(url_post, headers=headers, json=payload, verify=False)
    print(f"Status HTTP: {resp_post.status_code}")
    
    if resp_post.status_code in (200, 201):
        dados_retorno = resp_post.json()
        print("\n>>> SUCESSO! A análise foi processada/retornada.")
        print(json.dumps(dados_retorno, indent=2, ensure_ascii=False)[:1000]) # Mostra os primeiros 1000 caracteres
        
        # O Swagger diz que o retorno vai no campo 'data'
        data_obj = dados_retorno.get("data")
        if data_obj:
            analises = data_obj if isinstance(data_obj, list) else data_obj.get("analises", [])
            if isinstance(data_obj, dict) and not analises:
                analises = [data_obj]
                
            if analises:
                bloco_analise = analises[0].get("analise", {}) if "analise" in analises[0] else analises[0]
                bloco_calculos = bloco_analise.get("calculos", {})
                bloco_resultado = bloco_analise.get("resultado_da_analise", {})
                
                score = bloco_calculos.get("score_final") or bloco_analise.get("score")
                rating = bloco_resultado.get("alerta") or bloco_analise.get("restriction")
                
                print(f"\n--- DADOS EXTRAÍDOS DA NOVA ANÁLISE ---")
                print(f"SCORE: {score}")
                print(f"RATING/RESTRITIVO: {rating}")
            else:
                print("Lista de análises veio vazia no retorno.")
    else:
        print(f"\nFalha ao solicitar análise. Retorno da API: {resp_post.text}")
        
except Exception as e:
    print(f"Erro de conexão/execução: {e}")
