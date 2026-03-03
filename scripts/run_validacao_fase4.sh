#!/usr/bin/env bash
# Validação Fase 4 (040/041): test_config_finops + validate_reverse_po.
# Uso: ./scripts/run_validacao_fase4.sh [--skip-tests]
# Exit 0 se tudo OK; 1 se algum passo falhar.
# Ref: docs/issues/fase4-o-que-falta-finalizar.md §4

set -e
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

FAILED=0

echo "==> 1. test_config_finops.py"
if ! python3 app/test_config_finops.py 2>&1; then
  echo "[FALHA] test_config_finops.py" >&2
  FAILED=1
fi

echo "==> 2. validate_reverse_po (resumo cobre critérios → exit 0)"
CRITERIA_FILE="$REPO_ROOT/docs/agents-devs/CRITERIOS_ACEITE-example.md"
SUMMARY_OK="$(mktemp)"
SUMMARY_FAIL="$(mktemp)"
trap "rm -f '$SUMMARY_OK' '$SUMMARY_FAIL'" EXIT
echo "Resumo: usuário pode habilitar 2FA pelo perfil; código TOTP válido 30 segundos; tokens de backup 10 códigos uso único; sem 2FA login normal, com 2FA segundo fator obrigatório após senha." > "$SUMMARY_OK"
echo "Resumo curto sem critérios." > "$SUMMARY_FAIL"

if [ -f "$CRITERIA_FILE" ]; then
  if ! python3 scripts/validate_reverse_po.py --summary "$SUMMARY_OK" --criteria "$CRITERIA_FILE" 2>/dev/null; then
    echo "[FALHA] validate_reverse_po esperava exit 0 com resumo que cobre critérios" >&2
    FAILED=1
  fi
  if python3 app/validate_reverse_po.py --summary "$SUMMARY_FAIL" --criteria "$CRITERIA_FILE" 2>/dev/null; then
    echo "[FALHA] validate_reverse_po esperava exit 1 com resumo que omite critérios" >&2
    FAILED=1
  fi
else
  echo "[SKIP] CRITERIOS_ACEITE-example.md não encontrado; validate_reverse_po não testado com arquivo real"
fi

if [ "$FAILED" -eq 0 ]; then
  echo "==> Validação Fase 4 OK"
else
  echo "==> Validação Fase 4 FALHOU" >&2
  exit 1
fi
