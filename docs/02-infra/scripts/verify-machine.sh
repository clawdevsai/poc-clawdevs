#!/usr/bin/env bash
# Verificação da máquina (máquina de referência) — somente leitura.
# Uso: ./verify-machine.sh
# Ref: docs/scripts/verify-machine.md, docs/00-objetivo-e-maquina-referencia.md, docs/04-infraestrutura.md (65%)

set -e

echo "=== CPU (consumo: load average = uso recente) ==="
if command -v lscpu &>/dev/null; then
  lscpu 2>/dev/null | grep -E "Model name|CPU\(s\)|Thread\(s\) per core|Core\(s\) per socket|Nome do modelo|Thread\(s\) per núcleo|Núcleo\(s\) por soquete" 2>/dev/null || lscpu 2>/dev/null | head -20
fi
if [[ -r /proc/loadavg ]]; then
  read -r LOAD1 LOAD5 LOAD15 _ < /proc/loadavg 2>/dev/null || true
  CPUS_FOR_LOAD=$(lscpu 2>/dev/null | awk -F: '/^CPU\(s\):/{gsub(/ /,"",$2); print $2}')
  [[ -z "$CPUS_FOR_LOAD" || ! "$CPUS_FOR_LOAD" =~ ^[0-9]+$ ]] && CPUS_FOR_LOAD=1
  echo "  Load average: ${LOAD1:-?} ${LOAD5:-?} ${LOAD15:-?} (1m, 5m, 15m) | threads: ${CPUS_FOR_LOAD}"
fi
if ! command -v lscpu &>/dev/null; then
  echo "(lscpu não encontrado)"
fi

echo ""
echo "=== GPU (consumo: uso atual / total) ==="
if command -v nvidia-smi &>/dev/null; then
  nvidia-smi --query-gpu=name,memory.used,memory.total,memory.free,utilization.gpu,driver_version --format=csv,noheader 2>/dev/null | while IFS=, read -r name mem_used mem_total mem_free util driver; do
    echo "  Modelo: $name | VRAM: $mem_used / $mem_total (livre: $mem_free) | GPU util: $util | Driver: $driver"
  done
  [[ -z "$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null)" ]] && nvidia-smi 2>/dev/null | head -15
else
  echo "AVISO: nvidia-smi não encontrado (NVIDIA não instalada ou não disponível)."
  command -v lspci &>/dev/null && lspci 2>/dev/null | grep -iE "vga|3d" || true
fi

echo ""
echo "=== RAM (consumo: usado / total, disponível) ==="
free -h | head -2
if [[ -r /proc/meminfo ]]; then
  MEM_TOT_KB=$(awk '/^MemTotal:/{print $2}' /proc/meminfo)
  MEM_AVA_KB=$(awk '/^MemAvailable:/{print $2}' /proc/meminfo)
  if [[ -n "$MEM_TOT_KB" && "$MEM_TOT_KB" =~ ^[0-9]+$ && -n "$MEM_AVA_KB" && "$MEM_AVA_KB" =~ ^[0-9]+$ ]]; then
    MEM_USED_KB=$(( MEM_TOT_KB - MEM_AVA_KB ))
    MEM_TOT_GB=$(( MEM_TOT_KB / 1024 / 1024 ))
    MEM_USED_GB=$(( MEM_USED_KB / 1024 / 1024 ))
    MEM_AVA_GB=$(( MEM_AVA_KB / 1024 / 1024 ))
    PCT=$(( MEM_USED_KB * 100 / MEM_TOT_KB ))
    echo "  Consumo: ${MEM_USED_GB} GB usado / ${MEM_TOT_GB} GB total (${PCT}%) | disponível: ${MEM_AVA_GB} GB"
  fi
fi

echo ""
echo "=== SSD / Discos ==="
lsblk -d -o NAME,SIZE,ROTA,MODEL 2>/dev/null || true
df -h /

# --- Resumo OK/aviso e Quest 65% ---
echo ""
echo "----------------------------------------"
echo "Resumo e Quest 65% (limite cluster)"
echo "----------------------------------------"

# CPU: total de threads (lscpu "CPU(s)")
CPUS=0
if command -v lscpu &>/dev/null; then
  CPUS=$(lscpu 2>/dev/null | awk -F: '/^CPU\(s\):/{gsub(/ /,"",$2); print $2}')
  [[ -z "$CPUS" || ! "$CPUS" =~ ^[0-9]+$ ]] && CPUS=0
fi
if [[ "$CPUS" -gt 0 ]]; then
  # 65% dos CPUs (arredondado para inteiro, mínimo 1)
  CPU_65=$(( (CPUS * 65 + 50) / 100 ))
  [[ "$CPU_65" -lt 1 ]] && CPU_65=1
  echo "CPU: ${CPUS} threads → para Minikube (65%): --cpus=${CPU_65}"
else
  echo "CPU: (não foi possível obter o número de threads)"
fi

# RAM: total (MemTotal em kB em /proc/meminfo)
RAM_KB=0
if [[ -r /proc/meminfo ]]; then
  RAM_KB=$(awk '/^MemTotal:/{print $2}' /proc/meminfo 2>/dev/null)
  [[ -z "$RAM_KB" || ! "$RAM_KB" =~ ^[0-9]+$ ]] && RAM_KB=0
fi
if [[ "$RAM_KB" -gt 0 ]]; then
  RAM_GB=$(( RAM_KB / 1024 / 1024 ))
  RAM_65_GB=$(( (RAM_GB * 65 + 50) / 100 ))
  [[ "$RAM_65_GB" -lt 1 ]] && RAM_65_GB=1
  echo "RAM: ${RAM_GB} GB total → para Minikube (65%): --memory=${RAM_65_GB}g"
  if [[ "$RAM_GB" -lt 16 ]]; then
    echo "AVISO: RAM total (${RAM_GB} GB) abaixo do recomendado para máquina de referência (~31 GB)."
  fi
else
  echo "RAM: (não foi possível obter o total)"
fi

# GPU
if ! command -v nvidia-smi &>/dev/null; then
  echo "AVISO: GPU NVIDIA não detectada (nvidia-smi ausente). Inferência local (Ollama) com GPU não disponível."
elif ! nvidia-smi &>/dev/null; then
  echo "AVISO: nvidia-smi falhou. Verifique driver e container toolkit."
fi

echo ""
echo "Comando Minikube sugerido (ajuste driver conforme [04-infraestrutura.md]):"
echo "  minikube start --driver=docker --addons=nvidia-device-plugin --cpus=${CPU_65:-4} --memory=${RAM_65_GB:-16}g"
echo ""
echo "Referência: máquina de referência [00-objetivo-e-maquina-referencia.md], limites 65% [04-infraestrutura.md]"
