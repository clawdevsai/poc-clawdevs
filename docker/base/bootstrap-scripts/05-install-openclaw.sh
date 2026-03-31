#!/usr/bin/env bash

set -euo pipefail

OPENCLAW_STAMP="${OPENCLAW_STATE_DIR}/backlog/status/.openclaw-installed"

openclaw_runtime_ok() {
  command -v openclaw >/dev/null 2>&1 || return 1
  openclaw --help >/dev/null 2>&1 || return 1
  return 0
}

install_openclaw() {
  if [ -n "${OPENCLAW_VERSION:-}" ]; then
    echo "[bootstrap] instalando openclaw versao ${OPENCLAW_VERSION}"
    npm install -g "openclaw@${OPENCLAW_VERSION}" 2>/dev/null || npm install -g openclaw
  else
    echo "[bootstrap] instalando openclaw (latest)"
    npm install -g openclaw
  fi
}

if openclaw_runtime_ok; then
  echo "[bootstrap] openclaw ja instalado e runtime valido, pulando instalacao"
  touch "${OPENCLAW_STAMP}"
else
  if command -v openclaw >/dev/null 2>&1; then
    echo "[bootstrap] openclaw detectado mas runtime invalido; reinstalando"
  else
    echo "[bootstrap] openclaw ausente; instalando"
  fi
  install_openclaw
  touch "${OPENCLAW_STAMP}"
fi

if ! openclaw_runtime_ok; then
  echo "OpenClaw nao foi instalado corretamente" >&2
  exit 1
fi
