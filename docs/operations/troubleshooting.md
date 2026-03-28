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
kubectl get pods
kubectl describe pods

# Logs from all components
make openclaw-logs
make ollama-logs
make panel-logs-backend

# GPU status (if applicable)
make gpu-doctor
```

---

## Common Issues

### Pod Won't Start

**Symptom:** Pod status: `CrashLoopBackOff` or `Pending`

**Diagnosis:**
```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

**Solutions:**

1. **ImagePullBackOff** — Image not found
   ```bash
   # If using local build
   make images-build

   # Or use remote (default)
   kubectl set env deployment/<deploy> PUSH_IMAGE=remote
   ```

2. **Insufficient CPU/Memory**
   ```bash
   # Check Minikube allocation
   minikube config view

   # Increase resources
   minikube delete
   minikube start --cpus=4 --memory=8192
   ```

3. **PVC not bound**
   ```bash
   kubectl get pvc
   kubectl describe pvc <pvc-name>

   # Wait or delete stale PVC
   kubectl delete pvc <pvc-name>
   make storage-enable-expansion
   ```

---

### OpenClaw Gateway Not Responding

**Symptom:** Cannot connect to gateway, commands timeout

**Diagnosis:**
```bash
# Check if pod is running
kubectl get pod/openclaw-runtime-0

# Check logs
kubectl logs -f pod/openclaw-runtime-0 -c openclaw

# Test connectivity
kubectl port-forward service/openclaw-gateway 8080:8080
curl -v http://localhost:8080/health
```

**Solutions:**

1. **Gateway failed to start**
   ```bash
   # Check for config errors
   kubectl logs pod/openclaw-runtime-0

   # Rebuild config
   kubectl delete configmap openclaw-agent-config
   make stack-apply
   ```

2. **Authentication failed**
   ```bash
   # Verify token is set
   echo $OPENCLAW_GATEWAY_TOKEN

   # Must be non-empty and valid Bearer token

   # Regenerate if needed
   # Edit k8s/.env, then:
   make stack-apply
   ```

3. **Port not exposed**
   ```bash
   # For remote access
   make services-expose

   # For local testing
   kubectl port-forward service/openclaw-gateway 18789:18789
   ```

---

### Agents Not Running

**Symptom:** Agents don't execute on schedule, no logs

**Diagnosis:**
```bash
# Check if cron is enabled
kubectl exec -it pod/openclaw-runtime-0 -- env | grep CRON

# Check agent status
kubectl exec -it pod/openclaw-runtime-0 -- openclaw agents list

# Check workspace exists
kubectl exec -it pod/openclaw-runtime-0 -- ls -la /data/openclaw/workspace-*

# Trigger agent manually
kubectl exec -it pod/openclaw-runtime-0 -- \
  openclaw agent --agent dev_backend --message "test"
```

**Solutions:**

1. **Workspace not initialized**
   ```bash
   # Copy bootstrap files
   kubectl exec -it pod/openclaw-runtime-0 -- \
     cp -r /openclaw/config/agents/* /data/openclaw/workspace-*/

   # Restart
   kubectl delete pod/openclaw-runtime-0
   ```

2. **Cron expression invalid**
   ```bash
   # Verify in k8s/base/openclaw-pod.yaml
   # Format: minute hour day month day-of-week
   # Example: 0 * * * * (every hour)

   # Test with online tool: crontab.guru
   ```

3. **Memory too low**
   ```bash
   # Check available memory
   kubectl top pod openclaw-runtime-0

   # If >80% used, memory is issue
   # Increase in Minikube or reduce model size
   ```

---

### Ollama Models Not Loaded

**Symptom:** `ollama list` shows no models, or model inference fails

**Diagnosis:**
```bash
# Check what's in container
kubectl exec -it pod/ollama-runtime-0 -- ollama list

# Check logs
kubectl logs -f pod/ollama-runtime-0

# Check disk space
kubectl exec -it pod/ollama-runtime-0 -- df -h /

# Check model file
kubectl exec -it pod/ollama-runtime-0 -- ls -lh /root/.ollama/models/blobs/
```

**Solutions:**

1. **Models still downloading**
   ```bash
   # This can take 10-30 minutes for first run
   # Check logs:
   kubectl logs -f pod/ollama-runtime-0 | grep downloading

   # Wait or manually pull
   kubectl exec -it pod/ollama-runtime-0 -- \
     ollama pull nemotron-3-super:cloud
   ```

2. **Out of disk space**
   ```bash
   # Check available space
   kubectl exec -it pod/ollama-runtime-0 -- df -h

   # Need 200+ GB free on node

   # Clean up
   docker system prune --all

   # Or increase PVC in k8s/base/pvc.yaml
   ```

3. **Corrupt model**
   ```bash
   # Remove and re-download
   kubectl exec -it pod/ollama-runtime-0 -- \
     ollama rm nemotron-3-super:cloud

   kubectl exec -it pod/ollama-runtime-0 -- \
     ollama pull nemotron-3-super:cloud
   ```

---

### GPU Not Available

**Symptom:** GPU shown in `nvidia-smi` but Ollama uses CPU only

**Diagnosis:**
```bash
# Check NVIDIA device plugin
kubectl get pods -n kube-system | grep nvidia

# Check GPU on node
kubectl describe nodes

# Check GPU in pod
kubectl exec -it pod/ollama-runtime-0 -- nvidia-smi

# Check Ollama config
kubectl exec -it pod/ollama-runtime-0 -- env | grep OLLAMA
```

**Solutions:**

1. **Device plugin not installed**
   ```bash
   # Install it
   make gpu-plugin-apply

   # Wait for plugin to be ready
   kubectl get pods -n kube-system -w

   # Restart Ollama
   kubectl delete pod/ollama-runtime-0
   ```

2. **GPU resource not requested**
   ```bash
   # Edit k8s/base/ollama-pod.yaml
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
   # Then restart Minikube
   ```

---

### Control Panel Not Accessible

**Symptom:** Cannot reach http://localhost:3000

**Diagnosis:**
```bash
# Check pod status
kubectl get pod | grep panel

# Check port-forward
kubectl port-forward service/clawdevs-panel-frontend 3000:3000

# Check logs
make panel-logs-frontend
make panel-logs-backend
```

**Solutions:**

1. **Pod not running**
   ```bash
   # Check why
   kubectl describe pod <panel-pod>

   # Restart
   kubectl delete pod <panel-pod>

   # Or redeploy
   make panel-apply
   ```

2. **Database not connected**
   ```bash
   # Check PostgreSQL
   kubectl get pod | grep postgres

   # Check database status
   kubectl logs pod/postgres-xxx

   # Run migrations
   make panel-db-migrate
   ```

3. **Port 3000 already in use**
   ```bash
   # Kill process using port
   netstat -ano | findstr 3000    # Windows
   lsof -i :3000                  # macOS/Linux

   # Or use different port
   kubectl port-forward svc/clawdevs-panel-frontend 3001:3000
   # Access: http://localhost:3001
   ```

---

### Agent Stuck in Loop

**Symptom:** Agent keeps retrying same task, not progressing

**Diagnosis:**
```bash
# Watch logs
kubectl logs -f pod/openclaw-runtime-0 | tail -50

# Check specific agent
kubectl exec -it pod/openclaw-runtime-0 -- \
  openclaw sessions --agent dev_backend --json

# Look for: error message, infinite retries
```

**Solutions:**

1. **Kill stuck session**
   ```bash
   # Reset the session
   kubectl exec -it pod/openclaw-runtime-0 -- \
     openclaw session reset agent:dev_backend:main

   # Or delete and recreate
   kubectl exec -it pod/openclaw-runtime-0 -- \
     rm -rf /data/openclaw/sessions/agent_dev_backend_main*
   ```

2. **Tool failure causing loop**
   ```bash
   # Disable problematic tool temporarily
   # Edit k8s/base/openclaw-config/agents/dev_backend/AGENTS.md
   # Add to constraints: "Do not use tool X"

   # Redeploy
   make stack-apply
   ```

3. **LLM timeout**
   ```bash
   # Check if Ollama is responding
   kubectl exec -it pod/ollama-runtime-0 -- \
     curl http://localhost:11434/api/status

   # Increase timeout in openclaw.json
   # Or switch to cloud LLM:
   # PROVEDOR_LLM=openrouter
   # OPENROUTER_API_KEY=<key>
   ```

---

### Memory Issues (Out of Memory)

**Symptom:** Pod crashes with OOMKilled, slow performance

**Diagnosis:**
```bash
# Check memory usage
kubectl top pod

# Check limits
kubectl describe pod <pod> | grep -A 5 "Limits"

# Check node
kubectl describe nodes
```

**Solutions:**

1. **Increase memory limit**
   ```bash
   # In k8s/base/*.yaml, increase:
   # resources.limits.memory: 8Gi

   # Also increase Minikube
   minikube delete
   minikube start --memory=8192
   ```

2. **Reduce model size**
   ```bash
   # Switch to smaller model
   # In k8s/base/ollama-pod.yaml:
   # ollama run nemotron-3-super:cloud
   # Change to: qwen3-next:cloud (smaller)

   make stack-apply
   ```

3. **Enable swap**
   ```bash
   # In Minikube (Linux only)
   minikube ssh
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
kubectl get networkpolicy

# Test from pod
kubectl exec -it pod/openclaw-runtime-0 -- \
  curl -v https://api.github.com

# Check DNS
kubectl exec -it pod/openclaw-runtime-0 -- \
  nslookup api.github.com
```

**Solutions:**

1. **Network policy blocking traffic**
   ```bash
   # Check what's allowed
   kubectl describe networkpolicy <policy>

   # Temporarily disable for testing
   kubectl delete networkpolicy <policy>

   # Or update to allow egress
   # Edit k8s/base/networkpolicy-allow-egress.yaml
   ```

2. **DNS not working**
   ```bash
   # Check CoreDNS
   kubectl get pods -n kube-system | grep coredns

   # Restart if needed
   kubectl rollout restart deployment/coredns -n kube-system
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
# In k8s/.env
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
# Pod CPU/Memory
kubectl top pod

# Node resources
kubectl describe nodes

# Storage
kubectl get pvc

# Network
kubectl get services
kubectl describe svc <service>
```

---

## Useful Commands

```bash
# Get shell access
kubectl exec -it pod/<name> -- bash
kubectl exec -it statefulset/clawdevs-ai -c openclaw -- bash

# View detailed pod info
kubectl describe pod <name>

# Check events
kubectl get events

# Port forwarding
kubectl port-forward pod/<name> 8080:8080
kubectl port-forward svc/<name> 8080:8080

# Watch deployment progress
kubectl get pods -w

# See only errors
kubectl logs <pod> | grep ERROR
```

---

## When All Else Fails

Complete reset:

```bash
# Stop everything
make clawdevs-down

# Delete Minikube
minikube delete

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
