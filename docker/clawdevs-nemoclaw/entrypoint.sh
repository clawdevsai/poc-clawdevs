#!/usr/bin/env bash

set -euo pipefail

mkdir -p "${HOME}" /data/nemoclaw

# Check if NemoClaw runtime is available
nemoclaw_runtime_ok() {
  command -v nemoclaw >/dev/null 2>&1 || return 1
  nemoclaw --version >/dev/null 2>&1 || return 1
  return 0
}

# Install OpenShell from NVIDIA releases if needed
install_openshell_release() {
  local url="https://github.com/NVIDIA/OpenShell/releases/download/v1.0.0/openshell-linux-x64"
  echo "[entrypoint] Downloading OpenShell from ${url}..."

  if curl -fsSL --max-time 30 "${url}" -o /tmp/openshell; then
    chmod +x /tmp/openshell
    mv /tmp/openshell /usr/local/bin/openshell
    echo "[entrypoint] OpenShell installed successfully"
    return 0
  else
    echo "[entrypoint] Failed to download OpenShell from ${url}"
    return 1
  fi
}

# Verify NemoClaw is available (should be pre-installed in base image)
if ! nemoclaw_runtime_ok; then
  echo "[entrypoint] ERROR: NemoClaw runtime not found or not functional" >&2
  echo "[entrypoint] Make sure NemoClaw is installed in the base Docker image" >&2
  exit 1
else
  echo "[entrypoint] NemoClaw runtime verified successfully"
fi

# Try to install OpenShell if not already available
if ! command -v openshell >/dev/null 2>&1; then
  echo "[entrypoint] Installing OpenShell..."
  if install_openshell_release; then
    echo "[entrypoint] OpenShell ready"
  else
    echo "[entrypoint] WARNING: OpenShell installation failed, continuing without it..."
  fi
else
  echo "[entrypoint] OpenShell already available"
fi

# Set up NemoClaw environment variables
export NEMOCLAW_SANDBOX_NAME="${NEMOCLAW_SANDBOX_NAME:-clawdevs-ai}"
export NEMOCLAW_PROVIDER="${NEMOCLAW_PROVIDER:-ollama}"
export NEMOCLAW_MODEL="${NEMOCLAW_MODEL:-mistral}"
export NEMOCLAW_POLICY_MODE="${NEMOCLAW_POLICY_MODE:-skip}"

echo "[entrypoint] Environment variables configured:"
echo "[entrypoint]   NEMOCLAW_SANDBOX_NAME=${NEMOCLAW_SANDBOX_NAME}"
echo "[entrypoint]   NEMOCLAW_PROVIDER=${NEMOCLAW_PROVIDER}"
echo "[entrypoint]   NEMOCLAW_MODEL=${NEMOCLAW_MODEL}"
echo "[entrypoint]   NEMOCLAW_POLICY_MODE=${NEMOCLAW_POLICY_MODE}"

# Run onboarding if needed
ONBOARD_DONE_FILE="/data/nemoclaw/.onboarding-done"
if [ ! -f "${ONBOARD_DONE_FILE}" ]; then
  echo "[entrypoint] Running NemoClaw onboarding..."
  if nemoclaw onboard 2>&1; then
    touch "${ONBOARD_DONE_FILE}"
    echo "[entrypoint] Onboarding completed successfully"
  else
    echo "[entrypoint] WARNING: Onboarding encountered issues, but continuing..."
    touch "${ONBOARD_DONE_FILE}"
  fi
else
  echo "[entrypoint] Onboarding already completed"
fi

# Start the NemoClaw bridge service
if [ -f "/opt/nemoclaw-bridge-venv/bin/uvicorn" ]; then
  echo "[entrypoint] Starting NemoClaw bridge service on port 18789..."
  exec /opt/nemoclaw-bridge-venv/bin/uvicorn bridge:app --host 0.0.0.0 --port 18789 --app-dir /opt/nemoclaw-bridge
else
  echo "[entrypoint] ERROR: NemoClaw bridge service not found at /opt/nemoclaw-bridge-venv/bin/uvicorn" >&2
  echo "[entrypoint] Make sure the bridge service is installed in the base Docker image" >&2
  exit 1
fi
