#!/usr/bin/env bash
# ConfigMaps de segurança: rotation, url-sandbox, url-sandbox-trigger, quarantine, gateway-adapter.
# Uso: ./scripts/configmaps/phase2.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$SCRIPT_DIR/rotation.sh"
"$SCRIPT_DIR/url-sandbox.sh"
"$SCRIPT_DIR/url-sandbox-trigger.sh"
"$SCRIPT_DIR/quarantine.sh"
"$SCRIPT_DIR/gateway-adapter.sh"
echo "==> ConfigMaps de segurança aplicados."
