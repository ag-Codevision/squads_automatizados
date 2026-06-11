import os
import subprocess
import sys
import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("[ERRO] SUPABASE_URL ou SUPABASE_KEY não encontrados nas variáveis de ambiente.")
    sys.exit(1)

supabase: Client = create_client(url, key)

def main():
    print("🔍 [Orquestrador Geral] Buscando o próximo episódio agendado na fila do Supabase...")
    
    now_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    # Busca o próximo episódio pendente na fila independente de qual squad seja
    response = supabase.table('episodes_queue') \
        .select('*') \
        .eq('status', 'pending') \
        .or_(f"schedule_time.lte.{now_utc},schedule_time.is.null") \
        .order('created_at') \
        .limit(1) \
        .execute()
        
    episodios = response.data
    
    if not episodios:
        print("💤 Nenhum episódio agendado na fila de produção global. O robô voltará a dormir.")
        return
        
    episodio = episodios[0]
    squad = episodio.get('squad') or 'conexao_artificial'
    id_ep = episodio['id']
    
    print(f"📌 Encontrado episódio [{id_ep}] para o Squad: '{squad}'")
    
    # Direciona a execução para o orquestrador correto na pasta do squad
    squad_dir = os.path.join("squads", squad)
    if not os.path.exists(squad_dir):
        print(f"[ERRO] Diretório do squad '{squad}' não existe em: {squad_dir}")
        sys.exit(1)
        
    cmd = [sys.executable, "scripts/orquestrador.py"]
    print(f"▶️ Executando orquestrador do squad em: {squad_dir}")
    
    try:
        subprocess.run(cmd, cwd=squad_dir, check=True)
        print(f"[SUCESSO] Orquestrador do squad '{squad}' finalizou a execução.")
    except subprocess.CalledProcessError as e:
        print(f"[ERRO] Falha ao executar o orquestrador do squad '{squad}': {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
