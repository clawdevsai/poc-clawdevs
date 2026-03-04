# Prevenção e mitigação de riscos de infraestrutura (Fase 3 — 031)

Riscos operacionais do cluster ClawDevs e mitigações. Ref: [05-seguranca-e-etica.md](05-seguranca-e-etica.md), [14-seguranca-runtime-agentes.md](14-seguranca-runtime-agentes.md), [06-operacoes.md](06-operacoes.md), [04-infraestrutura.md](04-infraestrutura.md).

---

## Tabela de riscos e mitigações

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| **OOM GPU** (VRAM esgotada) | Pods evicted, inferência falha, driver instável | GPU Lock com TTL dinâmico; checkpoint 80°C; evict por prioridade; [30-manual-primeiros-socorros-gpu.md](30-manual-primeiros-socorros-gpu.md) (Fase 2: delete pod Ollama, DEL `gpu_active_lock`, restart nvidia-device-plugin). |
| **Colisão / expiração do lock** | Dois consumidores acessando GPU; estado inconsistente | Lock com heartbeat e TTL; script [gpu_lock.py](../scripts/gpu_lock.py); ao expirar, apenas um job obtém lock; manual GPU Fase 2 para limpar lock travado. |
| **CPU / carga no nó** | Lentidão, eviction de pods (BestEffort) | Requests/limits nos manifests; prioridade de pods; evict por prioridade; aumentar recursos do Minikube ou reduzir concorrência. |
| **Disco cheio** | Falha de I/O, pods evicted, Minikube instável | Monitorar uso no nó; `minikube ssh "df -h"`; limpeza: `docker system prune -a --volumes` (Fase 4 em [30-manual-primeiros-socorros-gpu.md](30-manual-primeiros-socorros-gpu.md)); retention de logs configurável. |
| **Custos de API (nuvem)** | Orçamento estourado, bloqueio de chamadas | Rotação de tokens; service account zerada no roteador; digest e métricas; orçamento de degradação (10–15%) para pausar esteira antes de escalar custo. |
| **Deadlocks (fila / lógica)** | Tarefas travadas, consumo parado | Ciclo de rascunho (draft_rejected) e disjuntor por épico (issue 127); timeouts em jobs/pods; Redis streams com consumer groups e idempotência. |
| **Persistência após sandbox** | Artefatos de código de terceiros no disco compartilhado | **Quarentena de disco:** artefatos do sandbox efêmero em volume isolado; diff determinístico antes de promover para workspace; pipeline de quarentena ([05-seguranca-e-etica.md](05-seguranca-e-etica.md)); nunca instalar de terceiros no container principal. |

---

## Configuração e scripts de apoio

- **Timeouts em pods:** definir `activeDeadlineSeconds` em Jobs/CronJobs que usam GPU para evitar jobs zumbis.
- **Limpeza de logs:** retention configurável (ex.: Fluent Bit ou truncate periódico) para evitar crescimento indefinido no disco.
- **Chaves Redis (orquestrador):** [44-fase2-seguranca-automacao.md](44-fase2-seguranca-automacao.md), [k8s/security/phase2-config-configmap.yaml](../k8s/security/phase2-config-configmap.yaml) — `DEGRADATION_THRESHOLD_PCT`, `orchestration:pause_degradation`, five strikes, omission_cosmetic.

---

## Referências

- [05-seguranca-e-etica.md](05-seguranca-e-etica.md) — Riscos residuais, Zero Trust, sandbox, quarentena.
- [14-seguranca-runtime-agentes.md](14-seguranca-runtime-agentes.md) — Validação pré-execução, SSRF, path traversal.
- [06-operacoes.md](06-operacoes.md) — Manual GPU, checkpoint 80°C, workflow de recuperação, orçamento de degradação.
- [30-manual-primeiros-socorros-gpu.md](30-manual-primeiros-socorros-gpu.md) — Passos manuais quando recuperação automática não bastar.
