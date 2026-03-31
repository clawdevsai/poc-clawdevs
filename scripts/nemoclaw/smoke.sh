#!/usr/bin/env bash

set -euo pipefail

SANDBOX_NAME="${SANDBOX_NAME:-clawdevs-ai}"

require_cmd() {
  local name="$1"
  command -v "$name" >/dev/null 2>&1 || {
    echo "ERRO: comando nao encontrado no PATH: $name" >&2
    exit 1
  }
}

require_cmd nemoclaw
require_cmd openshell

echo "[nemoclaw] status (json)"
nemoclaw "${SANDBOX_NAME}" status --json

echo ""
echo "[openshell] inference get"
openshell inference get

echo ""
echo "[hint] se travar/bloquear: openshell term (aprovar network policy)"
