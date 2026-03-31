#!/usr/bin/env bash

set -euo pipefail

NEMOCLAW_STATE_DIR="${NEMOCLAW_STATE_DIR:-/data/nemoclaw}"
OPENCLAW_STATE_DIR="${OPENCLAW_STATE_DIR:-${NEMOCLAW_STATE_DIR}}"

mkdir -p "${NEMOCLAW_STATE_DIR}/backlog/status"

install_nemoclaw() {
  if command -v nemoclaw >/dev/null 2>&1; then
    echo "[entrypoint] nemoclaw ja instalado"
    return 0
  fi
  echo "[entrypoint] instalando NemoClaw..."
  curl -fsSL https://www.nvidia.com/nemoclaw.sh | bash
}

install_nemoclaw

if [ -d "/opt/bootstrap-scripts" ]; then
  for script in /opt/bootstrap-scripts/00-env.sh \
                /opt/bootstrap-scripts/01-deps.sh \
                /opt/bootstrap-scripts/02-web-tools.sh \
                /opt/bootstrap-scripts/03-gh-auth.sh \
                /opt/bootstrap-scripts/04-repo-tools.sh \
                /opt/bootstrap-scripts/06-dirs.sh \
                /opt/bootstrap-scripts/07-agent-workspaces.sh \
                /opt/bootstrap-scripts/08-git-hooks.sh \
                /opt/bootstrap-scripts/10-background-services.sh; do
    if [ -f "${script}" ]; then
      echo "[entrypoint] executando $(basename "${script}")"
      source "${script}"
    fi
  done
fi

exec "$@"
