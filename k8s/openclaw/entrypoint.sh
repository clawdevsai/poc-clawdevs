#!/bin/sh
# Injeta TELEGRAM_CHAT_ID na config e inicia o gateway.
set -e
CONFIG_SRC="/config/openclaw.json"
CONFIG_RUN="/tmp/openclaw.json"
if [ -n "$TELEGRAM_CHAT_ID" ]; then
  sed "s/__TELEGRAM_CHAT_ID__/$TELEGRAM_CHAT_ID/g" "$CONFIG_SRC" > "$CONFIG_RUN"
else
  sed 's/"allowFrom": \["__TELEGRAM_CHAT_ID__"\]/"allowFrom": []/' "$CONFIG_SRC" | \
  sed 's/"dmPolicy": "allowlist"/"dmPolicy": "pairing"/' > "$CONFIG_RUN"
fi
export OPENCLAW_CONFIG_PATH="$CONFIG_RUN"
exec openclaw gateway --allow-unconfigured --port 18789 --bind lan
