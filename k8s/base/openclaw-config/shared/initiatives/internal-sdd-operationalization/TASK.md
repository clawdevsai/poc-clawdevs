# TASK

## Related artifacts
- BRIEF: `BRIEF.md`
- SPEC: `SPEC.md`
- Clarify: `CLARIFY.md`
- Plan: `PLAN.md`

## Objective
- Publicar e operacionalizar o fluxo SDD como padrao da ClawDevs AI.

## Scope
- Includes:
  - templates oficiais
  - prompts operacionais
  - checklist SDD
  - exemplo completo
- Does not include:
  - mudanca de arquitetura do gateway
  - mudanca de stack
  - reescrita do runtime do agente

## Acceptance criteria
1. Dado um novo agente, quando ele iniciar, entao encontra os artefatos SDD principais.
2. Dado uma nova iniciativa, quando ela for aberta, entao existe um caminho claro para BRIEF -> SPEC -> CLARIFY -> PLAN -> TASK -> VALIDATE.
3. Dado o README, quando alguém abrir o repo, entao o fluxo fica evidente em poucos segundos.

## Implementation steps
1. Publicar templates e contratos compartilhados.
2. Distribuir os arquivos aos workspaces dos agentes.
3. Atualizar README e Makefile.
4. Validar a renderização do Kustomize.

## Tests
- Unit: N/A
- Integration: `kubectl kustomize k8s`
- Validation: leitura dos prompts e atalhos

## NFRs
- Performance: impacto nulo no runtime.
- Cost: sem aumento material de custo.
- Security: sem segredos ou credenciais.
- Observability: docs rastreaveis em markdown.

## Done when
- O fluxo fica pronto para uso interno e para projetos.
