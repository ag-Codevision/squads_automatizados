---
execution: inline
agent: paulo-publicador
inputFile: squads/youtube-black-screen/output/video-gerado-info.md
outputFile: squads/youtube-black-screen/output/publicacao-info.md
---

# Step 05: Publicar Vídeo YouTube Studio

## Context Loading

Load these files before executing:
- `squads/youtube-black-screen/output/video-gerado-info.md` — Informações sobre o arquivo MP4 renderizado.
- `squads/youtube-black-screen/output/roteiro-e-metadados.md` — Metadados textuais otimizados.
- `_opensquad/_browser_profile/youtube.json` — Cookies de autenticação do canal.

## Instructions

### Process
1. Carregar os cookies de sessão do YouTube em `_opensquad/_browser_profile/youtube.json` e inicializar o Playwright.
2. Navegar para o painel de controle do YouTube Studio (`https://studio.youtube.com/`).
3. Se o login falhar, abrir o navegador em modo visível por 5 minutos para que o usuário faça o login de forma segura e re-salve a sessão de cookies.
4. Fazer o upload do arquivo MP4 gerado em `output/`.
5. Preencher os campos de Título, Descrição (contendo a prova de autoria e Zoom H6) e tags.
6. Definir a visibilidade de segurança inicial como "Não Listado" ou "Privado" e confirmar a publicação.

## Output Format

```yaml
plataforma: "YouTube"
status_envio: "SUCESSO" | "ERRO"
id_video: "..."
url_video: "..."
visibilidade_definida: "Privado" | "Não Listado" | "Público"
logs_upload: "..."
```

## Output Example

```yaml
plataforma: "YouTube"
status_envio: "SUCESSO"
id_video: "dQw4w9WgXcQ"
url_video: "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
visibilidade_definida: "Não Listado"
logs_upload: "Acessado YouTube Studio. Sessão válida carregada. Arquivo video_final.mp4 carregado com sucesso. Título e descrição inseridos. Visibilidade configurada como não listado."
```

## Veto Conditions

Reject and redo if ANY of these are true:
1. O upload não é concluído por falha de sessão e o script não abre fallback de login visual.
2. O preenchimento do título ou descrição no YouTube Studio falha.

## Quality Criteria

- [ ] A publicação é realizada no status "Não Listado" ou "Privado" por segurança.
- [ ] O link resultante do vídeo é gravado corretamente no output.
