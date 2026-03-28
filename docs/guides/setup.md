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
- **CPU:** 4+ cores (Minikube uses 2)
- **RAM:** 16 GB minimum (Minikube uses 7 GB)
- **Storage:** 500 GB free (200 GB for Ollama models + 100 GB for OpenClaw data)
- **GPU:** Optional (NVIDIA with CUDA support recommended)

### Software

| Component | Version | Purpose |
|-----------|---------|---------|
| Docker Desktop | Latest | Container runtime |
| Minikube | Latest | Local Kubernetes |
| kubectl | Latest | Kubernetes CLI |
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

3. **Install Minikube**
   ```bash
   # Using Chocolatey (if installed)
   choco install minikube

   # Or download from: https://minikube.sigs.k8s.io/docs/start/
   minikube version  # Verify
   ```

4. **Install kubectl**
   ```bash
   # Usually comes with Docker Desktop
   kubectl version --client  # Verify
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
cp k8s/.env.example k8s/.env

# Edit k8s/.env with your values
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

# Validate Kubernetes manifests
make manifests-validate
```

### 3. Start the Stack

```bash
# One-command setup (recommended for first run)
make clawdevs-up

# This runs:
# 1. Minikube setup with GPU support
# 2. Kubernetes add-ons (dashboard, storage, NVIDIA plugin)
# 3. Deploy OpenClaw, Ollama, Control Panel
# 4. Wait for readiness
# Takes 5-10 minutes
```

### 4. Verify Installation

```bash
# Check all pods are running
kubectl get pods

# Expected output:
# NAME                                    READY   STATUS
# openclaw-runtime-0                      1/1     Running
# ollama-runtime-0                        1/1     Running
# clawdevs-panel-backend-xxx              1/1     Running
# clawdevs-panel-frontend-xxx             1/1     Running
# postgres-xxx                            1/1     Running

# View logs
kubectl logs -f pod/openclaw-runtime-0 -c openclaw
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

Edit `k8s/.env`:

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
- ✓ Minikube supports `docker` driver
- ✓ 300+ GB free disk space
- ✓ `k8s/.env` filled with required values
- ✓ `make preflight` passes
- ✓ `make manifests-validate` passes

---

## Verification

### Health Checks

```bash
# Check cluster status
minikube status

# Expected:
# minikube: Running
# driver: docker
# kubeconfig: Configured

# Check pods
kubectl get pods --all-namespaces

# Check storage
kubectl get pvc

# Expected:
# openclaw-data    Bound    150 GB
# ollama-data      Bound    200 GB
# panel-db         Bound     20 GB

# Check services
kubectl get svc

# Expected:
# openclaw-gateway   ClusterIP   8080
# ollama-api        ClusterIP   11434
# panel-backend     ClusterIP   8000
# panel-frontend    ClusterIP   3000
```

### Gateway Connectivity

```bash
# Test OpenClaw gateway
kubectl port-forward service/openclaw-gateway 8080:8080

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
kubectl exec -it pod/ollama-runtime-0 -- ollama list

# Expected models:
# nemotron-3-super:cloud
# nomic-embed-text

# Test model
kubectl exec -it pod/ollama-runtime-0 -- ollama run nemotron-3-super:cloud "hello"
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

### Minikube Issues

**Problem:** `Minikube failed to start`

```bash
# Solution 1: Check Docker
docker ps  # Should return empty list, not error

# Solution 2: Reset Minikube
minikube delete
make minikube-up

# Solution 3: Use Docker driver explicitly
minikube start --driver=docker
```

**Problem:** `kubeconfig context not found`

```bash
# Solution: Set context
kubectl config use-context clawdevs-ai

# Or: Reset contexts
minikube delete
make minikube-context
```

### Storage Issues

**Problem:** `PersistentVolumeClaim pending`

```bash
# Check PVC status
kubectl describe pvc openclaw-data

# Solution: Enable storage-provisioner
make storage-enable-expansion

# Or: Check available disk space
df -h

# Need 300+ GB free
```

**Problem:** `No space left on device`

```bash
# Check usage
kubectl exec -it pod/ollama-runtime-0 -- df -h

# Solution 1: Delete old models
kubectl exec -it pod/ollama-runtime-0 -- ollama rm model-name

# Solution 2: Clean Docker
docker system prune --all

# Solution 3: Increase storage
# k8s/base/pvc.yaml - increase size in spec.resources.requests.storage
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
kubectl exec -it pod/ollama-runtime-0 -- env | grep OLLAMA

# Reduce model size or use CPU fallback
# Edit k8s/base/ollama-pod.yaml
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
kubectl exec -it statefulset/clawdevs-ai -c openclaw -- \
  openclaw agent --agent dev_backend --message "hello"
```

**Problem:** `Agent stuck in loop`

```bash
# Check logs
kubectl logs -f pod/openclaw-runtime-0 -c openclaw | grep ERROR

# Kill stuck session
kubectl exec -it statefulset/clawdevs-ai -c openclaw -- \
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
kubectl exec -it pod/postgres-xxx -- psql -U postgres

# Verify migrations ran
make panel-db-migrate
```

**Problem:** `Cannot connect to OpenClaw`

```bash
# Check gateway token
echo $OPENCLAW_GATEWAY_TOKEN

# Should be set in k8s/.env

# Verify connectivity
kubectl exec -it pod/clawdevs-panel-backend-xxx -- \
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
kubectl get pods          # List pods
kubectl describe pod <name>  # Pod details
kubectl logs -f pod/<name>   # Live logs
kubectl exec -it pod/<name> bash  # Shell access

# Cleanup
make reset-all            # Full reset (destructive)
make destroy-all          # Complete cleanup
```

---

**Questions?** Check [Glossary](../reference/glossary.md) for terminology.
