# GPU Lock (Redis)

Garante que apenas um agente use o Ollama (GPU) por vez no enxame. Deve ser importado nos agentes locais (Developer, QA, Architect, CyberSec, UX) antes de chamar o Ollama, para evitar OOM na VRAM. **Fundação (Phase 0):** o TTL do lock é **dinâmico** (calculado pelo tamanho do payload do evento no Redis) para evitar colisão mecânica quando um agente demora mais que 60 s (ex.: Architect em PR grande). **Garantia de não travar o cluster:** o release no Redis é **complementar**; a garantia vem do **hard timeout no Kubernetes**. O orquestrador deve configurar os pods que usam GPU com tempo máximo de execução (ex.: `activeDeadlineSeconds: 120` ou equivalente); ao exceder, o pod é morto e a tarefa volta à fila. Assim, mesmo se o processo morrer por OOM ou travamento sem executar `release()`, o cluster não fica em coma. Ver [03-arquitetura.md](../03-arquitetura.md), [04-infraestrutura.md](../04-infraestrutura.md) e [06-operacoes.md](../06-operacoes.md).

## Uso

```python
from gpu_lock import GPULock

# Uso explícito
lock = GPULock()
lock.acquire()
try:
    # chamar Ollama / usar GPU
    resposta = ollama.generate(model="deepseek-coder", prompt="...")
finally:
    lock.release()

# Ou como context manager
with GPULock():
    resposta = ollama.generate(model="deepseek-coder", prompt="...")
```

## Variáveis de ambiente

| Variável            | Descrição                                                                 | Padrão           |
|---------------------|---------------------------------------------------------------------------|------------------|
| `REDIS_HOST`        | Host do Redis no cluster                                                 | `redis-service`  |
| `POD_NAME`          | Nome do pod (identificação no lock)                                       | `unknown-agent`  |
| `GPU_LOCK_TTL`      | TTL fixo em segundos (usado se não houver payload/event_key; fallback)    | `60`             |
| `GPU_LOCK_EVENT_KEY`| Chave Redis do payload do evento (ex.: `issue:42`) para calcular TTL     | opcional         |

## Comportamento

- **Chave Redis:** `gpu_active_lock`
- **TTL dinâmico (obrigatório na fundação):** Calcular TTL com base no tamanho do payload do evento no Redis. Exemplo: ler a contagem de linhas do payload na chave indicada por `GPU_LOCK_EVENT_KEY` (ou do último evento consumido); se **maior que 500 linhas** (ex.: PR grande), usar TTL = **120 s**; caso contrário, TTL = **60 s**. Assim evita-se colisão quando o Architect (ou outro) demora mais que 60 s. Se não houver evento/payload disponível, usar `GPU_LOCK_TTL` (padrão 60 s).
- **Aquisição:** `SETNX` com espera em loop até obter o lock

## Dependência

```bash
pip install redis
```

## Código

```python
"""
GPU Lock com Redis: garante que apenas um agente use o Ollama (GPU) por vez.
TTL dinâmico: baseado na contagem de linhas do payload do evento (ex.: >500 → 120s, senão 60s).
Importar nos agentes locais (Dev, QA, Architect, etc.) antes de chamar o Ollama.
"""
import os
import time

def get_redis():
    try:
        import redis
        return redis.Redis(host=os.getenv("REDIS_HOST", "redis-service"), port=6379, db=0)
    except ImportError:
        raise RuntimeError("Instale redis: pip install redis")

def _compute_ttl(r, event_key):
    """Calcula TTL em segundos: payload > 500 linhas → 120s, senão 60s."""
    default_ttl = int(os.getenv("GPU_LOCK_TTL", "60"))
    if not event_key:
        return default_ttl
    try:
        payload = r.get(event_key)
        if payload is None:
            return default_ttl
        line_count = len(payload.decode("utf-8", errors="ignore").splitlines())
        return 120 if line_count > 500 else default_ttl
    except Exception:
        return default_ttl


class GPULock:
    def __init__(self, event_key=None):
        self.r = get_redis()
        self.lock_key = "gpu_active_lock"
        self.agent_name = os.getenv("POD_NAME", "unknown-agent")
        self.event_key = event_key or os.getenv("GPU_LOCK_EVENT_KEY")

    def _ttl(self):
        return _compute_ttl(self.r, self.event_key)

    def acquire(self):
        self.timeout_sec = self._ttl()
        print(f"[{self.agent_name}] Solicitando acesso à GPU (TTL={self.timeout_sec}s)...")
        while not self.r.set(self.lock_key, self.agent_name, nx=True, ex=self.timeout_sec):
            time.sleep(1)
        print(f"[{self.agent_name}] GPU bloqueada para uso.")

    def release(self):
        self.r.delete(self.lock_key)
        print(f"[{self.agent_name}] GPU liberada.")

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, *args):
        self.release()
```
