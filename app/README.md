# App — Python (`.py`)

Scripts Python do ClawDevs: workers (PO, Architect, Developer, DevOps, Revisão), gateway adapter, orquestrador, segurança, FinOps.

Os **scripts shell** ficam na pasta **`scripts/`**.

## ConfigMaps (Makefile)

O Makefile cria ConfigMaps a partir daqui para os pods. Ex.: `make configmap-developer` usa `app/developer_worker.py`, `app/gpu_lock.py`, etc.

## Dependência (GPU Lock)

`app/requirements-gpu-lock.txt` — usar nos agentes que importam `gpu_lock` (`pip install -r app/requirements-gpu-lock.txt` ou `pip install redis`).
