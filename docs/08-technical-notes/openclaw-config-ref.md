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

## Modelos e Ollama

O modelo de cada agente (CEO, PO, etc.) deve ser um dos listados em `models.providers.ollama.models` no ConfigMap. Esse conjunto deve coincidir com os modelos disponíveis no Ollama do cluster (`GET /api/tags` no serviço Ollama). Se um agente estiver configurado com um modelo que não existe no cluster, o gateway retorna 404 e a sessão pode falhar. Ao adicionar um novo modelo na config, fazer `ollama pull <modelo>` no pod do Ollama antes de trocar o agente para esse modelo.

## Session store (persistência no K8s)

Para que as sessões do CEO (e demais agentes) sobrevivam a restarts do deployment, o ConfigMap `openclaw-config` define `session.store: "/workspace/.openclaw-session-store/{agentId}/sessions/sessions.json"`. O path fica no PVC `openclaw-workspace-pvc` (montado em `/workspace`). O initContainer `workspace-init` no deployment cria o diretório `/workspace/.openclaw-session-store`. Ver [investigacao-openclaw-pod.md](investigacao-openclaw-pod.md) §6.

## Compaction e memory flush (placeholder {agentId})

O bloco `compaction.memoryFlush.prompt` no `openclaw-config` instrui o agente a gravar decisões, lições e bloqueios em arquivos de memória antes da compactação. O prompt usa o placeholder **`{agentId}`** no path (ex.: `/workspace/{agentId}/memory/`). O **runtime do OpenClaw** substitui `{agentId}` pelo id do agente da sessão atual (ex.: `ceo`, `po`, `architect`), da mesma forma que em `session.store`. Assim cada agente grava em seu próprio diretório (ex.: `/workspace/ceo/memory/`, `/workspace/developer/memory/`). Se em testes o path não for substituído, conferir na documentação oficial do OpenClaw (compaction / memory flush) e, se necessário, usar no prompt a instrução explícita: "escreva no diretório memory/ do seu workspace (ex.: /workspace/ceo/memory/ para CEO)".

## Editar SOUL / MEMORY / working-buffer

Edite os arquivos nos ConfigMaps em **k8s/** (soul-management-agents, soul-development-agents, workspace-ceo-configmap) e aplique com `kubectl apply -f k8s/...`.
