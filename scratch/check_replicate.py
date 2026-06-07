import os
import requests
from dotenv import load_dotenv

load_dotenv("squads/conexao_artificial/.env")

token = os.environ.get("REPLICATE_API_TOKEN")

if not token:
    print("REPLICATE_API_TOKEN não encontrado no .env")
    exit(1)

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# API do Replicate para listar predições
url = "https://api.replicate.com/v1/predictions"
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    predictions = data.get("results", [])
    print(f"Encontradas {len(predictions)} predições recentes:")
    for pred in predictions[:10]:
        model = pred.get("model")
        status = pred.get("status")
        created_at = pred.get("created_at")
        completed_at = pred.get("completed_at")
        error = pred.get("error")
        # Pega as primeiras palavras da entrada de texto, se houver
        input_data = pred.get("input", {})
        text = input_data.get("text", "")
        text_snippet = text[:40] if text else ""
        print(f"ID: {pred['id']} | Model: {model} | Status: {status} | Text: {text_snippet} | Created: {created_at} | Completed: {completed_at} | Error: {error}")
else:
    print(f"Erro ao consultar API do Replicate: {response.status_code} - {response.text}")
