# [team-devs-ai] Loop de consenso automatizado (pré-freio de mão) — orçamento de degradação

**Fase:** 3 — Operações  
**Labels:** ops, autonomy, degradation  
**Depende de:** [017-autonomia-nivel-4-matriz-escalonamento.md](017-autonomia-nivel-4-matriz-escalonamento.md), relatório de degradação (017 operacional — já implementado)

## Descrição

Completar o **orçamento de degradação**: orquestrador conta eventos de **5ª strike** e de **aprovações por omissão cosmética** de forma acumulativa. Ao atingir **10–15% das tarefas do sprint** nessa rota de fuga, **não** acionar freio de mão imediatamente; primeiro executar o **loop de consenso automatizado (pré-freio de mão)** com QA e Architect. Só se o loop falhar (ou não for aplicável), acionar **freio de mão** (pausa + relatório + desbloqueio explícito via `unblock-degradation.sh`).

## Critérios de aceite

- [ ] **Métrica acumulativa:** orquestrador mantém contagem de (a) eventos de 5ª strike e (b) aprovações por omissão cosmética no sprint atual. Limiar configurável (ex.: 10–15% das tarefas). Documentar em [06-operacoes.md](../06-operacoes.md) e [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md).
- [ ] **Pré-freio — Loop de consenso:** ao atingir o limiar, orquestrador aciona **subfluxo** com **QA** e **Architect**: usam o Degradation Report (ou rascunho) como **input** e propõem **ajuste temporário** (ex.: critérios de aceite do PO, fitness functions do Architect). Documentar em 06 (seção *Loop de consenso automatizado*).
- [ ] **Pilot em uma tarefa crítica:** o sistema **testa** o ajuste em **uma única tarefa** (escolhida deterministicamente — ex.: primeira da fila pendente ou por prioridade). **Critério de sucesso:** PR aprovado pelo Architect na pilot sem novo 5º strike. Se resolver, esteira segue sem acordar o Diretor; se **falhar**, orquestrador aciona **freio de mão** e workflow de recuperação (relatório + pausa + `unblock-degradation.sh`).
- [ ] Integração com [scripts/orchestrator_autonomy.py](../../scripts/orchestrator_autonomy.py) e com [docs/agents-devs/degradation-report-*.md](../agents-devs/) e [scripts/unblock-degradation.sh](../../scripts/unblock-degradation.sh).

## Referências

- [017-autonomia-nivel-4-matriz-escalonamento.md](017-autonomia-nivel-4-matriz-escalonamento.md)
- [06-operacoes.md](../06-operacoes.md) (Orçamento de degradação, loop de consenso, workflow de recuperação)
