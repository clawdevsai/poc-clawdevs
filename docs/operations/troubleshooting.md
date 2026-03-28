# Troubleshooting Guide

**For:** All engineers
**Purpose:** Debug common issues and find solutions
**Updated:** March 27, 2026

---

## Quick Diagnostics

Run these first when something is broken:

```bash
# System health check
make stack-status

# Detailed diagnostics
docker-compose get containers
docker-compose describe containers

# Logs from all components
make openclaw-logs
make ollama-logs
make panel-logs-backend

# GPU status (if applicable)
make gpu-doctor
```

---

## Common Issues

### Container Won't Start

**Symptom:** Container status: `CrashLoopBackOff` or `Pending`

**Diagnosis:**
```bash
docker-compose describe container <container-name>
docker-compose logs <container-name>
```

**Solutions:**

1. **ImagePullBackOff** — Image not found
   ```bash
   # If using local build
   make images-build

   # Or use remote (default)
   docker-compose set env deployment/<deploy> PUSH_IMAGE=remote
   ```

2. **Insufficient CPU/Memory**
   ```bash
   # Check Docker allocation
   docker config view

   # Increase resources
   docker delete
   docker start --cpus=4 --memory=8192
   ```

3. **PVC not bound**
   ```bash
   docker-compose get pvc
   docker-compose describe pvc <pvc-name>

   # Wait or delete stale PVC
   docker-compose delete pvc <pvc-name>
   make storage-enable-expansion
   ```

---

### OpenClaw Gateway Not Responding

**Symptom:** Cannot connect to gateway, commands timeout

**Diagnosis:**
```bash
# Check if container is running
docker-compose get container/openclaw-runtime-0

# Check logs
docker-compose logs -f container/openclaw-runtime-0 -c openclaw

# Test connectivity
docker-compose port-forward service/openclaw-gateway 8080:8080
curl -v http://localhost:8080/health
```

**Solutions:**

1. **Gateway failed to start**
   ```bash
   # Check for config errors
   docker-compose logs container/openclaw-runtime-0

   # Rebuild config
   docker-compose delete configmap openclaw-agent-config
   make stack-apply
   ```

2. **Authentication failed**
   ```bash
   # Verify token is set
   echo $OPENCLAW_GATEWAY_TOKEN

   # Must be non-empty and valid Bearer token

   # Regenerate if needed
   # Edit container/.env, then:
   make stack-apply
   ```

3. **Port not exposed**
   ```bash
   # For remote access
   make services-expose

   # For local testing
   docker-compose port-forward service/openclaw-gateway 18789:18789
   ```

---

### Agents Not Running

**Symptom:** Agents don't execute on schedule, no logs

**Diagnosis:**
```bash
# Check if cron is enabled
docker-compose exec -it container/openclaw-runtime-0 -- env | grep CRON

# Check agent status
docker-compose exec -it container/openclaw-runtime-0 -- openclaw agents list

# Check workspace exists
docker-compose exec -it container/openclaw-runtime-0 -- ls -la /data/openclaw/workspace-*

# Trigger agent manually
docker-compose exec -it container/openclaw-runtime-0 -- \
  openclaw agent --agent dev_backend --message "test"
```

**Solutions:**

1. **Workspace not initialized**
   ```bash
   # Copy bootstrap files
   docker-compose exec -it container/openclaw-runtime-0 -- \
     cp -r /openclaw/config/agents/* /data/openclaw/workspace-*/

   # Restart
   docker-compose delete container/openclaw-runtime-0
   ```

2. **Cron expression invalid**
   ```bash
   # Verify in docker/base/openclaw-container.yaml
   # Format: minute hour day month day-of-week
   # Example: 0 * * * * (every hour)

   # Test with online tool: crontab.guru
   ```

3. **Memory too low**
   ```bash
   # Check available memory
   docker-compose top container openclaw-runtime-0

   # If >80% used, memory is issue
   # Increase in Docker or reduce model size
   ```

---

### Ollama Models Not Loaded

**Symptom:** `ollama list` shows no models, or model inference fails

**Diagnosis:**
```bash
# Check what's in container
docker-compose exec -it container/ollama-runtime-0 -- ollama list

# Check logs
docker-compose logs -f container/ollama-runtime-0

# Check disk space
docker-compose exec -it container/ollama-runtime-0 -- df -h /

# Check model file
docker-compose exec -it container/ollama-runtime-0 -- ls -lh /root/.ollama/models/blobs/
```

**Solutions:**

1. **Models still downloading**
   ```bash
   # This can take 10-30 minutes for first run
   # Check logs:
   docker-compose logs -f container/ollama-runtime-0 | grep downloading

   # Wait or manually pull
   docker-compose exec -it container/ollama-runtime-0 -- \
     ollama pull nemotron-3-super:cloud
   ```

2. **Out of disk space**
   ```bash
   # Check available space
   docker-compose exec -it container/ollama-runtime-0 -- df -h

   # Need 200+ GB free on node

   # Clean up
   docker system prune --all

   # Or increase PVC in docker/base/pvc.yaml
   ```

3. **Corrupt model**
   ```bash
   # Remove and re-download
   docker-compose exec -it container/ollama-runtime-0 -- \
     ollama rm nemotron-3-super:cloud

   docker-compose exec -it container/ollama-runtime-0 -- \
     ollama pull nemotron-3-super:cloud
   ```

---

### GPU Not Available

**Symptom:** GPU shown in `nvidia-smi` but Ollama uses CPU only

**Diagnosis:**
```bash
# Check NVIDIA device plugin
docker-compose get containers -n kube-system | grep nvidia

# Check GPU on node
docker-compose describe nodes

# Check GPU in container
docker-compose exec -it container/ollama-runtime-0 -- nvidia-smi

# Check Ollama config
docker-compose exec -it container/ollama-runtime-0 -- env | grep OLLAMA
```

**Solutions:**

1. **Device plugin not installed**
   ```bash
   # Install it
   make gpu-plugin-apply

   # Wait for plugin to be ready
   docker-compose get containers -n kube-system -w

   # Restart Ollama
   docker-compose delete container/ollama-runtime-0
   ```

2. **GPU resource not requested**
   ```bash
   # Edit docker/base/ollama-container.yaml
   # Add:
   # resources:
   #   limits:
   #     nvidia.com/gpu: 1

   # Restart
   make stack-apply
   ```

3. **Docker Desktop GPU support disabled**
   ```bash
   # In Windows: Settings > Resources > GPU
   # Enable GPU checkbox

   # Restart Docker Desktop
   # Then restart Docker
   ```

---

### Control Panel Not Accessible

**Symptom:** Cannot reach http://localhost:3000

**Diagnosis:**
```bash
# Check container status
docker-compose get container | grep panel

# Check port-forward
docker-compose port-forward service/clawdevs-panel-frontend 3000:3000

# Check logs
make panel-logs-frontend
make panel-logs-backend
```

**Solutions:**

1. **Container not running**
   ```bash
   # Check why
   docker-compose describe container <panel-container>

   # Restart
   docker-compose delete container <panel-container>

   # Or redeploy
   make panel-apply
   ```

2. **Database not connected**
   ```bash
   # Check PostgreSQL
   docker-compose get container | grep postgres

   # Check database status
   docker-compose logs container/postgres-xxx

   # Run migrations
   make panel-db-migrate
   ```

3. **Port 3000 already in use**
   ```bash
   # Kill process using port
   netstat -ano | findstr 3000    # Windows
   lsof -i :3000                  # macOS/Linux

   # Or use different port
   docker-compose port-forward svc/clawdevs-panel-frontend 3001:3000
   # Access: http://localhost:3001
   ```

---

### Agent Stuck in Loop

**Symptom:** Agent keeps retrying same task, not progressing

**Diagnosis:**
```bash
# Watch logs
docker-compose logs -f container/openclaw-runtime-0 | tail -50

# Check specific agent
docker-compose exec -it container/openclaw-runtime-0 -- \
  openclaw sessions --agent dev_backend --json

# Look for: error message, infinite retries
```

**Solutions:**

1. **Kill stuck session**
   ```bash
   # Reset the session
   docker-compose exec -it container/openclaw-runtime-0 -- \
     openclaw session reset agent:dev_backend:main

   # Or delete and recreate
   docker-compose exec -it container/openclaw-runtime-0 -- \
     rm -rf /data/openclaw/sessions/agent_dev_backend_main*
   ```

2. **Tool failure causing loop**
   ```bash
   # Disable problematic tool temporarily
   # Edit docker/base/openclaw-config/agents/dev_backend/AGENTS.md
   # Add to constraints: "Do not use tool X"

   # Redeploy
   make stack-apply
   ```

3. **LLM timeout**
   ```bash
   # Check if Ollama is responding
   docker-compose exec -it container/ollama-runtime-0 -- \
     curl http://localhost:11434/api/status

   # Increase timeout in openclaw.json
   # Or switch to cloud LLM:
   # PROVEDOR_LLM=openrouter
   # OPENROUTER_API_KEY=<key>
   ```

---

### Memory Issues (Out of Memory)

**Symptom:** Container crashes with OOMKilled, slow performance

**Diagnosis:**
```bash
# Check memory usage
docker-compose top container

# Check limits
docker-compose describe container <container> | grep -A 5 "Limits"

# Check node
docker-compose describe nodes
```

**Solutions:**

1. **Increase memory limit**
   ```bash
   # In docker/base/*.yaml, increase:
   # resources.limits.memory: 8Gi

   # Also increase Docker
   docker delete
   docker start --memory=8192
   ```

2. **Reduce model size**
   ```bash
   # Switch to smaller model
   # In docker/base/ollama-container.yaml:
   # ollama run nemotron-3-super:cloud
   # Change to: qwen3-next:cloud (smaller)

   make stack-apply
   ```

3. **Enable swap**
   ```bash
   # In Docker (Linux only)
   docker ssh
   sudo fallocate -l 4G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

---

### Network Connectivity Issues

**Symptom:** Cannot reach GitHub, web search fails, or external APIs error

**Diagnosis:**
```bash
# Check network policy
docker-compose get networkpolicy

# Test from container
docker-compose exec -it container/openclaw-runtime-0 -- \
  curl -v https://api.github.com

# Check DNS
docker-compose exec -it container/openclaw-runtime-0 -- \
  nslookup api.github.com
```

**Solutions:**

1. **Network policy blocking traffic**
   ```bash
   # Check what's allowed
   docker-compose describe networkpolicy <policy>

   # Temporarily disable for testing
   docker-compose delete networkpolicy <policy>

   # Or update to allow egress
   # Edit docker/base/networkpolicy-allow-egress.yaml
   ```

2. **DNS not working**
   ```bash
   # Check CoreDNS
   docker-compose get containers -n kube-system | grep coredns

   # Restart if needed
   docker-compose rollout restart deployment/coredns -n kube-system
   ```

3. **Firewall blocking**
   ```bash
   # On Windows, check Windows Defender Firewall
   # Settings > Firewall & Network Protection
   # Allow Docker Desktop through firewall
   ```

---

## Debug Mode

Enable more verbose logging:

```bash
# In container/.env
DEBUG_LOG_ENABLED=true
OPENCLAW_LOG_LEVEL=debug

# Redeploy
make stack-apply

# Watch logs
make openclaw-logs
```

This increases output but helps diagnose issues.

---

## Checking Resource Usage

```bash
# Container CPU/Memory
docker-compose top container

# Node resources
docker-compose describe nodes

# Storage
docker-compose get pvc

# Network
docker-compose get services
docker-compose describe svc <service>
```

---

## Useful Commands

```bash
# Get shell access
docker-compose exec -it container/<name> -- bash
docker-compose exec -it statefulset/clawdevs-ai -c openclaw -- bash

# View detailed container info
docker-compose describe container <name>

# Check events
docker-compose get events

# Port forwarding
docker-compose port-forward container/<name> 8080:8080
docker-compose port-forward svc/<name> 8080:8080

# Watch deployment progress
docker-compose get containers -w

# See only errors
docker-compose logs <container> | grep ERROR
```

---

## When All Else Fails

Complete reset:

```bash
# Stop everything
make clawdevs-down

# Delete Docker
docker delete

# Start fresh
make clawdevs-up

# This takes 5-10 minutes but usually fixes everything
```

---

## Getting Help

1. **Check this guide** — 80% of issues are here
2. **Check logs** — Most errors are logged
3. **Check Glossary** — Ensure you understand terms
4. **Ask teammates** — Slack or in-person
5. **Create issue** — If bug is suspected

---

**Last Updated:** March 27, 2026

Need help? Check [Glossary](../reference/glossary.md) or [Architecture Overview](../architecture/overview.md).
