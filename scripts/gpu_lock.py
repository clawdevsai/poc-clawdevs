"""
ClawDevs — GPU Lock (Redis)
Garante que apenas um agente use o Ollama (GPU) por vez no enxame.
TTL dinâmico: payload > 500 linhas → 120s; senão 60s.
Importar nos agentes locais (Developer, QA, Architect, CyberSec, UX) antes de chamar o Ollama.
Referência: docs/scripts/gpu_lock.md | docs/issues/006-gpu-lock-script.md
"""

import os
import time
import logging
from contextlib import contextmanager
from typing import Optional

logger = logging.getLogger("clawdevs.gpu_lock")


def _get_redis():
    try:
        import redis as redis_lib

        host = os.getenv("REDIS_HOST", "redis-service")
        port = int(os.getenv("REDIS_PORT", "6379"))
        db = int(os.getenv("REDIS_DB", "0"))
        return redis_lib.Redis(host=host, port=port, db=db, decode_responses=False)
    except ImportError:
        raise RuntimeError("Instale redis: pip install redis")


def _compute_ttl(r, event_key: Optional[str]) -> int:
    """Calcula TTL em segundos com base no payload do evento no Redis.
    Payload > 500 linhas → 120s (PR grande / Architect); senão → 60s (padrão).
    """
    default_ttl = int(os.getenv("GPU_LOCK_TTL", "60"))
    if not event_key:
        return default_ttl
    try:
        payload = r.get(event_key)
        if payload is None:
            return default_ttl
        line_count = len(payload.decode("utf-8", errors="ignore").splitlines())
        ttl = 120 if line_count > 500 else default_ttl
        logger.debug("GPU Lock TTL calculado: %ds (payload=%d linhas)", ttl, line_count)
        return ttl
    except Exception as exc:
        logger.warning(
            "Erro ao calcular TTL dinâmico: %s — usando padrão %ds", exc, default_ttl
        )
        return default_ttl


class GPULock:
    """GPU Lock via Redis SETNX com TTL dinâmico.

    Uso como context manager (recomendado):
        with GPULock(event_key="issue:42"):
            resposta = ollama.generate(...)

    Uso explícito:
        lock = GPULock()
        lock.acquire()
        try:
            ...
        finally:
            lock.release()
    """

    LOCK_KEY = "gpu_active_lock"

    def __init__(self, event_key: Optional[str] = None, poll_interval: float = 1.0):
        self.r = _get_redis()
        self.agent_name = os.getenv("POD_NAME", "unknown-agent")
        self.event_key: Optional[str] = event_key or os.getenv("GPU_LOCK_EVENT_KEY")
        self.poll_interval = poll_interval
        self._acquired = False

    def _ttl(self) -> int:
        return _compute_ttl(self.r, self.event_key)

    def acquire(self) -> None:
        """Bloqueia até obter o lock. Aguarda em polling com intervalo configurável."""
        ttl = self._ttl()
        logger.info("[%s] Aguardando GPU Lock (TTL=%ds)...", self.agent_name, ttl)
        while not self.r.set(self.LOCK_KEY, self.agent_name, nx=True, ex=ttl):
            time.sleep(self.poll_interval)
        self._acquired = True
        logger.info("[%s] GPU Lock adquirido.", self.agent_name)

    def release(self) -> None:
        """Libera o lock se foi adquirido por este agente."""
        if self._acquired:
            holder = self.r.get(self.LOCK_KEY)
            if holder and holder.decode("utf-8", errors="ignore") == self.agent_name:
                self.r.delete(self.LOCK_KEY)
                logger.info("[%s] GPU Lock liberado.", self.agent_name)
            else:
                logger.warning(
                    "[%s] Lock não pertence a este agente (holder=%s); ignorando release.",
                    self.agent_name,
                    holder,
                )
            self._acquired = False

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, *_):
        self.release()


@contextmanager
def gpu_lock(event_key: Optional[str] = None):
    """Context manager funcional para GPU Lock."""
    lock = GPULock(event_key=event_key)
    lock.acquire()
    try:
        yield lock
    finally:
        lock.release()
