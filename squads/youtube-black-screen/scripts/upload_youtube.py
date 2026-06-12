import os
import sys
import re
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Scopes exigem permissão de upload
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # squads/youtube-black-screen
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
CLIENT_SECRET_FILE = os.path.join(SCRIPTS_DIR, "client_secret.json")
TOKEN_FILE = os.path.join(SCRIPTS_DIR, "token.json")

def get_authenticated_service():
    is_github = os.environ.get("GITHUB_ACTIONS") == "true"
    is_vps = os.path.exists("/root/squads_automatizados") or os.environ.get("PRODUCTION") == "true" or os.environ.get("IS_VPS") == "true"

    if not os.path.exists(CLIENT_SECRET_FILE):
        msg = f"[ERRO] O arquivo client_secret.json não foi encontrado em {CLIENT_SECRET_FILE}."
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

def parse_yaml_metadata(run_dir):
    path = os.path.join(run_dir, 'roteiro-e-metadados.md')
    fallback_title = "Som de Chuva Suave para Dormir"
    fallback_desc = "Vídeo de sono de 10 horas de tela preta com som de chuva relaxante."
    fallback_tags = ["chuva", "dormir", "relaxar", "tela preta"]
    
    if not os.path.exists(path):
        return fallback_title, fallback_desc, fallback_tags
        
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extrai a seção entre ```yaml e ```
        match_yaml = re.search(r'```yaml\s*(.*?)\s*```', content, re.DOTALL)
        yaml_text = match_yaml.group(1) if match_yaml else content
        
        # Extrai o título
        match_title = re.search(r'(?i)titulo:\s*"(.*?)"', yaml_text)
        if not match_title:
            match_title = re.search(r'(?i)titulo:\s*(.*)', yaml_text)
        title = match_title.group(1).strip().strip('"').strip("'") if match_title else fallback_title
        
        # Extrai as tags
        match_tags = re.search(r'(?i)tags:\s*"(.*?)"', yaml_text)
        if not match_tags:
            match_tags = re.search(r'(?i)tags:\s*(.*)', yaml_text)
        tags_str = match_tags.group(1).strip().strip('"').strip("'") if match_tags else "chuva, dormir, relaxar, sono"
        tags = [t.strip() for t in tags_str.split(',') if t.strip()]
        
        # Extrai a descrição
        match_desc = re.search(r'(?i)descricao:\s*\|\s*\n(.*?)(\n\s*tags:|\n\s*```|\Z)', yaml_text, re.DOTALL)
        if match_desc:
            description = match_desc.group(1)
            lines = description.splitlines()
            cleaned_lines = []
            for line in lines:
                if line.startswith("      "):
                    cleaned_lines.append(line[6:])
                elif line.startswith("    "):
                    cleaned_lines.append(line[4:])
                elif line.startswith("  "):
                    cleaned_lines.append(line[2:])
                else:
                    cleaned_lines.append(line)
            desc_text = "\n".join(cleaned_lines).strip()
        else:
            match_desc_simple = re.search(r'(?i)descricao:\s*"(.*?)"', yaml_text, re.DOTALL)
            desc_text = match_desc_simple.group(1).strip() if match_desc_simple else fallback_desc
            
        return title, desc_text, tags
    except Exception as e:
        print(f"[AVISO] Erro ao fazer parsing de metadados: {e}. Usando fallbacks.")
        return fallback_title, fallback_desc, fallback_tags

def upload_video(youtube, video_path):
    if not os.path.exists(video_path):
        print(f"[ERRO] Vídeo não encontrado: {video_path}")
        sys.exit(1)

    run_dir = os.path.dirname(video_path)
    title, description, tags = parse_yaml_metadata(run_dir)

    print(f"Preparando upload...\nTítulo: {title}\nTags: {tags}")

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags,
            "categoryId": "10" # Music (comum para som de dormir/relaxar) ou "28" (Science & Technology)
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }

    media_body = MediaFileUpload(video_path, chunksize=-1, resumable=True)

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
    if len(sys.argv) < 2:
        print("[ERRO] É necessário passar o caminho do arquivo de vídeo por parâmetro.")
        sys.exit(1)
        
    video_path = sys.argv[1]
    
    youtube = get_authenticated_service()
    if youtube:
        upload_video(youtube, video_path)
    else:
        print("[INFO] Autenticação do YouTube não estabelecida ou pulada no Actions.")
