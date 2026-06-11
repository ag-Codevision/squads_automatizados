---
execution: inline
agent: vera-veredito
inputFile: squads/youtube-black-screen/output/plano-tecnico.md
outputFile: squads/youtube-black-screen/output/revisao-qualidade.md
on_reject: 1
---

# Step 04: Revisar Qualidade Final

## Context Loading

Load these files before executing:
- `squads/youtube-black-screen/output/plano-tecnico.md` — O plano de áudio, vídeo e metadados.
- `pipeline/data/quality-criteria.md` — Os checklists e critérios de pontuação oficiais.

## Instructions

### Process
1. Ler os metadados e o plano de mixagem contidos no arquivo de entrada.
2. Comparar as informações com os checklists de qualidade (quality-criteria.md) para verificar conformidade com as políticas do YouTube.
3. Atribuir a nota de 1 a 10 baseada na rubrica.
4. Se a nota for inferior a 8.5, definir o status como "REPROVADO" e detalhar as correções necessárias (isso forçará o loop de retorno ao passo 1).
5. Se a nota for igual ou superior a 8.5, definir como "APROVADO".

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

```yaml
nota_geral: "9.0/10"
status: "APROVADO"
checklist:
  seo_otimizado: "SIM"
  prova_autoria_descricao: "SIM"
  visual_dinamico_e_fade: "SIM"
  limitador_trovoes_planejado: "SIM"
  crossfades_loops: "SIM"
parecer_detalhado: "O título atende os parâmetros de caracteres e palavras-chave. A descrição é longa e explica a gravação binaural. O plano de Sandro Som atende aos crossfades de 12s para loop invisível e limitador de picos de -7.5dB."
ajustes_obrigatorios: []
```

## Veto Conditions

Reject and redo if ANY of these are true:
1. O parecer aprova o conteúdo com nota inferior a 8.5/10.
2. O checklist técnico não foi respondido integralmente.

## Quality Criteria

- [ ] Apresenta nota numérica explícita.
- [ ] Detalha as justificativas para cada item do checklist.
- [ ] Dá feedbacks acionáveis.
