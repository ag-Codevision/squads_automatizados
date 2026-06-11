---
execution: inline
agent: mario-metadados
format: youtube-script
outputFile: squads/youtube-black-screen/output/roteiro-e-metadados.md
---

# Step 01: Criar Metadados e Roteiro

## Context Loading

Load these files before executing:
- `pipeline/data/research-brief.md` — Informações sobre o mercado, monetização e concorrentes.
- `pipeline/data/domain-framework.md` — Diretrizes de estrutura de roteiro, título e descrição.
- `pipeline/data/tone-of-voice.md` — Lista de tons permitidos.

## Instructions

### Process
1. Selecionar o tom adequado baseado nas diretrizes de `tone-of-voice.md`.
2. Elaborar um título de alta atratividade SEO para o YouTube contendo as palavras-chave do nicho escolhido.
3. Projetar o conceito visual da thumbnail e a estrutura detalhada de tempo do vídeo (duração de 10 horas).
4. Escrever a descrição completa (mínimo 250 palavras) e incluir a prova técnica de captação e edição de som (comprovando autoria humana).
5. Gerar tags e hashtags relevantes para preenchimento no YouTube.

## Output Format

```yaml
titulo: "..."
thumbnail_concept: "..."
estrutura_video:
  abertura: "0:00 - 3:00 | ..."
  transicao: "3:00 - 5:00 | ..."
  tela_preta: "5:00 - 9:59:00 | ..."
  encerramento: "9:59:00 - 10:00:00 | ..."
descricao: "..."
tags: "..."
```

## Output Example

```yaml
titulo: "Chuva Forte na Janela com Trovões para Dormir Rápido | 10 Horas Tela Preta (Sem Loops)"
thumbnail_concept: "Cabana de madeira aconchegante em meio a uma floresta chuvosa à noite, com luz de lareira brilhando. Texto '10 HORAS | TELA PRETA' no canto em alta legibilidade."
estrutura_video:
  abertura: "0:00 - 3:00 | Loop em 4K de gotas de chuva caindo no vidro da janela com lareira ao fundo."
  transicao: "3:00 - 5:00 | Fade out gradual da cena até a escuridão absoluta."
  tela_preta: "5:00 - 9:59:00 | Tela preta completa com som estável de chuva e trovoadas sem sobressaltos."
  encerramento: "9:59:00 - 10:00:00 | Fade out de 1 minuto do áudio até o silêncio."
descricao: |
  Relaxe e durma rapidamente esta noite ao som de chuva forte e trovões aconchegantes. Ideal para combater a insônia crônica e o estresse diário.
  Fórmula de Produção Humana: Este áudio é autoral, mixado em estúdio digital a partir de gravações de campo em floresta tropical usando gravadores portáteis Zoom H6. Aplicamos um compressor e limitador dinâmico nas trovoadas para não excederem -8dB, protegendo seu sono contra despertares.
  Desativamos todos os anúncios no meio do vídeo para uma noite inteira livre de interrupções.
tags: "som de chuva, chuva para dormir, tela preta, 10 horas tela preta, insônia, relaxar, som de trovão, ruído branco"
```

## Veto Conditions

Reject and redo if ANY of these are true:
1. A descrição gerada não contém a declaração de gravação com Zoom H6 ou equivalente (prova de esforço humano).
2. O título possui palavras chaves soltas empilhadas de forma artificial (Spam).

## Quality Criteria

- [ ] O título tem entre 50 e 80 caracteres.
- [ ] A descrição excede 250 palavras e tem tom empático.
- [ ] A estrutura temporal prevê a transição visual fade-out.
