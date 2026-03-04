#!/usr/bin/env bash
# Exibe URLs do Kanban UI e API.
# Uso: ./scripts/kanban/url.sh
set -e

IP=$(minikube ip)
echo "==> Kanban UI:  http://$IP:32000"
echo "==> Kanban API: http://$IP:32001"
