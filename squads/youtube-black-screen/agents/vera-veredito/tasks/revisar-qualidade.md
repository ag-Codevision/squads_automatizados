---
task: "Revisar Qualidade do Vídeo e Metadados"
order: 1
input: |
  - plano_tecnico: Contém os metadados de Mário Metadados e o plano de áudio/vídeo de Sandro Som.
output: |
  - avaliacao_revisao: Parecer com nota final, checklist de conformidade e pontos de correção obrigatórios.
---

# Revisar Qualidade do Vídeo e Metadados

Esta tarefa consiste em auditar todas as peças de planejamento criadas no pipeline, pontuar o trabalho e garantir conformidade com as diretrizes do YPP e o checklist de monetização do YouTube.

## Processo

1. Ler os metadados gerados (Mário Metadados) e os planos técnicos (Sandro Som).
2. Avaliar os itens baseando-se no checklist de qualidade (`quality-criteria.md`) e de erros (`anti-patterns.md`).
3. Calcular a nota final de 1 a 10 de acordo com os pesos (SEO, Originalidade/Autenticidade e Áudio Técnico).
4. Gerar o parecer final. Em caso de aprovação (nota >= 8.5), liberar o conteúdo. Em caso de rejeição, pontuar as alterações obrigatórias necessárias.

## Output Format

```yaml
nota_geral: "..."
status: "APROVADO" | "REPROVADO"
checklist:
  seo_otimizado: "SIM" | "NÃO"
  prova_autoria_descricao: "SIM" | "NÃO"
  visual_dinamico_e_fade: "SIM" | "NÃO"
  limitador_trovoes_planejado: "SIM" | "NÃO"
  crossfades_loops: "SIM" | "NÃO"
parecer_detalhado: "..."
ajustes_obrigatorios:
  - "..."
```

## Output Example

> Use as quality reference, not as rigid template.

```yaml
nota_geral: "9.2/10"
status: "APROVADO"
checklist:
  seo_otimizado: "SIM"
  prova_autoria_descricao: "SIM"
  visual_dinamico_e_fade: "SIM"
  limitador_trovoes_planejado: "SIM"
  crossfades_loops: "SIM"
parecer_detalhado: "O título de 72 caracteres contém palavras-chave exatas e boa curiosidade visual. A descrição possui 280 palavras com a prova de originalidade e menção aos gravadores Zoom H6. Sandro Som detalhou perfeitamente a mixagem com picos dinâmicos a -8dB nos trovões e transição de fade visual suave de 60s."
ajustes_obrigatorios: []
```

## Quality Criteria

- [ ] A avaliação contém nota numérica explícita.
- [ ] O checklist de compliance de monetização está totalmente respondido.
- [ ] Pontua erros de anti-patterns específicos se presentes.

## Veto Conditions

Reject and redo if ANY are true:
1. O parecer aprova o conteúdo com nota inferior a 8.5/10.
2. O parecer não detalha as correções necessárias em caso de reprovação.
