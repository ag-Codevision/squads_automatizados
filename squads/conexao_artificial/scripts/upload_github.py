import os
import subprocess
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

def run_cmd(cmd_list, ignore_error=False):
    print(f"Running: {' '.join(cmd_list)}")
    result = subprocess.run(cmd_list, cwd=OUTPUT_DIR, capture_output=True, text=True)
    if result.returncode != 0:
        error_msg = f"Error executing '{' '.join(cmd_list)}':\n{result.stderr}"
        print(error_msg)
        if not ignore_error:
            raise RuntimeError(error_msg)
    else:
        print(result.stdout)
    return result.returncode == 0

def upload_to_github():
    if not os.path.exists(OUTPUT_DIR):
        print(f"Output directory does not exist: {OUTPUT_DIR}")
        return

    # Inicializa o repositório git caso ainda não exista na pasta output
    if not os.path.exists(os.path.join(OUTPUT_DIR, ".git")):
        print("Initializing git repository...")
        run_cmd(["git", "init"])
        run_cmd(["git", "remote", "add", "origin", REPO_URL])
        run_cmd(["git", "branch", "-M", "main"])
    else:
        # Se o repositório já existir, garante que a URL está atualizada com o PAT atual
        run_cmd(["git", "remote", "set-url", "origin", REPO_URL])

    print("Staging files...")
    run_cmd(["git", "add", "."])

    print("Committing files...")
    # Verifica se há alterações para comitar
    status = subprocess.run(["git", "status", "--porcelain"], cwd=OUTPUT_DIR, capture_output=True, text=True)
    if status.stdout.strip():
        # Configura identidade temporária do Git localmente no repo output se não estiver global
        # Isso evita erro se as credenciais globais não estiverem configuradas
        run_cmd(["git", "config", "user.name", "OpenSquad Cloud Bot"], ignore_error=True)
        run_cmd(["git", "config", "user.email", "bot@opensquad.com"], ignore_error=True)

        run_cmd(["git", "commit", "-m", "Upload automático: Novo episódio do Conexão Artificial"])
    else:
        print("No new changes to commit. Proceeding to push local commits...")

    print("Sincronizando com o repositório remoto...")
    # Puxa as alterações remotas antes de enviar para evitar rejeição
    pull_ok = run_cmd(["git", "pull", "--rebase", "origin", "main"], ignore_error=True)

    print("Pushing to GitHub...")
    push_ok = run_cmd(["git", "push", "-u", "origin", "main"], ignore_error=True)

    if not push_ok:
        print("[AVISO] Push normal falhou. Tentando force push (repositório é unidirecional do bot)...")
        push_ok = run_cmd(["git", "push", "--force", "-u", "origin", "main"], ignore_error=True)

    if not push_ok:
        raise RuntimeError("Falha crítica: não foi possível enviar os arquivos para o GitHub Pages.")

    print("Upload concluído com sucesso!")

if __name__ == "__main__":
    upload_to_github()
