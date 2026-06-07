import os
import subprocess

# Caminho base do squad (um nível acima da pasta dos scripts)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Se houver um Token do GitHub configurado nos Secrets, autentica a URL
GH_PAT = os.environ.get("GH_PAT", "")
if GH_PAT:
    REPO_URL = f"https://{GH_PAT}@github.com/ag-Codevision/podcast-conexao-artificial.git"
else:
    REPO_URL = "https://github.com/ag-Codevision/podcast-conexao-artificial.git"

def run_cmd(cmd_list):
    print(f"Running: {' '.join(cmd_list)}")
    result = subprocess.run(cmd_list, cwd=OUTPUT_DIR, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error executing '{' '.join(cmd_list)}':\n{result.stderr}")
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
    if not status.stdout.strip():
        print("No changes to commit. Everything is up to date.")
        return

    # Configura identidade temporária do Git localmente no repo output se não estiver global
    # Isso evita erro se as credenciais globais não estiverem configuradas
    run_cmd(["git", "config", "user.name", "OpenSquad Cloud Bot"])
    run_cmd(["git", "config", "user.email", "bot@opensquad.com"])

    run_cmd(["git", "commit", "-m", "Upload automático: Novo episódio do Conexão Artificial"])

    print("Pushing to GitHub...")
    run_cmd(["git", "push", "-u", "origin", "main"])
    print("Upload concluído com sucesso!")

if __name__ == "__main__":
    upload_to_github()
