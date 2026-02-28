# Manual de primeiros socorros — GPU e cluster (Fase 3 — 030)

**Recuperação padrão é automática** (checkpoint 80°C, branch efêmera, Redis ACK, checkout limpo, Architect para conflitos). Este manual é **exceção** — use quando evict, balanceamento e recuperação automática não bastarem. Ref: [06-operacoes.md](06-operacoes.md), [00-objetivo-e-maquina-referencia.md](00-objetivo-e-maquina-referencia.md).

---

## Fase 1: Diagnóstico rápido (host)

No Pop!_OS, **fora do Minikube**, abrir um terminal:

```bash
nvidia-smi
```

- **Se o comando travar:** driver em nível de kernel falhou → ir para **Fase 3**.
- **Se mostrar "Memory Leak" ou processos zumbis:** pods segurando VRAM → ir para **Fase 2**.
- **Se responder normalmente:** anotar uso de VRAM/temperatura; considerar apenas limpeza de lock ou restart do pod Ollama (Fase 2).

**Script de referência:** [scripts/first-aid-gpu.sh](../scripts/first-aid-gpu.sh) (opção `--phase 1`).

---

## Fase 2: Reset cirúrgico (Kubernetes)

Sistema ainda responde; isolar e derrubar apenas o que causa o problema.

1. **Derrubar o serviço de inferência (Ollama):**
   ```bash
   kubectl delete pod -l app=ollama -n ai-agents --force
   ```

2. **Limpar o lock do Redis** (GPU Lock travado):
   ```bash
   kubectl exec -n ai-agents deploy/redis -- redis-cli DEL gpu_active_lock
   ```
   Chave: `gpu_active_lock`. Script: [scripts/gpu_lock.py](../scripts/gpu_lock.py).

3. **Reiniciar o Device Plugin da NVIDIA:**
   ```bash
   kubectl delete pod -n kube-system -l app=nvidia-device-plugin-daemonset
   ```

**Script:** `./scripts/first-aid-gpu.sh --phase 2`

---

## Fase 3: Reset de driver (opção nuclear)

Se `nvidia-smi` não responde ou a tela está instável: forçar o Linux a liberar a GPU sem reiniciar a máquina.

1. **Parar o Minikube:**
   ```bash
   minikube stop
   ```

2. **Listar e encerrar processos que usam a GPU:**
   ```bash
   sudo fuser -v /dev/nvidia*
   sudo fuser -kv /dev/nvidia*
   ```
   **Atenção:** pode fechar a interface gráfica.

3. **Recarregar o driver (se necessário):**
   ```bash
   sudo modprobe -r nvidia_uvm && sudo modprobe nvidia_uvm
   ```

**Script:** `./scripts/first-aid-gpu.sh --phase 3` (requer confirmação).

---

## Fase 4: Modo recuperação (disco/RAM)

Se o problema foi disco cheio ou RAM (Minikube Evicted):

- **Limpeza no nó:**
  ```bash
  minikube ssh "docker system prune -a --volumes"
  ```
- **Aumentar inotify** (muitos agentes):
  ```bash
  sudo sysctl fs.inotify.max_user_watches=524288
  echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf && sudo sysctl -p
  ```

---

## Referências

- [06-operacoes.md](06-operacoes.md) — Manual completo, prevenção, checkpoint 80°C, Redis idempotente.
- [04-infraestrutura.md](04-infraestrutura.md) — GPU Lock, hard timeout.
- [docs/scripts/verify-machine.md](scripts/verify-machine.md) — Máquina de referência.
