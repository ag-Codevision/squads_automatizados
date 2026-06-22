import os
import sys
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Scopes exigem permissão de upload
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
CLIENT_SECRET_FILE = os.path.join(SCRIPTS_DIR, "client_secret.json")
TOKEN_FILE = os.path.join(SCRIPTS_DIR, "token.json")

VIDEO_FILE = os.path.join(OUTPUT_DIR, "podcast_final.mp4")
METADATA_FILE = os.path.join(OUTPUT_DIR, "youtube_metadata.txt")

def get_authenticated_service():
    is_github = os.environ.get("GITHUB_ACTIONS") == "true"
    is_vps = os.path.exists("/root/squads_automatizados") or os.environ.get("PRODUCTION") == "true" or os.environ.get("IS_VPS") == "true"

    if not os.path.exists(CLIENT_SECRET_FILE):
        msg = f"[ERRO] O arquivo {CLIENT_SECRET_FILE} não foi encontrado."
        if is_github:
            print(f"{msg} Pulando upload no GitHub Actions.")
            return None
        else:
            print(msg)
            sys.exit(1)

    creds = None
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception as e_load:
            print(f"[AVISO] Falha ao carregar {TOKEN_FILE}: {e_load}")

    # Se credenciais forem nulas ou inválidas, tentamos renovar
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                print("Tentando renovar token do YouTube expirado...")
                creds.refresh(Request())
                with open(TOKEN_FILE, "w") as token:
                    token.write(creds.to_json())
                print("[OK] Token renovado com sucesso.")
            except Exception as ref_err:
                print(f"[AVISO] Falha ao renovar credenciais do YouTube: {ref_err}")
                creds = None
        else:
            creds = None

    # Se mesmo após a tentativa de renovação continuarmos sem credenciais válidas:
    if not creds or not creds.valid:
        if is_github:
            print("[AVISO] Autenticação do YouTube requer login interativo. Pulando no GitHub Actions.")
            return None
        elif is_vps:
            print("[ERRO] O token.json é inválido ou não foi encontrado e estamos rodando na VPS (Headless).")
            print("Por favor, execute o script localmente no seu computador para gerar o token.json e envie-o para a VPS.")
            sys.exit(1)
        else:
            print("[INFO] Iniciando fluxo de autenticação interativa no navegador local para obter credenciais do YouTube...")
            try:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
                with open(TOKEN_FILE, "w") as token:
                    token.write(creds.to_json())
                print(f"[OK] Novo token.json gerado com sucesso e salvo em {TOKEN_FILE}!")
            except Exception as auth_err:
                print(f"[ERRO] Falha na autenticação interativa local: {auth_err}")
                sys.exit(1)

    return build("youtube", "v3", credentials=creds)

def parse_metadata():
    if not os.path.exists(METADATA_FILE):
        return "Conexão Artificial Podcast", "Mais um episódio de tecnologia e IA.", []
        
    title = ""
    description = []
    tags = []
    
    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    current_section = None
    for line in lines:
        stripped = line.strip()
        if line.startswith("Título:"):
            title = line.replace("Título:", "").strip()
        elif line.startswith("Descrição:"):
            current_section = "desc"
        elif line.startswith("Tags:"):
            current_section = "tags"
        elif current_section == "desc":
            if not line.startswith("Assuntos abordados:"):
                description.append(line.rstrip("\n"))
            else:
                description.append(line.rstrip("\n"))
        elif current_section == "tags" and stripped:
            tags.extend([t.strip().replace("#", "") for t in stripped.split()])

    desc_text = "\n".join(description).strip()
    return title, desc_text, tags

def upload_video(youtube):
    if not os.path.exists(VIDEO_FILE):
        print(f"[ERRO] Vídeo não encontrado: {VIDEO_FILE}")
        sys.exit(1)

    title, description, tags = parse_metadata()

    print(f"Preparando upload...\nTítulo: {title}\nTags: {tags}")

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags,
            "categoryId": "28" # Science & Technology
        },
        "status": {
            "privacyStatus": "public", # Conforme solicitado pelo usuário
            "selfDeclaredMadeForKids": False
        }
    }

    media_body = MediaFileUpload(VIDEO_FILE, chunksize=-1, resumable=True)

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media_body
    )

    response = None
    print("Iniciando upload para o YouTube...")
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Progresso do upload: {int(status.progress() * 100)}%")

    video_id = response.get('id')
    print(f"\nUpload concluído! Vídeo ID: {video_id}")
    print(f"Assista em: https://youtu.be/{video_id}")
    # Imprime marcador para o orquestrador capturar a URL
    print(f"YOUTUBE_URL=https://youtu.be/{video_id}")
    return video_id

if __name__ == "__main__":
    youtube = get_authenticated_service()
    if youtube:
        upload_video(youtube)
    else:
        print("[ERRO] Autenticação do YouTube não estabelecida. O upload NÃO foi realizado.")
        sys.exit(1)
