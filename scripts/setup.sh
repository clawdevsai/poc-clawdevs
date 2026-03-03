#!/usr/bin/env bash
# Setup "um clique" — ClawDevs (Fase 0 — 002)
# Configura ambiente: dependências, Minikube 65%, Redis, Ollama, transcrição, OpenClaw/Telegram.
# Não executa como root. Pop!_OS recomendado. Executar a partir da raiz do repositório: ./scripts/setup.sh
set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." && pwd)"
ENXAME_DIR="${ENXAME_DIR:-$HOME/enxame}"
MINIKUBE_CPUS="${MINIKUBE_CPUS:-10}"
MINIKUBE_MEMORY="${MINIKUBE_MEMORY:-20g}"

echo "==> ClawDevs — Setup um clique"
echo "    Repositório: $REPO_ROOT"
echo "    Enxame (transcrição/config): $ENXAME_DIR"
echo ""

if [[ ! -f "$REPO_ROOT/Makefile" || ! -d "$REPO_ROOT/k8s" ]]; then
  echo "ERRO: Execute este script a partir do repositório ClawDevs (onde estão Makefile e k8s/)."
  exit 1
fi

# --- 1. Não rodar como root ---
if [[ "$(id -u)" -eq 0 ]]; then
  echo "ERRO: Não execute este script como root. Use um usuário normal (sudo será solicitado se necessário)."
  exit 1
fi

# --- 2. Verificar SO (Pop!_OS ou aviso) ---
if [[ -f /etc/os-release ]]; then
  source /etc/os-release
  if [[ "${ID:-}" != "pop" && "${ID_LIKE:-}" != *"ubuntu"* ]]; then
    echo "AVISO: Sistema detectado: $PRETTY_NAME. Este setup foi validado em Pop!_OS."
    read -r -p "Deseja continuar mesmo assim? [s/N] " resp
    case "${resp}" in
      [sS][iI][mM]|[sS]) ;;
      *) echo "Abortado."; exit 0 ;;
    esac
  fi
fi

# --- 3. Coletar chaves (Telegram obrigatório; Slack opcional) ---
echo "==> Chaves do Telegram (obrigatórias para o bot e o chat do Diretor — só o CEO usa Telegram)"
read -r -p "Telegram Bot Token: " TELEGRAM_BOT_TOKEN
read -r -p "Telegram Chat ID (numérico): " TELEGRAM_CHAT_ID
if [[ -z "$TELEGRAM_BOT_TOKEN" || -z "$TELEGRAM_CHAT_ID" ]]; then
  echo "ERRO: Token e Chat ID não podem ser vazios."
  exit 1
fi
echo ""
echo "==> Slack OpenClaw (opcional — app próprio para gateway DM + canal; discussões = Ollama local GPU)"
read -r -p "Habilitar Slack para OpenClaw? [s/N] " SLACK_YN
OPENCLAW_SLACK_APP_TOKEN=""
OPENCLAW_SLACK_BOT_TOKEN=""
OPENCLAW_SLACK_DIRECTOR_USER_ID=""
if [[ "${SLACK_YN,,}" == "s" || "${SLACK_YN,,}" == "sim" ]]; then
  read -r -p "OPENCLAW_SLACK_APP_TOKEN (xapp-...): " OPENCLAW_SLACK_APP_TOKEN
  read -r -p "OPENCLAW_SLACK_BOT_TOKEN (xoxb-...): " OPENCLAW_SLACK_BOT_TOKEN
  read -r -p "OPENCLAW_SLACK_DIRECTOR_USER_ID (opcional, ex. U01234ABCD): " OPENCLAW_SLACK_DIRECTOR_USER_ID || true
fi
echo "Opcional: Ollama Cloud (deixe vazio para uso 100% local no cluster)"
read -r -p "OLLAMA_API_KEY (Ollama Cloud): " OLLAMA_API_KEY_OPTIONAL || true

# --- 4. Dependências do sistema ---
echo ""
echo "==> Atualizando sistema e instalando dependências..."
sudo apt-get update -qq
sudo apt-get install -y -qq curl git python3 python3-venv python3-pip ffmpeg conntrack

# --- 5. Docker ---
if ! command -v docker &>/dev/null; then
  echo "==> Instalando Docker..."
  curl -fsSL https://get.docker.com | sh
  sudo usermod -aG docker "$USER" || true
  echo "    Faça logout/login ou execute 'newgrp docker' para usar docker sem sudo."
else
  echo "==> Docker já instalado."
fi

# --- 6. NVIDIA Container Toolkit (se GPU NVIDIA) ---
if command -v nvidia-smi &>/dev/null; then
  if ! dpkg -l nvidia-container-toolkit &>/dev/null; then
    echo "==> Instalando nvidia-container-toolkit..."
    distribution=$(. /etc/os-release;echo "$ID$VERSION_ID")
    curl -s -L https://nvidia.github.io/libnvidia-container/gpgkey | sudo apt-key add -
    curl -s -L "https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list" | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
    sudo apt-get update -qq && sudo apt-get install -y -qq nvidia-container-toolkit
    sudo nvidia-ctk runtime configure --runtime=docker
    echo "    Pode ser necessário reiniciar o Docker (ou o sistema)."
  fi
fi

# --- 7. kubectl e Minikube ---
if ! command -v kubectl &>/dev/null; then
  echo "==> Instalando kubectl..."
  curl -sLO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
  chmod +x kubectl && sudo mv kubectl /usr/local/bin/
fi
if ! command -v minikube &>/dev/null; then
  echo "==> Instalando Minikube..."
  curl -sLO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
  chmod +x minikube-linux-amd64 && sudo mv minikube-linux-amd64 /usr/local/bin/minikube
fi

# --- 8. Diretório de transcrição e m4a_to_md.py ---
echo ""
echo "==> Configurando transcrição (faster-whisper)..."
mkdir -p "$ENXAME_DIR/transcription" "$ENXAME_DIR/audio/transcriptions"
cp "$REPO_ROOT/app/m4a_to_md.py" "$ENXAME_DIR/transcription/"
python3 -m venv "$ENXAME_DIR/transcription/venv"
"$ENXAME_DIR/transcription/venv/bin/pip" install -q faster-whisper tqdm
chmod +x "$ENXAME_DIR/transcription/m4a_to_md.py"

# --- 9. Config OpenClaw (~/enxame/openclaw/config.yaml) ---
mkdir -p "$ENXAME_DIR/openclaw"
VOICE_CMD="$ENXAME_DIR/transcription/venv/bin/python $ENXAME_DIR/transcription/m4a_to_md.py"
cat > "$ENXAME_DIR/openclaw/config.yaml" << EOF
# Gerado por setup.sh — ClawDevs
channels:
  telegram:
    token: "$TELEGRAM_BOT_TOKEN"
    allowed_chat_ids:
      - $TELEGRAM_CHAT_ID
    voice_to_text:
      enabled: true
      command: "$VOICE_CMD"
      output_dir: "$ENXAME_DIR/audio/transcriptions"

# Ollama no cluster (make up aplica o deployment)
providers:
  ollama:
    host: "http://ollama-service.ai-agents.svc.cluster.local:11434"
    default_model: "glm-5:cloud"
EOF

# --- 10. Secret Kubernetes (para make up) ---
mkdir -p "$REPO_ROOT/k8s/management-team/openclaw"
SECRET_FILE="$REPO_ROOT/k8s/management-team/openclaw/secret.yaml"
{
  echo '# Gerado por setup.sh — NUNCA commitar com valores reais em repositório público'
  echo 'apiVersion: v1'
  echo 'kind: Secret'
  echo 'metadata:'
  echo '  name: openclaw-telegram'
  echo '  namespace: ai-agents'
  echo 'type: Opaque'
  echo 'stringData:'
  printf '  TELEGRAM_BOT_TOKEN: "%s"\n' "$TELEGRAM_BOT_TOKEN"
  printf '  TELEGRAM_CHAT_ID: "%s"\n' "$TELEGRAM_CHAT_ID"
  [[ -n "$OLLAMA_API_KEY_OPTIONAL" ]] && printf '  OLLAMA_API_KEY: "%s"\n' "$OLLAMA_API_KEY_OPTIONAL"
  [[ -n "$OPENCLAW_SLACK_APP_TOKEN" ]] && printf '  SLACK_APP_TOKEN: "%s"\n' "$OPENCLAW_SLACK_APP_TOKEN"
  [[ -n "$OPENCLAW_SLACK_BOT_TOKEN" ]] && printf '  SLACK_BOT_TOKEN: "%s"\n' "$OPENCLAW_SLACK_BOT_TOKEN"
  [[ -n "$OPENCLAW_SLACK_DIRECTOR_USER_ID" ]] && printf '  SLACK_DIRECTOR_USER_ID: "%s"\n' "$OPENCLAW_SLACK_DIRECTOR_USER_ID"
} > "$SECRET_FILE"
echo "    Secret gravado em k8s/management-team/openclaw/secret.yaml (não commitar)."

# --- 11. Aliases e start.sh ---
START_SH="$ENXAME_DIR/start.sh"
cat > "$START_SH" << 'STARTEOF'
#!/usr/bin/env bash
# Inicia Minikube (se necessário) e verifica pods do ClawDevs
set -e
if ! minikube status &>/dev/null; then
  minikube start --driver=docker --addons=nvidia-device-plugin --cpus=10 --memory=20g
  minikube addons enable nvidia-device-plugin 2>/dev/null || true
fi
echo "Minikube: $(minikube status 2>/dev/null | head -1)"
kubectl get pods -n ai-agents 2>/dev/null || true
STARTEOF
chmod +x "$START_SH"

ALIASES=(
  "alias enxame-status='minikube status 2>/dev/null; kubectl get pods -n ai-agents 2>/dev/null'"
  "alias transcrever='$ENXAME_DIR/transcription/venv/bin/python $ENXAME_DIR/transcription/m4a_to_md.py'"
  "alias ceo='kubectl logs -n ai-agents -l app=openclaw -f --tail=50'"
  "alias enxame-start='$START_SH'"
)
for a in "${ALIASES[@]}"; do
  if ! grep -F "$a" "$HOME/.bashrc" &>/dev/null; then
    echo "$a" >> "$HOME/.bashrc"
  fi
done
echo "    Aliases adicionados ao ~/.bashrc: enxame-status, transcrever, ceo, enxame-start"

# --- 12. Make prepare e make up (a partir do repositório) ---
echo ""
echo "==> Iniciando Minikube e aplicando recursos (make prepare && make up)..."
cd "$REPO_ROOT"
export MINIKUBE_CPUS MINIKUBE_MEMORY
make prepare
make up

# --- 13. Testes de validação ---
echo ""
echo "==> Validação rápida..."
docker run --rm hello-world &>/dev/null && echo "    Docker: OK" || echo "    Docker: falha (pode precisar newgrp docker)"
minikube status &>/dev/null && echo "    Minikube: OK" || echo "    Minikube: verifique com minikube status"
kubectl get pods -n ai-agents &>/dev/null && echo "    Namespace ai-agents: OK" || echo "    Namespace: verifique kubectl get pods -n ai-agents"
"$ENXAME_DIR/transcription/venv/bin/python" "$ENXAME_DIR/transcription/m4a_to_md.py" --help &>/dev/null && echo "    Transcrição (m4a_to_md): OK" || echo "    Transcrição: verifique venv"

# --- 14. Próximos passos ---
echo ""
echo "=== Setup concluído ==="
echo "  Diretórios: $ENXAME_DIR/transcription, $ENXAME_DIR/openclaw"
echo "  Recarregue o shell: source ~/.bashrc"
echo "  Comandos: enxame-status | transcrever arquivo.m4a | ceo (logs do gateway)"
echo "  Telegram: só o CEO. Slack: todos os agentes (se habilitado). Todos compartilham o mesmo workspace."
echo "  Discussões entre agentes no Slack: Ollama local GPU obrigatório."
echo "  Envie uma mensagem ao bot no Telegram (ou no Slack) para testar."
echo "  Documentação: $REPO_ROOT/docs/09-setup-e-scripts.md"
