#!/usr/bin/env bash
# load-env.sh — ClawDevs
# ──────────────────────────────────────────────────────────────────────────────
# Carrega o .env no shell atual ou em subprocessos.
# DEVE ser usado com 'source', não executado diretamente.
#
# USO:
#   source scripts/load-env.sh                  # shell interativo
#   source scripts/load-env.sh --quiet          # sem output
#   source scripts/load-env.sh --check          # só valida, não exporta
#
# Em scripts automatizados (Makefile, CI):
#   export $(grep -v '^#' .env | xargs)
#   OU: source scripts/load-env.sh --quiet
#
# Referência: docs/09-setup-e-scripts.md
# ──────────────────────────────────────────────────────────────────────────────

# Detectar se está sendo 'source'd ou executado diretamente
_SOURCED=0
if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
  _SOURCED=1
fi

# Cores
_GREEN="\033[0;32m"; _RED="\033[0;31m"; _YELLOW="\033[1;33m"
_BLUE="\033[0;34m"; _DIM="\033[2m"; _BOLD="\033[1m"; _RESET="\033[0m"

# Modo silencioso
_QUIET=0
_CHECK_ONLY=0
for arg in "$@"; do
  [[ "$arg" == "--quiet" || "$arg" == "-q" ]] && _QUIET=1
  [[ "$arg" == "--check" || "$arg" == "-c" ]] && _CHECK_ONLY=1
done

_info()  { [[ "$_QUIET" -eq 0 ]] && echo -e "${_BLUE}[ENV]${_RESET}  $*"; }
_ok()    { [[ "$_QUIET" -eq 0 ]] && echo -e "${_GREEN}[OK]${_RESET}   $*"; }
_warn()  { [[ "$_QUIET" -eq 0 ]] && echo -e "${_YELLOW}[AVISO]${_RESET} $*"; }
_error() { echo -e "${_RED}[ERRO]${_RESET} $*" >&2; }

# Localizar o .env
_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_PROJECT_DIR="$(cd "$_SCRIPT_DIR/.." && pwd)"
_ENV_FILE="$_PROJECT_DIR/.env"

if [[ ! -f "$_ENV_FILE" ]]; then
  _error ".env não encontrado em: $_ENV_FILE"
  _error "Execute primeiro: make configure"
  [[ "$_SOURCED" -eq 1 ]] && return 1 || exit 1
fi

# ─── Carregar variáveis ────────────────────────────────────────────────────────
if [[ "$_CHECK_ONLY" -eq 0 ]]; then
  _info "Carregando .env de: $_ENV_FILE"
  set -o allexport
  # shellcheck disable=SC1090
  source "$_ENV_FILE"
  set +o allexport
fi

# ─── Variáveis obrigatórias ───────────────────────────────────────────────────
_REQUIRED_VARS=(
  "GOOGLE_API_KEY"
  "TELEGRAM_TOKEN"
  "TELEGRAM_CHAT_ID"
)

_MISSING=0
for _var in "${_REQUIRED_VARS[@]}"; do
  _val="${!_var:-}"
  if [[ -z "$_val" || "$_val" == "<PREENCHER>" ]]; then
    _error "Variável obrigatória não definida: $_var"
    (( _MISSING++ )) || true
  fi
done

if [[ "$_MISSING" -gt 0 ]]; then
  _error "$_MISSING variável(eis) obrigatória(s) faltando."
  _error "Execute: make configure"
  [[ "$_SOURCED" -eq 1 ]] && return 1 || exit 1
fi

# ─── Resumo do ambiente carregado ─────────────────────────────────────────────
if [[ "$_QUIET" -eq 0 ]]; then
  echo ""
  echo -e "  ${_BOLD}ClawDevs — Ambiente carregado${_RESET}"
  echo -e "  ${_DIM}─────────────────────────────────────────────${_RESET}"

  # Chaves obrigatórias (mascaradas)
  _gak="${GOOGLE_API_KEY:-}"
  _tt="${TELEGRAM_TOKEN:-}"
  _tci="${TELEGRAM_CHAT_ID:-}"
  echo -e "  ${_GREEN}✓${_RESET} GOOGLE_API_KEY    = ${_DIM}${_gak:0:6}...${_gak: -4}${_RESET}"
  echo -e "  ${_GREEN}✓${_RESET} TELEGRAM_TOKEN    = ${_DIM}${_tt:0:6}...${_tt: -4}${_RESET}"
  echo -e "  ${_GREEN}✓${_RESET} TELEGRAM_CHAT_ID  = ${_DIM}${_tci}${_RESET}"

  # Chaves opcionais
  for _opt_var in GITHUB_TOKEN TRELLO_API_KEY OPENROUTER_API_KEY MATON_API_KEY EXA_API_KEY; do
    _opt_val="${!_opt_var:-}"
    if [[ -n "$_opt_val" ]]; then
      _masked="${_opt_val:0:6}...${_opt_val: -4}"
      echo -e "  ${_GREEN}✓${_RESET} ${_opt_var} = ${_DIM}${_masked}${_RESET}"
    fi
  done

  echo ""
  echo -e "  ${_GREEN}✓${_RESET} Minikube: ${MK_CPUS:-10} CPUs / ${MK_RAM_MB:-20480} MB RAM / ${MK_VRAM_MB:-5120} MB VRAM"
  echo -e "  ${_GREEN}✓${_RESET} Ollama: ${OLLAMA_HOST:-n/a} | KEEP_ALIVE=${OLLAMA_KEEP_ALIVE:-5m}"
  echo -e "  ${_GREEN}✓${_RESET} FinOps: Budget=\$${DAILY_API_BUDGET_USD:-5.00}/dia"
  echo -e "  ${_DIM}─────────────────────────────────────────────${_RESET}"
  echo ""
  _ok ".env carregado com sucesso."
fi

# Limpeza de variáveis internas
unset _SCRIPT_DIR _PROJECT_DIR _ENV_FILE _QUIET _CHECK_ONLY _SOURCED
unset _REQUIRED_VARS _MISSING _var _val _opt_var _opt_val _masked
unset _gak _tt _tci
unset _GREEN _RED _YELLOW _BLUE _DIM _BOLD _RESET
