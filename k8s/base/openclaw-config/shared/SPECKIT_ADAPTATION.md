# SPECKIT ADAPTATION

Este repositorio nao usa o Spec Kit oficial como dependencia obrigatoria.
Em vez disso, adota o mesmo modelo mental e o adapta aos artefatos da ClawDevs AI.

## Correspondencia entre Spec Kit e ClawDevs AI
- `constitution` -> `CONSTITUTION.md`
- `specify` -> `SPEC_TEMPLATE.md` e `backlog/specs/`
- `clarify` -> registro de ambiguidades, assumptions e revisoes da SPEC
- `plan` -> `ADR`, `TASK` e plano tecnico do Arquiteto
- `tasks` -> `TASK-XXX-<slug>.md`
- `analyze` -> validacao de NFRs, riscos, seguranca e custo
- `implement` -> Dev_Backend executando a task

## Objetivo operacional
- Manter o fluxo espec-driven tanto para a plataforma ClawDevs AI quanto para entregas de projetos.
- Preservar rastreabilidade de ponta a ponta.
- Evitar codigo "solto" sem contrato claro.

## Como usar
- O CEO consolida a demanda em Brief + SPEC.
- O PO refina a SPEC e cria User Stories.
- O Arquiteto converte SPEC/US em plano tecnico e tasks.
- O Dev_Backend implementa estritamente o que foi especificado.
