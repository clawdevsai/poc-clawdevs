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

- [01-visao-e-proposta.md](../../01-core/01-visao-e-proposta.md) (Chaos Engineering)

## Verificação (Fase 11)

- Cenários e manual de falhas: [chaos-engineering-manual-falhas.md](../../07-operations/chaos-engineering-manual-falhas.md) — requisitos contraditórios, biblioteca obsoleta/vulnerável, injeção, bypass segurança, skill não aprovada, estouro orçamento.
- Objetivo e processo: doc § Objetivo e § Processo (executar, registrar, ajustar prompts/guardrails).
- Comportamento esperado (bloqueio, escalação, kill switch): § Comportamento esperado e referências a 27, 027, 05.
