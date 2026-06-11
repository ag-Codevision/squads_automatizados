---
task: "Criar Roteiro e Metadados do Vídeo de Sono"
order: 1
input: |
  - tema_chuva: O cenário ou tipo de som que o vídeo abordará (ex: chuva na floresta com trovões)
output: |
  - roteiro_metadados: Roteiro contendo título, conceito de thumbnail, descrição otimizada, tags e estrutura temporal.
---

# Criar Roteiro e Metadados do Vídeo de Sono

Esta tarefa consiste em escrever todos os metadados textuais e a estrutura de tempo recomendada para o vídeo longo de sono no YouTube, garantindo SEO de alta performance e proteção contra spam.

## Processo

1. Analisar o tema do vídeo fornecido no input e pesquisar palavras-chave com alto volume de buscas associadas a esse tipo de som (ex: "tinnitus", "sono rápido").
2. Escrever o título do vídeo com no máximo 85 caracteres, mesclando o tom aconchegante com o terapêutico.
3. Elaborar uma descrição rica de no mínimo 250 palavras que conte com a prova de originalidade de áudio e a explicação do fade para tela preta.
4. Definir a estrutura temporal de 10 horas indicando os blocos de visual dinâmico, fade out visual e tela preta contínua.

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

> Use as quality reference, not as rigid template.

```yaml
titulo: "Chuva Forte na Janela com Trovões Distantes para Dormir | 10 Horas Tela Preta"
thumbnail_concept: "Vista da janela de um quarto quente e aconchegante iluminado por velas sob uma noite de tempestade. Texto 'TELA PRETA | 10 HORAS' em destaque."
estrutura_video:
  abertura: "0:00 - 3:00 | Vídeo dinâmico em 4K mostrando gotas escorrendo no vidro da janela."
  transicao: "3:00 - 5:00 | Esmaecimento gradual (fade to black) visual e diminuição de frequências agudas de som."
  tela_preta: "5:00 - 9:59:00 | Tela preta pura com som de chuva e trovoadas em loop de alta fidelidade sem picos."
  encerramento: "9:59:00 - 10:00:00 | Fade-out de áudio de 1 minuto até o silêncio."
descricao: |
  Durma profundamente com o som relaxante de chuva na janela com trovões distantes. Desenvolvido para alívio imediato de insônia crônica, estresse diário e ansiedade noturna.
  Detalhes de Produção: Gravado originalmente em floresta nativa utilizando microfone binaural profissional Zoom H6. Editado e mixado em estúdio digital eliminando picos de trovão para manter o espectador em sono ininterrupto.
  Sem anúncios mid-roll ativos.
tags: "som de chuva, chuva para dormir, tela preta, 10 horas de chuva, insônia, relaxar, ruído branco, som de trovão"
```

## Quality Criteria

- [ ] O título contém palavras-chave cruciais e possui tamanho ideal.
- [ ] A descrição detalha a captação e mixagem de áudio autoral.
- [ ] O conceito de thumbnail apresenta cores escuras de alto contraste.

## Veto Conditions

Reject and redo if ANY are true:
1. A descrição não cita equipamentos ou originalidade de mixagem.
2. O título possui palavras duplicadas excessivamente no formato spam.
