#!/bin/sh
# Curador: envia prompt de curadoria ao Architect em sessão isolada.
# Requer OPENCLAW_GATEWAY_WS; opcional OPENCLAW_GATEWAY_TOKEN, OPENCLAW_ARCHITECT_SESSION_KEY.
set -e
SESSION_KEY="${OPENCLAW_ARCHITECT_SESSION_KEY:-agent:architect:main}"
if [ -z "$OPENCLAW_GATEWAY_WS" ]; then
  echo "OPENCLAW_GATEWAY_WS not set" >&2
  exit 1
fi
# Build JSON params (message from file)
node -e "
const fs = require('fs');
const msg = fs.readFileSync('/scripts/curator-prompt.md', 'utf8');
const params = { sessionKey: process.env.OPENCLAW_ARCHITECT_SESSION_KEY || 'agent:architect:main', message: msg };
console.log(JSON.stringify(params));
" > /tmp/curator-params.json
if [ -n "$OPENCLAW_GATEWAY_TOKEN" ]; then
  openclaw gateway call sessions.send --url "$OPENCLAW_GATEWAY_WS" --params "$(cat /tmp/curator-params.json)" --token "$OPENCLAW_GATEWAY_TOKEN" --json
else
  openclaw gateway call sessions.send --url "$OPENCLAW_GATEWAY_WS" --params "$(cat /tmp/curator-params.json)" --json
fi
