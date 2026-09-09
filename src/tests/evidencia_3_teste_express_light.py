import os
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

api_url = os.getenv("RISK3_API_URL", "").rstrip('/')
user = os.getenv("RISK3_USER")
pwd = os.getenv("RISK3_PWD")

resp_login = requests.post(f"{api_url}/api/v0/login", json={"username": user, "password": pwd}, verify=False)
token = resp_login.json().get("data", {}).get("token")
headers = {"Venidera-AuthToken": str(token)}

print("=== EVIDÊNCIA 3: Endpoint detalhado sem parâmetro de produto ===")

# CNPJ do print da Web
cnpj_teste_web = "08540795001104" 

url_busca = f"{api_url}/api/v0/analises/cnpj/{cnpj_teste_web}"
print(f"Buscando: {url_busca}")

try:
    # Remoção do params={"product": "express_light"}
    resp = requests.get(url_busca, headers=headers, verify=False)
    print(f"Status HTTP: {resp.status_code}")
    
    if resp.status_code == 200:
        print("Sucesso! A análise foi encontrada.")
        print(f"Retorno: {resp.text[:300]}...")
    else:
        print(f"Retorno: {resp.text[:200]}")
except Exception as e:
    print(f"Erro: {e}")