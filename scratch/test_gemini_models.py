import os
import requests
from dotenv import load_dotenv

# Carrega o .env
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "squads", "conexao_artificial", ".env")
load_dotenv(dotenv_path)

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("GEMINI_API_KEY nao encontrada no .env!")
    exit(1)

print(f"Testando chave: {api_key[:10]}...")

modelos = ["gemini-1.5-flash", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]
versoes = ["v1beta", "v1"]

for versao in versoes:
    for modelo in modelos:
        url = f"https://generativelanguage.googleapis.com/{versao}/models/{modelo}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": "Diga apenas 'OK'."}]}]
        }
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=10)
            print(f"[{versao}] Modelo [{modelo}]: Status {r.status_code}")
            if r.status_code == 200:
                print(f" -> Resposta: {r.json()['candidates'][0]['content']['parts'][0]['text'].strip()}")
                print(f" -> SUCESSO! A URL funcional é: {url.replace(api_key, 'SUA_CHAVE')}")
                exit(0)
            else:
                print(f" -> Detalhes: {r.text[:200]}")
        except Exception as e:
            print(f" -> Erro no teste: {e}")
