#!/usr/bin/env bash
# Manual de primeiros socorros GPU (Fase 3 — 030). Use quando recuperação automática não bastar.
# Uso: ./scripts/ops/first-aid-gpu.sh [--phase 1|2|3]   (sem --phase: interativo)
set -e
NS="${NAMESPACE:-ai-agents}"
STEP=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --step|--phase) STEP="$2"; shift 2 ;;
    *) shift ;;
  esac
done

run_phase1() {
  echo "==> Fase 1: Diagnóstico (nvidia-smi)"
  if ! command -v nvidia-smi &>/dev/null; then
    echo "nvidia-smi não encontrado. Rode no host (Pop!_OS)."
    return 1
  fi
  if timeout 5 nvidia-smi &>/dev/null; then
    nvidia-smi
    echo ""
    echo "Se há Memory Leak ou zumbis, rode: $0 --phase 2"
  else
    echo "nvidia-smi travou. Rode: $0 --phase 3 (reset driver)"
    return 2
  fi
}

run_phase2() {
  echo "==> Fase 2: Limpeza (kill processos GPU zumbis)"
  if ! command -v nvidia-smi &>/dev/null; then
    echo "nvidia-smi não encontrado."
    return 1
  fi
  nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | while read -r pid; do
    [ -z "$pid" ] || kill -9 "$pid" 2>/dev/null || true
  done
  echo "Processos GPU encerrados. Se persistir, rode: $0 --phase 3"
}

run_phase3() {
  echo "==> Fase 3: Reset driver (requer sudo)"
  echo "Reiniciar o driver NVIDIA pode desligar telas. Continuar? [s/N]"
  read -r r
  case "$r" in
    [sS][iI][mM]|[sS])
      sudo nvidia-smi --gpu-reset 2>/dev/null || sudo rmmod nvidia_uvm nvidia_drm nvidia_modeset nvidia 2>/dev/null; sudo modprobe nvidia
      echo "Driver reiniciado. Teste: nvidia-smi"
      ;;
    *) echo "Cancelado." ;;
  esac
}

case "$STEP" in
  1) run_phase1 ;;
  2) run_phase2 ;;
  3) run_phase3 ;;
  *)
    run_phase1 || true
    echo ""
    echo "Próximo passo? [1=diagnóstico 2=limpeza 3=reset driver q=sair]"
    read -r next
    case "$next" in
      2) run_phase2 ;;
      3) run_phase3 ;;
      *) ;;
    esac
    ;;
esac
