# Development Team — Pipeline (openclaw-first)

Pods que **consomem Redis** e **enviam mensagens ao OpenClaw Gateway**. Não rodam LLM; a lógica fica nos agentes do Gateway.

## Fluxo

| Stream / evento | Pod | Ação |
|-----------------|-----|------|
| cmd:strategy | **po** | Envia ao agente PO (criar issues, publicar draft.2.issue) |
| draft.2.issue | **architect-draft** | Envia ao Architect (aprovar → task:backlog ou rejeitar) |
| task:backlog | **developer** | Envia ao Developer (implementar; publicar code:ready) |
| code:ready | **revisao-pos-dev** | Envia aos 6 papéis (Architect, QA, CyberSec, DBA, UX, PO); merge → event:devops |
| event:devops | **devops-worker** | Envia ao DevOps (Deployed, feature_complete) |
| audit:queue | **audit-runner** | Envia a QA, DBA, CyberSec, UX (auditoria periódica) |

**gateway-redis-adapter**: serviço HTTP para o Gateway/agentes publicarem em Redis (POST /publish, /write-strategy).

## Pastas

| Pasta | Deployment | ConfigMap env | ConfigMap scripts (Makefile) |
|-------|------------|---------------|------------------------------|
| **po/** | po | po-env | po-scripts (`make configmap-po`) |
| **architect-draft/** | architect-draft | architect-draft-env | architect-draft-scripts |
| **developer/** | developer | developer-env | developer-scripts |
| **revisao-pos-dev/** | revisao-pos-dev | revisao-pos-dev-env | revisao-slot-scripts |
| **devops-worker/** | devops-worker | devops-worker-env | devops-worker-scripts |
| **audit-runner/** | audit-runner | audit-runner-env | audit-runner-scripts |
| **gateway-redis-adapter/** | gateway-redis-adapter | (configmap-env) | gateway-redis-adapter-scripts |

Todos os triggers precisam de **OPENCLAW_GATEWAY_WS** (já em cada configmap-env). Os scripts precisam do **openclaw** CLI no container ou de um bridge; hoje os pods usam imagem `python:3.12-slim` e os scripts chamam o Gateway via `openclaw_gateway_call.py` (que usa subprocess do CLI). Para produção, use uma imagem que inclua o OpenClaw CLI ou exponha um serviço de bridge.

## Apply

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
```

Deployments sobem com **replicas: 0**. Escale quando for usar:

```bash
kubectl scale deployment po -n ai-agents --replicas=1
kubectl scale deployment architect-draft -n ai-agents --replicas=1
# etc.
```

## GitHub

Secret `clawdevs-github-secret` (GITHUB_TOKEN, GH_TOKEN) é referenciado com `optional: true`. Crie para os agentes usarem `gh`:

```bash
kubectl create secret generic clawdevs-github-secret -n ai-agents \
  --from-literal=GITHUB_TOKEN="..." --from-literal=GH_TOKEN="..."
```

Ref: [secret-github.example.yaml](secret-github.example.yaml), [docs/20-ferramenta-github-gh.md](../docs/20-ferramenta-github-gh.md).
