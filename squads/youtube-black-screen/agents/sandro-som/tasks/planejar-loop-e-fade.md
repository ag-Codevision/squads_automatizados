---
task: "Planejar Loops e Fades Visuais"
order: 2
input: |
  - plano_sonoro: Detalhes de áudio.
output: |
  - plano_visual: Tempo de abertura com vídeo dinâmico, transição de fade-out visual e especificações de exportação de vídeo.
---

# Planejar Loops e Fades Visuais

Esta tarefa consiste em planejar a estrutura visual do vídeo, definindo o tempo em que o vídeo de paisagem aconchegante fica ativo e a suavidade do fade out visual até a tela preta completa.

## Processo

1. Selecionar ou definir o conceito do loop de vídeo aconchegante para a introdução (ex: chuva no vidro, cabana com lareira).
2. Definir a duração exata da abertura dinâmica (recomendado entre 2 e 5 minutos).
3. Determinar o tempo exato e a curva do fade visual (esmaecimento lento de 60 a 120 segundos).
4. Estabelecer as especificações de exportação de vídeo (Resolução, Codec, Frame Rate) para postagem no YouTube.

## Output Format

```yaml
conceito_visual_introducao: "..."
tempo_abertura_dinamica: "...s"
tempo_fade_out_visual: "...s"
resolucao_video: "..."
codec_exportacao: "..."
garantia_tela_preta: "..."
```

## Output Example

> Use as quality reference, not as rigid template.

```yaml
conceito_visual_introducao: "Loop dinâmico de 3 minutos de gotas escorrendo lentamente por uma janela de vidro de cabana de madeira à noite, com luz âmbar suave e lareira ao fundo."
tempo_abertura_dinamica: "180 segundos (3 minutos)"
tempo_fade_out_visual: "60 segundos (Fade gradual até atingir preto absoluto RGB 0,0,0)"
resolucao_video: "3840x2160 (4K UHD) para melhor nitidez visual da chuva inicial"
codec_exportacao: "H.264 MP4, 30fps, Bitrate alvo 20Mbps"
garantia_tela_preta: "A tela preta cobre de 4:00 até 10:00:00 (fim do vídeo), sem elementos brilhantes, marcas d'água ou textos de crédito visual."
```

## Quality Criteria

- [ ] A abertura dinâmica possui pelo menos 2 minutos de duração para visualização real inicial.
- [ ] O fade out visual tem duração mínima de 30 segundos para transição suave.
- [ ] A tela preta posterior garante escuridão total (RGB 0,0,0).
- [ ] O planejamento confirma que o áudio de chuva contínua permanece ativo e sem atenuação durante e após o fade-out visual da imagem.

## Veto Conditions

Reject and redo if ANY are true:
1. O fade-out de imagem é menor que 15 segundos (transição brusca).
2. O plano inclui inserção de textos ou marcas d'água no meio da tela preta.
3. O plano sugere a atenuação ou aplicação de fade-out ao áudio de chuva durante o esmaecimento visual da imagem para a tela preta.
