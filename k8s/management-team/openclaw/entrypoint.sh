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

# 4) Conta Slack PO (multi-account): quando PO_SLACK_APP_TOKEN e PO_SLACK_BOT_TOKEN estão definidos, injeta accounts.po para @PO responder
if [ -n "$PO_SLACK_APP_TOKEN" ] && [ -n "$PO_SLACK_BOT_TOKEN" ]; then
  escape_json() { printf '%s' "$1" | tr -d '\n' | sed 's/\\/\\\\/g; s/"/\\"/g'; }
  PO_APP_ESC=$(escape_json "$PO_SLACK_APP_TOKEN")
  PO_BOT_ESC=$(escape_json "$PO_SLACK_BOT_TOKEN")
  PO_JSON="\"po\": { \"mode\": \"socket\", \"appToken\": \"$PO_APP_ESC\", \"botToken\": \"$PO_BOT_ESC\" }"
  PO_JSON_SED=$(printf '%s' "$PO_JSON" | sed 's/\\/\\\\/g; s/&/\\&/g')
  sed "s/\"accounts\": {}/\"accounts\": { $PO_JSON_SED }/" "$CONFIG_RUN" > "$CONFIG_RUN.tmp" && mv "$CONFIG_RUN.tmp" "$CONFIG_RUN"
fi

export OPENCLAW_CONFIG_PATH="$CONFIG_RUN"
exec openclaw gateway --allow-unconfigured --port 18789 --bind lan
