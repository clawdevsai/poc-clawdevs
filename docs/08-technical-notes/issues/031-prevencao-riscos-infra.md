# [team-devs-ai] Prevenção e mitigação de riscos de infraestrutura

**Fase:** 3 — Operações  
**Labels:** ops, infra, risk

## Descrição

Documentar e implementar mitigações para riscos: OOM GPU (singleton Ollama + GPU Lock), colisão por expiração do lock (referência a TTL dinâmico/balanceamento), picos de CPU (cpulimit/cgroups), disco cheio (deduplicação, limpeza de cache), custos de API (cache RAG), deadlocks (timeout por pod), **persistência após sandbox** (artefatos envenenados no disco compartilhado — mitigação: quarentena de disco e análise determinística de diff).

## Critérios de aceite

- [ ] Tabela de riscos com severidade e mitigação (OOM, colisão lock, CPU, disco, custos, deadlocks).
- [ ] **Persistência após sandbox:** risco de artefatos envenenados no disco compartilhado (script de pós-instalação malicioso grava no volume persistente). Mitigação: **quarentena de disco** + **análise determinística de diff** antes de transferir resultado do sandbox para o repositório principal (ref. [05-seguranca-e-etica.md](../05-seguranca-e-etica.md) e [14-seguranca-runtime-agentes.md](../14-seguranca-runtime-agentes.md)).
- [ ] Onde aplicável, configuração ou script que aplica a mitigação (ex.: timeout em pods, limpeza de logs).
- [ ] Referência à fundação (TTL dinâmico e node selectors já obrigatórios na Phase 0 — ver [006-gpu-lock-script.md](006-gpu-lock-script.md), [03-arquitetura.md](../03-arquitetura.md)) e à evolução adicional (PriorityClasses, balanceamento avançado) em [122-balanceamento-dinamico-gpu-cpu.md](122-balanceamento-dinamico-gpu-cpu.md).

## Referências

- [04-infraestrutura.md](../04-infraestrutura.md) (Riscos e mitigação)
- [06-operacoes.md](../06-operacoes.md)
