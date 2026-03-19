# BRIEF

## Title
- Operacionalizar SDD como padrao da ClawDevs AI

## Context
- A plataforma ja possui templates, checklist, prompts e contratos de SDD.
- Falta consolidar isso como fluxo operacional oficial e repetivel para todos os agentes.

## Goal
- Fazer com que qualquer iniciativa interna siga o mesmo contrato SDD sem depender de explicacao adicional.

## Scope
- Includes:
  - uso de Constitution, BRIEF, SPEC, CLARIFY, PLAN, TASK e VALIDATE
  - uso de prompts operacionais e templates
  - alinhamento dos agentes ao contrato compartilhado
- Does not include:
  - mudança de stack
  - mudança do runtime principal
  - reescrita funcional dos agentes

## Constraints
- Precisa funcionar em Windows / Docker Desktop / Kubernetes local.
- Precisa ser documentado e replicavel.
- Precisa manter custo operacional baixo.

## Success metrics
- Todo agente consegue localizar o fluxo em menos de 1 minuto.
- Toda iniciativa nova passa pelo checklist SDD antes de executar.
- O mesmo contrato serve para plataforma interna e projetos.

## Risks
- Risco: virar documentação sem uso.
- Mitigacao: tornar os prompts e templates o caminho normal de operacao.

## Assumptions
- O time aceita usar arquivos markdown como contrato operacional.

## Next step
- Produzir a SPEC de comportamento operacional.
