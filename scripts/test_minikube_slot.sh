#!/usr/bin/env bash
# Wrapper: delega para ops/test_minikube_slot.sh.
# Uso: ./scripts/test_minikube_slot.sh
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/ops/test_minikube_slot.sh" "$@"
