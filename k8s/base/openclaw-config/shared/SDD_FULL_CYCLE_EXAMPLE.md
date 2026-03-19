# SDD FULL CYCLE EXAMPLE

Este documento mostra um ciclo completo usando os templates do repositorio.
A iniciativa de exemplo e interna: reforcar o uso de SDD em todos os agentes e deixar o fluxo repetivel.

## Constitution
- Specification comes before implementation.
- The SPEC is the source of truth for intended behavior.
- Clarification happens before planning.
- Tasks must trace back to SPEC, BRIEF and the approved scope.

## Brief
### Title
- Padronizar o fluxo SDD para a ClawDevs AI interna e para projetos entregues.

### Context
- Hoje o sistema ja possui agentes, prompts, checklist e templates.
- Falta um exemplo completo e repetivel para orientar novas iniciativas.

### Goal
- Tornar o fluxo SDD operavel por qualquer agente sem ambiguidade.

### Scope
- Includes:
  - templates de BRIEF, SPEC, CLARIFY, PLAN, TASK e VALIDATE
  - checklist SDD
  - prompts operacionais por papel
  - alinhamento dos agentes ao mesmo contrato
- Does not include:
  - reescrita completa dos agentes
  - mudanca de stack
  - novos servicos externos

### Success metrics
- Novo agente consegue seguir o fluxo sem instrucoes adicionais.
- Cada iniciativa tem rastreabilidade BRIEF -> SPEC -> PLAN -> TASK -> VALIDATE.

## Spec
### Behavior
- Ao receber uma iniciativa, o CEO gera BRIEF e SPEC inicial.
- Se houver ambiguidade, o fluxo entra em CLARIFY antes de PLAN.
- O PO refina a SPEC em FEATURE e USER STORY.
- O Arquiteto converte em PLAN, TASK e validacao tecnica.
- O Dev_Backend implementa exatamente o que foi especificado.

### Contracts
- BRIEF define contexto, objetivo e escopo.
- SPEC define comportamento observavel, contratos, NFRs e criterios de aceite.
- CLARIFY registra duvidas, decisoes e assumptions.
- PLAN define arquitetura, fases, riscos e validacao.
- TASK define trabalho executavel e testavel.
- VALIDATE encerra com evidencias e decisao.

### Acceptance criteria
1. Dado uma iniciativa nova, quando o CEO iniciar o fluxo, entao ha BRIEF e SPEC inicial.
2. Dado uma ambiguidade, quando o fluxo encontrar um gap, entao existe CLARIFY antes de PLAN.
3. Dado uma TASK pronta, quando o Dev_Backend executar, entao o resultado e rastreavel ate a SPEC.

## Clarify
### Ambiguities
- Qual a melhor forma de exibir os templates para o time?
- O checklist precisa ser gate duro ou guia forte?

### Decisions
- Expor tudo no README e via `make` para reduzir atrito.
- Tratar o checklist como gate de prontidao.

### Assumptions
- O time prefere comandos curtos e artefatos enxutos.

## Plan
### Architecture
- `k8s/base/openclaw-config/shared/` guarda os templates oficiais.
- `k8s/base/openclaw-pod.yaml` copia os arquivos para os workspaces dos agentes.
- `k8s/base/kustomization.yaml` expõe os arquivos no configMap.
- `README.md` vira a porta de entrada do fluxo.
- `Makefile` oferece atalhos para abrir os artefatos.

### Phases
1. Criar templates e documento de convencao.
2. Copiar os artefatos para os agentes no bootstrap.
3. Expor atalhos de operacao.
4. Validar renderizacao e consistencia.

### Risks
- Risco: o fluxo virar apenas documentacao.
- Mitigacao: manter prompts operacionais e checklist obrigatorio.

## Tasks
1. Criar templates padrao e documento de operacao.
2. Integrar os templates ao bootstrap e ao configMap.
3. Atualizar README e Makefile.
4. Validar kustomize e consistencia do contrato.

## Validate
### Checks
- [x] Templates existem e estao referenciados.
- [x] Agentes recebem os arquivos no bootstrap.
- [x] README aponta o fluxo e os atalhos.
- [x] Makefile expõe comandos de apoio.
- [x] `kubectl kustomize k8s` renderiza com sucesso.

### Decision
- Status: aprovado para uso interno como referencia.
- Notes: este exemplo serve como molde para novas iniciativas.
