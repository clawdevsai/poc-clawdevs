# DevOps não responde no Slack — checklist

Quando você menciona **@DevOps** no canal (ou envia DM) e o agente não responde, verifique os pontos abaixo.

## 1. Conta DevOps no gateway

No modelo **multi-account** (1 app Slack por agente), o DevOps só recebe mensagens se existir a **conta** `devops` com tokens no cluster.

- **No `.env`** (raiz do repo): defina `DEVOPS_SLACK_APP_TOKEN` e `DEVOPS_SLACK_BOT_TOKEN` (tokens do app **DevOps** em [api.slack.com/apps](https://api.slack.com/apps)).
- **No cluster:** rode `./scripts/cluster/secrets-from-env.sh` e depois `kubectl rollout restart deployment/openclaw -n ai-agents`.
- **Validar:** use o script de diagnóstico: `./scripts/ops/slack-devops-check.sh` (verifica se a config do pod tem a conta `devops`).

Se você usa **um único app** (só `SLACK_APP_TOKEN` / `SLACK_BOT_TOKEN`), todas as mensagens vêm com `accountId` desse app e só o agente vinculado a ele responde; para o DevOps responder, é preciso um **app Slack separado** para o DevOps e os dois tokens no Secret.

## 2. App DevOps no canal

O app do DevOps (bot) precisa estar **no canal** onde você escreve (ex.: #all-clawdevsai).

- No Slack: **Integrações** (ou configurações do canal) → **Adicionar apps** → escolher o app do DevOps (ex.: "DevOps APP" ou o nome que você deu) e adicionar ao canal.
- Se o app não estiver no canal, ele **não recebe** o evento `app_mention` e o gateway nunca invoca o agente DevOps.

## 3. Scopes e eventos do app DevOps

Em [api.slack.com/apps](https://api.slack.com/apps) → app do DevOps → **OAuth & Permissions** → **Bot Token Scopes**, inclua:

- **`chat:write`** — para enviar respostas
- **`channels:read`** — para resolver canal (evita `missing_scope` nos logs)
- **`channels:history`** — para ler mensagens do canal
- **`app_mentions:read`** — para receber menções @DevOps
- **`users:read`** (recomendado) — para resolver usuários

Em **Event Subscriptions** (ou **Subscribe to bot events**):

- **`app_mention`** — evento quando alguém menciona o bot no canal

Depois: **Reinstall to Workspace** para aplicar os scopes.

## 4. Menção correta

Ao escrever no canal, use a **menção real** ao bot (selecionando o app do DevOps no autocomplete ao digitar @). Se você digitar só `@DevOps` como texto e não escolher o bot na lista, o Slack pode não enviar o evento para o app certo.

## 5. missing_scope nos logs

Se aparecer **`channel resolve failed; using config entries. Error: An API error occurred: missing_scope`**, um ou mais apps Slack (incluindo o do DevOps) estão sem o scope **`channels:read`**. O gateway continua usando a config do canal, mas é recomendável adicionar `channels:read` (e `channels:history`) em cada app em [api.slack.com/apps](https://api.slack.com/apps) → OAuth & Permissions → Bot Token Scopes, depois **Reinstall to Workspace**.

## 6. Logs e Ollama

- **Logs do gateway:** `kubectl logs -n ai-agents deploy/openclaw -c gateway --tail=100`  
  Procure por `[devops]`, erros ou `missing_scope`. Se aparecer `[slack] [devops] starting provider`, o provider subiu; se após uma mensagem não houver atividade do devops, a mensagem pode não estar chegando (conta/canal/evento).
- **Ollama:** se o modelo estiver lento ou indisponível, o agente pode demorar ou não responder. Verifique: `kubectl get pods -n ai-agents -l app=ollama`.

## Resumo rápido

| Verificação | Ação |
|------------|------|
| Tokens DevOps no cluster | `DEVOPS_SLACK_APP_TOKEN` e `DEVOPS_SLACK_BOT_TOKEN` no `.env` → `./scripts/cluster/secrets-from-env.sh` → `kubectl rollout restart deployment/openclaw -n ai-agents` |
| App no canal | Adicionar o app do DevOps ao canal (ex.: #all-clawdevsai) em Integrações → Adicionar apps |
| Scopes | `chat:write`, `channels:read`, `channels:history`, `app_mentions:read`; evento `app_mention` |
| Menção | Usar @ e selecionar o bot do DevOps no autocomplete |

## 7. Exec tool não roda (agente "planeja" mas não executa)

Se o agente responde no Slack com um plano (ex.: "vou criar o repositório") mas **nunca executa** o comando, pode ser que o exec esteja bloqueado por aprovação.

- **Config correta** (aplicada em 2026-03-04): no `configmap.yaml` do OpenClaw, cada agente (exceto CEO) tem `tools.exec` com `host: "gateway"`, `security: "full"`, `ask: "off"`. Sem isso, o exec em ambiente headless fica em `approval-pending` e o fallback é deny.
- **Verificar:** `kubectl logs -n ai-agents deploy/openclaw -c gateway --tail=200 | grep -i 'exec\|approval\|deny'`.
- Ref: [investigacao-devops-repos-github.md](investigacao-devops-repos-github.md) — seção "Exec bloqueado por aprovação".

## Referências

- [42-slack-tokens-setup.md](../07-operations/42-slack-tokens-setup.md) — scopes e Event Subscriptions
- [developer-nao-responde-slack.md](developer-nao-responde-slack.md) — mesmo checklist para Developer
- [investigacao-slack-nada-acontece.md](issues/investigacao-slack-nada-acontece.md) — multi-account e tokens
- [investigacao-devops-repos-github.md](investigacao-devops-repos-github.md) — investigação completa de criação de repos
