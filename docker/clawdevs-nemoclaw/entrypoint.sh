#!/usr/bin/env bash

set -euo pipefail

mkdir -p "${HOME}" /data/nemoclaw

# Check if NemoClaw runtime is valid
nemoclaw_runtime_ok() {
  command -v nemoclaw >/dev/null 2>&1 || return 1
  nemoclaw --help >/dev/null 2>&1 || return 1
  command -v openshell >/dev/null 2>&1 || return 1
  openshell --help >/dev/null 2>&1 || return 1
  return 0
}

# Try to install NemoClaw + OpenShell if not available
if ! nemoclaw_runtime_ok; then
  echo "[entrypoint] Installing NemoClaw and OpenShell..."

  # Download and run the official NVIDIA installer
  if ! curl -fsSL "https://www.nvidia.com/nemoclaw.sh" 2>/dev/null | bash -s -- --non-interactive 2>/dev/null; then
    echo "[entrypoint] NVIDIA installer failed. Attempting fallback installation..."

    # Fallback 1: try official NVIDIA OpenShell installer
    if ! command -v openshell >/dev/null 2>&1; then
      echo "[entrypoint] Trying official OpenShell installer..."
      if curl -LsSf https://raw.githubusercontent.com/NVIDIA/OpenShell/main/install.sh 2>/dev/null | OPENSHELL_VERSION=dev sh 2>/dev/null; then
        echo "[entrypoint] OpenShell installed from official installer"
      else
        echo "[entrypoint] Official installer failed. Trying GitHub releases..."

        # Fallback 2: install openshell CLI from GitHub releases
        OPENSHELL_VERSION="latest"
        OPENSHELL_URL="https://github.com/NVIDIA/OpenShell/releases/download/${OPENSHELL_VERSION}/openshell-linux-x64"

        if curl -fsSL "${OPENSHELL_URL}" -o /tmp/openshell 2>/dev/null; then
          chmod +x /tmp/openshell
          mv /tmp/openshell /usr/local/bin/openshell
          echo "[entrypoint] OpenShell installed from GitHub releases"
        else
          echo "[entrypoint] WARNING: Could not install OpenShell. Continuing without it..."
        fi
      fi
    fi
  fi
fi

# Verify critical components
if ! command -v nemoclaw >/dev/null 2>&1; then
  echo "[entrypoint] ERROR: NemoClaw not installed" >&2
  exit 1
fi

export NEMOCLAW_SANDBOX_NAME="${NEMOCLAW_SANDBOX_NAME:-clawdevs-ai}"
export NEMOCLAW_PROVIDER="${NEMOCLAW_PROVIDER:-ollama}"
export NEMOCLAW_MODEL="${NEMOCLAW_MODEL:-mistral}"
export NEMOCLAW_POLICY_MODE="${NEMOCLAW_POLICY_MODE:-skip}"

# Run onboarding only once with proper state management
ONBOARD_DONE_FILE="/data/nemoclaw/.onboarding-done"
if [ ! -f "${ONBOARD_DONE_FILE}" ]; then
  echo "[entrypoint] Running NemoClaw onboarding..."
  if nemoclaw onboard 2>/dev/null; then
    touch "${ONBOARD_DONE_FILE}"
    echo "[entrypoint] Onboarding completed successfully"
  else
    echo "[entrypoint] Onboarding failed, but continuing anyway..."
    touch "${ONBOARD_DONE_FILE}"
  fi
else
  echo "[entrypoint] Onboarding already completed"
fi

echo "[entrypoint] Starting NemoClaw bridge service..."
exec /opt/nemoclaw-bridge-venv/bin/uvicorn bridge:app --host 0.0.0.0 --port 18789 --app-dir /opt/nemoclaw-bridge
