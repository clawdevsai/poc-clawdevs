#!/bin/sh
# Injeta TELEGRAM_CHAT_ID e Slack (allowFrom, enabled) na config e inicia o gateway.
# Telegram: só CEO. Slack: todos os agentes; habilitado quando SLACK_APP_TOKEN e SLACK_BOT_TOKEN estão definidos.
set -e
CONFIG_SRC="/config/openclaw.json"
CONFIG_RUN="/tmp/openclaw.json"

# 1) Telegram
if [ -n "$TELEGRAM_CHAT_ID" ]; then
  sed "s/__TELEGRAM_CHAT_ID__/$TELEGRAM_CHAT_ID/g" "$CONFIG_SRC" > "$CONFIG_RUN"
else
  sed 's/"allowFrom": \["__TELEGRAM_CHAT_ID__"\]/"allowFrom": []/' "$CONFIG_SRC" | \
  sed 's/"dmPolicy": "allowlist"/"dmPolicy": "pairing"/' > "$CONFIG_RUN"
fi

# 2) Slack: habilitar e injetar allowFrom (Director + SLACK_ALLOWED_USER_IDS) quando tokens presentes
if [ -n "$SLACK_APP_TOKEN" ] && [ -n "$SLACK_BOT_TOKEN" ]; then
  # ConfigMap tem quebra de linha entre "slack": { e "enabled": false; substituir na região do bloco slack
  sed '/"slack": {/,/}/ s/"enabled": false/"enabled": true/' "$CONFIG_RUN" > "$CONFIG_RUN.tmp" && mv "$CONFIG_RUN.tmp" "$CONFIG_RUN"
  # build allowFrom JSON: SLACK_DIRECTOR_USER_ID + SLACK_ALLOWED_USER_IDS (comma-separated)
  ALLOW_FROM_JSON=""
  [ -n "$SLACK_DIRECTOR_USER_ID" ] && ALLOW_FROM_JSON="\"$SLACK_DIRECTOR_USER_ID\""
  if [ -n "$SLACK_ALLOWED_USER_IDS" ]; then
    for id in $(echo "$SLACK_ALLOWED_USER_IDS" | tr ',' ' '); do
      id=$(echo "$id" | tr -d ' ')
      [ -n "$id" ] && ALLOW_FROM_JSON="${ALLOW_FROM_JSON:+$ALLOW_FROM_JSON,}\"$id\""
    done
  fi
  if [ -n "$ALLOW_FROM_JSON" ]; then
    sed "s/__SLACK_ALLOW_FROM_JSON__/$ALLOW_FROM_JSON/g" "$CONFIG_RUN" > "$CONFIG_RUN.tmp" && mv "$CONFIG_RUN.tmp" "$CONFIG_RUN"
  else
    sed 's/\[__SLACK_ALLOW_FROM_JSON__\]/[]/' "$CONFIG_RUN" > "$CONFIG_RUN.tmp" && mv "$CONFIG_RUN.tmp" "$CONFIG_RUN"
    # only Slack block: switch to pairing when no allowFrom
    sed '/"mode": "socket"/,/}/ s/"dmPolicy": "allowlist"/"dmPolicy": "pairing"/' "$CONFIG_RUN" > "$CONFIG_RUN.tmp" && mv "$CONFIG_RUN.tmp" "$CONFIG_RUN"
  fi
else
  sed 's/\[__SLACK_ALLOW_FROM_JSON__\]/[]/' "$CONFIG_RUN" > "$CONFIG_RUN.tmp" && mv "$CONFIG_RUN.tmp" "$CONFIG_RUN"
fi

# 3) Canal #all-clawdevsai (ou outro): ID configurável por SLACK_ALL_CLAWDEVSAI_CHANNEL_ID (default CDAHISCLSQKC)
CHAN_ID="${SLACK_ALL_CLAWDEVSAI_CHANNEL_ID:-CDAHISCLSQKC}"
sed "s/__SLACK_ALL_CLAWDEVSAI_CHANNEL_ID__/$CHAN_ID/g" "$CONFIG_RUN" > "$CONFIG_RUN.tmp" && mv "$CONFIG_RUN.tmp" "$CONFIG_RUN"

# 4) Contas Slack por agente (multi-account): injeta accounts.<id> via Node (evita falha do sed com JSON longo)
if command -v node >/dev/null 2>&1; then
  CONFIG_RUN="$CONFIG_RUN" node -e "
    const fs = require('fs');
    const path = process.env.CONFIG_RUN || '/tmp/openclaw.json';
    const config = JSON.parse(fs.readFileSync(path, 'utf8'));
    if (!config.channels || !config.channels.slack) process.exit(0);
    const agents = [
      ['ceo','CEO'],['po','PO'],['devops','DEVOPS'],['architect','ARCHITECT'],['developer','DEVELOPER'],
      ['qa','QA'],['cybersec','CYBERSEC'],['ux','UX'],['dba','DBA']
    ];
    const accounts = {};
    for (const [id, prefix] of agents) {
      const app = process.env[prefix + '_SLACK_APP_TOKEN'];
      const bot = process.env[prefix + '_SLACK_BOT_TOKEN'];
      if (app && bot) accounts[id] = { mode: 'socket', appToken: app, botToken: bot };
    }
    if (Object.keys(accounts).length > 0) {
      config.channels.slack.accounts = accounts;
      fs.writeFileSync(path, JSON.stringify(config, null, 2));
    }
  "
fi

export OPENCLAW_CONFIG_PATH="$CONFIG_RUN"
exec openclaw gateway --allow-unconfigured --port 18789 --bind lan
