---
execution: inline
agent: paulo-publicador
inputFile: squads/youtube-black-screen/output/plano-tecnico.md
outputFile: squads/youtube-black-screen/output/video-gerado-info.md
---

# Step 04: Renderizar Vídeo FFMPEG

## Context Loading

Load these files before executing:
- `squads/youtube-black-screen/output/plano-tecnico.md` — Plano de áudio e vídeo definidos nos passos anteriores.
- `pipeline/data/domain-framework.md` — Configurações padrão de vídeo longo e loop.

## Instructions

### Process
1. Executar o script `obter-fundo.js` passando a pasta de output do run atual por parâmetro para baixar um vídeo de chuva HD (1280x720) contemplativo sem pessoas, salvando como `output/{RUN_ID}/v1/chuva_fundo.mp4`.
2. Montar a linha de comando unificada do FFMPEG para gerar o áudio mixado procedural de 10 horas (ruído marrom + ruído rosa) e renderizar o vídeo acoplando o fundo em loop (`-stream_loop -1`) e a chuva dinâmica em overlay HD (`1280x720`).
3. Aplicar o fade-out gradual e linear apenas na camada de vídeo (esmaecimento da imagem do fundo e chuva) iniciando aos **30 segundos** e durando 10 segundos (até o segundo 40), tornando o vídeo tela preta absoluta do segundo 40 em diante, enquanto o áudio permanece contínuo e intacto até o final do vídeo (segundo 36000).
4. Executar o comando unificado do FFMPEG localmente no sistema.
5. Gravar os logs de renderização do FFMPEG e extrair metadados físicos do arquivo MP4 final de 10 horas resultante.

## Output Format

```yaml
comando_obter_fundo: "node squads/youtube-black-screen/agents/paulo-publicador/obter-fundo.js ..."
comando_ffmpeg_video_10h: "..."
caminho_video_saida: "..."
tamanho_arquivo_mb: "..."
duracao_detectada_segundos: "..."
status_renderizacao: "SUCESSO" | "ERRO"
logs_ffmpeg: "..."
```

## Output Example

```yaml
comando_obter_fundo: "node squads/youtube-black-screen/agents/paulo-publicador/obter-fundo.js squads/youtube-black-screen/output/10-06-26-17-30/v1"
comando_ffmpeg_video_10h: "ffmpeg -y -stream_loop -1 -i output/v1/chuva_fundo.mp4 -f lavfi -i 'nullsrc=s=1280x720:d=36000' -f lavfi -i 'anoisesrc=c=brown:d=36000' -f lavfi -i 'anoisesrc=c=pink:d=36000' -filter_complex '[2:a][3:a]amix=inputs=2:duration=first:dropout_transition=0,volume=1.5[audio];[1:v]noise=alls=15:allf=t,lutyuv=y=\"if(gt(val,230),val,0)\":u=128:v=128,scale=1280:80:flags=neighbor,scale=1280:720:flags=neighbor,setsar=1[rain];[0:v]scale=1280:720,setsar=1[bg];[bg][rain]blend=all_mode=\"screen\":all_opacity=0.15,fade=t=out:st=30:d=10,setdar=16/9[v]' -map '[v]' -map '[audio]' -c:v libx264 -pix_fmt yuv420p -c:a aac -b:a 192k -t 36000 -movflags +faststart output/v1/video_final_10h.mp4"
caminho_video_saida: "squads/youtube-black-screen/output/10-06-26-17-30/v1/video_final_10h.mp4"
tamanho_arquivo_mb: "1150MB (1.15 GB)"
duracao_detectada_segundos: "36000 segundos (10 horas)"
status_renderizacao: "SUCESSO"
logs_ffmpeg: "video:84200KiB audio:825000KiB muxing overhead: 0.1%"
```

## Veto Conditions

Reject and redo if ANY of these are true:
1. O FFMPEG falha gerando arquivos vazios ou corrompidos de 0 bytes.
2. O arquivo MP4 final não é localizado na pasta de saída.
3. O áudio de 10 horas sofre atenuação ou fade-out sincronizado com o vídeo durante a transição da tela preta.
4. O vídeo contém pessoas ou movimentação urbana movimentada.

## Quality Criteria

- [ ] O vídeo de plano de fundo dinâmico (`chuva_fundo.mp4`) é uma paisagem de chuva na natureza ou janela calmo e sem pessoas.
- [ ] A renderização é concluída de forma unificada para economizar armazenamento local.
- [ ] O fade out inicia aos 30s e termina aos 40s, aplicado unicamente à camada de vídeo, mantendo o áudio constante.
- [ ] O vídeo final está na proporção widescreen HD (1280x720, setsar=1:1, setdar=16:9).
