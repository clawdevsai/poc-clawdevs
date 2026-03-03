# Kubernetes — ClawDevs

Recursos para rodar o ecossistema no cluster (Minikube ou outro). Arquitetura **openclaw-first**: o Gateway OpenClaw roda os agentes; os pods do pipeline são **triggers** que consomem Redis e enviam mensagens ao Gateway.

## Estrutura

| Pasta | Conteúdo |
|-------|----------|
| **namespace.yaml** | Namespace `ai-agents` |
| **limits.yaml** | ResourceQuota e LimitRange (ex.: 65% hardware) |
| **llm-providers-configmap.yaml** | Provedores LLM por agente (ollama_local, etc.) |
| **redis/** | Redis (deployment, service), streams-configmap, job-init-streams |
| **ollama/** | Ollama GPU (deployment, service, PVC) |
| **management-team/** | OpenClaw (gateway), SOUL management, config; opcional deploy CEO/PO separado |
| **development-team/** | Triggers do pipeline (PO, Architect-draft, Developer, Revisão-slot, DevOps, Audit) + gateway-redis-adapter |
| **orchestrator/** | Consumer Slack (orchestrator:events), CronJobs (audit-queue, digest, cosmetic) |
| **security/** | Fase 2: phase2-config, egress-whitelist, token rotation, url-sandbox, quarentena |
| **governance-team/** | Governance Proposer (opcional) |
| **sandbox/** | Job quarentena pipeline (opcional) |

## Ordem de apply (recomendada)

Use **`make up`** para subir o núcleo (namespace, Redis, Ollama, OpenClaw, phase2, orchestrator).

Para o pipeline completo (triggers que chamam o Gateway):

```bash
make configmaps-pipeline
kubectl apply -f k8s/development-team/configmap.yaml
kubectl apply -f k8s/development-team/po/
kubectl apply -f k8s/development-team/architect-draft/
kubectl apply -f k8s/development-team/developer/
kubectl apply -f k8s/development-team/revisao-pos-dev/
kubectl apply -f k8s/development-team/devops-worker/
kubectl apply -f k8s/development-team/audit-runner/
kubectl apply -f k8s/development-team/gateway-redis-adapter/
# Ajuste replicas conforme necessário (ex.: kubectl scale deployment po -n ai-agents --replicas=1)
```

Ou aplique tudo de uma vez (cada subpasta tem deployment + configmap-env):

```bash
make configmaps-pipeline
for dir in po architect-draft developer revisao-pos-dev devops-worker audit-runner gateway-redis-adapter; do
  kubectl apply -f k8s/development-team/$dir/
done
```

## Pré-requisitos

- **OpenClaw** rodando no cluster (deployment `openclaw`, service expondo porta 18789).
- **ConfigMaps de scripts** criados com `make configmaps-pipeline` (po-scripts, architect-draft-scripts, etc.).
- **OPENCLAW_GATEWAY_WS** nos ConfigMaps de env dos triggers (já definido como `ws://openclaw.ai-agents.svc.cluster.local:18789`). Se o Service do OpenClaw tiver outro nome/porta, edite os configmap-env.
- **Secrets**: `clawdevs-github-secret` (opcional) para gh nos pods; `openclaw-telegram` para o gateway; `orchestrator-slack` para o consumer Slack.

## Referências

- [docs/agents-devs/openclaw-first-triggers.md](../docs/agents-devs/openclaw-first-triggers.md) — papel dos triggers e ferramentas dos agentes
- [docs/openclaw-sub-agents-architecture.md](../docs/openclaw-sub-agents-architecture.md)
- [docs/38-redis-streams-estado-global.md](../docs/38-redis-streams-estado-global.md)
