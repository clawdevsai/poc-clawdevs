#!/usr/bin/env bash

set -euo pipefail

mkdir -p "${HOME}" /data/nemoclaw

# Check if NemoClaw runtime is available
nemoclaw_runtime_ok() {
  command -v nemoclaw >/dev/null 2>&1 || return 1
  nemoclaw --version >/dev/null 2>&1 || return 1
  return 0
}

# Verify NemoClaw is installed (should be in base image)
echo "[entrypoint] Verifying NemoClaw installation..."
if nemoclaw_runtime_ok; then
  echo "[entrypoint] NemoClaw runtime found and operational"
else
  echo "[entrypoint] ERROR: NemoClaw not available in container" >&2
  echo "[entrypoint] Ensure NemoClaw is installed in the base Docker image" >&2
  exit 1
fi

export NEMOCLAW_SANDBOX_NAME="${NEMOCLAW_SANDBOX_NAME:-clawdevs-ai}"
export NEMOCLAW_PROVIDER="${NEMOCLAW_PROVIDER:-ollama}"
export NEMOCLAW_MODEL="${NEMOCLAW_MODEL:-mistral}"
export NEMOCLAW_POLICY_MODE="${NEMOCLAW_POLICY_MODE:-skip}"

# Initialize NemoClaw workspace if needed
if [ ! -d "/data/nemoclaw/workspace" ]; then
  echo "[entrypoint] Initializing NemoClaw workspace..."
  mkdir -p /data/nemoclaw/workspace
  echo "[entrypoint] Workspace initialized at /data/nemoclaw/workspace"
fi

# Run onboarding only once with proper state management
ONBOARD_DONE_FILE="/data/nemoclaw/.onboarding-done"
if [ ! -f "${ONBOARD_DONE_FILE}" ]; then
  echo "[entrypoint] Initializing NemoClaw configuration..."
  if nemoclaw init 2>/dev/null || true; then
    touch "${ONBOARD_DONE_FILE}"
    echo "[entrypoint] NemoClaw initialization completed"
  else
    echo "[entrypoint] NemoClaw initialization skipped, continuing..."
    touch "${ONBOARD_DONE_FILE}"
  fi
else
  echo "[entrypoint] NemoClaw already initialized"
fi

echo "[entrypoint] Configuration complete, ready for operations"
echo "[entrypoint] NemoClaw version: $(nemoclaw --version 2>/dev/null || echo 'unknown')"
echo "[entrypoint] Workspace: /data/nemoclaw/workspace"
echo "[entrypoint] Starting application..."

# Start NemoClaw bridge service if available
if [ -f "/opt/nemoclaw-bridge/bridge.py" ] && [ -d "/opt/nemoclaw-bridge-venv" ]; then
  echo "[entrypoint] Starting NemoClaw bridge service on port 18789..."
  exec /opt/nemoclaw-bridge-venv/bin/uvicorn bridge:app --host 0.0.0.0 --port 18789 --app-dir /opt/nemoclaw-bridge
else
  echo "[entrypoint] NemoClaw bridge not found, keeping container alive..."
  tail -f /dev/null
fi
