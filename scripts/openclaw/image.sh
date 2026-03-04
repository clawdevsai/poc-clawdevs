#!/usr/bin/env bash
# Build da imagem openclaw-gateway:local no Docker do Minikube.
# Uso: ./scripts/openclaw/image.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"
K8S_DIR="${K8S_DIR:-k8s}"
OPENCLAW_DIR="$K8S_DIR/management-team/openclaw"

echo "==> Build openclaw-gateway:local (Minikube Docker)..."
eval "$(minikube docker-env)" && docker build -f "$OPENCLAW_DIR/Dockerfile" -t openclaw-gateway:local "$OPENCLAW_DIR"
echo "==> openclaw-image concluído."
