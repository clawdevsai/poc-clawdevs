# [team-devs-ai] Script de GPU Lock (Redis SETNX + TTL dinâmico)

**Fase:** 0 — Fundação  
**Labels:** foundation, infra, gpu

## Descrição

Implementar o mecanismo de GPU Lock para que apenas um agente por vez use o Ollama (e a GPU). Evita OOM quando Architect, QA, CyberSec e UX acordam simultaneamente. Lock via Redis (SETNX com **TTL dinâmico** calculado pelo tamanho do payload no Redis — ex.: mais de 500 linhas → 120 s, senão 60 s); agente adquire antes de carregar modelo, libera ao terminar. Node selectors garantem DevOps e UX em CPU (Phi-3 Mini), reservando VRAM para Developer, Architect e QA.

## Critérios de aceite

- [ ] Script ou módulo (ex.: `gpu_lock.py`) que adquire lock no Redis (SETNX com **TTL dinâmico**).
- [ ] **TTL dinâmico:** cálculo baseado no tamanho do payload do evento no Redis (ex.: contagem de linhas do payload; se > 500 linhas → TTL 120 s, senão 60 s). Variável `GPU_LOCK_EVENT_KEY` opcional para indicar a chave do payload.
- [ ] Comportamento: tentar adquirir; se não conseguir, aguardar em loop até obter lock ou timeout.
- [ ] Liberação explícita ao terminar uso da GPU.
- [ ] **Hard timeout no Kubernetes:** configuração no orquestrador (ex.: `activeDeadlineSeconds: 120` ou equivalente) para pods que usam GPU; ao exceder o tempo, o pod é morto e a tarefa volta à fila. Documentar em [04-infraestrutura.md](../04-infraestrutura.md) e [06-operacoes.md](../06-operacoes.md). Garantia contra lock órfão (processo morre por OOM/travamento sem liberar).
- [ ] Integração documentada para os agentes locais (Developer, Architect, QA, CyberSec, UX) chamarem o lock antes de usar Ollama.
- [ ] Node selectors (em `limits.yaml` ou manifests): DevOps e UX configurados para usar exclusivamente CPU (Phi-3 Mini), reservando VRAM para Developer, Architect e QA — ver [04-infraestrutura.md](../04-infraestrutura.md).
- [ ] **Validação pré-GPU (opcional):** pipeline que roda SLM em CPU (sintaxe, lint, aderência SOLID) antes da tarefa entrar na fila do GPU Lock; documentar em [03-arquitetura.md](../03-arquitetura.md) e [06-operacoes.md](../06-operacoes.md).
- [ ] **Batching de PRs (opcional):** orquestrador pode agrupar micro-PRs para revisão em lote pelo Architect; documentar em [03-arquitetura.md](../03-arquitetura.md) e [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md).

## Referências

- [03-arquitetura.md](../03-arquitetura.md) (Fila de prioridade, estágio pré-GPU, batching de PRs)
- [04-infraestrutura.md](../04-infraestrutura.md) (GPU Lock)
- [06-operacoes.md](../06-operacoes.md) (Prevenção: hard timeout, validação CPU, batching)
- [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) (Batching de PRs)
- [09-setup-e-scripts.md](../09-setup-e-scripts.md)
