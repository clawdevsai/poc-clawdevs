#!/usr/bin/env bash
# Fase 2 — 022: Análise estática em git hooks (segredos e padrões conhecidos).
# Uso: ln -sf ../../scripts/owasp-pre-commit.sh .git/hooks/pre-commit
# Ou: pre-commit run --hook-stage commit (com pre-commit framework).
# Ref: docs/15-seguranca-aplicacao-owasp.md, docs/issues/022-owasp-auditoria-codificacao-segura.md

set -e
REDIS_URL_PATTERN='redis://[^[:space:]]*:[^[:space:]]*@'
AWS_KEY_PATTERN='AKIA[0-9A-Z]{16}'
GENERIC_SECRET_PATTERN='(api[_-]?key|apikey|secret|password|passwd|token)\s*[:=]\s*['\''"]?[a-zA-Z0-9_\-]{20,}'
FAIL=0

# Arquivos staged (a serem commitados)
FILES=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null || true)
for f in $FILES; do
  [ -f "$f" ] || continue
  # Ignorar binários e vendored
  case "$f" in
    *.png|*.jpg|*.jpeg|*.gif|*.ico|*.woff2|*.wasm|*.min.js) continue ;;
    *node_modules*|*vendor*|*.lock) continue ;;
  esac
  if grep -qE "$REDIS_URL_PATTERN|$AWS_KEY_PATTERN" "$f" 2>/dev/null; then
    echo "SECRET: possível credencial em $f (redis URL ou AWS key)" >&2
    FAIL=1
  fi
  if grep -qiE "$GENERIC_SECRET_PATTERN" "$f" 2>/dev/null; then
    echo "SECRET: possível api_key/secret/password em $f" >&2
    FAIL=1
  fi
done

# Opcional: gitleaks se instalado (detect-run em staged)
if command -v gitleaks >/dev/null 2>&1; then
  if ! gitleaks detect --no-banner --source . --redact 2>/dev/null; then
    echo "GITLEAKS: possível vazamento de segredo (gitleaks detect)" >&2
    FAIL=1
  fi
fi

[ $FAIL -eq 0 ] || exit 1
