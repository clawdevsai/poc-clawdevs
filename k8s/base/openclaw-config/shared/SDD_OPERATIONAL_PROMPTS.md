# SDD OPERATIONAL PROMPTS

Use estes prompts como ponto de partida para operar o fluxo SDD no ClawDevs AI.
Substitua os colchetes pelos dados da iniciativa.

## CEO

### Intake
`Quero estruturar a iniciativa [nome] com foco em [resultado]. Monte o BRIEF, a SPEC inicial e indique os riscos, restricoes e criterio de sucesso.`

### Spec first
`Transforme esta demanda em uma SPEC objetiva com comportamento observavel, contratos, NFRs e criterios de aceite: [demanda].`

### Clarify
`A SPEC abaixo tem ambiguidades. Liste as duvidas, suposicoes e decisoes que precisam ser registradas antes do plan: [spec].`

### Handoff to PO
`Com base neste BRIEF e nesta SPEC, prepare o handoff para o PO com escopo, valor, restricoes e o menor slice demonstravel: [brief/spec].`

## PO

### Product refinement
`Refine o BRIEF em SPEC funcional. Mantenha comportamento observavel, escopo claro, NFRs e rastreabilidade para US e TASK: [brief].`

### User story
`Converta esta SPEC em USER STORY e FEATURE com criterios BDD, escopo, nao-escopo e metricas de sucesso: [spec].`

### Clarify
`Esta iniciativa ainda tem ambiguidades. Use o CLARIFY_TEMPLATE e registre decisoes, assumptions e impactos no plano: [brief/spec].`

### Prioritization
`Priorize este conjunto de iniciativas com criterio explicito de valor, risco e custo. Entregue a ordem sugerida e o motivo: [lista].`

## Arquiteto

### Technical plan
`A partir desta SPEC e destas USER STORIES, produza o PLAN tecnico com arquitetura, fases, alternativas, riscos e validacao: [spec/us].`

### Task breakdown
`Quebre esta iniciativa em TASKs pequenas, executaveis e rastreaveis. Inclua criterios de aceite, dependencias e NFRs: [spec/us/plan].`

### ADR
`Esta decisao tecnica merece ADR? Se sim, redija o ADR com tradeoffs, alternativas, custo, performance e rollback: [contexto].`

### Validate
`Revise este PLAN/TASK/checklist e diga se a entrega esta pronta para executar ou se falta clarificar algo: [artefatos].`

## Dev_Backend

### Implement
`Implemente estritamente esta TASK usando a SPEC como contrato de comportamento. Nao invente requisitos: [task/spec].`

### Test
`Execute os testes relevantes desta TASK e reporte os resultados com evidencias e impacto nos NFRs: [task].`

### Hardening
`Depois do slice funcional, adicione hardening: logs, metricas, tratamento de erro e validacao final: [task/spec].`

### Status
`Reporte status curto com arquivos alterados, testes executados, riscos e proximo passo: [contexto].`

## Regras de uso
- Sempre comece pela constitution e pelo checklist SDD.
- Sempre use SPEC quando houver ambiguidade.
- Sempre mantenha rastreabilidade entre BRIEF, SPEC, US, TASK e VALIDATE.
- Sempre prefira slices pequenos e demonstraveis.
