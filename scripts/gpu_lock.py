#!/usr/bin/env python3
"""
GPU Lock com Redis: garante que apenas um agente use o Ollama (GPU) por vez.
TTL dinâmico: baseado na contagem de linhas do payload do evento (ex.: >500 → 120s, senão 60s).
Importar nos agentes locais (Dev, QA, Architect, CyberSec, UX) antes de chamar o Ollama.

Ref: docs/scripts/gpu_lock.md, docs/04-infraestrutura.md, docs/issues/006-gpu-lock-script.md
"""
import os
import time


def get_redis():
    try:
        import redis
        host = os.getenv("REDIS_HOST", "redis-service.ai-agents.svc.cluster.local")
        port = int(os.getenv("REDIS_PORT", "6379"))
        return redis.Redis(host=host, port=port, db=0, decode_responses=True)
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
        line_count = len((payload if isinstance(payload, str) else payload.decode("utf-8", errors="ignore")).splitlines())
        return 120 if line_count > 500 else default_ttl
    except Exception:
        return default_ttl


class GPULock:
    LOCK_KEY = "gpu_active_lock"

    def __init__(self, event_key=None):
        self.r = get_redis()
        self.lock_key = self.LOCK_KEY
        self.agent_name = os.getenv("POD_NAME", os.getenv("HOSTNAME", "unknown-agent"))
        self.event_key = event_key or os.getenv("GPU_LOCK_EVENT_KEY")

    def _ttl(self):
        return _compute_ttl(self.r, self.event_key)

    def acquire(self, wait_timeout_sec=None):
        """
        Adquire o lock (SETNX com TTL dinâmico). Se não conseguir, aguarda em loop
        até obter o lock ou até wait_timeout_sec (None = espera indefinida).
        """
        ttl = self._ttl()
        print(f"[{self.agent_name}] Solicitando acesso à GPU (TTL={ttl}s)...")
        start = time.monotonic()
        while True:
            if self.r.set(self.lock_key, str(self.agent_name), nx=True, ex=ttl):
                print(f"[{self.agent_name}] GPU bloqueada para uso.")
                return
            if wait_timeout_sec is not None and (time.monotonic() - start) >= wait_timeout_sec:
                raise TimeoutError(f"[{self.agent_name}] Timeout ao aguardar GPU Lock após {wait_timeout_sec}s")
            time.sleep(1)

    def release(self):
        self.r.delete(self.lock_key)
        print(f"[{self.agent_name}] GPU liberada.")

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, *args):
        self.release()


if __name__ == "__main__":
    # Teste rápido: adquirir, segurar 2s, liberar
    import sys
    with GPULock() as lock:
        print("Lock adquirido. Segurando 2s...")
        time.sleep(2)
    print("OK")
