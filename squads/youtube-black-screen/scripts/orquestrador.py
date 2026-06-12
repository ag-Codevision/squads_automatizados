import os
import subprocess
import sys
import datetime
import re
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# O GitHub Actions vai injetar essas senhas com segurança
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("[ERRO] SUPABASE_URL ou SUPABASE_KEY não encontrados nas variáveis de ambiente.")
    sys.exit(1)

supabase: Client = create_client(url, key)

def extrair_titulo_do_arquivo(run_dir):
    path = os.path.join(run_dir, 'roteiro-e-metadados.md')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(r'(?i)titulo:\s*"(.*?)"', content)
        if match:
            return match.group(1).strip()
    return None

def ler_roteiro_do_arquivo(run_dir):
    path = os.path.join(run_dir, 'roteiro-e-metadados.md')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def main():
    print("🔍 [Orquestrador YTBS] Iniciando busca de episódios para YouTube Black Screen...")
    
    # Obtém a data/hora atual em UTC ISO String
    now_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    # Atualiza o timestamp do cron no banco para o squad youtube-black-screen
    try:
        settings_res = supabase.table('squad_settings').select('*').eq('squad', 'youtube-black-screen').limit(1).execute()
        if settings_res.data:
            settings_id = settings_res.data[0]['id']
            supabase.table('squad_settings').update({'last_cron_run': now_utc}).eq('id', settings_id).execute()
            print(f"⏰ Timestamp do Cron atualizado: {now_utc}")
    except Exception as e:
        print(f"⚠️ Erro ao atualizar timestamp do cron: {e}")
        
    # Busca apenas 1 episódio pendente do squad 'youtube-black-screen'
    response = supabase.table('episodes_queue') \
        .select('*') \
        .eq('status', 'pending') \
        .eq('squad', 'youtube-black-screen') \
        .or_(f"schedule_time.lte.{now_utc},schedule_time.is.null") \
        .order('created_at') \
        .limit(1) \
        .execute()
        
    episodios = response.data
    
    if not episodios:
        print("💤 Nenhum episódio agendado para YouTube Black Screen. O robô voltará a dormir.")
        return
        
    episodio = episodios[0]
    id_ep = episodio['id']
    tema = episodio['topic']
    
    print(f"🚀 Iniciando produção do Vídeo [{id_ep}] - Tema: {tema}")
    
    # Trava o episódio na fila (muda para processing)
    supabase.table('episodes_queue').update({'status': 'processing'}).eq('id', id_ep).execute()
    
    # Carrega configurações dinâmicas do Supabase
    print("⚙️ Carregando configurações dinâmicas...")
    try:
        settings_res = supabase.table('squad_settings').select('*').eq('squad', 'youtube-black-screen').limit(1).execute()
        settings = settings_res.data[0] if settings_res.data else {}
    except Exception as e:
        print(f"⚠️ Erro ao carregar configurações: {e}")
        settings = {}

    omni_model = settings.get('omni_model', 'g')
    
    # Cria ambiente clonado do sistema e injeta as variáveis
    process_env = os.environ.copy()
    process_env['OMNI_MODEL'] = omni_model
    
    # Cria a pasta de run baseada na data atual formatada: YY-MM-DD-HH-MM
    run_id = datetime.datetime.now().strftime("%y-%m-%d-%H-%M")
    run_dir = os.path.join("output", run_id, "v1")
    os.makedirs(run_dir, exist_ok=True)
    
    try:
        # A Esteira de Produção
        # 1. Gerar Roteiro
        print("\n▶️ Executando módulo: scripts/gerar_roteiro.py")
        subprocess.run([sys.executable, "scripts/gerar_roteiro.py", tema, run_dir], env=process_env, check=True)
        
        # Sincroniza metadados com o Supabase
        try:
            titulo_real = extrair_titulo_do_arquivo(run_dir)
            roteiro_texto = ler_roteiro_do_arquivo(run_dir)
            
            update_data = {}
            if titulo_real:
                update_data['topic'] = titulo_real
                print(f"📝 Título extraído: {titulo_real}")
            if roteiro_texto:
                update_data['script_text'] = roteiro_texto
                print(f"📝 Roteiro carregado ({len(roteiro_texto)} caracteres)")
                
            if update_data:
                supabase.table('episodes_queue').update(update_data).eq('id', id_ep).execute()
        except Exception as ex_update:
            print(f"⚠️ Erro ao atualizar metadados no Supabase: {ex_update}")
            
        # 2. Baixar Fundo
        print("\n▶️ Executando módulo: obter-fundo.js")
        subprocess.run(["node", "agents/paulo-publicador/obter-fundo.js", run_dir], check=True)
        
        # 3. Renderizar Vídeo
        print("\n▶️ Executando módulo: scripts/gerar_video.py")
        subprocess.run([sys.executable, "scripts/gerar_video.py", run_dir], env=process_env, check=True)
        
        # 4. Enviar para YouTube (API Oficial v3)
        print("\n▶️ Executando módulo: scripts/upload_youtube.py")
        cmd_upload = [sys.executable, "scripts/upload_youtube.py", os.path.join(run_dir, "video_final_10h.mp4")]
        subprocess.run(cmd_upload, check=True)
            
        # Sucesso! Marca como completo
        supabase.table('episodes_queue').update({'status': 'completed'}).eq('id', id_ep).execute()
        print(f"\n🎉 Vídeo [{id_ep}] finalizado e publicado com sucesso!")
        
    except Exception as e:
        print(f"\n❌ FALHA CRÍTICA na esteira de produção: {e}")
        supabase.table('episodes_queue').update({'status': 'failed', 'error_message': str(e)}).eq('id', id_ep).execute()

if __name__ == "__main__":
    main()
