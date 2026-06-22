import os
import subprocess
import sys
import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# O GitHub Actions vai injetar essas senhas com segurança
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("[ERRO] SUPABASE_URL ou SUPABASE_KEY nao encontrados nas variaveis de ambiente.")
    sys.exit(1)

supabase: Client = create_client(url, key)

def main():
    print("🔍 [Orquestrador] Acordando e buscando episódios na fila do Supabase...")
    
    # Obtém a data/hora atual em UTC ISO String para comparação
    now_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    # Atualiza o timestamp do cron no banco de dados para monitoramento no dashboard
    try:
        settings_res = supabase.table('squad_settings').select('*').limit(1).execute()
        if settings_res.data:
            settings_id = settings_res.data[0]['id']
            supabase.table('squad_settings').update({'last_cron_run': now_utc}).eq('id', settings_id).execute()
            print(f"⏰ Timestamp do Cron atualizado no Supabase: {now_utc}")
    except Exception as e:
        print(f"⚠️ Erro ao atualizar timestamp do cron no Supabase: {e}")
        
    # Busca apenas 1 episódio pendente do squad 'conexao_artificial' que já esteja no horário de postagem ou com agendamento nulo (imediato)
    response = supabase.table('episodes_queue') \
        .select('*') \
        .eq('status', 'pending') \
        .eq('squad', 'conexao_artificial') \
        .or_(f"schedule_time.lte.{now_utc},schedule_time.is.null") \
        .order('created_at') \
        .limit(1) \
        .execute()
    
    episodios = response.data
    
    if not episodios:
        print("💤 Nenhum episódio agendado na fila. O robô voltará a dormir.")
        return
        
    episodio = episodios[0]
    id_ep = episodio['id']
    tema = episodio['topic']
    
    print(f"🚀 Iniciando produção do Episódio [{id_ep}] - Tema: {tema}")
    
    # Trava o episódio na fila (muda para processing) para não repetir
    supabase.table('episodes_queue').update({'status': 'processing'}).eq('id', id_ep).execute()
    
    # Carrega configurações dinâmicas de cérebro e vozes do Supabase
    print("⚙️ Carregando configurações dinâmicas de Cérebro & Vozes...")
    try:
        settings_res = supabase.table('squad_settings').select('*').limit(1).execute()
        settings = settings_res.data[0] if settings_res.data else {}
    except Exception as e:
        print(f"⚠️ Erro ao carregar configurações (usando padrões): {e}")
        settings = {}

    omni_model = settings.get('omni_model', 'g')
    voice_ton = settings.get('voice_ton', '4za2kOXGgUd57HRSQ1fn')
    voice_bia = settings.get('voice_bia', '7iqXtOF3wl3pomwXFY7G')

    print(f"   🧠 Modelo IA (Cérebro): {omni_model}")
    print(f"   🎙️ Voz Ton: {voice_ton}")
    print(f"   🎙️ Voz Bia: {voice_bia}")

    # Cria ambiente clonado do sistema e injeta as variáveis
    process_env = os.environ.copy()
    process_env['OMNI_MODEL'] = omni_model
    process_env['VOICE_TON'] = voice_ton
    process_env['VOICE_BIA'] = voice_bia
    
    def extrair_titulo_do_arquivo():
        import re
        path = os.path.join('output', 'youtube_metadata.txt')
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            match = re.search(r'(?i)T[ií]tulo:\s*(?:\[(.*?)\]|(.*?))(?:\n|$)', content)
            if match:
                titulo = match.group(1) or match.group(2)
                return titulo.strip()
        return None

    def ler_roteiro_do_arquivo():
        path = os.path.join('output', 'roteiro_episodio.txt')
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        return None

    try:
        # A Esteira de Produção
        # Usamos sys.executable para garantir que usa o python correto
        scripts = [
            [sys.executable, "scripts/gerar_roteiro.py", tema],
            [sys.executable, "scripts/gerar_audio.py"],
            [sys.executable, "scripts/gerar_video.py"],
            [sys.executable, "scripts/upload_youtube.py"],
            [sys.executable, "scripts/organizar_episodio.py"],
            [sys.executable, "scripts/gerar_rss_spotify.py"],
            [sys.executable, "scripts/upload_github.py"]
        ]
        
        for cmd in scripts:
            print(f"\n▶️ Executando módulo: {cmd[1]}", flush=True)
            # Passa a env com as configurações dinâmicas para os scripts
            result = subprocess.run(cmd, env=process_env, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"--- STDOUT DO MÓDULO {cmd[1]} ---", flush=True)
                print(result.stdout, flush=True)
                print(f"--- STDERR DO MÓDULO {cmd[1]} ---", flush=True)
                print(result.stderr, flush=True)
                raise subprocess.CalledProcessError(result.returncode, cmd, output=result.stdout, stderr=result.stderr)
            
            print(result.stdout, flush=True)

            # Se for a geração do roteiro, atualiza o título e o roteiro no Supabase imediatamente
            if "gerar_roteiro.py" in cmd[1]:
                try:
                    titulo_real = extrair_titulo_do_arquivo()
                    roteiro_texto = ler_roteiro_do_arquivo()
                    
                    update_data = {}
                    if titulo_real:
                        update_data['topic'] = titulo_real
                        print(f"📝 Título do episódio extraído: {titulo_real}")
                    if roteiro_texto:
                        update_data['script_text'] = roteiro_texto
                        print(f"📝 Roteiro do episódio carregado ({len(roteiro_texto)} caracteres)")
                        
                    if update_data:
                        print("💾 Sincronizando metadados do episódio com o Supabase...")
                        supabase.table('episodes_queue').update(update_data).eq('id', id_ep).execute()
                        print("[OK] Supabase atualizado com sucesso!")
                except Exception as ex_update:
                    print(f"⚠️ Erro ao atualizar metadados no Supabase: {ex_update}")
            
        # Sucesso! Marca como completo
        supabase.table('episodes_queue').update({'status': 'completed'}).eq('id', id_ep).execute()
        print(f"\n🎉 Episódio [{id_ep}] finalizado e publicado com sucesso!")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ FALHA CRÍTICA na esteira de produção: {e}")
        # Marca como failed no painel para o usuário ver
        supabase.table('episodes_queue').update({'status': 'failed', 'error_message': str(e)}).eq('id', id_ep).execute()

if __name__ == "__main__":
    main()
