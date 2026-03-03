#!/usr/bin/env bash
# Teste E2E no Minikube: sobe Redis + slot Revisão pós-Dev, publica code:ready, valida logs.
# Uso: ./scripts/test_minikube_slot.sh
# Requer: minikube, kubectl. Opcional: make up já rodado (senão o script aplica o mínimo).
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
NS="${NAMESPACE:-ai-agents}"
cd "$REPO_ROOT"

echo "==> 1. Minikube e namespace"
if ! minikube status >/dev/null 2>&1; then
  echo "Minikube não está rodando. Inicie com: make prepare (ou minikube start ...)"
  exit 1
fi
kubectl apply -f k8s/namespace.yaml 2>/dev/null || true
kubectl get namespace "$NS" >/dev/null 2>&1 || kubectl create namespace "$NS"

echo "==> 2. Redis"
kubectl apply -f k8s/redis/deployment.yaml
kubectl apply -f k8s/redis/streams-configmap.yaml
kubectl rollout status deployment/redis -n "$NS" --timeout=120s 2>/dev/null || true

echo "==> 3. ConfigMap slot + revisao-pos-dev"
make revisao-slot-configmap
kubectl apply -f k8s/development-team/revisao-pos-dev/configmap-env.yaml
kubectl apply -f k8s/development-team/revisao-pos-dev/deployment.yaml
kubectl rollout status deployment/revisao-pos-dev -n "$NS" --timeout=120s 2>/dev/null || true

echo "==> 4. Inicializar stream code:ready e consumer group revisao-pos-dev"
kubectl exec -n "$NS" deploy/redis -- redis-cli XGROUP CREATE code:ready revisao-pos-dev \$ MKSTREAM 2>/dev/null || echo "    (group já existe)"

echo "==> 5. Publicar evento code:ready (issue_id=42)"
kubectl port-forward -n "$NS" svc/redis-service 6379:6379 &
PF_PID=$!
sleep 2
cleanup() { kill $PF_PID 2>/dev/null || true; }
trap cleanup EXIT
if command -v redis-cli &>/dev/null; then
  redis-cli -h 127.0.0.1 -p 6379 XADD code:ready "*" issue_id 42 branch main ts "$(date +%s)" && echo "    Publicado via redis-cli"
elif [ -d "$REPO_ROOT/.venv" ] && [ -f "$REPO_ROOT/.venv/bin/python3" ]; then
  (cd "$REPO_ROOT" && . .venv/bin/activate && REDIS_HOST=127.0.0.1 REDIS_PORT=6379 python3 app/publish_event_redis.py code:ready issue_id=42 branch=main) && echo "    Publicado via publish_event_redis.py"
else
  (cd "$REPO_ROOT" && REDIS_HOST=127.0.0.1 REDIS_PORT=6379 python3 app/publish_event_redis.py code:ready issue_id=42 branch=main 2>/dev/null) && echo "    Publicado" || echo "    (instale redis: pip install redis ou use redis-cli)"
fi
sleep 5
cleanup 2>/dev/null || true

echo "==> 6. Logs do slot Revisão pós-Dev (últimas 80 linhas)"
kubectl logs -n "$NS" deployment/revisao-pos-dev --tail=80 2>/dev/null || kubectl logs -n "$NS" -l app=revisao-pos-dev --tail=80 2>/dev/null || echo "Nenhum log ainda (aguarde o consumidor processar)."
echo "==> Concluído. Para acompanhar: kubectl logs -n $NS -f deployment/revisao-pos-dev"
