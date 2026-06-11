---
execution: inline
agent: sandro-som
inputFile: squads/youtube-black-screen/output/roteiro-e-metadados.md
outputFile: squads/youtube-black-screen/output/plano-tecnico.md
---

# Step 02: Planejar Visual e Áudio

## Context Loading

Load these files before executing:
- `squads/youtube-black-screen/output/roteiro-e-metadados.md` — Roteiro e metadados gerados no Passo 1.
- `pipeline/data/anti-patterns.md` — Práticas a evitar em mixagem de áudio e visual.

## Instructions

### Process
1. Analisar as especificações de roteiro e o tipo de som propostos no arquivo de entrada.
2. Definir o design das camadas de som de áudio (volumes relativos em dB, frequências e fontes de base).
3. Especificar os parâmetros dinâmicos de compressão de áudio para evitar picos abruptos em trovões ou vento.
4. Planejar o fluxo visual com tempos exatos de início do loop em 4K e fade out gradual visual de transição para a tela preta.

## Output Format

```yaml
roteiro_original:
  titulo: "..."
plano_audio:
  camadas:
    - som: "..."
      volume: "..."
      funcao: "..."
  processamento:
    limitador_picos: "...dB"
    tamanho_crossfade: "...s"
plano_visual:
  abertura: "..."
  fade_duracao: "..."
  tela_preta: "..."
```

## Output Example

```yaml
roteiro_original:
  titulo: "Chuva Forte na Janela com Trovões para Dormir Rápido | 10 Horas Tela Preta"
plano_audio:
  camadas:
    - som: "Chuva torrencial de base"
      volume: "-12dB"
      funcao: "Sustentar a sensação de isolamento e ruído branco."
    - som: "Trovoadas distantes com eco abafado"
      volume: "-16dB"
      funcao: "Adicionar dinamismo natural sem acordar o ouvinte."
  processamento:
    limitador_picos: "-7.5dB max (Brickwall Limiter na saída Master)"
    tamanho_crossfade: "12 segundos em curva logarítmica para transição sem estalos"
plano_visual:
  abertura: "Loop dinâmico de 180s mostrando janela com chuva à noite em cabana aconchegante."
  fade_duracao: "60 segundos de esmaecimento gradual de brilho e opacidade."
  tela_preta: "Preto total e contínuo (RGB 0,0,0) sem marcas d'água de 4:00 até 10:00:00."
```

## Veto Conditions

Reject and redo if ANY of these are true:
1. O plano sonoro não especifica o controle de picos em trovões ou deixa o limite de pico acima de -5dB.
2. A duração sugerida do fade-out visual é inferior a 30 segundos.

## Quality Criteria

- [ ] Detalhamento de pelo menos 3 camadas de som.
- [ ] Planejamento exato em dB para cada trilha.
- [ ] O crossfade de áudio tem tempo suficiente para emenda imperceptível.
