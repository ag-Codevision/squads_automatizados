import os
import subprocess
import shutil
import tempfile
from dotenv import load_dotenv

# Caminho base do squad (um nível acima da pasta dos scripts)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Carrega as variáveis de ambiente do arquivo .env local do squad
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Se houver um Token do GitHub configurado nos Secrets, autentica a URL
GH_PAT = os.environ.get("GH_PAT", "")
if GH_PAT:
    REPO_URL = f"https://{GH_PAT}@github.com/ag-Codevision/podcast-conexao-artificial.git"
else:
    REPO_URL = "https://github.com/ag-Codevision/podcast-conexao-artificial.git"

# Arquivos grandes que NÃO devem ser enviados ao GitHub (limite de 100 MB)
EXTENSOES_IGNORADAS = {'.mp4', '.wav', '.ogg', '.avi', '.mkv', '.flac', '.aac'}

def run_cmd(cmd_list, cwd=None, ignore_error=False):
    """Executa um comando e retorna True se teve sucesso."""
    print(f"Running: {' '.join(cmd_list)}")
    result = subprocess.run(cmd_list, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        error_msg = f"Error executing '{' '.join(cmd_list)}':\n{result.stderr}"
        print(error_msg)
        if not ignore_error:
            raise RuntimeError(error_msg)
    else:
        if result.stdout.strip():
            print(result.stdout)
    return result.returncode == 0

def copiar_arquivos_seguros(origem, destino):
    """Copia arquivos do output para o repo, ignorando arquivos grandes."""
    arquivos_copiados = 0
    arquivos_ignorados = 0
    
    for root, dirs, files in os.walk(origem):
        # Ignora a pasta .git do output (se existir)
        dirs[:] = [d for d in dirs if d != '.git']
        
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            src = os.path.join(root, f)
            
            # Pula arquivos com extensões grandes
            if ext in EXTENSOES_IGNORADAS:
                tamanho_mb = os.path.getsize(src) / (1024 * 1024)
                print(f"  [SKIP] {f} ({tamanho_mb:.1f} MB) - extensão {ext} ignorada")
                arquivos_ignorados += 1
                continue
            
            # Calcula o caminho relativo e copia para o destino
            rel_path = os.path.relpath(src, origem)
            dst = os.path.join(destino, rel_path)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            arquivos_copiados += 1
    
    print(f"  [INFO] {arquivos_copiados} arquivos copiados, {arquivos_ignorados} ignorados (grandes demais)")
    return arquivos_copiados

def upload_to_github():
    if not os.path.exists(OUTPUT_DIR):
        print(f"[ERRO] Diretório de output não existe: {OUTPUT_DIR}")
        raise RuntimeError(f"Diretório de output não existe: {OUTPUT_DIR}")

    # Estratégia: Clona o repo existente, copia os novos arquivos, e faz push
    # Isso evita conflitos de histórico e garante que o push funcione
    
    clone_dir = tempfile.mkdtemp(prefix="opensquad_gh_")
    print(f"Clonando repositório de destino em: {clone_dir}")
    
    try:
        # 1. Clona o repositório existente
        run_cmd(["git", "clone", "--depth", "1", REPO_URL, clone_dir])
        
        # 2. Configura identidade do bot
        run_cmd(["git", "config", "user.name", "OpenSquad Cloud Bot"], cwd=clone_dir)
        run_cmd(["git", "config", "user.email", "bot@opensquad.com"], cwd=clone_dir)
        
        # 3. Copia apenas arquivos seguros (sem .mp4, .wav, etc.)
        print("Copiando arquivos do episódio para o repositório...")
        qtd = copiar_arquivos_seguros(OUTPUT_DIR, clone_dir)
        
        if qtd == 0:
            print("[AVISO] Nenhum arquivo novo para copiar. Nada a fazer.")
            return
        
        # 4. Adiciona e comita
        run_cmd(["git", "add", "."], cwd=clone_dir)
        
        # Verifica se há mudanças
        status = subprocess.run(["git", "status", "--porcelain"], cwd=clone_dir, capture_output=True, text=True)
        if not status.stdout.strip():
            print("Nenhuma alteração detectada. Pulando push.")
            return
            
        run_cmd(["git", "commit", "-m", "Upload automático: Novo episódio do Conexão Artificial"], cwd=clone_dir)
        
        # 5. Push (deve funcionar sem conflitos pois clonamos o repo)
        print("Pushing to GitHub...")
        push_ok = run_cmd(["git", "push", "origin", "main"], cwd=clone_dir, ignore_error=True)
        
        if not push_ok:
            raise RuntimeError("Falha crítica: não foi possível enviar os arquivos para o GitHub Pages.")
        
        print("Upload concluído com sucesso!")
        
    finally:
        # Limpa o diretório temporário
        try:
            shutil.rmtree(clone_dir)
            print(f"Diretório temporário removido: {clone_dir}")
        except Exception as e:
            print(f"[AVISO] Não foi possível remover o diretório temporário: {e}")

if __name__ == "__main__":
    upload_to_github()
