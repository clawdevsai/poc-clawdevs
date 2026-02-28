#!/usr/bin/env bash
# Fase 2 — 023: Varredura local do ambiente (somente leitura). Zero telemetria.
# Uso: ./scripts/ciso_local_scan.sh [--fix] (--fix aplica correções seguras com confirmação)
# Ref: docs/16-ciso-habilidades.md § 1.5, docs/issues/023-ciso-habilidades.md

set -e
FIX="${1:-}"
SCORE=100
CRITICAL=0 WARNING=0 PASS=0 INFO=0

report() { echo "[$1] $2"; }
crit() { report "CRITICAL" "$1"; CRITICAL=$((CRITICAL+1)); SCORE=$((SCORE-25)); }
warn() { report "WARNING"  "$1"; WARNING=$((WARNING+1));  SCORE=$((SCORE-10)); }
pass() { report "PASS"     "$1"; PASS=$((PASS+1)); }
info() { report "INFO"     "$1"; INFO=$((INFO+1)); }

# .env ou segredos em arquivos rastreados
if [ -d .git ]; then
  if git ls-files --error-unmatch .env 2>/dev/null; then
    crit ".env está versionado (remova e adicione ao .gitignore)"
  else
    pass ".env não versionado"
  fi
  if [ -f .gitignore ] && grep -qE '^\.env$|^\.env\.' .gitignore 2>/dev/null; then
    pass ".gitignore cobre .env"
  else
    warn ".gitignore pode não cobrir .env*"
  fi
fi

# Permissões de arquivos sensíveis (se existirem)
for f in .env .env.local k8s/**/secret.yaml 2>/dev/null; do
  [ -f "$f" ] || continue
  perms=$(stat -c %a "$f" 2>/dev/null || stat -f %A "$f" 2>/dev/null || true)
  if [ "$perms" = "600" ] || [ "$perms" = "400" ]; then
    pass "$f permissões restritas ($perms)"
  else
    warn "$f permissões $perms (recomendado 600)"
  fi
done

# Resumo
SCORE=$((SCORE < 0 ? 0 : SCORE))
echo ""
echo "--- RESUMO ---"
echo "CRÍTICO: $CRITICAL | WARNING: $WARNING | PASS: $PASS | INFO: $INFO"
echo "Pontuação (0-100): $SCORE"
[ $CRITICAL -gt 0 ] && exit 2 || true
[ $WARNING -gt 0 ] && exit 1 || exit 0
