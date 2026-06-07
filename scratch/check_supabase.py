import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv("squads/conexao_artificial/.env")

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("SUPABASE_URL ou SUPABASE_KEY não configurados no .env")
    exit(1)

supabase: Client = create_client(url, key)

response = supabase.table('episodes_queue').select('*').order('created_at', desc=True).limit(5).execute()
for ep in response.data:
    script_len = len(ep.get('script_text') or '')
    print(f"ID: {ep['id']} | Topic: {ep['topic']} | Status: {ep['status']} | Script Len: {script_len} | Error: {ep.get('error_message')}")
