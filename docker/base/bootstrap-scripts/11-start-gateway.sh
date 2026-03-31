#!/usr/bin/env bash

set -euo pipefail

OPENCLAW_GATEWAY_PORT="${OPENCLAW_GATEWAY_PORT:-18789}"

echo "[bootstrap] iniciando openclaw gateway na porta ${OPENCLAW_GATEWAY_PORT}"

if command -v openclaw >/dev/null 2>&1; then
  openclaw gateway start \
    --port "${OPENCLAW_GATEWAY_PORT}" \
    --state-dir "${OPENCLAW_STATE_DIR}" \
    &
  echo "[bootstrap] openclaw gateway iniciado (PID: $!)"
else
  echo "[bootstrap][error] openclaw nao encontrado no PATH" >&2
  exit 1
fi
