#!/usr/bin/env bash
# Wrapper para chamar validate_reverse_po após gerar resumo (config-perfis/truncamento-finops).
# Uso: após gravar o resumo em um arquivo, rodar:
#   scripts/validate_reverse_po_after_summary.sh /caminho/do/resumo.md /caminho/da/issue-com-criterios.md
# Se exit 1: resumo omite critérios; não substituir o buffer pelo resumo (reestruturar ou refazer).
# Ref: docs/issues/integracao-040-041-gateway-orquestrador.md, docs/soul/PO.md

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SUMMARY_FILE="${1:?Uso: $0 SUMMARY_FILE CRITERIA_FILE}"
CRITERIA_FILE="${2:?Uso: $0 SUMMARY_FILE CRITERIA_FILE}"

if [[ ! -f "$SUMMARY_FILE" ]]; then
  echo "Arquivo de resumo não encontrado: $SUMMARY_FILE" >&2
  exit 2
fi
if [[ ! -f "$CRITERIA_FILE" ]]; then
  echo "Arquivo de critérios não encontrado: $CRITERIA_FILE" >&2
  exit 2
fi

exec python3 "$SCRIPT_DIR/validate_reverse_po.py" --summary "$SUMMARY_FILE" --criteria "$CRITERIA_FILE"
