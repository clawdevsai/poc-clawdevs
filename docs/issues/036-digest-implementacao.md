# Digest diário (036) — Implementação no repositório

**Script:** [scripts/digest_daily.py](../../scripts/digest_daily.py) — lê o stream `digest:daily` (configurável via `STREAM_DIGEST` no phase2-config), gera Markdown em `DIGEST_OUTPUT_DIR` (ex.: `docs/agents-devs/digest-YYYY-MM-DD.md`). Opcional: envia para Telegram se `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID` estiverem definidos.

**CronJob:** [k8s/orchestrator/cronjob-digest-daily.yaml](../../k8s/orchestrator/cronjob-digest-daily.yaml) — agenda diária 18:00 UTC; usa ConfigMap `orchestrator-scripts` (com `digest_daily.py`) e `orchestrator-env` (ex.: `DIGEST_OUTPUT_DIR`, Redis).

**Alertas imediatos** (segurança, $5/dia, freio de mão) não passam pelo digest — são enviados no momento pelo gateway/orquestrador (ex.: [scripts/consumer_orchestrator_events_slack.py](../../scripts/consumer_orchestrator_events_slack.py), gateway FinOps).

Ref: [036-digest-diario-alertas.md](036-digest-diario-alertas.md), [06-operacoes.md](../06-operacoes.md), [05-seguranca-e-etica.md](../05-seguranca-e-etica.md).
