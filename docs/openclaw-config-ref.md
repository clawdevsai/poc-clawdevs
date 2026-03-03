# Config OpenClaw — referência (tudo no K8s)

O gateway OpenClaw, Telegram, Slack e Ollama rodam **dentro do cluster**. A configuração está toda em **k8s/**.

## Onde está a configuração

| O que | Onde no K8s |
|-------|---------------|
| Config do gateway (openclaw.json) | `k8s/management-team/openclaw/configmap.yaml` (ConfigMap `openclaw-config`) |
| SOUL dos agentes (CEO, PO, etc.) | `k8s/management-team/soul/configmap.yaml`, `k8s/development-team/soul/configmap.yaml` |
| Templates MEMORY.md e working-buffer | `k8s/management-team/openclaw/workspace-ceo-configmap.yaml` |
| Secrets (Telegram, Slack) | Secret no namespace `ai-agents` (ver `.env.example` e `scripts/k8s-openclaw-secret-from-env.sh`) |
| Example config local (emergência/debug) | `k8s/management-team/openclaw/openclaw.local.json5.example` |

## Como subir e usar

1. No cluster: `make up` (ou aplique os YAMLs em `k8s/`).
2. Tokens no cluster: `./scripts/k8s-openclaw-secret-from-env.sh` e `kubectl rollout restart deployment/openclaw -n ai-agents`.
3. Logs: `kubectl logs -n ai-agents -l app=openclaw -f --tail=100`.

Para Slack, canal #all-clawdevsai, pairing, múltiplos agentes e fluxo de tema, ver [42-slack-tokens-setup.md](42-slack-tokens-setup.md), [43-fluxo-slack-all-clawdevsai-tema-analise.md](43-fluxo-slack-all-clawdevsai-tema-analise.md).

## Editar SOUL / MEMORY / working-buffer

Edite os arquivos nos ConfigMaps em **k8s/** (soul-management-agents, soul-development-agents, workspace-ceo-configmap) e aplique com `kubectl apply -f k8s/...`.
