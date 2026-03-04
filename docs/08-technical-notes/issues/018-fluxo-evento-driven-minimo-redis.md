# [team-devs-ai] Fluxo evento-driven mínimo — publicação em Redis (CEO → PO → backlog)

**Fase:** 1 — Agentes  
**Labels:** agents, redis, event-driven

## Descrição

Garantir o **lado produtor** do fluxo evento-driven: o gateway (CEO/PO) ou um orquestrador deve **publicar** eventos nos streams Redis quando o CEO emite diretriz estratégica e quando o PO prioriza e envia tarefas. Hoje os consumidores (Developer, slot Revisão pós-Dev) e os streams existem; falta documentar e, se possível, fornecer um **contrato** ou **stub** de publicação para testes E2E.

## Critérios de aceite

- [x] Contrato de eventos documentado: formato de mensagem (ex.: `cmd:strategy` com campos mínimos; `task:backlog` com `issue_id` ou payload; `draft.2.issue` com campos para o Architect). → [38-redis-streams-estado-global.md](../38-redis-streams-estado-global.md) §2.
- [x] Documentação em [38-redis-streams-estado-global.md](../38-redis-streams-estado-global.md) ou [42-fluxo-e2e-operacao-2fa.md](../42-fluxo-e2e-operacao-2fa.md) indicando **quem publica** em cada stream (CEO → cmd:strategy; PO → draft.2.issue, task:backlog).
- [x] Script ou ferramenta mínima para **publicar** em Redis: [scripts/publish_event_redis.py](../scripts/publish_event_redis.py) (XADD com stream e pares key=value).

## Referências

- [38-redis-streams-estado-global.md](../38-redis-streams-estado-global.md)
- [42-fluxo-e2e-operacao-2fa.md](../42-fluxo-e2e-operacao-2fa.md)
- [39-consumer-groups-pipeline-revisao.md](../39-consumer-groups-pipeline-revisao.md)
