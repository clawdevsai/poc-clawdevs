"""
Helper para escrita do working buffer no Redis com TTL (truncamento-finops).
Qualquer script que escreva buffer de conversas deve usar write_working_buffer()
para que as chaves expirem automaticamente (WORKING_BUFFER_TTL_SEC).
Ref: docs/issues/041-truncamento-contexto-finops.md, working_buffer_ttl.py
"""
import os

REDIS_HOST = os.environ.get("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD") or None
WORKING_BUFFER_TTL_SEC = int(os.environ.get("WORKING_BUFFER_TTL_SEC", "86400"))
WORKING_BUFFER_KEY_PREFIX = os.environ.get("WORKING_BUFFER_KEY_PREFIX", "project:v1:working_buffer:")


def get_redis():
    try:
        import redis
        return redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            decode_responses=True,
        )
    except ImportError:
        raise RuntimeError("Instale redis: pip install redis")


def write_working_buffer(key_suffix: str, value: str, ttl_sec: int = None) -> None:
    """
    Escreve valor no working buffer com TTL. Chave = WORKING_BUFFER_KEY_PREFIX + key_suffix.
    Ex.: write_working_buffer("session:123", json.dumps(messages))
    """
    r = get_redis()
    key = f"{WORKING_BUFFER_KEY_PREFIX}{key_suffix}"
    ttl = ttl_sec if ttl_sec is not None else WORKING_BUFFER_TTL_SEC
    try:
        from working_buffer_ttl import set_buffer_key
        set_buffer_key(r, key, value, ttl)
    except ImportError:
        r.set(key, value, ex=ttl)
