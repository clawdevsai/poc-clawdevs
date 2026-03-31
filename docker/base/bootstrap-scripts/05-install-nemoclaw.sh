#!/usr/bin/env bash

set -euo pipefail

NEMOCLAW_STAMP="${OPENCLAW_STATE_DIR}/backlog/status/.nemoclaw-installed"

nemoclaw_runtime_ok() {
  command -v nemoclaw >/dev/null 2>&1 || return 1
  nemoclaw --help >/dev/null 2>&1 || return 1
  command -v openshell >/dev/null 2>&1 || return 1
  openshell --help >/dev/null 2>&1 || return 1
  return 0
}

install_nemoclaw() {
  # Official installer installs NemoClaw + OpenShell on the host.
  # In container mode this is mostly for consistency/testing; real host-side
  # installs should be done outside Docker.
  curl -fsSL "https://www.nvidia.com/nemoclaw.sh" | bash
}

if nemoclaw_runtime_ok; then
  echo "[bootstrap] nemoclaw/openshell ja instalados e runtime valido, pulando instalacao"
  touch "${NEMOCLAW_STAMP}"
else
  if command -v nemoclaw >/dev/null 2>&1; then
    echo "[bootstrap] nemoclaw detectado mas runtime invalido; reinstalando"
  else
    echo "[bootstrap] nemoclaw ausente; instalando"
  fi
  install_nemoclaw
  touch "${NEMOCLAW_STAMP}"
fi

if ! nemoclaw_runtime_ok; then
  echo "NemoClaw/OpenShell nao foram instalados corretamente" >&2
  exit 1
fi
