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

print("=== EVIDÊNCIA 1: Histórico Restrito e Paginação ===")
try:
    r = requests.get(f"{api_url}/api/v0/analises", headers=headers, params={"limit": 10000, "product": "express_light"}, verify=False)
    if r.status_code == 200:
        data = r.json().get("data", {})
        
        # Inspeciona as chaves do JSON para procurar metadados de paginação (total_pages, etc)
        if isinstance(data, dict):
            print(f"Metadados retornados na resposta (chaves): {list(data.keys())}")
            lista = data.get("solicitações", []) or data.get("analises", []) or data.get("data", [])
        elif isinstance(data, list):
            lista = data
        else:
            lista = []
            
        print(f"Sucesso! A API retornou {len(lista)} análises nesta página/requisição.")
        print(f"Amostra dos dados brutos: {str(data)[:300]}...")
    else:
        print(f"Falha: {r.status_code} - {r.text[:200]}")
except Exception as e:
    print(f"Erro: {e}")