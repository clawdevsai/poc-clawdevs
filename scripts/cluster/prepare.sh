#!/usr/bin/env bash
# Prepara o ambiente: Docker, kubectl, Minikube e inicia o cluster básico.
# Uso: ./scripts/cluster/prepare.sh
# Variáveis: MINIKUBE_CPUS, MINIKUBE_MEMORY (opcionais)
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

MINIKUBE_CPUS="${MINIKUBE_CPUS:-10}"
MINIKUBE_MEMORY="${MINIKUBE_MEMORY:-20g}"

echo "==> Verificando Docker..."
if ! command -v docker >/dev/null 2>&1; then
  echo "Docker não encontrado. Instalando (requer sudo)..."
  curl -fsSL https://get.docker.com | sh
  sudo usermod -aG docker "$USER" 2>/dev/null || true
  echo "  Log out e log in (ou newgrp docker) para usar docker sem sudo."
fi

echo "==> Verificando kubectl..."
if ! command -v kubectl >/dev/null 2>&1; then
  echo "kubectl não encontrado. Instalando..."
  curl -sLO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
  chmod +x kubectl
  sudo mv kubectl /usr/local/bin/
fi

echo "==> Verificando Minikube..."
if ! command -v minikube >/dev/null 2>&1; then
  echo "Minikube não encontrado. Instalando..."
  curl -sLO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
  chmod +x minikube-linux-amd64
  sudo mv minikube-linux-amd64 /usr/local/bin/minikube
fi

echo "==> Iniciando Minikube com Docker e GPU..."
if ! minikube status >/dev/null 2>&1; then
  minikube start --driver=docker --addons=nvidia-device-plugin --cpus="$MINIKUBE_CPUS" --memory="$MINIKUBE_MEMORY"
else
  echo "  Minikube já está rodando."
fi
minikube addons enable nvidia-device-plugin 2>/dev/null || true

echo "==> prepare concluído. Use 'make up' para aplicar os recursos."
