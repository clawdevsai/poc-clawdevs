#!/usr/bin/env bash
# Configura GPU NVIDIA dentro do Minikube (Docker driver).
# Deve ser executado APÓS "minikube start --gpus=all".
#
# O que faz:
#   1. Copia driver libs do host (/usr/lib/x86_64-linux-gnu/libnvidia*, libcuda*) para dentro do container Minikube
#   2. Copia nvidia-smi
#   3. Configura Docker runtime nvidia como default (nvidia-ctk)
#   4. Gera CDI spec
#   5. Reinicia Docker daemon dentro do Minikube
#   6. Reinicia o NVIDIA device plugin DaemonSet
#   7. Aguarda o node anunciar nvidia.com/gpu
#
# Uso: ./scripts/ops/minikube-gpu-setup.sh
# Pré-requisitos: Minikube rodando (docker driver + --gpus=all), NVIDIA driver no host.

set -euo pipefail

MINIKUBE_CONTAINER="${MINIKUBE_CONTAINER:-minikube}"
HOST_LIB="/usr/lib/x86_64-linux-gnu"
TARGET_LIB="/usr/lib/x86_64-linux-gnu"
NS="${NAMESPACE:-kube-system}"

info()  { echo -e "\033[1;34m[INFO]\033[0m $*"; }
ok()    { echo -e "\033[1;32m[ OK ]\033[0m $*"; }
fail()  { echo -e "\033[1;31m[FAIL]\033[0m $*"; }

if ! docker inspect "$MINIKUBE_CONTAINER" &>/dev/null; then
  fail "Container '$MINIKUBE_CONTAINER' não encontrado. Minikube está rodando?"
  exit 1
fi

if ! nvidia-smi &>/dev/null; then
  fail "nvidia-smi não disponível no host. Driver NVIDIA instalado?"
  exit 1
fi

DRIVER_VERSION=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null | head -1)
info "Driver NVIDIA no host: $DRIVER_VERSION"

info "Copiando driver libs para dentro do Minikube..."
COPIED=0
for pattern in "libnvidia-ml" "libcuda" "libnvidia-ptxjitcompiler" "libnvidia-gpucomp" \
               "libnvidia-nvvm" "libnvidia-encode" "libnvidia-allocator" "libnvidia-opencl" \
               "libnvidia-api" "libnvidia-cfg"; do
  for lib in "$HOST_LIB"/${pattern}.so*; do
    [ -e "$lib" ] || continue
    fname=$(basename "$lib")
    if [ -L "$lib" ]; then
      target=$(readlink "$lib")
      docker exec "$MINIKUBE_CONTAINER" ln -sf "$target" "$TARGET_LIB/$fname" 2>/dev/null || true
    else
      docker cp "$lib" "$MINIKUBE_CONTAINER:$TARGET_LIB/$fname" 2>/dev/null || true
    fi
    COPIED=$((COPIED + 1))
  done
done
ok "$COPIED libs copiadas"

info "Copiando nvidia-smi..."
docker cp "$(which nvidia-smi)" "$MINIKUBE_CONTAINER:/usr/bin/nvidia-smi" 2>/dev/null
ok "nvidia-smi copiado"

info "Atualizando ldconfig dentro do Minikube..."
docker exec "$MINIKUBE_CONTAINER" ldconfig 2>/dev/null

info "Verificando nvidia-smi dentro do Minikube..."
GPU_NAME=$(docker exec "$MINIKUBE_CONTAINER" nvidia-smi --query-gpu=name --format=csv,noheader 2>&1 || true)
if [ -z "$GPU_NAME" ]; then
  fail "nvidia-smi falhou dentro do Minikube. Verifique se --gpus=all foi usado."
  exit 1
fi
ok "GPU detectada: $GPU_NAME"

info "Configurando Docker runtime nvidia (nvidia-ctk)..."
docker exec "$MINIKUBE_CONTAINER" nvidia-ctk runtime configure --runtime=docker --set-as-default 2>&1 | grep -v "^time=" || true
ok "Docker runtime configurado"

info "Gerando CDI spec..."
docker exec "$MINIKUBE_CONTAINER" sh -c 'mkdir -p /etc/cdi && nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml 2>&1' | grep -E "^time.*level=(info|error)" || true
ok "CDI spec gerado"

info "Reiniciando Docker daemon dentro do Minikube (SIGHUP)..."
docker exec "$MINIKUBE_CONTAINER" pkill -SIGHUP dockerd 2>/dev/null || true
sleep 5

DEFAULT_RT=$(docker exec "$MINIKUBE_CONTAINER" docker info 2>/dev/null | grep "Default Runtime" || true)
ok "Docker: $DEFAULT_RT"

info "Reiniciando NVIDIA device plugin DaemonSet..."
kubectl rollout restart ds/nvidia-device-plugin-daemonset -n "$NS" 2>/dev/null || true
sleep 15

info "Verificando se o node anuncia nvidia.com/gpu..."
for i in $(seq 1 6); do
  GPU_COUNT=$(kubectl get nodes -o jsonpath='{.items[0].status.capacity.nvidia\.com/gpu}' 2>/dev/null || true)
  if [ -n "$GPU_COUNT" ] && [ "$GPU_COUNT" != "0" ]; then
    ok "Node anuncia nvidia.com/gpu: $GPU_COUNT"
    break
  fi
  if [ "$i" -eq 6 ]; then
    fail "Timeout: node não anuncia nvidia.com/gpu após 90s"
    echo "  Verifique: kubectl logs -n $NS -l name=nvidia-device-plugin-ds --tail=10"
    exit 1
  fi
  sleep 15
done

echo ""
ok "GPU configurada no Minikube. Próximos passos:"
echo "  kubectl rollout restart deploy/ollama-gpu -n ai-agents"
echo "  kubectl exec -n ai-agents deploy/ollama-gpu -- ollama ps  # deve mostrar 'GPU' na coluna PROCESSOR"
