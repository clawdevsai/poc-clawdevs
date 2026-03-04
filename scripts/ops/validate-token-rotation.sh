#!/usr/bin/env bash
# Valida no cluster a rotação de tokens (Fase 2 — 025).
# Uso: ./scripts/ops/validate-token-rotation.sh
set -e
NS="${NAMESPACE:-ai-agents}"
FAIL=0

echo "==> Validando rotação de tokens (namespace=$NS)"
echo ""

if ! kubectl get namespace "$NS" &>/dev/null; then
  echo "[FAIL] Namespace $NS não existe. Rode: make up"
  FAIL=1
else
  echo "[OK] Namespace $NS existe"
fi

if ! kubectl get configmap rotation-scripts -n "$NS" &>/dev/null; then
  echo "[FAIL] ConfigMap rotation-scripts não existe. Rode: make up ou make rotation-configmap"
  FAIL=1
else
  echo "[OK] ConfigMap rotation-scripts existe"
fi

if ! kubectl get serviceaccount token-rotation -n "$NS" &>/dev/null; then
  echo "[FAIL] ServiceAccount token-rotation não existe. Rode: kubectl apply -f k8s/security/rotation-rbac.yaml"
  FAIL=1
else
  echo "[OK] ServiceAccount token-rotation existe"
fi

if ! kubectl get role token-rotation -n "$NS" &>/dev/null; then
  echo "[FAIL] Role token-rotation não existe. Rode: kubectl apply -f k8s/security/rotation-rbac.yaml"
  FAIL=1
else
  echo "[OK] Role token-rotation existe"
fi

if ! kubectl get rolebinding token-rotation -n "$NS" &>/dev/null; then
  echo "[FAIL] RoleBinding token-rotation não existe."
  FAIL=1
else
  echo "[OK] RoleBinding token-rotation existe"
fi

if ! kubectl get cronjob token-rotation -n "$NS" &>/dev/null; then
  echo "[FAIL] CronJob token-rotation não existe. Rode: kubectl apply -f k8s/security/cronjob-token-rotation.yaml"
  FAIL=1
else
  echo "[OK] CronJob token-rotation existe"
  kubectl get cronjob token-rotation -n "$NS" --no-headers 2>/dev/null || true
fi

if ! kubectl get secret openclaw-telegram -n "$NS" &>/dev/null; then
  echo "[WARN] Secret openclaw-telegram não existe (opcional para Telegram). CronJob fará no-op até haver fonte."
fi

if ! kubectl get secret openclaw-telegram-rotation-source -n "$NS" &>/dev/null; then
  echo "[WARN] Secret openclaw-telegram-rotation-source não existe. Para ativar rotação automática:"
  echo "       kubectl create secret generic openclaw-telegram-rotation-source -n $NS \\"
  echo "         --from-literal=TELEGRAM_BOT_TOKEN=<token> --from-literal=TELEGRAM_CHAT_ID=<chat_id>"
else
  echo "[OK] Secret openclaw-telegram-rotation-source existe (fonte para rotação)"
fi

echo ""
if [ $FAIL -eq 0 ]; then
  echo "==> Validação rotação de tokens: OK"
  echo "    CronJob roda a cada 3 min. Para testar agora: kubectl create job -n $NS token-rotation-manual --from=cronjob/token-rotation"
  exit 0
else
  echo "==> Validação: FALHOU ($FAIL item(ns))"
  exit 1
fi
