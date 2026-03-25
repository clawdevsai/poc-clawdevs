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

## Gates operacionais obrigatorios

### Readiness gate (antes de executar)
`Valide o SDD_CHECKLIST para esta iniciativa e responda em formato de gate: STATUS=READY|BLOCKED, itens criticos faltantes, owner por item e proxima acao. Contexto: [brief/spec/plan/task].`

### Validate gate (antes de marcar concluido)
`Preencha o VALIDATE_TEMPLATE com evidencias objetivas (comando, resultado, artefatos e rastreabilidade). Se faltar evidencia, retorne BLOCKED com pendencias: [task/spec].`

## Saida minima para auditoria
- `status`: READY | BLOCKED | DONE
- `traceability`: BRIEF -> SPEC -> US -> TASK -> VALIDATE (com caminhos)
- `checklist`: resumo do SDD_CHECKLIST (ok/pendente por item critico)
- `evidence`: comandos executados e resultados objetivos
- `decision`: aprovado para proxima etapa ou bloqueado com owner

## Few-shot rapido (entrada -> saida)

### CEO
Entrada:
`Nova iniciativa: reduzir tempo de onboarding em 40%.`
Saida esperada:
`BRIEF+SPEC inicial com objetivo observavel, escopo/nao-escopo, riscos, NFRs e menor slice demonstravel; handoff para PO com caminhos dos artefatos.`

### PO
Entrada:
`Refinar SPEC de onboarding em USER STORY.`
Saida esperada:
`FEATURE+US com criterios BDD, metricas de sucesso, NFRs e rastreabilidade para SPEC/TASK; STATUS=READY ou BLOCKED com pendencias.`

### Arquiteto
Entrada:
`Quebrar SPEC em TASKs executaveis.`
Saida esperada:
`PLAN+TASKs pequenas com dependencias, BDD, NFRs numericos e gate SDD; sem SPEC funcional => STATUS=BLOCKED.`

### Dev_Backend
Entrada:
`Implementar TASK-123 com SPEC-045.`
Saida esperada:
`Implementacao aderente a SPEC, testes executados, evidencia objetiva e VALIDATE preenchido; sem checklist/SPEC/TASK => STATUS=BLOCKED.`

## Reverse prompting operacional

### Reverse: gerar prompt a partir da saida desejada
`Quero este resultado final: [cole formato alvo de BRIEF/SPEC/US/TASK/VALIDATE]. Reconstrua o melhor prompt operacional para o papel [CEO|PO|Arquiteto|Dev_Backend], inclua restricoes, checklist minimo e criterios de bloqueio.`

### Reverse: depurar prompt que produziu saida ruim
`Dada esta saida ruim: [saida], proponha um prompt revisado com: 1) objetivo observavel, 2) formato de saida, 3) contraexemplos, 4) checklist gate READY/BLOCKED, 5) evidencias obrigatorias.`

### Reverse: alinhar com SDD
`Converta esta saida desejada em instrucao compativel com SDD: manter rastreabilidade BRIEF->SPEC->US->TASK->VALIDATE, usar CLARIFY quando houver ambiguidade e bloquear execucao sem SPEC valida. Resultado em formato prompt reutilizavel.`

## Regras de uso
- Sempre comece pela constitution e pelo checklist SDD.
- Sempre use SPEC quando houver ambiguidade.
- Sempre mantenha rastreabilidade entre BRIEF, SPEC, US, TASK e VALIDATE.
- Sempre prefira slices pequenos e demonstraveis.
