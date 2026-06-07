import os
import requests
from dotenv import load_dotenv

# Carrega do .env da squad
load_dotenv("squads/conexao_artificial/.env")

# Carrega do .env.local do dashboard para obter o GITHUB_PAT
dashboard_env = {}
with open("opensquad-dashboard/.env.local", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            dashboard_env[k.strip()] = v.strip()

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
github_pat = dashboard_env.get("GITHUB_PAT")

if not supabase_url or not supabase_key or not github_pat:
    print(f"Erro: Faltando chaves. Supabase URL: {bool(supabase_url)}, Supabase Key: {bool(supabase_key)}, Github PAT: {bool(github_pat)}")
    exit(1)

# 1. Inserir episódio "Aleatório (Notícias do dia)" na fila
print("[TESTE] Inserindo novo episodio pendente no Supabase...")
headers_sb = {
    "apikey": supabase_key,
    "Authorization": f"Bearer {supabase_key}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

payload_sb = {
    "topic": "Aleatório (Notícias do dia)",
    "status": "pending",
    "voice_ton": "google/gemini-3.1-flash-tts",
    "voice_bia": "google/gemini-3.1-flash-tts"
}

url_sb = f"{supabase_url}/rest/v1/episodes_queue"
res_sb = requests.post(url_sb, json=payload_sb, headers=headers_sb)

if res_sb.status_code == 201:
    ep_data = res_sb.json()[0]
    ep_id = ep_data["id"]
    print(f"[SUCESSO] Episodio inserido com sucesso! ID: {ep_id}")
else:
    print(f"[ERRO] Erro ao inserir episodio: {res_sb.status_code} - {res_sb.text}")
    exit(1)

# 2. Disparar a Action do GitHub
print("[TESTE] Disparando o workflow no GitHub Actions...")
url_gh = "https://api.github.com/repos/ag-Codevision/conexao-artificial-cloud/actions/workflows/robocast.yml/dispatches"
headers_gh = {
    "Authorization": f"Bearer {github_pat}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "Content-Type": "application/json",
    "User-Agent": "OpenSquad-Test-Trigger"
}

payload_gh = {
    "ref": "main"
}

res_gh = requests.post(url_gh, json=payload_gh, headers=headers_gh)

if res_gh.status_code == 204:
    print("[SUCESSO] Workflow disparado com sucesso no GitHub Actions!")
    print(f"Monitore o status no Supabase para o ID: {ep_id}")
else:
    print(f"[ERRO] Erro ao disparar workflow: {res_gh.status_code} - {res_gh.text}")
