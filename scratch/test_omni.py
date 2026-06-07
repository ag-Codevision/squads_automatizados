import os
import requests
from dotenv import load_dotenv

# Carrega as variáveis do .env do squad
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "squads", "conexao_artificial", ".env")
load_dotenv(dotenv_path)

url = os.environ.get("OMNI_URL", "http://srv1268090.hstgr.cloud:20128/v1/chat/completions")
api_key = os.environ.get("OMNI_API_KEY", "sk-c50ed36fd3f69f11-057eaa-08ce3407")

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

modelos = ["ws/gpt-4o-mini", "pu/gpt-4o-mini", "ws/gpt-4o", "bb/gpt-4o"]

print(f"Testando conexões com a API {url}...")

for modelo in modelos:
    payload = {
        "model": modelo,
        "messages": [{"role": "user", "content": "Olá, responda apenas 'OK' se receber esta mensagem."}],
        "temperature": 0.5
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"Modelo [{modelo}]: Status {r.status_code}")
        if r.status_code == 200:
            print(f" -> Resposta: {r.json()['choices'][0]['message']['content'].strip()}")
            # Se funcionar, avisa qual modelo funcionou
            break
        else:
            print(f" -> Detalhes: {r.text[:200]}")
    except Exception as e:
        print(f"Erro no modelo [{modelo}]: {e}")
