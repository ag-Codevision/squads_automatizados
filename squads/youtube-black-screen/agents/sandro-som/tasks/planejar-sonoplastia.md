---
task: "Planejar Sonoplastia e Mixagem"
order: 1
input: |
  - roteiro_metadados: Título e estilo de chuva sugeridos.
output: |
  - plano_sonoro: Detalhes das camadas de áudio, crossfades, volume relativo e atenuação de trovões.
---

# Planejar Sonoplastia e Mixagem

Esta tarefa consiste em desenhar a estrutura e as especificações de áudio para o vídeo longo, garantindo a imersão binaural e a segurança contra picos de volume incômodos.

## Processo

1. Analisar o estilo de chuva proposto e definir as camadas de áudio necessárias para compor a paisagem sonora (ex: chuva de base, vento, trovões).
2. Definir o volume relativo de cada camada em decibéis (dB) para garantir equilíbrio.
3. Especificar os parâmetros do compressor e do limitador (limite máximo de volume para os picos de trovões).
4. Determinar o tempo e a suavidade da curva de crossfade (transição de loop).

## Output Format

```yaml
camadas_audio:
  - nome: "..."
    volume: "...dB"
    funcao: "..."
compressor_limitador:
  treshold: "...dB"
  peak_limit: "...dB"
transicoes_loop:
  tipo: "..."
  duracao_crossfade: "...s"
especificacao_tecnica: "..."
```

## Output Example

> Use as quality reference, not as rigid template.

```yaml
camadas_audio:
  - nome: "Chuva Fina de Base"
    volume: "-14dB"
    funcao: "Ruído constante para mascarar sons externos e relaxar."
  - nome: "Chuva no Telhado de Zinco (Foley)"
    volume: "-12dB"
    funcao: "Som ASMR de textura principal que estimula o sono."
  - nome: "Trovoadas Distantes"
    volume: "-18dB"
    funcao: "Ruidos de baixa frequência para aconchego espacial."
compressor_limitador:
  treshold: "-15dB"
  peak_limit: "-8dB (Garante trovões suaves sem sobressaltos)"
transicoes_loop:
  tipo: "Crossfade linear sobreposto"
  duracao_crossfade: "15 segundos (Totalmente imperceptível)"
especificacao_tecnica: "Áudio exportado em Stereo PCM 24-bit 48kHz, otimizado para reprodução em alto-falantes de TV e fones de ouvido."
```

## Quality Criteria

- [ ] Definição clara de pelo menos 3 camadas de som independentes.
- [ ] Limitação de picos de som de trovões abaixo de -6dB.
- [ ] Definição de transição de loop com crossfade longo (mínimo 10 segundos).

## Veto Conditions

Reject and redo if ANY are true:
1. O plano de mixagem não indica limitador dinâmico de picos.
2. O plano técnico sugere loops de áudio curtos (abaixo de 10 minutos por arquivo original).
