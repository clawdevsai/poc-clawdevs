# Kubernetes — ClawDevs

Estrutura **centralizada por times**. Na raiz de `k8s/` ficam apenas pastas principais e arquivos cluster-wide.

Provedor de LLM por agente: `llm-providers-configmap.yaml` (ollama_local, ollama_cloud, openrouter, etc.). Ver [07-configuracao-e-prompts.md](docs/07-configuracao-e-prompts.md).

## Estrutura (pastas principais)

| Pasta | Conteúdo |
|-------|----------|
| **ollama/** | Deployment Ollama GPU, Service, PVC. Inferência local no cluster. |
| **redis/** | Redis (deployment, service), streams-configmap.yaml, job-init-streams.yaml. Ref: [docs/38-redis-streams-estado-global.md](docs/38-redis-streams-estado-global.md). |
| **management-team/** | CEO e PO. **openclaw/** — gateway (Dockerfile, configmap, deployment, workspace-ceo-configmap, openclaw.local.json5.example). **soul/** — ConfigMap soul-management-agents (CEO, PO). |
| **development-team/** | Time técnico (100% offline). **soul/** — ConfigMap soul-development-agents (devops, architect, developer, qa, cybersec, ux, dba). **developer/**, **revisao-pos-dev/**, configmap, networkpolicy, gpu-lock-hard-timeout-example.yaml. |
| **governance-team/** | Governance Proposer. **soul/** — SOUL do agente. configmap.yaml, deployment.yaml. |

Arquivos na raiz: `namespace.yaml`, `limits.yaml` (ResourceQuota 65%), `llm-providers-configmap.yaml`.

## Ordem de apply (make up)

```bash
kubectl apply -f namespace.yaml
kubectl apply -f limits.yaml
kubectl apply -f redis/
kubectl apply -f ollama/deployment.yaml
kubectl apply -f llm-providers-configmap.yaml
# Gateway e SOUL
kubectl apply -f management-team/openclaw/configmap.yaml
kubectl apply -f management-team/openclaw/workspace-ceo-configmap.yaml
kubectl apply -f management-team/openclaw/deployment.yaml
kubectl apply -f management-team/soul/configmap.yaml
# Secret Telegram: management-team/openclaw/secret.yaml (opcional)
```

Ou use **`make up`** (build da imagem com `make openclaw-image`).

## Layout por time

- **Management:** Gateway em `management-team/openclaw/`; SOUL em `management-team/soul/`. Alternativa só CEO/PO: `make up-management` (scale openclaw a 0 para um único gateway Telegram). Ref: Fase 1 — 012.
- **Development:** Developer pod em `development-team/developer/` (`make developer-configmap` + `kubectl apply -f development-team/developer/`). Slot revisão em `development-team/revisao-pos-dev/` (`make revisao-slot-configmap` + apply). SOUL dev em `development-team/soul/`.
- **Governance:** `governance-team/` (soul/, configmap, deployment).

Ref: [docs/openclaw-sub-agents-architecture.md](docs/openclaw-sub-agents-architecture.md), [docs/04-infraestrutura.md](docs/04-infraestrutura.md), [docs/41-fase1-agentes-soul-pods.md](docs/41-fase1-agentes-soul-pods.md).
