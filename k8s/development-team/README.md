# Development Team — Time técnico (100% offline)

Agentes técnicos: **DevOps**, **Architect**, **Developer**, **QA**, **CyberSec**, **UX**, **DBA**. Operam **100% offline** da internet (NetworkPolicy egress bloqueado); inferência via **Ollama GPU** no cluster por padrão.

Provedor de LLM por agente: ConfigMap `clawdevs-llm-providers` (chaves `agent_devops`, `agent_architect`, etc.). Valores: `ollama_local` | `ollama_cloud` | `openrouter` | `qwen_oauth` | `moonshot_ai` | `openai` | `huggingface_inference`. Padrão: **ollama_local**.

Na Fase 0 atual, o time técnico roda como **sub-agents** do gateway Management (CEO/PO); um deployment dedicado 100% offline pode ser adicionado em fases posteriores usando este ConfigMap e a NetworkPolicy.

**Revisão pós-Dev (slot único):** [revisao-pos-dev/](revisao-pos-dev/) consome `code:ready`, executa Architect→QA→CyberSec→DBA em sequência. **Pods separados (evolução 014):** [architect/](architect/), [qa/](qa/), [cybersec/](cybersec/), [dba/](dba/) formam um pipeline (replicas: 0 por padrão); `make agent-slots-configmap` e aplicar os manifestos; inicializar consumer groups com [scripts/redis-streams-init.sh](../scripts/redis-streams-init.sh).

## Apply

```bash
kubectl apply -f k8s/development-team/configmap.yaml
# Opcional (quando houver pod dedicado): kubectl apply -f k8s/development-team/networkpolicy.yaml
```

Ref: [docs/04-infraestrutura.md](../docs/04-infraestrutura.md), [docs/14-seguranca-runtime-agentes.md](../docs/14-seguranca-runtime-agentes.md).
