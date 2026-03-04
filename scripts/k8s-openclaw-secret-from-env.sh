#!/usr/bin/env bash
# Wrapper: delega para openclaw/k8s-openclaw-secret-from-env.sh.
# Uso: ./scripts/k8s-openclaw-secret-from-env.sh
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/openclaw/k8s-openclaw-secret-from-env.sh"
