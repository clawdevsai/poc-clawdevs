# Kubernetes — ClawDevs

Estrutura por times e integração com **Ollama GPU** por padrão. Provedor de LLM por agente configurável em `llm-providers-configmap.yaml` (opções: ollama_local, ollama_cloud, openrouter, qwen_oauth, moonshot_ai, openai, huggingface_inference).

## Estrutura de pastas

| Pasta | Conteúdo |
|-------|----------|
| **ollama/** | Deployment Ollama GPU, Service, PVC. Inferência local no cluster. |
| **management-team/** | CEO e PO — gateway OpenClaw com Telegram, Redis, Ollama (e nuvem opcional). |
| **development-team/** | DevOps, Architect, Developer, QA, CyberSec, UX, DBA — config e NetworkPolicy (100% offline). |
| **governance-team/** | Governance Proposer — config e deployment (CPU, sessão isolada). |
| **redis/** | Redis (deployment, service), **streams-configmap.yaml** (nomes dos streams e chaves), **job-init-streams.yaml** (opcional, cria consumer groups). Ref: [docs/38-redis-streams-estado-global.md](docs/38-redis-streams-estado-global.md). |
| **openclaw/** | Gateway único (Fase 0): Dockerfile, entrypoint, configmap com todos os agentes, deployment. |
| **limits.yaml** | ResourceQuota (65% hardware) e LimitRange por container (Fase 0 — 004). |

## Ordem de apply (Fase 0)

```bash
kubectl apply -f namespace.yaml
kubectl apply -f limits.yaml
kubectl apply -f redis/deployment.yaml
kubectl apply -f redis/streams-configmap.yaml
# Opcional: criar streams e consumer group (uma vez) — kubectl apply -f redis/job-init-streams.yaml
kubectl apply -f ollama/deployment.yaml
kubectl apply -f llm-providers-configmap.yaml
# Secret Telegram: kubectl create secret generic openclaw-telegram -n ai-agents --from-literal=TELEGRAM_BOT_TOKEN='...' --from-literal=TELEGRAM_CHAT_ID='...'
kubectl apply -f openclaw/configmap.yaml
kubectl apply -f openclaw/workspace-ceo-configmap.yaml
kubectl apply -f openclaw/deployment.yaml
```

Ou use `make up` (aplica o fluxo acima e usa a imagem buildada com `make openclaw-image`).

## Provedor de LLM por agente

ConfigMap `clawdevs-llm-providers`: chaves `agent_ceo`, `agent_po`, `agent_devops`, etc. Valores: `ollama_local` (padrão, Ollama GPU no cluster) | `ollama_cloud` | `openrouter` | `qwen_oauth` | `moonshot_ai` | `openai` | `huggingface_inference`. Para usar nuvem, criar secrets correspondentes no namespace (OPENROUTER_API_KEY, OPENAI_API_KEY, etc.) e ajustar o modelo no config do OpenClaw (ex.: `openrouter/model-id`).

## Layout por time

- **Management (CEO, PO):** servem Telegram; podem usar Ollama GPU ou nuvem. Config e deployment alternativos em `management-team/`.
- **Development (time técnico):** 100% offline por padrão; Ollama GPU. Config fragmento em `development-team/`; NetworkPolicy para pod dedicado.
- **Governance:** Governance Proposer em `governance-team/` (replicas: 0 por padrão; ativar sob demanda).

Ref: [docs/openclaw-sub-agents-architecture.md](docs/openclaw-sub-agents-architecture.md), [docs/04-infraestrutura.md](docs/04-infraestrutura.md), [docs/07-configuracao-e-prompts.md](docs/07-configuracao-e-prompts.md).
