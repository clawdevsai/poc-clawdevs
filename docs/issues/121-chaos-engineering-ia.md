# [team-devs-ai] Chaos Engineering para IA

**Fase:** 11 — Avançado  
**Labels:** advanced, testing, security

## Descrição

Cenários de estresse: Issue com requisitos contraditórios ou biblioteca obsoleta para validar se Architect e CyberSec barram o PR. Gerar "manual de falhas" para calibrar prompts e garantir que o kill switch (Q-Suite) funcione sob pressão.

## Critérios de aceite

- [ ] Cenários de chaos documentados: requisitos contraditórios, biblioteca obsoleta/vulnerável, input malicioso (injeção), etc.
- [ ] Objetivo: validar que Architect e CyberSec barram PRs inadequados; validar kill switch em cenários de pressão.
- [ ] Processo: executar cenários (manual ou automatizado), registrar resultado, ajustar prompts/guardrails.
- [ ] "Manual de falhas" ou documento que descreve cenários e comportamento esperado (bloqueio, escalação).

## Referências

- [01-visao-e-proposta.md](../01-visao-e-proposta.md) (Chaos Engineering)
