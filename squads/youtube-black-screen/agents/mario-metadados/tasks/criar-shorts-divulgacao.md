---
task: "Criar Shorts de Divulgação"
order: 2
input: |
  - tema_chuva: O cenário ou tipo de som que o vídeo principal abordará.
output: |
  - roteiro_shorts: Ideia visual, roteiro do texto na tela e descrição com tags para o YouTube Shorts.
---

# Criar Shorts de Divulgação

Esta tarefa consiste em elaborar um roteiro de 15 a 30 segundos para o YouTube Shorts, com apelo visual estético e ganchos rápidos para atrair novos espectadores para o vídeo completo de longa duração.

## Processo

1. Definir o conceito de imagem ou clipe visual estético em alta resolução (B-Roll) relacionado ao tema.
2. Escrever o texto dinâmico que aparecerá sobre a tela, contendo um gancho direto de identificação com insônia/estresse.
3. Redigir a chamada para ação (CTA) direcionando o espectador ao link fixado nos comentários do vídeo completo.
4. Fornecer hashtags otimizadas de alta circulação para Shorts de relaxamento.

## Output Format

```yaml
shorts_titulo: "..."
conceito_visual: "..."
texto_tela: "..."
audio_efeito: "..."
descricao_comentarios: "..."
hashtags: "..."
```

## Output Example

> Use as quality reference, not as rigid template.

```yaml
shorts_titulo: "Não consegue dormir hoje? 🌧️ #shorts"
conceito_visual: "Vídeo macro estético em close-up de gotas de chuva batendo nas folhas sob a luz âmbar de um poste de rua à noite."
texto_tela: "Mente inquieta tentando dormir? Respire fundo... 🌧️ Som de chuva realista. Link do vídeo de 10 horas com tela preta fixado nos comentários!"
audio_efeito: "Som limpo e próximo (ASMR) de chuva forte caindo."
descricao_comentarios: "Acesse o link do canal para ouvir o vídeo completo de 10 horas de chuva forte com tela preta e descanse a noite toda. Não se esqueça de se inscrever para novos sons semanais."
hashtags: "#shorts #somdechuva #insonia #relaxar #dormirrapido #asmrrain"
```

## Quality Criteria

- [ ] O texto na tela contém um gancho emocional e apelo à dor imediata (insônia).
- [ ] A chamada para ação (CTA) para o vídeo completo está clara.
- [ ] Foram incluídas hashtags exclusivas para o YouTube Shorts.

## Veto Conditions

Reject and redo if ANY are true:
1. O roteiro não incentiva ou não inclui a chamada para ação de acessar o vídeo longo.
2. O texto de tela excede 50 palavras (Shorts exigem textos muito rápidos e concisos).
