#!/usr/bin/env bash
# setup.sh — ClawDevs
# Setup "um clique" do enxame de agentes de IA.
# Configura: dependências, Minikube (65% dos recursos), Redis, Ollama,
#            transcrição de áudio e OpenClaw com Telegram e voz.
#
# Referência: docs/issues/002-setup-um-clique.md | docs/09-setup-e-scripts.md
#
# USO:
#   chmod +x setup.sh && ./setup.sh
#   source ~/.bashrc   # após a conclusão

set -euo pipefail

# ─── Verificação de root ──────────────────────────────────────────────────────
if [[ "$EUID" -eq 0 ]]; then
  echo "ERRO: Não execute este script como root."
  echo "Execute como usuário normal: ./setup.sh"
  exit 1
fi

# ─── Cores e helpers ─────────────────────────────────────────────────────────
GREEN="\033[0;32m"; YELLOW="\033[1;33m"; BLUE="\033[0;34m"; RED="\033[0;31m"; RESET="\033[0m"
info()  { echo -e "${BLUE}[INFO]${RESET}  $*"; }
ok()    { echo -e "${GREEN}[OK]${RESET}    $*"; }
warn()  { echo -e "${YELLOW}[AVISO]${RESET} $*"; }
error() { echo -e "${RED}[ERRO]${RESET}  $*"; exit 1; }

banner() {
cat << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║          ClawDevs — Setup "Um Clique"                        ║
║  Time de Agentes de IA em Kubernetes + OpenClaw              ║
║  Criador: Diego Silva Morais                                 ║
╚══════════════════════════════════════════════════════════════╝
EOF
}
banner

# ─── Verificação de SO ───────────────────────────────────────────────────────
check_os() {
  if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    if [[ "$NAME" != "Pop!_OS" ]]; then
      warn "Sistema detectado: $NAME (recomendado: Pop!_OS 22.04/24.04)"
      read -rp "Deseja continuar mesmo assim? [s/N]: " CONTINUE
      [[ "${CONTINUE,,}" == "s" ]] || error "Setup cancelado."
    else
      ok "SO: $NAME $VERSION_ID"
    fi
  else
    warn "Não foi possível detectar o SO. Continuando..."
  fi
}
check_os

# ─── Coleta de chaves ────────────────────────────────────────────────────────
collect_keys() {
  info "Coletando chaves de API..."
  
  # Carrega variáveis do .env se existir para não perguntar novamente
  local SCRIPT_DIR
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  if [[ -f "$SCRIPT_DIR/../.env" ]]; then
    set -a; source "$SCRIPT_DIR/../.env" 2>/dev/null || true; set +a
  elif [[ -f "./.env" ]]; then
    set -a; source "./.env" 2>/dev/null || true; set +a
  fi

  while [[ -z "${GOOGLE_API_KEY:-}" ]]; do
    read -rp "Google AI Key (Gemini) [obrigatório]: " GOOGLE_API_KEY
  done
  while [[ -z "${TELEGRAM_TOKEN:-}" ]]; do
    read -rp "Telegram Bot Token [obrigatório]: " TELEGRAM_TOKEN
  done
  while [[ -z "${TELEGRAM_CHAT_ID:-}" ]]; do
    read -rp "Telegram Chat ID [obrigatório]: " TELEGRAM_CHAT_ID
  done
  ok "Chaves coletadas."
}
collect_keys

# ─── Cálculo de 65% da máquina ───────────────────────────────────────────────
TOTAL_CPUS=$(nproc)
TOTAL_RAM_GB=$(free -g | awk '$1 ~ /^Mem/ {print $2}')
GPU_VRAM_MB=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' ' || echo "0")

MK_CPUS=$(( TOTAL_CPUS * 65 / 100 ))
MK_RAM_MB=$(( TOTAL_RAM_GB * 1024 * 65 / 100 )) # Convert GB to MB for Minikube
MK_VRAM_MB=$(( GPU_VRAM_MB * 65 / 100 ))

[[ "$MK_CPUS" -lt 2 ]] && MK_CPUS=2
[[ "$MK_RAM_MB" -lt 4096 ]] && MK_RAM_MB=4096

info "Recursos detectados: ${TOTAL_CPUS} CPUs, ${TOTAL_RAM_GB}GB RAM, ${GPU_VRAM_MB}MB VRAM"
info "Limites de 65% aplicados: ${MK_CPUS} CPUs, ${MK_RAM_MB}MB RAM, ${MK_VRAM_MB}MB VRAM"

# ─── Atualização + dependências base ─────────────────────────────────────────
install_deps() {
  info "Atualizando sistema e instalando dependências..."
  sudo apt-get update -qq
  sudo apt-get upgrade -y -qq
  sudo apt-get install -y -qq \
    curl wget git python3 python3-pip python3-venv \
    ffmpeg conntrack socat ebtables \
    apt-transport-https ca-certificates gnupg lsb-release
  ok "Dependências base instaladas."
}
install_deps

# ─── Docker ──────────────────────────────────────────────────────────────────
install_docker() {
  if command -v docker &>/dev/null; then
    ok "Docker já instalado: $(docker --version)"
    return
  fi
  info "Instalando Docker (repositório oficial)..."
  sudo install -m 0755 -d /etc/apt/keyrings
  sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
  sudo chmod a+r /etc/apt/keyrings/docker.asc
  # Pop!_OS usa repositórios ubuntu nativamente. $(lsb_release -cs) deve voltar jammy ou o nome compatível.
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  sudo apt-get update -qq
  sudo apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  sudo usermod -aG docker "$USER"
  ok "Docker instalado. (Faça logout/login depois para grupos entrarem em vigor)"
}
install_docker

# ─── NVIDIA Container Toolkit ─────────────────────────────────────────────────
install_nvidia_toolkit() {
  if ! command -v nvidia-smi &>/dev/null; then
    warn "nvidia-smi não encontrado. Pulando instalação do NVIDIA Container Toolkit."
    return
  fi
  info "Instalando NVIDIA Container Toolkit..."
  curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \
    | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
  curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
    | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
    | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
  sudo apt-get update -qq
  sudo apt-get install -y -qq nvidia-container-toolkit
  sudo nvidia-ctk runtime configure --runtime=docker
  sudo systemctl restart docker
  ok "NVIDIA Container Toolkit instalado."
}
install_nvidia_toolkit

# ─── Minikube ────────────────────────────────────────────────────────────────
install_minikube() {
  if command -v minikube &>/dev/null; then
    ok "Minikube já instalado: $(minikube version --short)"
    return
  fi
  info "Instalando Minikube..."
  curl -Lo /tmp/minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
  sudo install /tmp/minikube /usr/local/bin/minikube
  rm /tmp/minikube
  ok "Minikube instalado."
}
install_minikube

# ─── kubectl ─────────────────────────────────────────────────────────────────
install_kubectl() {
  if command -v kubectl &>/dev/null; then
    ok "kubectl já instalado: $(kubectl version --client --short 2>/dev/null || kubectl version --client)"
    return
  fi
  info "Instalando kubectl..."
  sudo curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.29/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
  sudo chmod 644 /etc/apt/keyrings/kubernetes-apt-keyring.gpg
  echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.29/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
  sudo apt-get update -qq
  sudo apt-get install -y -qq kubectl
  ok "kubectl instalado."
}
install_kubectl

# ─── Helm ───────────────────────────────────────────────────────────────────
install_helm() {
  if command -v helm &>/dev/null; then
    ok "Helm já instalado: $(helm version --short)"
    return
  fi
  info "Instalando Helm..."
  curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
  ok "Helm instalado."
}
install_helm

# ─── Minikube start ──────────────────────────────────────────────────────────
start_minikube() {
  if minikube status 2>/dev/null | grep -q "Running"; then
    ok "Minikube já em execução."
  else
    info "Iniciando Minikube (${MK_CPUS} CPUs, ${MK_RAM_MB}MB RAM, driver=docker)..."
    ADDONS="ingress,dashboard"
    GPU_ARGS=""
    if [[ "$GPU_VRAM_MB" -gt 0 ]]; then
      # Conforme https://minikube.sigs.k8s.io/docs/tutorials/nvidia/
      GPU_ARGS="--container-runtime=docker --gpus all"
      ADDONS="${ADDONS},nvidia-device-plugin"
    fi
    
    minikube start \
      --driver=docker \
      --cpus="${MK_CPUS}" \
      --memory="${MK_RAM_MB}mb" \
      --addons="${ADDONS}" \
      ${GPU_ARGS}
    ok "Minikube iniciado."
  fi

  info "Configurando rótulos de nós e quotas..."
  # Garantir que o nó tenha os labels esperados pelos deployments
  kubectl label node minikube workload-type=gpu --overwrite 2>/dev/null || true
  kubectl label node minikube workload-type=cpu --overwrite 2>/dev/null || true
  kubectl label node minikube workload-type=cpu-only --overwrite 2>/dev/null || true
}
start_minikube

# ─── Namespace ai-agents ────────────────────────────────────────────────────
setup_namespace() {
  info "Criando namespace ai-agents e Quotas dinâmicas..."
  kubectl create namespace ai-agents --dry-run=client -o yaml | kubectl apply -f -
  
  # Gerar ResourceQuota dinâmico baseado nos 65% detectados
  cat <<EOF | kubectl apply -n ai-agents -f -
apiVersion: v1
kind: ResourceQuota
metadata:
  name: limite-65-por-cento
spec:
  hard:
    requests.cpu: "$(( MK_CPUS * 80 / 100 ))"
    limits.cpu: "$MK_CPUS"
    requests.memory: "$(( MK_RAM_MB * 80 / 100 ))Mi"
    limits.memory: "${MK_RAM_MB}Mi"
    pods: "20"
EOF

  ok "Namespace ai-agents e quota de ${MK_CPUS} CPUs / ${MK_RAM_MB}MB RAM configurados."
}
setup_namespace

# ─── Redis ──────────────────────────────────────────────────────────────────
install_redis() {
  if kubectl get pods -n ai-agents 2>/dev/null | grep -q "redis"; then
    ok "Redis já em execução no cluster."
    return
  fi
  info "Instalando Redis via Helm..."
  helm repo add bitnami https://charts.bitnami.com/bitnami --force-update
  helm upgrade --install redis bitnami/redis \
    --namespace ai-agents \
    --set architecture=standalone \
    --set auth.enabled=false \
    --set master.persistence.enabled=false \
    --wait --timeout 120s
  ok "Redis instalado no cluster."
}
install_redis

# ─── Ollama ─────────────────────────────────────────────────────────────────
deploy_ollama() {
  if kubectl get pods -n ai-agents 2>/dev/null | grep -q "ollama"; then
    ok "Ollama já em execução no cluster."
    return
  fi
  info "Implantando Ollama com limites dinâmicos (VRAM Max: ${MK_VRAM_MB}MB)..."
  
  OLLAMA_DIR="$(dirname "$0")/../k8s/ollama"
  # Patch dinâmico no deployment do Ollama para respeitar os 65% de VRAM e RAM
  sed -i "s/value: \"7168\"/value: \"$MK_VRAM_MB\"/" "$OLLAMA_DIR/deployment.yaml"
  
  kubectl apply -f "$OLLAMA_DIR/" -n ai-agents
  kubectl wait --for=condition=available deployment/ollama -n ai-agents --timeout=120s 2>/dev/null || \
    warn "Timeout aguardando Ollama. Verifique: kubectl get pods -n ai-agents"
  ok "Ollama implantado."
}
deploy_ollama

# ─── Transcrição de áudio ────────────────────────────────────────────────────
setup_transcription() {
  TRANSCRIPTION_DIR="$HOME/enxame/transcription"
  info "Configurando transcrição de áudio em $TRANSCRIPTION_DIR..."
  mkdir -p "$TRANSCRIPTION_DIR"
  cp "$(dirname "$0")/m4a_to_md.py" "$TRANSCRIPTION_DIR/m4a_to_md.py"
  python3 -m venv "$TRANSCRIPTION_DIR/venv"
  "$TRANSCRIPTION_DIR/venv/bin/pip" install --quiet faster-whisper tqdm
  ok "Transcrição configurada."
}
setup_transcription

# ─── OpenClaw config ─────────────────────────────────────────────────────────
setup_openclaw_config() {
  OPENCLAW_DIR="$HOME/enxame/openclaw"
  mkdir -p "$OPENCLAW_DIR"
  info "Gerando config.yaml do OpenClaw em $OPENCLAW_DIR..."
  cat > "$OPENCLAW_DIR/config.yaml" <<YAML
channels:
  telegram:
    token: "${TELEGRAM_TOKEN}"
    allowed_chat_ids:
      - ${TELEGRAM_CHAT_ID}
    voice_to_text:
      enabled: true
      command: "${HOME}/enxame/transcription/venv/bin/python ${HOME}/enxame/transcription/m4a_to_md.py"
      output_dir: "${HOME}/enxame/audio/transcriptions"

providers:
  google:
    api_key: "${GOOGLE_API_KEY}"
    model: "gemini-1.5-pro"
  ollama:
    base_url: "http://localhost:11434"
    default_model: "llama3:8b"

storage:
  redis:
    host: "redis-master.ai-agents.svc.cluster.local"
    port: 6379
    db: 0

agents:
  ceo:
    provider: google
    model: "gemini-1.5-pro"
    max_tokens: 4096
  po:
    provider: google
    model: "gemini-1.5-flash"
    max_tokens: 4096
  developer:
    provider: ollama
    model: "deepseek-coder:6.7b"
    max_tokens: 8192
  architect:
    provider: ollama
    model: "llama3:8b"
    max_tokens: 4096
  qa:
    provider: ollama
    model: "llama3:8b"
    max_tokens: 4096
  cybersec:
    provider: ollama
    model: "mistral:7b"
    max_tokens: 4096
  ux:
    provider: ollama
    model: "phi3:mini"
    max_tokens: 2048
  devops:
    provider: ollama
    model: "phi3:mini"
    max_tokens: 2048
  dba:
    provider: ollama
    model: "llama3:8b"
    max_tokens: 4096
YAML
  ok "config.yaml gerado."
}
setup_openclaw_config

# ─── Aliases e start.sh ──────────────────────────────────────────────────────
setup_aliases() {
  info "Adicionando aliases ao ~/.bashrc..."
  ALIASES_BLOCK="
# ─── ClawDevs Aliases ───────────────────────────────────────────────────────
alias k='kubectl'
alias h='helm'
alias m='minikube'
alias enxame='cd ~/enxame'
alias enxame-status='minikube status; echo \"---\"; kubectl get pods -n ai-agents; echo \"---\"; kubectl get svc -n ai-agents'
alias enxame-start='~/enxame/start.sh'
alias transcrever='${HOME}/enxame/transcription/venv/bin/python ${HOME}/enxame/transcription/m4a_to_md.py'
alias ceo='kubectl logs -f -n ai-agents -l app=agent-ceo'
alias logs-ollama='kubectl logs -f -n ai-agents -l app=ollama'
# ────────────────────────────────────────────────────────────────────────────
"
  if ! grep -q "ClawDevs Aliases" ~/.bashrc; then
    echo "$ALIASES_BLOCK" >> ~/.bashrc
  fi

  mkdir -p "$HOME/enxame"
  cat > "$HOME/enxame/start.sh" <<'STARTSH'
#!/usr/bin/env bash
set -euo pipefail
echo "Iniciando ClawDevs..."
minikube start --driver=docker 2>/dev/null || true
echo "=== Pods ==="
kubectl get pods -n ai-agents
echo "=== Serviços ==="
kubectl get svc -n ai-agents
echo ""
echo "Redis:"
kubectl exec -n ai-agents \
  $(kubectl get pods -n ai-agents -l app.kubernetes.io/name=redis -o jsonpath='{.items[0].metadata.name}' 2>/dev/null) \
  -- redis-cli ping 2>/dev/null || echo "Redis ainda iniciando..."
echo ""
echo "Ollama:"
kubectl exec -n ai-agents \
  $(kubectl get pods -n ai-agents -l app=ollama -o jsonpath='{.items[0].metadata.name}' 2>/dev/null) \
  -- ollama list 2>/dev/null || echo "Ollama ainda iniciando..."
echo ""
echo "ClawDevs pronto. Envie uma mensagem de áudio ou texto ao bot Telegram."
STARTSH
  chmod +x "$HOME/enxame/start.sh"
  ok "Aliases e start.sh configurados."
}
setup_aliases

# ─── Testes de validação ─────────────────────────────────────────────────────
run_tests() {
  info "Executando testes de validação..."
  echo -n "  Docker: "
  docker run --rm hello-world &>/dev/null && echo "OK" || echo "FALHA"
  echo -n "  Kubernetes: "
  kubectl get nodes &>/dev/null && echo "OK" || echo "FALHA"
  echo -n "  Redis: "
  kubectl get pods -n ai-agents 2>/dev/null | grep -q "redis" && echo "OK (pod encontrado)" || echo "Aguardando..."
  echo -n "  Transcrição: "
  python3 -c "import importlib.util; spec=importlib.util.find_spec('faster_whisper'); print('OK' if spec else 'AVISO (módulo não encontrado no PATH global; use o venv)')"
  ok "Testes concluídos."
}
run_tests

# ─── Mensagem final ──────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${GREEN}║  ClawDevs configurado com sucesso!                           ║${RESET}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${RESET}"
echo ""
echo "  Diretórios criados:"
echo "    ~/enxame/               — raiz do projeto"
echo "    ~/enxame/transcription/ — script e venv de transcrição"
echo "    ~/enxame/openclaw/      — config.yaml do OpenClaw"
echo "    ~/enxame/start.sh       — script de inicialização"
echo ""
echo "  Próximos passos:"
echo "    1. source ~/.bashrc        # Recarregue o shell"
echo "    2. enxame-start            # Inicie o enxame"
echo "    3. kubectl get pods -n ai-agents  # Verifique os pods"
echo "    4. Envie um áudio ou mensagem ao bot Telegram"
echo ""
echo "  Limites do cluster: ${MK_CPUS} CPUs / ${MK_RAM_GB}g RAM (65% da máquina)"
echo "  Docs: docs/README.md | Issues: docs/issues/README.md"
echo ""
warn "Recarregue o shell: source ~/.bashrc"
