<!-- 
  Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.
 -->

# SDD OPERATIONAL PROMPTS

Use these prompts as a starting point for operating the SDD flow in ClawDevs AI.
Replace the square brackets with the initiative data.

##CEO

### Intake
`Quero estruturar a iniciativa [nome] com foco em [resultado]. Monte o BRIEF, a SPEC inicial e indique os riscos, restricoes e criterio de sucesso.`

### Spec first
`Transforme esta demanda em uma SPEC objetiva com comportamento observavel, contratos, NFRs e criterios de aceite: [demanda].`

### Clarify
`A SPEC abaixo tem ambiguidades. Liste as duvidas, suposicoes e decisoes que precisam ser registradas antes do plan: [spec].`

### Handoff to PO
`Com base neste BRIEF e nesta SPEC, prepare o handoff para o PO com escopo, valor, restricoes e o smallest demonstrable slice: [brief/spec].`

## PO

### Product refinement
`Refine o BRIEF em SPEC funcional. Mantenha comportamento observavel, escopo claro, NFRs e rastreabilidade para US e TASK: [brief].`

###User story
`Converta esta SPEC em USER STORY e FEATURE com criterios BDD, escopo, not-escopo e metricas de sucesso: [spec].`

### Clarify
`Esta iniciativa ainda tem ambiguidades. Use o CLARIFY_TEMPLATE e registre decisoes, assumptions e impactos no plano: [brief/spec].`

### Prioritization
`Priorize este conjunto de iniciativas com criterio explicito de valor, risco e custo. Entregue a ordem sugerida e o motivo: [lista].`

## Architect

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

###Test
`Execute os testes relevantes desta TASK e reporte os resultados com evidencias e impacto nos NFRs: [task].`

### Hardening
`Depois do slice funcional, adicione hardening: logs, metricas, tratamento de erro e validacao final: [task/spec].`

### Status
`Reporte status curto com arquivos alterados, testes executados, riscos e next step: [contexto].`

## Mandatory operational gates

### Readiness gate (before executing)
`Valide o SDD_CHECKLIST para esta iniciativa e responda em formato de gate: STATUS=READY|BLOCKED, itens criticos faltantes, owner por item e proxima acao. Contexto: [brief/spec/plan/task].`

### Validate gate (before marking completed)
`Preencha o VALIDATE_TEMPLATE com evidencias objetivas (comando, resultado, artefatos e rastreabilidade). Se faltar evidencia, retorne BLOCKED com pendencias: [task/spec].`

## Minimum output for audit
- `status`: READY | BLOCKED | DONE
- `traceability`: BRIEF -> SPEC -> US -> TASK -> VALIDATE (with paths)
- `checklist`: SDD_CHECKLIST summary (ok/pending for critical item)
- `evidence`: executed commands and objective results
- `decision`: approved for next stage or blocked with owner

## Fast few-shot (input -> output)

###CEO
Entrada:
`Nova iniciativa: reduzir tempo de onboarding em 40%.`
Expected output:
`Initial BRIEF+SPEC with observable objective, in-scope/out-of-scope, risks, NFRs, and the smallest demonstrable slice; handoff to the PO with artifact paths.`

### PO
Entrada:
`Refinar SPEC de onboarding em USER STORY.`
Expected output:
`FEATURE+US com criterios BDD, metricas de sucesso, NFRs e rastreabilidade para SPEC/TASK; STATUS=READY ou BLOCKED com pendencias.`

### Architect
Entrada:
`Quebrar SPEC em TASKs executaveis.`
Expected output:
`PLAN+TASKs pequenas com dependencias, BDD, NFRs numericos e gate SDD; sem SPEC funcional => STATUS=BLOCKED.`

### Dev_Backend
Entrada:
`Implementar TASK-123 com SPEC-045.`
Expected output:
`Implementacao aderente a SPEC, testes executados, evidencia objetiva e VALIDATE preenchido; sem checklist/SPEC/TASK => STATUS=BLOCKED.`

## Reverse operational prompting

### Reverse: generate prompt from the desired output
`Quero este resultado final: [cole formato alvo de BRIEF/SPEC/US/TASK/VALIDATE]. Reconstrua o melhor prompt operacional para o papel [CEO|PO|Arquiteto|Dev_Backend], inclua restricoes, checklist minimo e criterios de bloqueio.`

### Reverse: debug prompt that produced bad output
`Given this poor output: [output], propose a revised prompt with: 1) observable objective, 2) output format, 3) counterexamples, 4) READY/BLOCKED checklist gate, 5) mandatory evidence.`

### Reverse: align with SDD
`Converta esta output desejada em instrucao compativel com SDD: manter rastreabilidade BRIEF->SPEC->US->TASK->VALIDATE, usar CLARIFY quando houver ambiguidade e bloquear execucao sem SPEC valida. Resultado em formato prompt reutilizavel.`

## Usage rules
- Always start with the constitution and the SDD checklist.
- Always use SPEC when there is ambiguity.
- Always maintain traceability between BRIEF, SPEC, US, TASK and VALIDATE.
- Always prefer small, demonstrable slices.
