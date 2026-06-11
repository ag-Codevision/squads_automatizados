---
execution: inline
agent: vera-veredito
inputFile: squads/youtube-black-screen/output/publicacao-info.md
outputFile: squads/youtube-black-screen/output/revisao-qualidade.md
on_reject: 1
---

# Step 06: Revisar Qualidade Final

## Context Loading

Load these files before executing:
- `squads/youtube-black-screen/output/publicacao-info.md` — As informações da publicação automatizada.
- `squads/youtube-black-screen/output/plano-tecnico.md` — Roteiro, metadados e plano de áudio/vídeo.
- `pipeline/data/quality-criteria.md` — Critérios de pontuação oficiais.

## Instructions

### Process
1. Ler os metadados gerados, as configurações de áudio/vídeo e as informações do upload no YouTube.
2. Comparar as entregas com as diretrizes de originalidade do YouTube Partner Program (YPP).
3. Atribuir a nota de 1 a 10 ao vídeo produzido e postado de acordo com a rubrica.
4. Se a nota for inferior a 8.5, definir o status como "REPROVADO" e apontar os ajustes de roteiro (retorna ao passo 1).
5. Se a nota for superior ou igual a 8.5, aprovar.

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
  upload_realizado_youtube: "SIM" | "NÃO"
parecer_detalhado: "..."
ajustes_obrigatorios:
  - "..."
```

## Output Example

```yaml
nota_geral: "9.0/10"
status: "APROVADO"
checklist:
  seo_otimizado: "SIM"
  prova_autoria_descricao: "SIM"
  visual_dinamico_e_fade: "SIM"
  limitador_trovoes_planejado: "SIM"
  crossfades_loops: "SIM"
  upload_realizado_youtube: "SIM"
parecer_detalhado: "Os metadados contêm títulos corretos e descrição blindada de autoria de áudio. O plano técnico atende a compressão e os crossfades. O upload no YouTube Studio foi realizado com sucesso sob status Não Listado para validação do usuário."
ajustes_obrigatorios: []
```

## Veto Conditions

Reject and redo if ANY of these are true:
1. O parecer aprova o conteúdo com nota inferior a 8.5/10.
2. O checklist de qualidade não foi respondido integralmente.

## Quality Criteria

- [ ] Contém avaliação de nota numérica clara.
- [ ] O checklist foi respondido na totalidade.
- [ ] Fornece feedbacks pedagógicos.
