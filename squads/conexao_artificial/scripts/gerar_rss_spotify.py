import os
import datetime
from email.utils import formatdate
import glob
import html

# Configurações do Podcast
PODCAST_TITLE = "Conexão Artificial"
PODCAST_LINK = "https://conexaoartificial.com"
PODCAST_DESC = "Podcast diário sobre Tecnologia e Inteligência Artificial, apresentado por Ton e Bia."
PODCAST_LANGUAGE = "pt-BR"
PODCAST_AUTHOR = "Ton e Bia"
PODCAST_EMAIL = "meupod.ia@gmail.com"

# URL Base onde os episódios estarão hospedados
# IMPORTANTE: Você precisa hospedar a pasta 'episodios' em um servidor ou GitHub Pages.
# Exemplo: Se usar GitHub Pages, seria "https://seu-usuario.github.io/conexao_artificial/episodios"
BASE_REPO_URL = "https://ag-Codevision.github.io/podcast-conexao-artificial"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
EPISODES_DIR = os.path.join(OUTPUT_DIR, "episodios")
RSS_FILE = os.path.join(OUTPUT_DIR, "rss.xml")

def generate_rss():
    # 1. Clona o repositório remoto para restaurar episódios anteriores no ambiente local
    GH_PAT = os.environ.get("GH_PAT", "")
    if GH_PAT:
        repo_url = f"https://{GH_PAT}@github.com/ag-Codevision/podcast-conexao-artificial.git"
    else:
        repo_url = "https://github.com/ag-Codevision/podcast-conexao-artificial.git"
        
    import tempfile
    import shutil
    import subprocess
    
    clone_dir = tempfile.mkdtemp(prefix="restore_eps_")
    print(f"Restaurando episódios anteriores do repositório remoto: {repo_url}...")
    try:
        # Clona de forma superficial para rapidez
        subprocess.run(["git", "clone", "--depth", "1", repo_url, clone_dir], capture_output=True)
        
        remote_eps_dir = os.path.join(clone_dir, "episodios")
        if os.path.exists(remote_eps_dir):
            if not os.path.exists(EPISODES_DIR):
                os.makedirs(EPISODES_DIR)
                
            for folder in os.listdir(remote_eps_dir):
                src_folder = os.path.join(remote_eps_dir, folder)
                dst_folder = os.path.join(EPISODES_DIR, folder)
                
                # Ignora a pasta duplicada "episodios"
                if os.path.isdir(src_folder) and folder != "episodios":
                    if not os.path.exists(dst_folder):
                        print(f"   [RESTORE] Restaurando episódio anterior: {folder}")
                        shutil.copytree(src_folder, dst_folder)
    except Exception as e:
        print(f"[AVISO] Falha ao restaurar episódios do repositório: {e}")
    finally:
        try:
            shutil.rmtree(clone_dir)
        except:
            pass

    if not os.path.exists(EPISODES_DIR):
        print("Nenhuma pasta de episódios encontrada.")
        return

    rss_items = ""
    
    # Encontra todas as pastas de episódios, ordenadas pela mais recente (com base na data real do nome da pasta)
    def parse_folder_date(folder):
        try:
            date_str = folder.split("__")[0]
            time_str = folder.split("__")[1].split("_")[0]
            return datetime.datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H.%M")
        except:
            return datetime.datetime.min

    folders = sorted(
        [f for f in os.listdir(EPISODES_DIR) if os.path.isdir(os.path.join(EPISODES_DIR, f))],
        key=parse_folder_date,
        reverse=True
    )
    
    for folder in folders:
        folder_path = os.path.join(EPISODES_DIR, folder)
        audio_file = os.path.join(folder_path, "podcast_audio_mixed.mp3")
        if not os.path.exists(audio_file):
            audio_file = os.path.join(folder_path, "podcast_audio.mp3")
            
        metadata_file = os.path.join(folder_path, "youtube_metadata.txt")
        
        if not os.path.exists(audio_file) or not os.path.exists(metadata_file):
            continue
            
        # Parse metadata
        title = "Episódio sem título"
        description = ""
        with open(metadata_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        current_section = None
        desc_lines = []
        for line in lines:
            if line.startswith("Título:"):
                title = line.replace("Título:", "").strip()
            elif line.startswith("Descrição:"):
                current_section = "desc"
            elif line.startswith("Tags:"):
                current_section = "tags"
            elif current_section == "desc":
                desc_lines.append(line.strip())
                
        description = "<br>".join(desc_lines).strip()
        if not description:
            description = "Mais um episódio do Conexão Artificial."
            
        # File info
        file_size = os.path.getsize(audio_file)
        
        import urllib.parse
        safe_folder = urllib.parse.quote(folder)
        safe_audio = urllib.parse.quote(os.path.basename(audio_file))
        audio_url = f"{BASE_REPO_URL}/episodios/{safe_folder}/{safe_audio}"
        
        # Date from folder name (DD.MM.YYYY__HH.MM_theme)
        try:
            date_str = folder.split("__")[0]
            time_str = folder.split("__")[1].split("_")[0]
            dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H.%M")
        except:
            dt = datetime.datetime.now()
            
        pub_date = formatdate(dt.timestamp(), localtime=False)
        
        safe_title = html.escape(title)
        item = f"""
        <item>
            <title>{safe_title}</title>
            <description><![CDATA[{description}]]></description>
            <pubDate>{pub_date}</pubDate>
            <enclosure url="{audio_url}" length="{file_size}" type="audio/mpeg"/>
            <guid isPermaLink="false">{folder}</guid>
            <itunes:author>{PODCAST_AUTHOR}</itunes:author>
            <itunes:explicit>no</itunes:explicit>
        </item>"""
        rss_items += item

    rss_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <title>{PODCAST_TITLE}</title>
    <link>{PODCAST_LINK}</link>
    <language>{PODCAST_LANGUAGE}</language>
    <itunes:author>{PODCAST_AUTHOR}</itunes:author>
    <itunes:owner>
      <itunes:name>{PODCAST_AUTHOR}</itunes:name>
      <itunes:email>{PODCAST_EMAIL}</itunes:email>
    </itunes:owner>
    <description>{PODCAST_DESC}</description>
    <itunes:category text="Technology"/>
    <itunes:explicit>no</itunes:explicit>
    <itunes:image href="{BASE_REPO_URL}/capa.jpg"/>
    {rss_items}
  </channel>
</rss>"""

    with open(RSS_FILE, "w", encoding="utf-8") as f:
        f.write(rss_content)
        
    print(f"Feed RSS atualizado com sucesso em: {RSS_FILE}")
    print("Lembre-se de hospedar a pasta 'episodios' e apontar o Spotify para este RSS.")

if __name__ == "__main__":
    generate_rss()
