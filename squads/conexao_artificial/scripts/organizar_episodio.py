import os
import shutil
import datetime
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
EPISODES_DIR = os.path.join(OUTPUT_DIR, "episodios")
METADATA_FILE = os.path.join(OUTPUT_DIR, "youtube_metadata.txt")

FILES_TO_MOVE = [
    "noticias_do_dia.md",
    "roteiro_episodio.txt",
    "podcast_audio.mp3",
    "podcast_audio_mixed.mp3",
    "podcast_final.mp4",
    "youtube_metadata.txt"
]

def slugify(text):
    # Converte para minúsculo e remove caracteres especiais
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    # Pega as primeiras 4 palavras que tenham mais de 2 letras (ignora 'a', 'de', 'o')
    words = [w for w in text.split() if len(w) > 2]
    return "_".join(words[:4])

def organize():
    if not os.path.exists(EPISODES_DIR):
        os.makedirs(EPISODES_DIR)

    theme_slug = "tema_geral"
    # Tenta extrair o tema a partir do título gerado no metadado
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("Título:"):
                    # Pega a parte antes do "| Conexão Artificial"
                    title = line.replace("Título:", "").split("|")[0].strip()
                    theme_slug = slugify(title)
                    break
    
    # Formata a data e hora: DD.MM.YYYY__HH.MM
    now = datetime.datetime.now()
    folder_name = f"{now.strftime('%d.%m.%Y__%H.%M')}_{theme_slug}"
    target_folder = os.path.join(EPISODES_DIR, folder_name)
    
    os.makedirs(target_folder, exist_ok=True)
    
    moved_count = 0
    for file_name in FILES_TO_MOVE:
        src = os.path.join(OUTPUT_DIR, file_name)
        dst = os.path.join(target_folder, file_name)
        if os.path.exists(src):
            shutil.move(src, dst)
            moved_count += 1
            
    print(f"Sucesso! {moved_count} arquivos do episódio foram arquivados em:\n{target_folder}")

if __name__ == "__main__":
    organize()
