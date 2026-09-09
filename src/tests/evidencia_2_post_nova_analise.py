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

print("=== EVIDÊNCIA 4: POST com parâmetro na Query String (Recomendação do Suporte) ===")
cnpj_alvo = "00601731000192"

url_post = f"{api_url}/api/v0/analises"

# O 'product' entra aqui, no params (Query String)
params = {"product": "express_light"}

# O payload JSON fica limpo, apenas com o CNPJ e cache
payload = {
    "cnpjs": [cnpj_alvo],
    "rule": {},
    "analysis_cache": 1
}

try:
    resp_post = requests.post(url_post, headers=headers, params=params, json=payload, verify=False)
    print(f"Status do POST: {resp_post.status_code}")
    print(f"Resultado:\n{resp_post.text[:500]}")
except Exception as e:
    print(f"Erro: {e}")