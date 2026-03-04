#!/usr/bin/env bash
# Valida FinOps e validação reversa PO: test_config_finops + validate_reverse_po.
# Uso: ./scripts/run_validacao_finops_po.sh [--skip-tests]
# Exit 0 se tudo OK; 1 se algum passo falhar.
# Ref: docs/issues/040-041-pendentes.md, integracao-040-041-gateway-orquestrador.md

set -e
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

FAILED=0

echo "==> 1. test_config_finops.py"
if ! python3 app/features/test_config_finops.py 2>&1; then
  echo "[FALHA] test_config_finops.py" >&2
  FAILED=1
fi

echo "==> 2. validate_reverse_po (resumo cobre critérios → exit 0)"
CRITERIA_FILE="$REPO_ROOT/docs/03-agents/agents-devs/CRITERIOS_ACEITE-example.md"
SUMMARY_OK="$(mktemp)"
SUMMARY_FAIL="$(mktemp)"
trap "rm -f '$SUMMARY_OK' '$SUMMARY_FAIL'" EXIT
echo "Resumo: usuário pode habilitar 2FA pelo perfil; código TOTP válido 30 segundos; tokens de backup 10 códigos uso único; sem 2FA login normal, com 2FA segundo fator obrigatório após senha." > "$SUMMARY_OK"
echo "Resumo curto sem critérios." > "$SUMMARY_FAIL"

if [ -f "$CRITERIA_FILE" ]; then
  if ! python3 app/features/validate_reverse_po.py --summary "$SUMMARY_OK" --criteria "$CRITERIA_FILE" 2>/dev/null; then
    echo "[FALHA] validate_reverse_po esperava exit 0 com resumo que cobre critérios" >&2
    FAILED=1
  fi
  if python3 app/features/validate_reverse_po.py --summary "$SUMMARY_FAIL" --criteria "$CRITERIA_FILE" 2>/dev/null; then
    echo "[FALHA] validate_reverse_po esperava exit 1 com resumo que omite critérios" >&2
    FAILED=1
  fi
else
  echo "[SKIP] CRITERIOS_ACEITE-example.md não encontrado; validate_reverse_po não testado com arquivo real"
fi

if [ "$FAILED" -eq 0 ]; then
  echo "==> Validação FinOps e PO OK"
else
  echo "==> Validação FinOps e PO FALHOU" >&2
  exit 1
fi
