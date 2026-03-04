#!/usr/bin/env bash
# Build da imagem kanban-ui:v8 no Docker do Minikube.
# Uso: ./scripts/kanban/image.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

echo "==> Build kanban-ui:local (Minikube Docker)..."
eval "$(minikube docker-env)" && docker build -t kanban-ui:v8 kanban-ui
echo "==> kanban-ui:local concluído."
