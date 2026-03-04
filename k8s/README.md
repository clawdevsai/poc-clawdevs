# Kubernetes — ClawDevs

Recursos para rodar o ecossistema no cluster (Minikube ou outro). Arquitetura **openclaw-first**: o Gateway OpenClaw roda os agentes; os pods do pipeline são **triggers** que consomem Redis e enviam mensagens ao Gateway.

## Estrutura

| Pasta | Conteúdo |
|-------|----------|
| **shared/infra/** | Namespace, limites, llm-providers |
| **shared/development-team/** | NetworkPolicy, segredos, componentes compartilhados (Audit, Gateway-adapter, PO) |
| **redis/** | Redis (deployment, service), streams-configmap, job-init-streams |
| **ollama/** | Ollama GPU (deployment, service, PVC) |
| **management-team/** | OpenClaw (gateway), SOUL management, config |
| **development-team/** | Agentes individuais (Architect, Developer, QA, CyberSec, UX, DBA, DevOps) com suas SOULs e IDs separados |
| **orchestrator/** | Consumer Slack (orchestrator:events), CronJobs (audit-queue, digest, cosmetic) |
| **security/** | Fase 2: phase2-config, egress-whitelist, token rotation, url-sandbox, quarentena |
| **governance-team/** | Governance Proposer (opcional) |
| **sandbox/** | Job quarentena pipeline (opcional) |

## Ordem de apply (recomendada)

Use **`make up`** para subir o núcleo (namespace, Redis, Ollama, OpenClaw, phase2, orchestrator). O `make up` inclui **init-memory**: cria a estrutura de memória por agente (`/workspace/{agent}/memory/`), memória compartilhada (`/workspace/shared/memory/`) e `.learnings/` no workspace. Se o Job init-memory falhar (ex.: PVC ainda não bound), rode **`make init-memory`** manualmente após o primeiro up.

Para o pipeline completo (triggers que chamam o Gateway):

```bash
make configmaps-pipeline
# Aplica infra e shared
kubectl apply -f k8s/shared/infra/
kubectl apply -f k8s/shared/development-team/
kubectl apply -f k8s/shared/development-team/components/

# Aplica cada agente individualmente
for agent in architect developer qa cybersec ux dba devops; do
  kubectl apply -R -f k8s/development-team/$agent/
done
```


## Workspace compartilhado (pasta no host)

Para usar uma **pasta física na sua máquina** como workspace dos agentes (ver soul, memória, skills e repositórios clonados): [management-team/openclaw/README.md](management-team/openclaw/README.md) — passos do `minikube mount`, PV/PVC e estrutura da pasta.

## Pré-requisitos

- **OpenClaw** rodando no cluster (deployment `openclaw`, service expondo porta 18789).
- **ConfigMaps de scripts** criados com `make configmaps-pipeline` (po-scripts, architect-draft-scripts, etc.).
- **OPENCLAW_GATEWAY_WS** nos ConfigMaps de env dos triggers (já definido como `ws://openclaw.ai-agents.svc.cluster.local:18789`). Se o Service do OpenClaw tiver outro nome/porta, edite os configmap-env.
- **Secrets**: `clawdevs-github-secret` (opcional) para gh nos pods; `openclaw-telegram` para o gateway; `orchestrator-slack` para o consumer Slack.

## Referências

- [docs/agents-devs/openclaw-first-triggers.md](../docs/agents-devs/openclaw-first-triggers.md) — papel dos triggers e ferramentas dos agentes
- [docs/openclaw-sub-agents-architecture.md](../docs/openclaw-sub-agents-architecture.md)
- [docs/38-redis-streams-estado-global.md](../docs/38-redis-streams-estado-global.md)
