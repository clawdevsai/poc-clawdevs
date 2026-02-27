# Management Team — CEO e PO

Gateway OpenClaw para **CEO** e **Product Owner**: interface com o Diretor via **Telegram**, estado em Redis, inferência via **Ollama GPU** no cluster (padrão) ou provedores em nuvem (OpenRouter, OpenAI, Ollama Cloud, Qwen, Moonshot AI, Hugging Face).

- **CEO:** único agente que recebe mensagens do Telegram; delega ao PO e ao time técnico via sub-agents.
- **PO:** backlog, priorização, rascunhos para o Architect.

## Provedor de LLM por agente

Cada agente pode usar um provedor diferente. Configuração em `k8s/llm-providers-configmap.yaml` (chaves `agent_ceo`, `agent_po`). Valores: `ollama_local` | `ollama_cloud` | `openrouter` | `qwen_oauth` | `moonshot_ai` | `openai` | `huggingface_inference`. Padrão: **ollama_local** (Ollama GPU no cluster).

## Apply

Ordem (após namespace, Redis, Ollama e `clawdevs-llm-providers`):

```bash
kubectl apply -f k8s/management-team/configmap.yaml
kubectl apply -f k8s/management-team/workspace-ceo-configmap.yaml
kubectl apply -f k8s/management-team/deployment.yaml
# Secret Telegram: kubectl apply -f k8s/management-team/secret.yaml
```

Ref: [docs/openclaw-sub-agents-architecture.md](../docs/openclaw-sub-agents-architecture.md), [docs/37-deploy-fase0-telegram-ceo-ollama.md](../docs/37-deploy-fase0-telegram-ceo-ollama.md).
