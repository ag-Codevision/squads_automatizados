---
task: "Renderizar Vídeo FFMPEG"
order: 1
input: |
  - plano_tecnico: Caminhos de áudio e imagem/vídeo iniciais definidos por Sandro Som.
output: |
  - video_gerado_info: Nome do arquivo gerado, tamanho e logs de renderização do FFMPEG.
---

# Renderizar Vídeo FFMPEG

Esta tarefa consiste em compilar e executar a geração de mídia via FFMPEG local para gerar o vídeo final MP4 de **10 horas** de sono na pasta de output.

## Processo

1. **Obtenção do Vídeo de Fundo Dinâmico:** Executar o script `obter-fundo.js` passando a pasta de output do run atual por parâmetro para baixar um vídeo de chuva HD (1280x720) contemplativo da natureza ou janela livre de pessoas, salvando como `output/{RUN_ID}/v1/chuva_fundo.mp4`.
2. **Renderização do Vídeo e Áudio Unificados (10 Horas):** Montar o comando FFMPEG que gera o áudio mixado procedural de 10 horas (ruído marrom + rosa com limitador de volume a 1.5) e renderiza o vídeo unificando a mídia de plano de fundo em loop (`-stream_loop -1`) e a chuva dinâmica em overlay HD (`setsar=1:1`, `setdar=16:9`, escala `1280x720`).
3. **Fade Out Visual Isolado:** Aplicar o fade-out gradual e linear apenas na camada de vídeo (esmaecimento da chuva e do fundo) iniciando aos **30 segundos** e durando 10 segundos (até o segundo 40), tornando o vídeo tela preta absoluta a partir do segundo 40, enquanto o áudio de tempestade de 10 horas permanece tocando no volume normal contínuo até o final do vídeo (segundo 36000), sem sofrer fade de som.
4. **Execução:** Chamar o FFMPEG local e salvar o MP4 final de 10 horas diretamente na pasta de output, sem a necessidade de gravar arquivos WAV gigantes intermediários no disco.

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

> Use as quality reference, not as rigid template.

```yaml
comando_obter_fundo: "node squads/youtube-black-screen/agents/paulo-publicador/obter-fundo.js squads/youtube-black-screen/output/10-06-26-17-30/v1"
comando_ffmpeg_video_10h: "ffmpeg -y -stream_loop -1 -i output/v1/chuva_fundo.mp4 -f lavfi -i 'nullsrc=s=1280x720:d=36000' -f lavfi -i 'anoisesrc=c=brown:d=36000' -f lavfi -i 'anoisesrc=c=pink:d=36000' -filter_complex '[2:a][3:a]amix=inputs=2:duration=first:dropout_transition=0,volume=1.5[audio];[1:v]noise=alls=15:allf=t,lutyuv=y=\"if(gt(val,230),val,0)\":u=128:v=128,scale=1280:80:flags=neighbor,scale=1280:720:flags=neighbor,setsar=1[rain];[0:v]scale=1280:720,setsar=1[bg];[bg][rain]blend=all_mode=\"screen\":all_opacity=0.15,fade=t=out:st=30:d=10,setdar=16/9[v]' -map '[v]' -map '[audio]' -c:v libx264 -pix_fmt yuv420p -c:a aac -b:a 192k -t 36000 -movflags +faststart output/v1/video_final_10h.mp4"
caminho_video_saida: "squads/youtube-black-screen/output/10-06-26-17-30/v1/video_final_10h.mp4"
tamanho_arquivo_mb: "1150MB (1.15 GB)"
duracao_detectada_segundos: "36000 segundos (10 horas)"
status_renderizacao: "SUCESSO"
logs_ffmpeg: "video:84200KiB audio:825000KiB muxing overhead: 0.1%"
```

## Quality Criteria

- [ ] O vídeo de plano de fundo dinâmico (`chuva_fundo.mp4`) é uma paisagem de chuva natural calma e sem pessoas.
- [ ] A renderização de 10 horas é executada via comando unificado FFMPEG para economizar espaço de armazenamento.
- [ ] O fade out visual de 10s inicia exatamente aos 30 segundos do vídeo, sem atenuar o áudio de tempestade de 10 horas.
- [ ] O vídeo final está na proporção widescreen HD (1280x720, setsar=1:1, setdar=16:9).

## Veto Conditions

Reject and redo if ANY are true:
1. O comando FFMPEG falha ou o arquivo MP4 não é localizado.
2. O áudio sofre fade-out ou atenuação de volume durante o vídeo (o áudio de 10 horas deve tocar sem alteração até o final).
3. O vídeo final contém cenas urbanas movimentadas ou pessoas transitando.
