#!/usr/bin/env bash
# Manual de primeiros socorros GPU (Fase 3 — 030). Use quando recuperação automática não bastar.
# Uso: ./scripts/first-aid-gpu.sh [--phase 1|2|3]   (sem --phase: interativo)
# Ref: docs/30-manual-primeiros-socorros-gpu.md, docs/06-operacoes.md
set -e
NS="${NAMESPACE:-ai-agents}"
PHASE=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --phase) PHASE="$2"; shift 2 ;;
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
  echo "==> Fase 2: Reset cirúrgico (K8s)"
  kubectl delete pod -l app=ollama -n "$NS" --force --ignore-not-found --timeout=30s 2>/dev/null || true
  kubectl exec -n "$NS" deploy/redis -- redis-cli DEL gpu_active_lock 2>/dev/null || true
  kubectl delete pod -n kube-system -l app=nvidia-device-plugin-daemonset --force --ignore-not-found --timeout=30s 2>/dev/null || true
  echo "Fase 2 concluída. Aguarde pods subirem."
}

run_phase3() {
  echo "==> Fase 3: Reset de driver (nuclear)"
  echo "Isso pode fechar a interface gráfica. Continuar? [y/N]"
  read -r r
  [[ "$r" != "y" && "$r" != "Y" ]] && exit 0
  minikube stop 2>/dev/null || true
  echo "Encerrando processos em /dev/nvidia*..."
  sudo fuser -kv /dev/nvidia* 2>/dev/null || true
  echo "Recarregando nvidia_uvm..."
  sudo modprobe -r nvidia_uvm 2>/dev/null || true
  sudo modprobe nvidia_uvm 2>/dev/null || true
  echo "Fase 3 concluída. Reinicie minikube: minikube start ..."
}

if [[ -n "$PHASE" ]]; then
  case "$PHASE" in
    1) run_phase1 ;;
    2) run_phase2 ;;
    3) run_phase3 ;;
    *) echo "Uso: $0 --phase 1|2|3"; exit 2 ;;
  esac
  exit 0
fi

# Interativo
run_phase1 || true
echo ""
echo "Próximo passo: 2 = reset cirúrgico K8s, 3 = reset driver (nuclear), Enter = sair"
read -r next
case "$next" in
  2) run_phase2 ;;
  3) run_phase3 ;;
esac
