#!/usr/bin/env bash
# verify-machine.sh — ClawDevs
# Verifica se a máquina atende aos requisitos mínimos da máquina de referência.
# Apenas leitura; não altera nenhuma configuração.
# Referência: docs/00-objetivo-e-maquina-referencia.md | docs/scripts/verify-machine.md

set -euo pipefail

# ─── Cores ───────────────────────────────────────────────────────────────────
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
RESET="\033[0m"

ok()   { echo -e "${GREEN}[OK]${RESET}    $*"; }
warn() { echo -e "${YELLOW}[AVISO]${RESET} $*"; }
fail() { echo -e "${RED}[FALHA]${RESET} $*"; }

echo "============================================================"
echo "  ClawDevs — Verificação da Máquina de Referência"
echo "============================================================"
echo ""

# ─── CPU ─────────────────────────────────────────────────────────────────────
echo "=== CPU ==="
if command -v lscpu &>/dev/null; then
  lscpu 2>/dev/null | grep -E "Nome do modelo|Model name|CPU\(s\)|Thread|Núcleo|Core" || lscpu | head -20
  CPU_THREADS=$(lscpu | grep "^CPU(s):" | awk '{print $2}' | tr -d ' ')
  if [[ -z "$CPU_THREADS" ]]; then
    CPU_THREADS=$(lscpu | grep "^CPU(s)" | awk '{print $NF}')
  fi
  if [[ "$CPU_THREADS" -ge 16 ]] 2>/dev/null; then
    ok "CPU: $CPU_THREADS threads (≥16 — equivalente à referência)"
  elif [[ "$CPU_THREADS" -ge 8 ]] 2>/dev/null; then
    warn "CPU: $CPU_THREADS threads (mínimo aceitável; referência é 16 threads)"
  else
    fail "CPU: $CPU_THREADS threads (abaixo do mínimo recomendado de 8)"
  fi
else
  warn "lscpu não encontrado."
fi
echo ""

# ─── GPU ─────────────────────────────────────────────────────────────────────
echo "=== GPU ==="
if command -v nvidia-smi &>/dev/null; then
  nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader 2>/dev/null || nvidia-smi | head -15
  GPU_MEM_MB=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' ')
  if [[ "$GPU_MEM_MB" -ge 8000 ]] 2>/dev/null; then
    ok "GPU: ${GPU_MEM_MB} MiB VRAM (≥8 GB — equivalente à referência RTX 3060 Ti 8GB)"
  elif [[ "$GPU_MEM_MB" -ge 6000 ]] 2>/dev/null; then
    warn "GPU: ${GPU_MEM_MB} MiB VRAM (6–8 GB; alguns modelos podem não caber na VRAM)"
  else
    fail "GPU: ${GPU_MEM_MB} MiB VRAM (abaixo de 6 GB; GPU insuficiente para Ollama com modelos 7B)"
  fi
else
  warn "nvidia-smi não encontrado. Verificando PCI:"
  lspci 2>/dev/null | grep -iE "vga|3d" || warn "Nenhuma GPU detectada."
fi
echo ""

# ─── RAM ─────────────────────────────────────────────────────────────────────
echo "=== RAM ==="
free -h | head -2
TOTAL_RAM_GB=$(free -g | awk '$1 ~ /^Mem/ {print $2}')
if [[ "$TOTAL_RAM_GB" -ge 31 ]] 2>/dev/null; then
  ok "RAM: ${TOTAL_RAM_GB} GB (≥31 GB — equivalente à referência)"
elif [[ "$TOTAL_RAM_GB" -ge 16 ]] 2>/dev/null; then
  warn "RAM: ${TOTAL_RAM_GB} GB (16–31 GB; reduzir memória alocada ao Minikube proporcionalmente)"
else
  fail "RAM: ${TOTAL_RAM_GB} GB (abaixo de 16 GB; pode causar OOM com o cluster em 65%)"
fi
echo ""

# ─── SSD / Discos ────────────────────────────────────────────────────────────
echo "=== SSD / Discos ==="
lsblk -d -o NAME,SIZE,ROTA,MODEL 2>/dev/null || warn "lsblk não disponível."
echo ""
df -h /
ROOT_AVAIL_GB=$(df -BG / | awk 'NR==2{print $4}' | tr -d 'G')
if [[ "$ROOT_AVAIL_GB" -ge 200 ]] 2>/dev/null; then
  ok "Disco: ${ROOT_AVAIL_GB} GB livres na raiz (≥200 GB — OK para volumes do cluster)"
elif [[ "$ROOT_AVAIL_GB" -ge 100 ]] 2>/dev/null; then
  warn "Disco: ${ROOT_AVAIL_GB} GB livres na raiz (100–200 GB; suficiente mas monitore)"
else
  fail "Disco: ${ROOT_AVAIL_GB} GB livres na raiz (abaixo de 100 GB; risco de disco cheio)"
fi
echo ""

# ─── Dependências opcionais ───────────────────────────────────────────────────
echo "=== Dependências opcionais ==="
for cmd in docker minikube kubectl helm python3 ffmpeg git; do
  if command -v "$cmd" &>/dev/null; then
    ok "$cmd: $(command -v "$cmd")"
  else
    warn "$cmd: não instalado (execute setup.sh para instalar)"
  fi
done
echo ""

echo "============================================================"
echo "  Verificação concluída."
echo "  Referência: docs/00-objetivo-e-maquina-referencia.md"
echo "  Setup completo: ./scripts/setup.sh"
echo "============================================================"
