# App

Codigo Python do ClawDevs AI.

## Nucleo vivo

- `agents/`: papeis do fluxo principal e wrappers de execucao
- `runtime/`: loop compartilhado, contexto, budgets, logging e tools
- `core/`: governanca e degradacao
- `shared/`: Redis e estado de issue

## Fluxo principal atual

```text
cmd:strategy -> PO -> draft.2.issue -> Architect -> task:backlog -> Developer -> code:ready -> pr:review -> QA + DBA + CyberSec -> consenso (approve => event:devops | blocked => task:backlog) -> (>=6 rounds => Architect-review) -> DevOps
```

## Observacao

O repositorio foi reduzido para o fluxo principal. A evolucao daqui em diante deve priorizar runtime, workflow e dominio, sem reintroduzir subsistemas perifericos.
