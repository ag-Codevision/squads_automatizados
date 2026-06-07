import os
import subprocess
import platform
import shutil

# Caminho base do squad (um nível acima da pasta dos scripts)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_FILE = os.path.join(BASE_DIR, "output", "podcast_audio.mp3")
MUSIC_FILE = os.path.join(BASE_DIR, "assets", "Trilha sonora oficial.m4a")
MIXED_AUDIO = os.path.join(BASE_DIR, "output", "podcast_audio_mixed.mp3")
VIDEO_TEMPLATE = os.path.join(BASE_DIR, "assets", "youtube fundo template.mp4")
OUTPUT_FILE = os.path.join(BASE_DIR, "output", "podcast_final.mp4")

# Configuração dinâmica do FFmpeg/FFprobe conforme o SO
if platform.system() == "Windows":
    ffmpeg_in_path = shutil.which("ffmpeg")
    ffprobe_in_path = shutil.which("ffprobe")
    FFMPEG_EXE = "ffmpeg" if ffmpeg_in_path else r"C:\Users\Marcio\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin\ffmpeg.exe"
    FFPROBE_EXE = "ffprobe" if ffprobe_in_path else r"C:\Users\Marcio\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin\ffprobe.exe"
else:
    FFMPEG_EXE = "ffmpeg"
    FFPROBE_EXE = "ffprobe"

def generate_video():
    if not os.path.exists(AUDIO_FILE):
        print(f"Erro: Audio file not found at {AUDIO_FILE}")
        return
        
    if not os.path.exists(VIDEO_TEMPLATE):
        print(f"Erro: Video template not found at {VIDEO_TEMPLATE}")
        return

    if not os.path.exists(MUSIC_FILE):
        print(f"Erro: Music file not found at {MUSIC_FILE}")
        return
        
    print("Getting audio duration using ffprobe...")
    try:
        duration_cmd = [FFPROBE_EXE, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", AUDIO_FILE]
        duration_str = subprocess.check_output(duration_cmd).decode('utf-8').strip()
        duration = float(duration_str)
        print(f"Audio duration is {duration} seconds.")
    except Exception as e:
        print(f"Erro getting duration: {e}")
        return

    # Passo 1: Mixar a voz com a trilha sonora (Ducking e Fading)
    print("Misturando a voz com a trilha sonora (Ducking effect)...")
    fade_out_start = max(0, duration - 3)
    
    # 0:a = voz, 1:a = trilha sonora
    # A trilha sonora original possui volume muito baixo (pico de -18.3 dB e média de -34.9 dB).
    # Ajustamos para volume=1.8 para mantê-la audível como som de fundo sob as vozes.
    filter_complex = (
        f"[1:a]volume=1.8,afade=t=in:st=0:d=3,afade=t=out:st={fade_out_start}:d=3[music_faded];"
        f"[0:a][music_faded]amix=inputs=2:duration=first:dropout_transition=2:normalize=0,volume=2.0[a_out]"
    )
    
    mix_cmd = [
        FFMPEG_EXE, "-y",
        "-i", AUDIO_FILE,
        "-stream_loop", "-1",
        "-i", MUSIC_FILE,
        "-filter_complex", filter_complex,
        "-map", "[a_out]",
        "-t", str(duration),
        "-c:a", "libmp3lame",
        "-q:a", "2",
        MIXED_AUDIO
    ]
    
    try:
        subprocess.run(mix_cmd, check=True)
        print(f"Mixed audio created at: {MIXED_AUDIO}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to mix audio: {e}")
        return

    # Passo 2: Juntar o áudio mixado com a capa do vídeo
    # O erro "sem áudio" acontecia porque o template já tinha uma trilha de áudio vazia e o ffmpeg puxava ela.
    # Usando '-map 0:v:0' (pegar o vídeo do input 0) e '-map 1:a:0' (pegar o áudio do input 1), forçamos o uso do áudio correto.
    print("Combinando o áudio mixado com o vídeo em loop...")
    video_cmd = [
        FFMPEG_EXE, "-y",
        "-stream_loop", "-1",
        "-i", VIDEO_TEMPLATE,
        "-i", MIXED_AUDIO,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", "aac",
        "-t", str(duration),
        "-fflags", "+genpts",
        OUTPUT_FILE
    ]
    
    try:
        subprocess.run(video_cmd, check=True)
        print(f"Podcast video successfully created at: {OUTPUT_FILE}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to generate video: {e}")

if __name__ == "__main__":
    generate_video()
