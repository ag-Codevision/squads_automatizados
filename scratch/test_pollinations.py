import requests

url = "https://text.pollinations.ai/"
modelos = ["openai", "mistral", "llama", "qwen", "qwen-coder", "mistral-large"]

print("Testando modelos na API da Pollinations...")

for modelo in modelos:
    payload = {
        "messages": [
            {"role": "system", "content": "Seja breve."},
            {"role": "user", "content": "Olá, responda apenas 'OK' se receber esta mensagem."}
        ],
        "model": modelo
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        print(f"Modelo [{modelo}]: Status {r.status_code}")
        if r.status_code == 200:
            print(f" -> Resposta: {r.text.strip()}")
            break
        else:
            print(f" -> Detalhes: {r.text[:200]}")
    except Exception as e:
        print(f"Erro no modelo [{modelo}]: {e}")
