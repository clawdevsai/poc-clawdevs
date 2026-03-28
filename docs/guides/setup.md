# Local Development Setup

**For:** All engineers (backend, frontend, DevOps)
**Duration:** 30-45 minutes
**Prerequisites:** Windows 11, Docker Desktop, make, git

---

## Table of Contents

1. [Requirements](#requirements)
2. [Quick Start](#quick-start)
3. [Configuration](#configuration)
4. [Verification](#verification)
5. [Troubleshooting](#troubleshooting)

---

## Requirements

### System Requirements

- **OS:** Windows 11 (Docker Desktop required)
- **CPU:** 4+ cores (Docker uses 2)
- **RAM:** 16 GB minimum (Docker uses 7 GB)
- **Storage:** 500 GB free (200 GB for Ollama models + 100 GB for OpenClaw data)
- **GPU:** Optional (NVIDIA with CUDA support recommended)

### Software

| Component | Version | Purpose |
|-----------|---------|---------|
| Docker Desktop | Latest | Container runtime |
| Docker | Latest | Local Docker Compose |
| docker-compose | Latest | Docker Compose CLI |
| make | GNU 4.3+ | Build automation |
| git | Latest | Version control |
| bash/zsh | Latest | Shell (Git Bash on Windows) |

### Installation

#### Windows 11 Setup

1. **Enable Virtualization**
   - Open Settings → System → About
   - Click "Advanced system settings"
   - Ensure "Virtualization Technology" is enabled in BIOS

2. **Install Docker Desktop**
   ```bash
   # Download and install from https://www.docker.com/products/docker-desktop
   docker --version  # Verify: should show version
   ```

3. **Install Docker**
   ```bash
   # Using Chocolatey (if installed)
   choco install docker

   # Or download from: https://docker.sigs.container.io/docs/start/
   docker version  # Verify
   ```

4. **Install docker-compose**
   ```bash
   # Usually comes with Docker Desktop
   docker-compose version --client  # Verify
   ```

5. **Install GNU make**
   ```bash
   # Using Chocolatey
   choco install make

   # Or: https://sourceforge.net/projects/gnuwin32/files/make/
   make --version  # Verify
   ```

6. **Clone the repository**
   ```bash
   git clone https://github.com/<ORG>/clawdevs-ai.git
   cd clawdevs-ai
   ```

---

## Quick Start

### 1. Prepare Configuration

```bash
# Copy environment template
cp container/.env.example container/.env

# Edit container/.env with your values
# Required (minimum):
OPENCLAW_GATEWAY_TOKEN=your-token-here
GIT_TOKEN=ghp_your-github-token
GIT_ORG=your-org
```

See [Environment Reference](../reference/environment.md) for all variables.

### 2. Validate Configuration

```bash
# Check required variables are set
make preflight

# Validate Docker Compose manifests
make manifests-validate
```

### 3. Start the Stack

```bash
# One-command setup (recommended for first run)
make clawdevs-up

# This runs:
# 1. Docker setup with GPU support
# 2. Docker Compose add-ons (dashboard, storage, NVIDIA plugin)
# 3. Deploy OpenClaw, Ollama, Control Panel
# 4. Wait for readiness
# Takes 5-10 minutes
```

### 4. Verify Installation

```bash
# Check all containers are running
docker-compose get containers

# Expected output:
# NAME                                    READY   STATUS
# openclaw-runtime-0                      1/1     Running
# ollama-runtime-0                        1/1     Running
# clawdevs-panel-backend-xxx              1/1     Running
# clawdevs-panel-frontend-xxx             1/1     Running
# postgres-xxx                            1/1     Running

# View logs
docker-compose logs -f container/openclaw-runtime-0 -c openclaw
```

### 5. Access the System

```bash
# Get Control Panel URL
make panel-url

# Output will show:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs

# Open browser to http://localhost:3000
```

---

## Configuration

### Environment Variables

Edit `container/.env`:

```bash
# OpenClaw
OPENCLAW_GATEWAY_TOKEN=<required>  # Bearer token for API
OPENCLAW_LOG_LEVEL=info            # debug|info|warn|error

# GitHub Integration
GIT_TOKEN=<required>               # Personal Access Token
GIT_ORG=<required>                 # Organization name
GIT_DEFAULT_REPOSITORY=<optional>  # org/repo fallback

# Telegram (Optional)
TELEGRAM_BOT_TOKEN_CEO=<optional>  # Bot token: id:hash
TELEGRAM_CHAT_ID_CEO=<optional>    # Chat ID for notifications

# LLM Provider
PROVEDOR_LLM=ollama                # ollama|openrouter
OPENROUTER_API_KEY=<optional>      # For cloud models
OPENROUTER_MODEL=<optional>        # stepfun/step-3.5-flash:free

# Image Building
PUSH_IMAGE=remote                  # remote|local

# Other
DEBUG_LOG_ENABLED=false            # true for verbose logs
LANGUAGE=pt-BR                     # en-US|pt-BR
```

### First Run Checklist

- ✓ Docker Desktop running with GPU (if available)
- ✓ Docker supports `docker` driver
- ✓ 300+ GB free disk space
- ✓ `container/.env` filled with required values
- ✓ `make preflight` passes
- ✓ `make manifests-validate` passes

---

## Verification

### Health Checks

```bash
# Check cluster status
docker status

# Expected:
# docker: Running
# driver: docker
# docker compose config: Configured

# Check containers
docker-compose get containers --all-environments

# Check storage
docker-compose get pvc

# Expected:
# openclaw-data    Bound    150 GB
# ollama-data      Bound    200 GB
# panel-db         Bound     20 GB

# Check services
docker-compose get svc

# Expected:
# openclaw-gateway   ClusterIP   8080
# ollama-api        ClusterIP   11434
# panel-backend     ClusterIP   8000
# panel-frontend    ClusterIP   3000
```

### Gateway Connectivity

```bash
# Test OpenClaw gateway
docker-compose port-forward service/openclaw-gateway 8080:8080

# In another terminal
curl -H "Authorization: Bearer $OPENCLAW_GATEWAY_TOKEN" \
  http://localhost:8080/health

# Expected: 200 OK with JSON response
```

### Control Panel Access

```bash
# Port-forward to local
make panel-forward

# Open browser: http://localhost:3000
# Expected: Control Panel login screen
```

### Ollama Verification

```bash
# Check models are loaded
docker-compose exec -it container/ollama-runtime-0 -- ollama list

# Expected models:
# nemotron-3-super:cloud
# nomic-embed-text

# Test model
docker-compose exec -it container/ollama-runtime-0 -- ollama run nemotron-3-super:cloud "hello"
```

---

## Troubleshooting

### Docker Desktop Issues

**Problem:** `Docker daemon is not running`

```bash
# Solution 1: Start Docker Desktop
# Solution 2: Check if WSL 2 backend is enabled
docker run hello-world  # Test
```

**Problem:** `Cannot allocate memory`

```bash
# Solution: Increase Docker Desktop resources
# Settings → Resources → Memory: 12 GB or more
```

### Docker Issues

**Problem:** `Docker failed to start`

```bash
# Solution 1: Check Docker
docker ps  # Should return empty list, not error

# Solution 2: Reset Docker
docker delete
make docker-up

# Solution 3: Use Docker driver explicitly
docker start --driver=docker
```

**Problem:** `docker compose config context not found`

```bash
# Solution: Set context
docker-compose config use-context clawdevs-ai

# Or: Reset contexts
docker delete
make docker-context
```

### Storage Issues

**Problem:** `PersistentVolumeClaim pending`

```bash
# Check PVC status
docker-compose describe pvc openclaw-data

# Solution: Enable storage-provisioner
make storage-enable-expansion

# Or: Check available disk space
df -h

# Need 300+ GB free
```

**Problem:** `No space left on device`

```bash
# Check usage
docker-compose exec -it container/ollama-runtime-0 -- df -h

# Solution 1: Delete old models
docker-compose exec -it container/ollama-runtime-0 -- ollama rm model-name

# Solution 2: Clean Docker
docker system prune --all

# Solution 3: Increase storage
# container/base/pvc.yaml - increase size in spec.resources.requests.storage
```

### GPU Issues

**Problem:** `GPU not available`

```bash
# Check GPU
make gpu-doctor

# Expected: GPU listed and accessible

# If not found:
make gpu-plugin-apply
make gpu-node-check
```

**Problem:** `Out of GPU memory`

```bash
# Check Ollama GPU allocation
docker-compose exec -it container/ollama-runtime-0 -- env | grep OLLAMA

# Reduce model size or use CPU fallback
# Edit container/base/ollama-container.yaml
# Change model to smaller (qwen3-next instead of nemotron-3-super)
make ollama-restart
```

### Agent Issues

**Problem:** `No agents running`

```bash
# Check OpenClaw logs
make openclaw-logs

# Look for: "Agent registered", "Session started"

# Trigger manually
docker-compose exec -it statefulset/clawdevs-ai -c openclaw -- \
  openclaw agent --agent dev_backend --message "hello"
```

**Problem:** `Agent stuck in loop`

```bash
# Check logs
docker-compose logs -f container/openclaw-runtime-0 -c openclaw | grep ERROR

# Kill stuck session
docker-compose exec -it statefulset/clawdevs-ai -c openclaw -- \
  openclaw session reset agent:dev_backend:main

# Or reset everything
make reset-all
```

### Control Panel Issues

**Problem:** `Panel shows no agents`

```bash
# Check backend logs
make panel-logs-backend

# Check database
docker-compose exec -it container/postgres-xxx -- psql -U postgres

# Verify migrations ran
make panel-db-migrate
```

**Problem:** `Cannot connect to OpenClaw`

```bash
# Check gateway token
echo $OPENCLAW_GATEWAY_TOKEN

# Should be set in container/.env

# Verify connectivity
docker-compose exec -it container/clawdevs-panel-backend-xxx -- \
  curl -H "Authorization: Bearer $OPENCLAW_GATEWAY_TOKEN" \
  http://openclaw-gateway:8080/health
```

---

## Next Steps

1. **Run your first task**
   ```bash
   # Open Control Panel: http://localhost:3000
   # Trigger dev_backend agent
   # Check logs in real-time
   ```

2. **Understand the system**
   - Read [Architecture Overview](../architecture/overview.md)
   - Read [Agents Architecture](../architecture/agents.md)

3. **Start development**
   - Backend: [Backend Setup](./backend-setup.md)
   - Frontend: [Frontend Setup](./frontend-setup.md)
   - Infrastructure: [Deployment Guide](./deployment.md)

4. **Debug issues**
   - See [Troubleshooting Guide](../operations/troubleshooting.md)

---

## Commands Reference

```bash
# Management
make help                  # All available commands
make clawdevs-up          # Full setup
make clawdevs-down        # Tear down
make stack-status         # Check health

# Monitoring
make openclaw-logs        # Agent logs
make panel-logs-backend   # API logs
make gpu-doctor           # GPU diagnostics

# Development
docker-compose get containers          # List containers
docker-compose describe container <name>  # Container details
docker-compose logs -f container/<name>   # Live logs
docker-compose exec -it container/<name> bash  # Shell access

# Cleanup
make reset-all            # Full reset (destructive)
make destroy-all          # Complete cleanup
```

---

**Questions?** Check [Glossary](../reference/glossary.md) for terminology.
