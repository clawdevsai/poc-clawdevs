#!/usr/bin/env python3
"""
Singleton Redis client compartilhado entre todos os módulos ClawDevs.

Centraliza a configuração de conexão e elimina a duplicação de get_redis()
que existia em 7+ módulos (orchestration.py, acefalo_redis.py, disjuntor_draft_rejected.py,
gpu_lock.py, gateway_token_bucket.py, working_buffer_ttl.py, redis_buffer_writer.py).

Uso:
    from shared.redis_client import get_redis, get_redis_with_retry

Variáveis de ambiente:
    REDIS_HOST       — padrão: 127.0.0.1
    REDIS_PORT       — padrão: 6379
    REDIS_PASSWORD   — padrão: None
"""
import os
import time
import sys

REDIS_HOST = os.environ.get("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD") or None


def get_redis():
    """
    Retorna cliente Redis configurado via variáveis de ambiente.
    Lança RuntimeError se a biblioteca redis não estiver instalada.
    """
    try:
        import redis
    except ImportError:
        raise RuntimeError(
            "Dependência ausente: instale redis via 'pip install redis'"
        )
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=True,
    )


def get_redis_with_retry(max_attempts: int = 30, delay_sec: float = 10.0):
    """
    Tenta conectar ao Redis com retries.
    Usado em pods que iniciam antes do Redis estar pronto.

    Args:
        max_attempts: Número máximo de tentativas.
        delay_sec: Segundos entre tentativas.

    Returns:
        Cliente Redis conectado.

    Raises:
        SystemExit: Se esgotar as tentativas.
    """
    try:
        import redis
    except ImportError:
        raise RuntimeError(
            "Dependência ausente: instale redis via 'pip install redis'"
        )

    for attempt in range(1, max_attempts + 1):
        try:
            client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                password=REDIS_PASSWORD,
                decode_responses=True,
            )
            client.ping()
            return client
        except redis.ConnectionError as exc:
            print(
                f"[redis_client] Tentativa {attempt}/{max_attempts} — Redis indisponível: {exc}",
                file=sys.stderr,
            )
            if attempt < max_attempts:
                time.sleep(delay_sec)

    print(
        f"[redis_client] Redis não respondeu após {max_attempts} tentativas. Encerrando.",
        file=sys.stderr,
    )
    sys.exit(1)
