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
    if not os.path.exists(CLIENT_SECRET_FILE):
        print(f"[AVISO] O arquivo {CLIENT_SECRET_FILE} não foi encontrado. Pulando upload para o YouTube.")
        return None

    # Se estiver rodando no GitHub Actions e o token.json não estiver presente,
    # pulamos o upload para evitar travar o console headless.
    if os.environ.get("GITHUB_ACTIONS") == "true" and not os.path.exists(TOKEN_FILE):
        print("[AVISO] Ambiente headless GitHub Actions sem token.json. Pulando upload do YouTube para evitar travamentos.")
        return None

    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as ref_err:
                print(f"[AVISO] Falha ao renovar credenciais do YouTube: {ref_err}. Pulando upload.")
                return None
        else:
            if os.environ.get("GITHUB_ACTIONS") == "true":
                print("[AVISO] Autenticação do YouTube requer login interativo. Pulando na nuvem.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

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

    print(f"\nUpload concluído! Vídeo ID: {response.get('id')}")
    print(f"Assista em: https://youtu.be/{response.get('id')}")

if __name__ == "__main__":
    youtube = get_authenticated_service()
    if youtube:
        upload_video(youtube)
    else:
        print("[INFO] Autenticação do YouTube não estabelecida. O upload foi pulado de forma segura.")
