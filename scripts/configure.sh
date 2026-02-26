#!/usr/bin/env bash
# configure.sh — ClawDevs
# ──────────────────────────────────────────────────────────────────────────────
# Assistente interativo de pré-configuração.
# Detecta hardware, coleta chaves de API, gera .env e valida o ambiente.
#
# USO:
#   chmod +x scripts/configure.sh && scripts/configure.sh
#   OU:  make configure
#
# Referência: docs/09-setup-e-scripts.md | docs/04-infraestrutura.md
# ──────────────────────────────────────────────────────────────────────────────

set -euo pipefail

# ─── Verificação de root ──────────────────────────────────────────────────────
if [[ "$EUID" -eq 0 ]]; then
  echo "ERRO: Não execute este script como root. Execute como usuário normal."
  exit 1
fi

# ─── Localização do projeto ───────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$PROJECT_DIR/.env"
ENV_EXAMPLE="$PROJECT_DIR/.env.example"

# ─── Cores e helpers ─────────────────────────────────────────────────────────
RED="\033[0;31m"; GREEN="\033[0;32m"; YELLOW="\033[1;33m"
BLUE="\033[0;34m"; CYAN="\033[0;36m"; BOLD="\033[1m"; RESET="\033[0m"
DIM="\033[2m"

info()    { echo -e "${BLUE}[INFO]${RESET}  $*"; }
ok()      { echo -e "${GREEN}[OK]${RESET}    $*"; }
warn()    { echo -e "${YELLOW}[AVISO]${RESET} $*"; }
error()   { echo -e "${RED}[ERRO]${RESET}  $*" >&2; exit 1; }
section() { echo -e "\n${BOLD}${CYAN}══════════════════════════════════════════${RESET}"; \
            echo -e "${BOLD}${CYAN}  $*${RESET}"; \
            echo -e "${BOLD}${CYAN}══════════════════════════════════════════${RESET}"; }
ask()     { echo -e "${YELLOW}▶${RESET} $*"; }
dim()     { echo -e "${DIM}$*${RESET}"; }

# ─── Função: ler valor com padrão ────────────────────────────────────────────
# Uso: read_value "Descrição" "VAR_NAME" "VALOR_PADRÃO" [obrigatorio]
read_value() {
  local desc="$1"
  local varname="$2"
  local default="$3"
  local required="${4:-false}"
  local current="${!varname:-}"
  local prompt_default=""

  # Mascara chaves de API já preenchidas
  if [[ -n "$current" && "$varname" == *KEY* || "$varname" == *TOKEN* || "$varname" == *SECRET* ]]; then
    prompt_default="${current:0:6}...${current: -4} (atual)"
  elif [[ -n "$current" ]]; then
    prompt_default="$current (atual)"
  elif [[ -n "$default" ]]; then
    prompt_default="$default"
  fi

  while true; do
    if [[ -n "$prompt_default" ]]; then
      ask "$desc [${DIM}${prompt_default}${RESET}]: "
    else
      ask "$desc: "
    fi
    read -r input

    if [[ -z "$input" ]]; then
      if [[ -n "$current" ]]; then
        # Manter valor atual
        break
      elif [[ -n "$default" ]]; then
        export "$varname"="$default"
        break
      elif [[ "$required" == "true" ]]; then
        echo -e "  ${RED}Este campo é obrigatório. Por favor, informe um valor.${RESET}"
        continue
      else
        export "$varname"=""
        break
      fi
    else
      export "$varname"="$input"
      break
    fi
  done
}

# ─── Função: validar URL ──────────────────────────────────────────────────────
validate_url() {
  local url="$1"
  if [[ "$url" =~ ^https?:// ]]; then
    return 0
  fi
  return 1
}

# ─── Função: carregar .env existente ─────────────────────────────────────────
load_existing_env() {
  if [[ -f "$ENV_FILE" ]]; then
    warn "Arquivo .env existente encontrado. Os valores atuais serão mantidos se você pressionar Enter."
    # shellcheck disable=SC1090
    set -o allexport
    source "$ENV_FILE" 2>/dev/null || true
    set +o allexport
  fi
}

# ─── Função: detectar hardware ───────────────────────────────────────────────
detect_hardware() {
  section "🖥️  Detectando hardware da máquina"

  TOTAL_CPUS=$(nproc 2>/dev/null || echo "4")
  TOTAL_RAM_GB=$(free -g 2>/dev/null | awk '$1 ~ /^Mem/ {print $2}' || echo "8")
  TOTAL_RAM_MB=$((TOTAL_RAM_GB * 1024))

  # GPU VRAM
  if command -v nvidia-smi &>/dev/null; then
    GPU_VRAM_MB=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' ' || echo "0")
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1 || echo "N/A")
  else
    GPU_VRAM_MB=0
    GPU_NAME="Não detectada (sem nvidia-smi)"
    warn "GPU NVIDIA não detectada. Modo CPU-only ativado."
  fi

  # Calcular 65%
  MK_CPUS_CALC=$(( TOTAL_CPUS * 65 / 100 ))
  MK_RAM_MB_CALC=$(( TOTAL_RAM_MB * 65 / 100 ))
  MK_VRAM_MB_CALC=$(( GPU_VRAM_MB * 65 / 100 ))

  # Garantir mínimos
  [[ "$MK_CPUS_CALC" -lt 2 ]] && MK_CPUS_CALC=2
  [[ "$MK_RAM_MB_CALC" -lt 4096 ]] && MK_RAM_MB_CALC=4096

  echo ""
  echo -e "  ${BOLD}CPU:${RESET}   ${TOTAL_CPUS} threads  →  ${GREEN}${MK_CPUS_CALC} para o cluster (65%)${RESET}"
  echo -e "  ${BOLD}RAM:${RESET}   ${TOTAL_RAM_GB} GB       →  ${GREEN}$(( MK_RAM_MB_CALC / 1024 )) GB para o cluster (65%)${RESET}"
  echo -e "  ${BOLD}GPU:${RESET}   ${GPU_NAME}"
  if [[ "$GPU_VRAM_MB" -gt 0 ]]; then
    echo -e "  ${BOLD}VRAM:${RESET}  ${GPU_VRAM_MB} MB      →  ${GREEN}${MK_VRAM_MB_CALC} MB para o Ollama (65%)${RESET}"
  fi
  echo ""

  # Verificar se é máquina de referência ou equivalente
  if [[ "$TOTAL_CPUS" -ge 16 && "$TOTAL_RAM_GB" -ge 30 && "$GPU_VRAM_MB" -ge 8000 ]]; then
    ok "Máquina equivalente ou superior à referência (Ryzen 5800X / 31 GB / RTX 3060 Ti)."
  elif [[ "$TOTAL_CPUS" -ge 8 && "$TOTAL_RAM_GB" -ge 16 ]]; then
    warn "Máquina abaixo da referência. O ClawDevs funcionará, mas com capacidade reduzida."
  else
    warn "Máquina significativamente abaixo da referência. Considere usar hardware mais robusto."
    warn "Docs: docs/00-objetivo-e-maquina-referencia.md"
  fi

  # Exportar valores detectados como padrões
  MK_CPUS="${MK_CPUS:-$MK_CPUS_CALC}"
  MK_RAM_MB="${MK_RAM_MB:-$MK_RAM_MB_CALC}"
  MK_VRAM_MB="${MK_VRAM_MB:-$MK_VRAM_MB_CALC}"

  ok "Hardware detectado."
}

# ─── Banner ───────────────────────────────────────────────────────────────────
banner() {
cat << 'EOF'

  ╔═══════════════════════════════════════════════════════════════════╗
  ║                                                                   ║
  ║    ██████╗██╗      █████╗ ██╗    ██╗██████╗ ███████╗██╗   ██╗   ║
  ║   ██╔════╝██║     ██╔══██╗██║    ██║██╔══██╗██╔════╝██║   ██║   ║
  ║   ██║     ██║     ███████║██║ █╗ ██║██║  ██║█████╗  ██║   ██║   ║
  ║   ██║     ██║     ██╔══██║██║███╗██║██║  ██║██╔══╝  ╚██╗ ██╔╝   ║
  ║   ╚██████╗███████╗██║  ██║╚███╔███╔╝██████╔╝███████╗ ╚████╔╝    ║
  ║    ╚═════╝╚══════╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚═════╝ ╚══════╝  ╚═══╝    ║
  ║                                                                   ║
  ║          Assistente de Pré-Configuração — v1.0                   ║
  ║          Time de Agentes de IA em Kubernetes                     ║
  ║                                                                   ║
  ╚═══════════════════════════════════════════════════════════════════╝

EOF
echo -e "  Este assistente vai gerar o arquivo ${BOLD}.env${RESET} com todas as"
echo -e "  configurações necessárias para iniciar o ClawDevs."
echo -e "  ${DIM}Pressione Enter para manter o valor atual/padrão.${RESET}"
echo ""
}

# ─── Passo 1: Chaves obrigatórias ────────────────────────────────────────────
step_required_keys() {
  section "🔑 Passo 1/6 — Chaves de API Obrigatórias"

  echo ""
  echo -e "  ${BOLD}Google AI Key (Gemini)${RESET}"
  dim "  Usada pelo CEO e PO para tarefas estratégicas em nuvem."
  dim "  Obter em: https://aistudio.google.com/app/apikey"
  echo ""
  read_value "Google API Key" "GOOGLE_API_KEY" "" "true"
  echo ""

  echo -e "  ${BOLD}Telegram Bot Token${RESET}"
  dim "  O bot pelo qual você (Diretor) se comunica com o enxame."
  dim "  Criar em: https://t.me/BotFather  →  /newbot"
  echo ""
  read_value "Telegram Bot Token" "TELEGRAM_TOKEN" "" "true"
  echo ""

  echo -e "  ${BOLD}Telegram Chat ID${RESET}"
  dim "  Seu ID de usuário do Telegram. Apenas você pode dar ordens."
  dim "  Obter em: https://t.me/userinfobot"
  echo ""
  read_value "Telegram Chat ID" "TELEGRAM_CHAT_ID" "" "true"
  echo ""

  ok "Chaves obrigatórias configuradas."
}

# ─── Passo 2: Chaves opcionais ───────────────────────────────────────────────
step_optional_keys() {
  section "🔑 Passo 2/6 — Chaves de API Opcionais"
  echo ""
  dim "  Pressione Enter para pular e configurar depois."
  echo ""

  echo -e "  ${BOLD}GitHub Token${RESET}"
  dim "  Para PO e Developer manipularem Issues/PRs via gh CLI."
  dim "  Criar em: https://github.com/settings/tokens (escopos: repo, read:org)"
  echo ""
  read_value "GitHub Token (opcional)" "GITHUB_TOKEN" ""
  echo ""

  echo -e "  ${BOLD}Trello${RESET}"
  dim "  Integração do PO com quadros Kanban do Trello."
  dim "  Criar em: https://trello.com/power-ups/admin"
  echo ""
  read_value "Trello API Key (opcional)" "TRELLO_API_KEY" ""
  if [[ -n "${TRELLO_API_KEY:-}" ]]; then
    read_value "Trello Token (opcional)" "TRELLO_TOKEN" ""
    read_value "Trello Board ID (opcional)" "TRELLO_BOARD_ID" ""
  fi
  echo ""

  echo -e "  ${BOLD}OpenRouter${RESET}"
  dim "  Modelos em nuvem alternativos / gratuitos (FreeRide)."
  dim "  Criar em: https://openrouter.ai/keys"
  echo ""
  read_value "OpenRouter API Key (opcional)" "OPENROUTER_API_KEY" ""
  echo ""

  echo -e "  ${BOLD}Maton API Gateway${RESET}"
  dim "  100+ APIs externas com OAuth gerenciado (Slack, Notion, Google, etc.)."
  dim "  Criar em: https://maton.ai/settings"
  echo ""
  read_value "Maton API Key (opcional)" "MATON_API_KEY" ""
  echo ""

  echo -e "  ${BOLD}Exa Web Search${RESET}"
  dim "  Busca web semântica para CEO e PO pesquisarem na internet."
  dim "  Criar em: https://exa.ai"
  echo ""
  read_value "Exa API Key (opcional)" "EXA_API_KEY" ""
  echo ""

  ok "Chaves opcionais configuradas."
}

# ─── Passo 3: Ollama ────────────────────────────────────────────────────────
step_ollama() {
  section "🤖 Passo 3/6 — Ollama (Inferência Local)"
  echo ""

  echo -e "  ${BOLD}Host do Ollama${RESET}"
  dim "  Endpoint do serviço Ollama dentro do cluster Kubernetes."
  dim "  Padrão: ollama-service.ai-agents.svc.cluster.local:11434"
  echo ""
  read_value "OLLAMA_HOST" "OLLAMA_HOST" "http://ollama-service.ai-agents.svc.cluster.local:11434"
  echo ""

  echo -e "  ${BOLD}OLLAMA_KEEP_ALIVE${RESET}"
  dim "  Tempo que o modelo fica na VRAM após a última chamada."
  dim "  '5m' = 5 minutos | '0' = descarregar imediatamente | '-1' = manter sempre"
  dim "  Docs: docs/estrategia-uso-hardware-gpu-cpu.md"
  echo ""
  read_value "OLLAMA_KEEP_ALIVE" "OLLAMA_KEEP_ALIVE" "5m"
  echo ""

  echo -e "  ${BOLD}Modelos por agente${RESET} ${DIM}(quantizados 4-bit recomendados para RTX 3060 Ti 8GB)${RESET}"
  echo ""
  read_value "Developer  (deepseek-coder:6.7b)" "OLLAMA_MODEL_DEVELOPER" "deepseek-coder:6.7b"
  read_value "Architect  (llama3:8b)"            "OLLAMA_MODEL_ARCHITECT" "llama3:8b"
  read_value "QA         (llama3:8b)"            "OLLAMA_MODEL_QA"        "llama3:8b"
  read_value "CyberSec   (mistral:7b)"           "OLLAMA_MODEL_CYBERSEC"  "mistral:7b"
  read_value "DevOps     (phi3:mini)"            "OLLAMA_MODEL_DEVOPS"    "phi3:mini"
  read_value "UX         (phi3:mini)"            "OLLAMA_MODEL_UX"        "phi3:mini"
  read_value "DBA        (llama3:8b)"            "OLLAMA_MODEL_DBA"       "llama3:8b"
  read_value "CEO local  (llama3:8b)"            "OLLAMA_MODEL_CEO_LOCAL" "llama3:8b"
  read_value "PO local   (llama3:8b)"            "OLLAMA_MODEL_PO_LOCAL"  "llama3:8b"
  echo ""

  ok "Ollama configurado."
}

# ─── Passo 4: Hardware e limites ─────────────────────────────────────────────
step_hardware() {
  section "💻 Passo 4/6 — Hardware e Limites de Recursos (65%)"
  echo ""
  echo -e "  Os valores foram detectados automaticamente com base na sua máquina."
  dim "  Altere apenas se necessário. Docs: docs/04-infraestrutura.md"
  echo ""

  read_value "CPUs para o Minikube"      "MK_CPUS"    "${MK_CPUS:-10}"
  read_value "RAM para o Minikube (MB)"  "MK_RAM_MB"  "${MK_RAM_MB:-20480}"
  read_value "VRAM máxima Ollama (MB)"   "MK_VRAM_MB" "${MK_VRAM_MB:-5120}"
  read_value "Driver do Minikube"        "MINIKUBE_DRIVER" "docker"
  echo ""

  echo -e "  ${BOLD}Redis${RESET}"
  read_value "Redis Host"    "REDIS_HOST" "redis-master.ai-agents.svc.cluster.local"
  read_value "Redis Port"    "REDIS_PORT" "6379"
  read_value "Redis DB"      "REDIS_DB"   "0"
  echo ""

  echo -e "  ${BOLD}GPU Lock${RESET}"
  dim "  TTL do lock Redis para uso da GPU. Docs: docs/04-infraestrutura.md"
  read_value "TTL curto (seg, payload < 500 linhas)"   "GPU_LOCK_TTL_SHORT"          "60"
  read_value "TTL longo (seg, payload >= 500 linhas)"  "GPU_LOCK_TTL_LONG"           "120"
  read_value "Limiar de linhas para TTL longo"         "GPU_LOCK_PAYLOAD_THRESHOLD"  "500"
  read_value "TTL working buffer Redis (seg)"          "REDIS_WORKING_BUFFER_TTL"    "3600"
  echo ""

  echo -e "  ${BOLD}Temperatura de segurança${RESET}"
  dim "  Docs: docs/07-configuracao-e-prompts.md (DevOps/SRE)"
  read_value "Temperatura checkpoint (°C)" "GPU_TEMP_CHECKPOINT" "80"
  read_value "Temperatura pausa total (°C)" "GPU_TEMP_PAUSE"     "82"
  read_value "Temperatura retomada (°C)"   "GPU_TEMP_RESUME"     "65"
  echo ""

  ok "Hardware e limites configurados."
}

# ─── Passo 5: FinOps ─────────────────────────────────────────────────────────
step_finops() {
  section "💰 Passo 5/6 — FinOps e Controle de Custos"
  echo ""
  dim "  Docs: docs/07-configuracao-e-prompts.md (seção 2.1)"
  echo ""

  echo -e "  ${BOLD}Modelos Google Gemini${RESET}"
  read_value "Modelo CEO em nuvem"   "GOOGLE_MODEL_CEO" "gemini-1.5-pro"
  read_value "Modelo PO em nuvem"    "GOOGLE_MODEL_PO"  "gemini-1.5-flash"
  read_value "Max tokens CEO/request" "GOOGLE_MAX_TOKENS_CEO" "8000"
  read_value "Max tokens PO/request"  "GOOGLE_MAX_TOKENS_PO"  "4096"
  echo ""

  echo -e "  ${BOLD}Orçamento e limites${RESET}"
  read_value "Limite diário de API em USD (freio de emergência)" "DAILY_API_BUDGET_USD" "5.00"
  read_value "Max eventos de estratégia CEO/hora"                "CEO_MAX_STRATEGY_EVENTS_PER_HOUR" "5"
  read_value "Taxa mínima de aprovação CEO→PO antes rebaixamento (%)" "CEO_APPROVAL_RATE_THRESHOLD" "40"
  echo ""

  echo -e "  ${BOLD}Pipeline de truncamento e sumarização${RESET}"
  read_value "Interações antes do pré-voo de sumarização" "SUMMARIZE_PREFLIGHT_THRESHOLD" "3"
  read_value "Limite de tokens antes do truncamento"      "CONTEXT_TRUNCATION_TOKEN_LIMIT" "4000"
  echo ""

  echo -e "  ${BOLD}Autonomia do CEO${RESET}"
  dim "  always_ask | threshold | full_auto"
  read_value "Modo de autonomia" "CEO_AUTONOMY_MODE" "always_ask"
  read_value "Custo (USD) para pedir aprovação do Diretor" "CEO_COST_APPROVAL_THRESHOLD" "0.50"
  echo ""

  ok "FinOps configurado."
}

# ─── Passo 6: Segurança ──────────────────────────────────────────────────────
step_security() {
  section "🔒 Passo 6/6 — Segurança e Namespace"
  echo ""
  dim "  Docs: docs/05-seguranca-e-etica.md"
  echo ""

  read_value "Namespace Kubernetes"     "K8S_NAMESPACE"  "ai-agents"
  read_value "Diretório raiz enxame"   "ENXAME_DIR"     "${HOME}/enxame"
  echo ""

  echo -e "  ${BOLD}Modo Zero Trust${RESET}"
  read_value "Zero Trust estrito (true/false)"     "ZERO_TRUST_STRICT"      "true"
  read_value "Quarentena de dependências (true/false)" "DEPENDENCY_QUARANTINE" "true"
  read_value "Egress apenas whitelist (true/false)" "EGRESS_WHITELIST_ONLY"  "true"
  echo ""

  echo -e "  ${BOLD}Resiliência${RESET}"
  read_value "Timeout cluster acéfalo (seg)"         "HEADLESS_CLUSTER_TIMEOUT"        "300"
  read_value "Ciclos estáveis para retomada"         "HEADLESS_RESUME_STABLE_CYCLES"   "3"
  echo ""

  ok "Segurança configurada."
}

# ─── Gerar .env ───────────────────────────────────────────────────────────────
write_env_file() {
  section "📝 Gerando arquivo .env"

  # Timestamp de geração
  local timestamp
  timestamp=$(date '+%Y-%m-%d %H:%M:%S')

  cat > "$ENV_FILE" << ENVFILE
##############################################################################
# .env — ClawDevs
# Gerado em: ${timestamp}
# NÃO commite este arquivo — ele está no .gitignore
# Para regenerar: make configure
##############################################################################

# ── Chaves obrigatórias ────────────────────────────────────────────────────
GOOGLE_API_KEY=${GOOGLE_API_KEY:-}
TELEGRAM_TOKEN=${TELEGRAM_TOKEN:-}
TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID:-}

# ── Chaves opcionais ───────────────────────────────────────────────────────
GITHUB_TOKEN=${GITHUB_TOKEN:-}
TRELLO_API_KEY=${TRELLO_API_KEY:-}
TRELLO_TOKEN=${TRELLO_TOKEN:-}
TRELLO_BOARD_ID=${TRELLO_BOARD_ID:-}
OPENROUTER_API_KEY=${OPENROUTER_API_KEY:-}
MATON_API_KEY=${MATON_API_KEY:-}
EXA_API_KEY=${EXA_API_KEY:-}

# ── Ollama ─────────────────────────────────────────────────────────────────
OLLAMA_HOST=${OLLAMA_HOST:-http://ollama-service.ai-agents.svc.cluster.local:11434}
OLLAMA_KEEP_ALIVE=${OLLAMA_KEEP_ALIVE:-5m}
OLLAMA_MODEL_DEVELOPER=${OLLAMA_MODEL_DEVELOPER:-deepseek-coder:6.7b}
OLLAMA_MODEL_ARCHITECT=${OLLAMA_MODEL_ARCHITECT:-llama3:8b}
OLLAMA_MODEL_QA=${OLLAMA_MODEL_QA:-llama3:8b}
OLLAMA_MODEL_CYBERSEC=${OLLAMA_MODEL_CYBERSEC:-mistral:7b}
OLLAMA_MODEL_DEVOPS=${OLLAMA_MODEL_DEVOPS:-phi3:mini}
OLLAMA_MODEL_UX=${OLLAMA_MODEL_UX:-phi3:mini}
OLLAMA_MODEL_DBA=${OLLAMA_MODEL_DBA:-llama3:8b}
OLLAMA_MODEL_CEO_LOCAL=${OLLAMA_MODEL_CEO_LOCAL:-llama3:8b}
OLLAMA_MODEL_PO_LOCAL=${OLLAMA_MODEL_PO_LOCAL:-llama3:8b}

# ── Hardware / Minikube ────────────────────────────────────────────────────
MK_CPUS=${MK_CPUS:-10}
MK_RAM_MB=${MK_RAM_MB:-20480}
MK_VRAM_MB=${MK_VRAM_MB:-5120}
MINIKUBE_DRIVER=${MINIKUBE_DRIVER:-docker}

# ── Redis ──────────────────────────────────────────────────────────────────
REDIS_HOST=${REDIS_HOST:-redis-master.ai-agents.svc.cluster.local}
REDIS_PORT=${REDIS_PORT:-6379}
REDIS_DB=${REDIS_DB:-0}
GPU_LOCK_TTL_SHORT=${GPU_LOCK_TTL_SHORT:-60}
GPU_LOCK_TTL_LONG=${GPU_LOCK_TTL_LONG:-120}
GPU_LOCK_PAYLOAD_THRESHOLD=${GPU_LOCK_PAYLOAD_THRESHOLD:-500}
REDIS_WORKING_BUFFER_TTL=${REDIS_WORKING_BUFFER_TTL:-3600}

# ── Temperatura de segurança ───────────────────────────────────────────────
GPU_TEMP_CHECKPOINT=${GPU_TEMP_CHECKPOINT:-80}
GPU_TEMP_PAUSE=${GPU_TEMP_PAUSE:-82}
GPU_TEMP_RESUME=${GPU_TEMP_RESUME:-65}

# ── Google Gemini ──────────────────────────────────────────────────────────
GOOGLE_MODEL_CEO=${GOOGLE_MODEL_CEO:-gemini-1.5-pro}
GOOGLE_MODEL_PO=${GOOGLE_MODEL_PO:-gemini-1.5-flash}
GOOGLE_MAX_TOKENS_CEO=${GOOGLE_MAX_TOKENS_CEO:-8000}
GOOGLE_MAX_TOKENS_PO=${GOOGLE_MAX_TOKENS_PO:-4096}

# ── FinOps ─────────────────────────────────────────────────────────────────
DAILY_API_BUDGET_USD=${DAILY_API_BUDGET_USD:-5.00}
CEO_MAX_STRATEGY_EVENTS_PER_HOUR=${CEO_MAX_STRATEGY_EVENTS_PER_HOUR:-5}
CEO_APPROVAL_RATE_THRESHOLD=${CEO_APPROVAL_RATE_THRESHOLD:-40}
SUMMARIZE_PREFLIGHT_THRESHOLD=${SUMMARIZE_PREFLIGHT_THRESHOLD:-3}
CONTEXT_TRUNCATION_TOKEN_LIMIT=${CONTEXT_TRUNCATION_TOKEN_LIMIT:-4000}
CEO_AUTONOMY_MODE=${CEO_AUTONOMY_MODE:-always_ask}
CEO_COST_APPROVAL_THRESHOLD=${CEO_COST_APPROVAL_THRESHOLD:-0.50}
FALLBACK_CPU_MODEL=${FALLBACK_CPU_MODEL:-phi3:mini}
EMBEDDING_MODEL=${EMBEDDING_MODEL:-bge-m3}

# ── Namespace e caminhos ───────────────────────────────────────────────────
K8S_NAMESPACE=${K8S_NAMESPACE:-ai-agents}
ENXAME_DIR=${ENXAME_DIR:-${HOME}/enxame}
TRANSCRIPTION_DIR=${ENXAME_DIR:-${HOME}/enxame}/transcription
AUDIO_TRANSCRIPTIONS_DIR=${ENXAME_DIR:-${HOME}/enxame}/audio/transcriptions

# ── Segurança ──────────────────────────────────────────────────────────────
ZERO_TRUST_STRICT=${ZERO_TRUST_STRICT:-true}
DEPENDENCY_QUARANTINE=${DEPENDENCY_QUARANTINE:-true}
EGRESS_WHITELIST_ONLY=${EGRESS_WHITELIST_ONLY:-true}

# ── Resiliência ────────────────────────────────────────────────────────────
HEADLESS_CLUSTER_TIMEOUT=${HEADLESS_CLUSTER_TIMEOUT:-300}
HEADLESS_RESUME_STABLE_CYCLES=${HEADLESS_RESUME_STABLE_CYCLES:-3}
ENVFILE

  chmod 600 "$ENV_FILE"
  ok ".env gerado em: ${ENV_FILE}"
  ok "Permissões definidas: 600 (somente leitura pelo dono)"
}

# ─── Validação final ─────────────────────────────────────────────────────────
validate_env() {
  section "✅ Validando configuração"
  local errors=0

  echo ""
  # Verificar chaves obrigatórias
  for var in GOOGLE_API_KEY TELEGRAM_TOKEN TELEGRAM_CHAT_ID; do
    val="${!var:-}"
    if [[ -z "$val" ]]; then
      echo -e "  ${RED}✗${RESET} $var — FALTANDO"
      ((errors++))
    elif [[ "$val" == "<PREENCHER>" ]]; then
      echo -e "  ${RED}✗${RESET} $var — ainda com valor placeholder"
      ((errors++))
    else
      # Mascarar para exibição
      masked="${val:0:6}...${val: -4}"
      echo -e "  ${GREEN}✓${RESET} $var = ${DIM}${masked}${RESET}"
    fi
  done

  # Verificar chaves opcionais preenchidas
  for var in GITHUB_TOKEN TRELLO_API_KEY OPENROUTER_API_KEY MATON_API_KEY EXA_API_KEY; do
    val="${!var:-}"
    if [[ -n "$val" ]]; then
      masked="${val:0:6}...${val: -4}"
      echo -e "  ${GREEN}✓${RESET} $var = ${DIM}${masked}${RESET} (opcional)"
    else
      echo -e "  ${DIM}  $var = (não configurado — opcional)${RESET}"
    fi
  done

  # Hardware
  echo ""
  echo -e "  ${GREEN}✓${RESET} Minikube: ${MK_CPUS} CPUs / ${MK_RAM_MB} MB RAM / ${MK_VRAM_MB} MB VRAM"
  echo -e "  ${GREEN}✓${RESET} Ollama: KEEP_ALIVE=${OLLAMA_KEEP_ALIVE} | Default model=${OLLAMA_MODEL_DEVELOPER}"
  echo -e "  ${GREEN}✓${RESET} FinOps: Budget=\$${DAILY_API_BUDGET_USD}/dia | CEO max ${CEO_MAX_STRATEGY_EVENTS_PER_HOUR} eventos/hora"
  echo ""

  if [[ "$errors" -gt 0 ]]; then
    warn "${errors} variável(eis) obrigatória(s) não configurada(s)."
    warn "Execute 'make configure' novamente para corrigir."
    return 1
  fi

  ok "Todas as variáveis obrigatórias estão configuradas."
}

# ─── Resumo final ─────────────────────────────────────────────────────────────
print_summary() {
  echo ""
  echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════════╗${RESET}"
  echo -e "${GREEN}║  ClawDevs — Pré-configuração concluída!                           ║${RESET}"
  echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════════╝${RESET}"
  echo ""
  echo -e "  ${BOLD}Arquivo gerado:${RESET} ${ENV_FILE}"
  echo ""
  echo -e "  ${BOLD}Próximos passos:${RESET}"
  echo -e "    ${CYAN}1.${RESET} source scripts/load-env.sh    # Carregar .env no shell atual"
  echo -e "    ${CYAN}2.${RESET} make verify                   # Verificar requisitos da máquina"
  echo -e "    ${CYAN}3.${RESET} make setup                    # Setup completo (instala tudo)"
  echo -e "    ${CYAN}4.${RESET} make apply-all                # Aplicar manifestos Kubernetes"
  echo -e "    ${CYAN}5.${RESET} make pull-models              # Baixar modelos Ollama"
  echo -e "    ${CYAN}6.${RESET} make status                   # Ver status do cluster"
  echo ""
  echo -e "  ${DIM}Docs: docs/09-setup-e-scripts.md | Dúvidas: docs/README.md${RESET}"
  echo ""
}

# ─── Main ─────────────────────────────────────────────────────────────────────
main() {
  banner
  load_existing_env
  detect_hardware
  step_required_keys
  step_optional_keys
  step_ollama
  step_hardware
  step_finops
  step_security
  write_env_file
  validate_env
  print_summary
}

main "$@"
