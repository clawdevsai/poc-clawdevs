# Scripts — Shell (`.sh`)

Scripts shell do ClawDevs: setup, Redis init, validação, testes, primeiro-socorro GPU, secrets K8s.

Os **arquivos Python** ficam na pasta **`app/`** na raiz do repositório.

## Como rodar

A partir da raiz do repositório:

- `./scripts/up-all.sh`
- `./scripts/redis-streams-init.sh` (ou via job K8s)
- `make reset-memory` → chama `scripts/reset_agent_memory.sh`

## ConfigMaps (Makefile)

O Makefile cria ConfigMaps a partir de `app/*.py` (pasta **app/**). Ex.: `make configmap-developer` usa `app/developer_worker.py`, `app/gpu_lock.py`, etc.
