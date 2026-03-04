#!/usr/bin/env bash
# Monta workspace compartilhado no Minikube (~/clawdevs-shared -> /agent-shared).
# Uso: ./scripts/utils/shared.sh
set -e

echo "==> Montando workspace compartilhado no Minikube (uid=0, gid=0)..."
mkdir -p ~/clawdevs-shared
for pid in $(pgrep -x minikube 2>/dev/null); do
  if grep -q 'mount.*agent-shared' /proc/"$pid"/cmdline 2>/dev/null; then
    kill "$pid" 2>/dev/null || true
  fi
done
sleep 1
nohup minikube mount ~/clawdevs-shared:/agent-shared --uid=0 --gid=0 > ~/minikube-mount.log 2>&1 &
sleep 3
if pgrep -x minikube >/dev/null 2>&1 && grep -q "Successfully mounted" ~/minikube-mount.log 2>/dev/null; then
  echo "==> Mount ativo (uid=0, gid=0). Logs em ~/minikube-mount.log"
else
  echo "ERRO: minikube mount não iniciou. Verifique ~/minikube-mount.log"
  exit 1
fi
