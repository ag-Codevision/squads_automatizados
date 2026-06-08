import os
import sys
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
CLIENT_SECRET_FILE = os.path.join(SCRIPTS_DIR, "client_secret.json")
TOKEN_FILE = os.path.join(SCRIPTS_DIR, "token.json")

def autenticar():
    if not os.path.exists(CLIENT_SECRET_FILE):
        print(f"[ERRO] O arquivo {CLIENT_SECRET_FILE} não foi encontrado.")
        sys.exit(1)

    print("[INFO] Iniciando autenticação do YouTube...")
    creds = None
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            print("[INFO] Token existente carregado.")
        except Exception as e:
            print(f"[AVISO] Falha ao carregar token existente: {e}")

    # Forçar fluxo de login interativo no navegador
    try:
        print("[INFO] Abrindo navegador para login no Google e autorização do canal...")
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token_f:
            token_f.write(creds.to_json())
        print(f"\n[OK] Autenticação realizada com sucesso!")
        print(f"O novo arquivo token.json foi gerado em: {TOKEN_FILE}")
        print("\nPronto! Agora avise o agente no chat para copiar esse novo token para a VPS e concluir o upload.")
    except Exception as e:
        print(f"[ERRO] Falha ao autenticar: {e}")
        sys.exit(1)

if __name__ == "__main__":
    autenticar()
