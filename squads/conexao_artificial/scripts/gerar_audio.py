import os
import subprocess
import re
import requests
from dotenv import load_dotenv

load_dotenv()
import platform
import shutil

# Caminho base do squad (um nível acima da pasta dos scripts)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, "output", "roteiro_episodio.txt")
OUTPUT_FILE = os.path.join(BASE_DIR, "output", "podcast_audio.mp3")
TEMP_DIR = os.path.join(BASE_DIR, "output", "temp_audio")

TTS_TON_PROV = os.environ.get("VOICE_TON")
if not TTS_TON_PROV or TTS_TON_PROV.strip() == "":
    TTS_TON_PROV = "elevenlabs"

TTS_BIA_PROV = os.environ.get("VOICE_BIA")
if not TTS_BIA_PROV or TTS_BIA_PROV.strip() == "":
    TTS_BIA_PROV = "elevenlabs"

# Vozes do ElevenLabs padrão para Ton e Bia
VOICE_TON_EL = "4za2kOXGgUd57HRSQ1fn"
VOICE_BIA_EL = "7iqXtOF3wl3pomwXFY7G"

API_URL = "https://gen.pollinations.ai/v1/audio/speech"
API_KEY = os.environ.get("POLLINATIONS_API_KEY", "")

# Configuração dinâmica do FFmpeg
if platform.system() == "Windows":
    ffmpeg_in_path = shutil.which("ffmpeg")
    if ffmpeg_in_path:
        FFMPEG_EXE = "ffmpeg"
    else:
        FFMPEG_EXE = r"C:\Users\Marcio\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin\ffmpeg.exe"
else:
    FFMPEG_EXE = "ffmpeg"


def mapear_e_limpar_tags(texto):
    # Dicionário de mapeamento de tags de sentimentos/atitudes geradas pela IA para as oficiais do Gemini TTS
    mapeamento = {
        "[smiling]": "",
        "[laughing]": "[laughter]",
        "[intrigued]": "",
        "[impressed]": "",
        "[explained]": "",
        "[concerned]": "[sadly]",
        "[thoughtfully]": "[sighs]",
        "[curiously]": "",
        "[amazed]": "[excitedly]"
    }
    
    # Substitui as tags mapeadas
    for tag_antiga, tag_nova in mapeamento.items():
        texto = texto.replace(tag_antiga, tag_nova)
        texto = texto.replace(tag_antiga.upper(), tag_nova)
        
    # As tags oficiais válidas do Gemini TTS
    tags_validas = ["[excitedly]", "[laughter]", "[whispering]", "[gasp]", "[sighs]", "[sadly]"]
    
    # Remove qualquer outro conteúdo entre colchetes que não seja uma tag oficial para evitar alucinações de fala
    def filter_brackets(match):
        bracket_content = match.group(0).lower()
        if bracket_content in tags_validas:
            return match.group(0)
        return ""
        
    texto = re.sub(r'\[[^\]]+\]', filter_brackets, texto)
    
    # Remove espaços duplos criados pela remoção das tags
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto


def generate_audio():
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)
        
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    audio_files = []

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Regex robusta para capturar os apresentadores (Ton:, Tom:, Bia:, com ou sem espaços ou caracteres especiais)
    parts = re.split(r'(?i)\b(Ton|Tom|Bia)\b\s*:\s*', content)
    
    current_provider = None
    current_role = None
    current_speaker = None
    
    for i, part in enumerate(parts):
        if i == 0:
            # Texto antes do primeiro palestrante (geralmente vazio)
            continue
            
        if i % 2 == 1:
            # Esta parte é o nome do orador capturado
            speaker_name = part.lower()
            if speaker_name in ["ton", "tom"]:
                current_provider = TTS_TON_PROV
                current_role = "Tom"
                current_speaker = "default" if current_provider == "microsoft" else VOICE_TON_EL
            elif speaker_name == "bia":
                current_provider = TTS_BIA_PROV
                current_role = "Bia"
                current_speaker = "default" if current_provider == "microsoft" else VOICE_BIA_EL
        else:
            # Esta parte é o texto da fala correspondente
            part_text = part.strip()
            if not part_text or not current_provider:
                continue
                
            idx = len(audio_files)
            ext = "wav" if (current_provider == "google/gemini-3.1-flash-tts") else "mp3"
            temp_file = os.path.join(TEMP_DIR, f"part_{idx:03d}.{ext}")
            
            if current_provider == "google/gemini-3.1-flash-tts":
                import time
                import base64
                import wave
                
                # Tenta gerar com a API direta do Gemini com até 3 retentativas
                max_attempts = 3
                retry_delay = 5
                success = False
                gemini_key = os.environ.get("GEMINI_API_KEY", "")
                
                for attempt in range(max_attempts):
                    try:
                        voice_name = "Zubenelgenubi" if current_role == "Tom" else "Laomedeia"
                        texto_limpo = mapear_e_limpar_tags(part_text)
                        
                        print(f"Generating audio part {idx} via Gemini Developer API (Voice: {voice_name}, Attempt {attempt+1})...")
                        
                        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key={gemini_key}"
                        headers = {"Content-Type": "application/json"}
                        
                        payload = {
                            "contents": [
                                {"parts": [{"text": f'"{texto_limpo}"'}]}
                            ],
                            "generationConfig": {
                                "responseModalities": ["AUDIO"],
                                "speechConfig": {
                                    "voiceConfig": {
                                        "prebuiltVoiceConfig": {
                                            "voiceName": voice_name
                                        }
                                    }
                                }
                            }
                        }
                        
                        response = requests.post(url, headers=headers, json=payload)
                        response.raise_for_status()
                        response_json = response.json()
                        
                        if "candidates" in response_json:
                            inline_data = response_json["candidates"][0]["content"]["parts"][0]["inlineData"]
                            raw_bytes = base64.b64decode(inline_data["data"])
                            
                            # Salva em formato WAV com o cabeçalho RIFF de 44 bytes usando o módulo wave
                            with wave.open(temp_file, "wb") as wav_file:
                                wav_file.setnchannels(1)      # Mono
                                wav_file.setsampwidth(2)      # 16-bit (2 bytes)
                                wav_file.setframerate(24000)  # 24kHz
                                wav_file.writeframes(raw_bytes)
                                
                            audio_files.append(temp_file)
                            print(f"[OK] Part {idx} generated successfully on attempt {attempt+1}!")
                            
                            # Pequeno atraso para evitar rate limiting da API direta do Gemini
                            time.sleep(1.5)
                            success = True
                            break
                        else:
                            raise Exception(f"Gemini API unexpected response format: {response_json}")
                            
                    except Exception as e:
                        print(f"[WARN] Attempt {attempt+1} failed for part {idx}: {e}")
                        if attempt < max_attempts - 1:
                            print(f"Aguardando {retry_delay} segundos antes de tentar novamente...")
                            time.sleep(retry_delay)
                
                if not success:
                    # Fallback final para ElevenLabs se todas as tentativas falharem
                    print(f"[RETRY] All Gemini API attempts failed. Retrying part {idx} with ElevenLabs fallback...")
                    temp_file_mp3 = os.path.join(TEMP_DIR, f"part_{idx:03d}_fallback.mp3")
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {API_KEY}"
                    }
                    fallback_voice = VOICE_TON_EL if current_role == "Tom" else VOICE_BIA_EL
                    payload = {
                        "model": "elevenlabs",
                        "input": part_text,
                        "voice": fallback_voice
                    }
                    try:
                        response = requests.post(API_URL, headers=headers, json=payload)
                        response.raise_for_status()
                        with open(temp_file_mp3, "wb") as audio_file:
                            audio_file.write(response.content)
                            
                        # Converte MP3 para WAV de 24kHz mono para manter consistência no concat do ffmpeg
                        print(f"Converting fallback MP3 to WAV for part {idx}...")
                        conv_cmd = [
                            FFMPEG_EXE, "-y", "-i", temp_file_mp3,
                            "-ar", "24000", "-ac", "1", temp_file
                        ]
                        subprocess.run(conv_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        
                        if os.path.exists(temp_file_mp3):
                            os.remove(temp_file_mp3)
                            
                        audio_files.append(temp_file)
                        print(f"[OK] Fallback to ElevenLabs succeeded and converted to WAV for part {idx}!")
                    except Exception as fallback_err:
                        print(f"[ERROR] Fallback also failed for part {idx}: {fallback_err}")
                        
            else:
                # Outros provedores de áudio (ElevenLabs, Microsoft via Pollinations, etc.)
                print(f"Generating audio part {idx} via {current_provider} (Voice: {current_speaker})...")
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {API_KEY}"
                }
                payload = {
                    "model": current_provider,
                    "input": part_text,
                    "voice": current_speaker
                }
                try:
                    response = requests.post(API_URL, headers=headers, json=payload)
                    response.raise_for_status()
                    with open(temp_file, "wb") as audio_file:
                        audio_file.write(response.content)
                    audio_files.append(temp_file)
                except Exception as e:
                    print(f"[ERROR] Failed to generate part {idx} with {current_provider}: {e}")
                    if current_provider != "elevenlabs":
                        print(f"[RETRY] Retrying part {idx} with ElevenLabs fallback...")
                        fallback_voice = VOICE_TON_EL if current_role == "Tom" else VOICE_BIA_EL
                        payload["model"] = "elevenlabs"
                        payload["voice"] = fallback_voice
                        try:
                            response = requests.post(API_URL, headers=headers, json=payload)
                            response.raise_for_status()
                            with open(temp_file, "wb") as audio_file:
                                audio_file.write(response.content)
                            audio_files.append(temp_file)
                            print(f"[OK] Fallback to ElevenLabs succeeded for part {idx}!")
                        except Exception as fallback_err:
                            print(f"[ERROR] Fallback also failed for part {idx}: {fallback_err}")

    if not audio_files:
        print("No audio parts generated. Check the script formatting (should contain 'Tom:' and 'Bia:').")
        return

    # Combine using ffmpeg
    list_file = os.path.join(TEMP_DIR, "file_list.txt")
    with open(list_file, "w", encoding="utf-8") as f:
        for audio_file in audio_files:
            safe_path = audio_file.replace('\\', '/')
            f.write(f"file '{safe_path}'\n")
            
    print("Combining audio files with ffmpeg...")
    # Re-encodamos para garantir compatibilidade se houver formatos mistos (.wav do Gemini e .mp3 do ElevenLabs)
    concat_cmd = [FFMPEG_EXE, "-y", "-f", "concat", "-safe", "0", "-i", list_file, "-c:a", "libmp3lame", "-b:a", "192k", OUTPUT_FILE]
    subprocess.run(concat_cmd, check=True)
    
    print(f"Podcast audio successfully created at: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_audio()
