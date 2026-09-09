import os
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from dotenv import load_dotenv

# Ajuste o caminho se necessário para encontrar o .env
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

api_url = os.getenv("RISK3_API_URL", "").rstrip('/')
user = os.getenv("RISK3_USER")
pwd = os.getenv("RISK3_PWD")

print(f"Testando conexão com o ambiente: {api_url}")

# 1. Autenticação
resp_login = requests.post(f"{api_url}/api/v0/login", json={"username": user, "password": pwd}, verify=False)
if resp_login.status_code != 200:
    print(f"Erro na Autenticação (HTTP {resp_login.status_code}): {resp_login.text}")
    exit()

token = resp_login.json().get("data", {}).get("token")
headers = {"Venidera-AuthToken": str(token)}

# 2. Teste de Listagem Geral (Validação de Volume)
print("\n--- Teste 1: Histórico Geral (Light) ---")
r_list = requests.get(
    f"{api_url}/api/v0/analises", 
    headers=headers, 
    params={"limit": 5, "product": "express_light"}, 
    verify=False
)

if r_list.status_code == 200:
    solicitacoes = r_list.json().get("data", {}).get("solicitações", [])
    print(f"Sucesso! Retornou {len(solicitacoes)} registros na amostra.")
    if solicitacoes:
        print(f"CNPJ mais recente na base: {solicitacoes[0].get('cnpj')}")
else:
    print(f"Erro no GET geral: {r_list.text}")

# 3. Teste do CNPJ Específico (O que retornava 404 na homologação)
cnpj_alvo = "08540795001104"
print(f"\n--- Teste 2: Busca por CNPJ Específico ({cnpj_alvo}) ---")
r_cnpj = requests.get(
    f"{api_url}/api/v0/analises/cnpj/{cnpj_alvo}", 
    headers=headers, 
    params={"product": "express_light"}, 
    verify=False
)

print(f"Status HTTP: {r_cnpj.status_code}")
print(f"Resposta Bruta: {r_cnpj.text}")