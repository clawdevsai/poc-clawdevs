# GPU Lock (Redis)

Implementação em **[../scripts/gpu_lock.py](../scripts/gpu_lock.py)**. Garante que apenas um agente use o Ollama (GPU) por vez no enxame. Deve ser importado nos agentes locais (Developer, QA, Architect, CyberSec, UX) antes de chamar o Ollama, para evitar OOM na VRAM. **Fundação (Phase 0):** o TTL do lock é **dinâmico** (calculado pelo tamanho do payload do evento no Redis) para evitar colisão mecânica quando um agente demora mais que 60 s (ex.: Architect em PR grande). **Garantia de não travar o cluster:** o release no Redis é **complementar**; a garantia vem do **hard timeout no Kubernetes**. O orquestrador deve configurar os pods que usam GPU com tempo máximo de execução (ex.: `activeDeadlineSeconds: 120` ou equivalente); ao exceder, o pod é morto e a tarefa volta à fila. Assim, mesmo se o processo morrer por OOM ou travamento sem executar `release()`, o cluster não fica em coma. Ver [03-arquitetura.md](../03-arquitetura.md), [04-infraestrutura.md](../04-infraestrutura.md) e [06-operacoes.md](../06-operacoes.md).

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
| `REDIS_HOST`        | Host do Redis no cluster                                                 | `redis-service.ai-agents.svc.cluster.local`  |
| `REDIS_PORT`        | Porta do Redis                                                            | `6379`  |
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

O código canônico está em **[scripts/gpu_lock.py](../scripts/gpu_lock.py)**. Dependência: `pip install -r scripts/requirements-gpu-lock.txt` (ou `pip install redis`).
