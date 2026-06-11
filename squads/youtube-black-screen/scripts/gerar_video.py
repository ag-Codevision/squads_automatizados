import os
import subprocess
import sys
from dotenv import load_dotenv

load_dotenv()

def main():
    run_dir = sys.argv[1] if len(sys.argv) > 1 else "output"
    
    # Duração em segundos (padrão 10h = 36000s). 
    # Permite ler da env VIDEO_DURATION para podermos testar com tempos curtos (ex: 60)
    duration_str = os.environ.get("VIDEO_DURATION") or (sys.argv[2] if len(sys.argv) > 2 else "36000")
    try:
        duration = int(duration_str)
    except ValueError:
        duration = 36000
        
    print(f"=== INICIANDO RENDERIZAÇÃO DO VÍDEO ===")
    print(f"Diretório da run: {run_dir}")
    print(f"Duração configurada: {duration} segundos ({duration / 3600:.2f} horas)")
    
    video_fundo = os.path.join(run_dir, "chuva_fundo.mp4")
    video_saida = os.path.join(run_dir, "video_final_10h.mp4")
    
    if not os.path.exists(video_fundo):
        print(f"[ERRO] Vídeo de fundo não encontrado em: {video_fundo}")
        sys.exit(1)
        
    # Comando unificado do FFMPEG para gerar o vídeo e o áudio mixado de ruído marrom/rosa
    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1",
        "-i", video_fundo,
        "-f", "lavfi", "-i", f"nullsrc=s=1280x720:d={duration}",
        "-f", "lavfi", "-i", f"anoisesrc=c=brown:d={duration}",
        "-f", "lavfi", "-i", f"anoisesrc=c=pink:d={duration}",
        "-filter_complex", (
            f"[2:a][3:a]amix=inputs=2:duration=first:dropout_transition=0,volume=1.5[audio];"
            f"[1:v]noise=alls=15:allf=t,lutyuv=y='if(gt(val\\,230)\\,val\\,0)':u=128:v=128,"
            f"scale=1280:80:flags=neighbor,scale=1280:720:flags=neighbor,setsar=1[rain];"
            f"[0:v]scale=1280:720,setsar=1[bg];"
            f"[bg][rain]blend=all_mode=screen:all_opacity=0.15,fade=t=out:st=30:d=10,setdar=16/9[v]"
        ),
        "-map", "[v]",
        "-map", "[audio]",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-tune", "stillimage",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", str(duration),
        "-movflags", "+faststart",
        video_saida
    ]
    
    print(f"Executando FFMPEG...")
    try:
        # Mostra o progresso no console
        subprocess.run(cmd, check=True)
        print(f"[SUCESSO] Vídeo gerado com sucesso em: {video_saida}")
    except subprocess.CalledProcessError as e:
        print(f"[ERRO CRÍTICO] Falha ao renderizar vídeo com FFMPEG: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
