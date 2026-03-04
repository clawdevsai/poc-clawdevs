#!/usr/bin/env bash
# Abre o dashboard do Minikube no navegador.
# Uso: ./scripts/utils/dashboard.sh
set -e

minikube addons enable dashboard 2>/dev/null || true
minikube dashboard
