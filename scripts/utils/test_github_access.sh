#!/usr/bin/env bash
# Testa se o acesso ao GitHub está ok: no host (usando .env) e/ou nos pods (secret clawdevs-github-secret).
# Uso: ./scripts/utils/test_github_access.sh [host|cluster|all]
set -e

MODE="${1:-all}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
NAMESPACE="${K8S_NAMESPACE:-ai-agents}"

test_via_api() {
  local token="$1"
  local label="$2"
  if [ -z "$token" ]; then
    echo "  $label: token não definido."
    return 1
  fi
  local code
  code=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $token" -H "Accept: application/vnd.github.v3+json" "https://api.github.com/user" 2>/dev/null || true)
  if [ "$code" = "200" ]; then
    echo "  $label: OK (API respondeu 200)."
    return 0
  fi
  echo "  $label: falhou (HTTP $code). Token inválido ou sem permissão."
  return 1
}

test_host() {
  echo "==> Teste no host (.env)..."
  if [ -f "$REPO_ROOT/.env" ]; then
    export $(grep -E '^GITHUB_TOKEN=|^GH_TOKEN=' "$REPO_ROOT/.env" 2>/dev/null | xargs) 2>/dev/null || true
  fi
  local t="${GITHUB_TOKEN:-$GH_TOKEN}"
  test_via_api "$t" "Host (GITHUB_TOKEN/GH_TOKEN)"
}

test_cluster() {
  echo "==> Teste no cluster (pods com clawdevs-github-secret)..."
  if ! kubectl get namespace "$NAMESPACE" &>/dev/null; then
    echo "  Namespace $NAMESPACE não existe. Ignorando teste no cluster."
    return 0
  fi
  if ! kubectl get secret clawdevs-github-secret -n "$NAMESPACE" &>/dev/null; then
    echo "  Secret clawdevs-github-secret não existe. Crie com: export \$(grep -E '^GITHUB_TOKEN=|^GH_TOKEN=' .env | xargs) && kubectl create secret generic clawdevs-github-secret -n ai-agents --from-literal=GITHUB_TOKEN=\"\$GITHUB_TOKEN\" --from-literal=GH_TOKEN=\"\${GH_TOKEN:-\$GITHUB_TOKEN}\""
    return 1
  fi
  for deploy in openclaw; do
    if ! kubectl get deploy "$deploy" -n "$NAMESPACE" &>/dev/null; then
      continue
    fi
    local pod
    pod=$(kubectl get pods -n "$NAMESPACE" -l app="$deploy" -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || true)
    if [ -z "$pod" ]; then
      echo "  Deploy $deploy: nenhum pod rodando."
      continue
    fi
    if kubectl exec -n "$NAMESPACE" "$pod" -c gateway -- sh -c 'test -n "$GITHUB_TOKEN" || test -n "$GH_TOKEN"' 2>/dev/null; then
      local code
      code=$(kubectl exec -n "$NAMESPACE" "$pod" -c gateway -- sh -c 'curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer ${GITHUB_TOKEN:-$GH_TOKEN}" -H "Accept: application/vnd.github.v3+json" https://api.github.com/user' 2>/dev/null || echo "000")
      if [ "$code" = "200" ]; then
        echo "  Pod $deploy ($pod): OK (API 200)."
      else
        echo "  Pod $deploy ($pod): falhou (HTTP ${code:-sem curl})."
      fi
    else
      echo "  Pod $deploy: variáveis GITHUB_TOKEN/GH_TOKEN não definidas no container."
    fi
  done
}

case "$MODE" in
  host)   test_host ;;
  cluster) test_cluster ;;
  all)    test_host; test_cluster ;;
  *)      echo "Uso: $0 [host|cluster|all]"; exit 1 ;;
esac
echo "==> Fim do teste de acesso GitHub."
