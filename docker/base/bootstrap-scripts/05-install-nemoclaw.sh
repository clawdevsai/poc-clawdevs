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

install_nemoclaw_official() {
  # Official installer installs NemoClaw + OpenShell on the host.
  curl -fsSL "https://www.nvidia.com/nemoclaw.sh" | bash
}

install_openshell_fallback() {
  # Fallback: install openshell CLI
  if command -v openshell >/dev/null 2>&1; then
    return 0
  fi

  # Try official installer first
  echo "[bootstrap] Trying official OpenShell installer..."
  if curl -LsSf https://raw.githubusercontent.com/NVIDIA/OpenShell/main/install.sh 2>/dev/null | OPENSHELL_VERSION=dev sh 2>/dev/null; then
    echo "[bootstrap] OpenShell installed from official installer"
    return 0
  fi

  # Fallback to GitHub releases
  echo "[bootstrap] Trying GitHub releases..."
  OPENSHELL_VERSION="latest"
  OPENSHELL_URL="https://github.com/NVIDIA/OpenShell/releases/download/${OPENSHELL_VERSION}/openshell-linux-x64"

  if curl -fsSL "${OPENSHELL_URL}" -o /tmp/openshell 2>/dev/null; then
    chmod +x /tmp/openshell
    mv /tmp/openshell /usr/local/bin/openshell
    echo "[bootstrap] OpenShell installed from GitHub releases"
    return 0
  else
    echo "[bootstrap] WARNING: Could not install OpenShell"
    return 1
  fi
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

  # Try official installer first
  if install_nemoclaw_official; then
    echo "[bootstrap] NemoClaw installed successfully"
  else
    echo "[bootstrap] Official installer failed, trying fallback..."
    install_openshell_fallback || true
  fi

  touch "${NEMOCLAW_STAMP}"
fi

# Final validation - only nemoclaw is critical for bootstrap
if ! command -v nemoclaw >/dev/null 2>&1; then
  echo "[bootstrap] ERROR: NemoClaw failed to install" >&2
  exit 1
fi

if nemoclaw_runtime_ok; then
  echo "[bootstrap] NemoClaw/OpenShell fully operational"
else
  echo "[bootstrap] WARNING: NemoClaw is available but OpenShell is not. Some features may be limited."
fi
