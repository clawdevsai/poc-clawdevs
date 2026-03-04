# Orquestrador — automação no cluster (Fase 3)

Recursos do orquestrador: digest diário, timers cosméticos, loop de consenso e consumidor de eventos para Slack.

- **Consumidor Slack:** Deployment que lê `orchestrator:events` e posta no Slack.
- **Autonomia (017, 032–036):** Deployment `orchestrator-autonomy` — loop contínuo: orçamento de degradação, loop de consenso pré-freio, freio de mão, digest/alertas.
- **Disjuntor (127):** Deployment `orchestrator-disjuntor` — consome stream `draft_rejected`; 3 rejeições consecutivas → RAG health check e descongelar.
- **Contingência cluster acéfalo (124):** Deployments `acefalo-monitor` e `acefalo-heartbeat`. Heartbeat atualiza `ceo:last_strategy_ts` quando há conectividade; monitor dispara contingência (branch efêmera, pausa) após 5 min sem heartbeat e retomada automática após 3 health checks OK. Requer `make configmap-acefalo` antes de aplicar.
- **Digest diário:** CronJob — gera `digest-YYYY-MM-DD.md` (18:00 UTC).
- **Timers cosméticos:** CronJob — `cosmetic_omission.py check-timers` e `write-qa-file` a cada 10 min.
- **Loop de consenso:** lógica dentro de `orchestrator_autonomy.py` (emite `consensus_loop_requested`; pilot via `set_consensus_pilot_result.py`).
- **Curador (merge de .learnings/):** CronJob — em sessão isolada (02:00 UTC), envia prompt de curadoria ao Architect para ler `/workspace/.learnings/`, consolidar e injetar em SOUL.md/AGENTS.md/TOOLS.md. Requer ConfigMaps `curator-env` e `curator-scripts`; imagem `openclaw-gateway:local`. Ref: [10-self-improvement-agentes.md](../03-agents/10-self-improvement-agentes.md).

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

Ref: [06-operacoes.md](06-operacoes.md).
