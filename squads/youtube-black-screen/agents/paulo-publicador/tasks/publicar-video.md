---
task: "Publicar Vídeo YouTube Studio"
order: 2
input: |
  - video_gerado_info: Informações do vídeo final MP4 gerado.
  - roteiro_metadados: Roteiro com títulos, descrições e tags a serem preenchidos.
output: |
  - publicacao_info: Status do upload, ID do vídeo e URL se gerada.
---

# Publicar Vídeo YouTube Studio

Esta tarefa consiste em rodar o script de automação de navegador Playwright para acessar o YouTube Studio, logar com a sessão existente de `youtube.json`, subir o arquivo de vídeo gerado e preencher o formulário de envio com os metadados corretos.

## Processo

1. Carregar a sessão salva em `_opensquad/_browser_profile/youtube.json` no Playwright.
2. Navegar para `https://studio.youtube.com/` e verificar se a sessão de login está ativa.
3. Se deslogado, abrir o navegador em modo visível por 5 minutos para o usuário logar e atualizar os cookies.
4. Clicar em "Criar" -> "Enviar Vídeos" e selecionar o arquivo MP4 na pasta `output/`.
5. Preencher os campos de Título, Descrição (contendo a prova de originalidade) e Tags.
6. Configurar a visibilidade como "Não Listado" ou "Privado" e confirmar o salvamento.

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

> Use as quality reference, not as rigid template.

```yaml
plataforma: "YouTube"
status_envio: "SUCESSO"
id_video: "dQw4w9WgXcQ"
url_video: "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
visibilidade_definida: "Não Listado"
logs_upload: "Acessado YouTube Studio. Sessão válida carregada. Arquivo video_final.mp4 carregado com sucesso. Título e descrição inseridos. Visibilidade configurada como não listado."
```

## Quality Criteria

- [ ] O script utiliza a sessão correta em `_browser_profile/youtube.json`.
- [ ] O preenchimento da descrição não contém quebras de tags ou formatações HTML inválidas.
- [ ] O vídeo é publicado com visibilidade de segurança inicial ("Não Listado" ou "Privado").

## Veto Conditions

Reject and redo if ANY are true:
1. O upload falha por cookies inválidos e o script não notifica ou não abre a tela de login visível.
2. O vídeo é enviado sem título ou com descrição em branco.
