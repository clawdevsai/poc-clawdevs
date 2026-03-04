# Orquestrador — automação no cluster (Fase 3)

Recursos do orquestrador: digest diário, timers cosméticos, loop de consenso e consumidor de eventos para Slack.

- **Consumidor Slack:** Deployment que lê `orchestrator:events` e posta no Slack.
- **Digest diário:** CronJob — gera `digest-YYYY-MM-DD.md` (18:00 UTC).
- **Timers cosméticos:** CronJob — `cosmetic_omission.py check-timers` e `write-qa-file` a cada 10 min.
- **Loop de consenso:** CronJob — `consensus_loop_runner.py --once` a cada 2 min.
- **Curador (merge de .learnings/):** CronJob — em sessão isolada (02:00 UTC), envia prompt de curadoria ao Architect para ler `/workspace/.learnings/`, consolidar e injetar em SOUL.md/AGENTS.md/TOOLS.md. Requer ConfigMaps `curator-env` e `curator-scripts`; imagem `openclaw-gateway:local`. Ref: docs/03-agents/10-self-improvement-agentes.md.

## Pré-requisitos

1. **ConfigMap orchestrator-scripts:** `make orchestrator-configmap`
2. **ConfigMap orchestrator-env:** em `configmap-env.yaml`
3. **Secret orchestrator-slack** (opcional): app e canal **próprios** do orquestrador. Chaves no Secret: `SLACK_WEBHOOK_URL` ou `SLACK_BOT_TOKEN` + `SLACK_ALERTS_CHANNEL_ID`. Para rodar scripts localmente, use `ORCHESTRATOR_SLACK_WEBHOOK_URL` / `ORCHESTRATOR_SLACK_BOT_TOKEN` / `ORCHESTRATOR_SLACK_ALERTS_CHANNEL_ID` no `.env`.

```bash
kubectl create secret generic orchestrator-slack -n ai-agents \
  --from-literal=SLACK_WEBHOOK_URL='https://hooks.slack.com/services/...'
```

## Aplicar

```bash
make orchestrator-configmap
kubectl apply -f k8s/orchestrator/
```

## Migração desde phase3

Os recursos que estavam em `k8s/phase3/` foram movidos para `k8s/orchestrator/`. Se você já tinha o Secret `phase3-slack`, crie um equivalente `orchestrator-slack` com as mesmas chaves (`SLACK_WEBHOOK_URL` ou `SLACK_BOT_TOKEN` + `SLACK_ALERTS_CHANNEL_ID`).

Ref: [docs/06-operacoes.md](../../docs/06-operacoes.md).
