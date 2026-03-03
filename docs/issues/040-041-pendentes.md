# config-perfis / truncamento-finops — O que ainda falta implementar

Resumo do que já existe vs. o que falta para fechar os critérios de aceite (perfis por agente e truncamento/FinOps).

Ref: [040-perfis-agente-manifesto-config.md](040-perfis-agente-manifesto-config.md), [041-truncamento-contexto-finops.md](041-truncamento-contexto-finops.md).

---

## config-perfis — Perfis por agente

| Critério | Estado | O que falta |
|----------|--------|-------------|
| Perfil CEO, PO, perfis locais | Config (agent-profiles) e doc 07 | — |
| **Constraints por agente aplicadas** | Parcial | Gateway **lê** agent-profiles (gateway_redis_adapter `_get_profile_json`, envFrom no deployment). Architect 80% no slot; DevOps 82°C em phase2-config. Outras constraints (CEO, PO) no OpenClaw/orquestrador. |
| **DevOps/UX apenas CPU** | Implementado | **gateway-redis-adapter** tem `nodeSelector: workload-type: cpu-only`. Para pods DevOps/UX dedicados futuros: usar o mesmo selector (ver k8s/limits.yaml). Nó sem label: remover selector ou `kubectl label node minikube workload-type=cpu-only`. |

---

## truncamento-finops — Truncamento e FinOps

| Critério | Estado | O que falta |
|----------|--------|-------------|
| Documentação da causa raiz | OK (doc 07) | — |
| **Max tokens no Gateway** | Config (finops-config) + envFrom no OpenClaw | Gateway OpenClaw recebe env; **aplicar** o limite no código do OpenClaw depende da stack externa. Script **apply_max_tokens.py** disponível para pipelines que enviam payload à nuvem (pipe antes de enviar). |
| **Pre-flight Summarize** | **Script preflight_summarize.py** (Ollama local) | Orquestrador ou gateway deve **invocar** o script para payloads com >3 interações antes de enviar à nuvem (contrato de integração). |
| **Truncamento na borda** | **Integrado** | **publish_event_redis.py** e **gateway_redis_adapter.py** truncam valores grandes antes de enfileirar; ConfigMap gateway inclui truncate_payload_border.py. |
| **TTL working buffer** | **working_buffer_ttl.py** com `set_buffer_key(r, key, value, ttl)` | Quem escreve no buffer deve usar essa função ou `SET key value EX TTL` (ler WORKING_BUFFER_TTL_SEC de finops-config). |
| Pipeline descrito | Doc 07 | OK. |
| Memória em camadas e RAG | Doc 28 e 07 | Integração explícita com Warm Store na próxima fase. |
| **MicroADR** | **Implementado** | **slot_revisao_pos_dev.py** chama **microadr_generate.py** ao aprovar; microADR armazenado no Redis (project:v1:microadr:{issue_id}). ConfigMap revisao-slot inclui microadr_generate.py. |
| **Invariantes / segregação** | Tag, compact_preserve_protected, **devops_compact_safe.sh** | DevOps deve usar `scripts/devops_compact_safe.sh` ou `compact_preserve_protected.py` na higiene de buffer. |
| **Validação reversa (PO)** | **Script validate_reverse_po.py** + SOUL PO atualizado | PO pode chamar o script; doc soul/PO.md descreve o fluxo. |
| Freio $5/dia e token bucket | Fase 2 | — |
| Acelerador preditivo | phase2-config (PREDICTIVE_LOCAL_THRESHOLD_DIFF_LINES) | Gateway/orchestrator aplica se implementado no adapter. |
| **Persistência + FinOps** | **Script finops_attempt_cost.py** | Contador de tentativas por issue no Redis; script retorna exit 1 se deve interromper (devolver ao PO). Orquestrador pode chamar antes do pre-flight. |
| **Limite de gastos no painel** | **Doc operacoes-limite-gastos-provedor.md** | Passo a passo para OpenRouter, OpenAI, Google Cloud, Ollama Cloud. |

---

## Resumo — implementado nesta rodada

- Truncamento na borda integrado em **publish_event_redis.py** e **gateway_redis_adapter.py**; truncate_payload_border no ConfigMap do adapter.
- **preflight_summarize.py**: sumarização local via Ollama para payloads com >3 interações (quem chama: orquestrador/gateway).
- **apply_max_tokens.py**: aplicar limite de tokens por perfil antes de enviar à nuvem.
- **OpenClaw deployment**: envFrom finops-config; **gateway-redis-adapter**: envFrom finops-config + nodeSelector cpu-only.
- **microadr_generate.py** e chamada no **slot_revisao_pos_dev** ao aprovar; microADR no Redis.
- **validate_reverse_po.py** e regra no **soul/PO.md**.
- **devops_compact_safe.sh** (wrapper para compact_preserve_protected); **working_buffer_ttl.set_buffer_key** para escrita com TTL.
- **finops_attempt_cost.py** para persistência acoplada ao FinOps (interromper tarefa e devolver ao PO).
- **docs/operacoes-limite-gastos-provedor.md** e referência em doc 07.

### Integração implementada no repositório

- **Gateway adapter:** rota **`POST /publish-to-cloud`** aplica pre-flight summarize (se payload com >N interações) e max tokens por perfil; depois publica no Redis. Ver [integracao-040-041-gateway-orquestrador.md](integracao-040-041-gateway-orquestrador.md).
- **Developer worker:** antes do GPU Lock, chama **finops_attempt_cost** (increment_attempt + should_stop_task); se deve interromper, faz XACK e emite `task_returned_to_po` sem processar.
- **Working buffer:** usar **redis_buffer_writer.write_working_buffer(key_suffix, value)** ao escrever buffer no Redis (TTL automático).
- **Validação reversa PO:** chamar **validate_reverse_po.py --summary ... --criteria ...** no pipeline que gera resumo; se exit 1, não aplicar o resumo.

O que ainda depende de integração externa: **OpenClaw** (código fora do repo) usar a rota `/publish-to-cloud` em vez de `/publish` quando o evento for destinado à nuvem, e aplicar MAX_TOKENS ao enviar ao provedor se não passar pelo adapter.
