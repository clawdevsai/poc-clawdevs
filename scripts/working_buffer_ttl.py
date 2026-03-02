#!/usr/bin/env python3
"""
truncamento-finops: Aplica TTL às chaves do working buffer no Redis para expiração automática.
Mensagens antigas evaporam sem depender do agente DevOps para limpar.
Ref: docs/issues/041-truncamento-contexto-finops.md, docs/07-configuracao-e-prompts.md (TTL working buffer)
Uso: REDIS_HOST=localhost REDIS_PORT=6379 WORKING_BUFFER_TTL_SEC=86400 python working_buffer_ttl.py [--scan]
      --scan: percorre chaves com prefixo e aplica TTL; sem --scan: apenas documenta o contrato (quem escreve deve usar SET key val EX ttl).
"""
import argparse
import os
import sys

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
        raise SystemExit("Instale redis: pip install redis")


def set_buffer_key(r, key: str, value: str, ttl_sec: int = None) -> None:
    """Escreve chave do working buffer com TTL (truncamento-finops). Use ao publicar no buffer."""
    ttl = ttl_sec if ttl_sec is not None else WORKING_BUFFER_TTL_SEC
    r.set(key, value, ex=ttl)


def main() -> None:
    ap = argparse.ArgumentParser(description="Aplicar TTL às chaves do working buffer (truncamento-finops)")
    ap.add_argument("--scan", action="store_true", help="Percorrer chaves com prefixo e aplicar TTL")
    args = ap.parse_args()

    if not args.scan:
        print(
            "Contrato TTL working buffer (truncamento-finops): ao escrever chaves do buffer, use SET key value EX "
            + str(WORKING_BUFFER_TTL_SEC)
            + "\nExemplo Redis: SET project:v1:working_buffer:session:123 '...' EX "
            + str(WORKING_BUFFER_TTL_SEC),
            file=sys.stderr,
        )
        return

    r = get_redis()
    cursor = 0
    count = 0
    while True:
        cursor, keys = r.scan(cursor=cursor, match=WORKING_BUFFER_KEY_PREFIX + "*", count=100)
        for k in keys:
            r.expire(k, WORKING_BUFFER_TTL_SEC)
            count += 1
        if cursor == 0:
            break
    print(f"Aplicado TTL={WORKING_BUFFER_TTL_SEC}s a {count} chaves com prefixo {WORKING_BUFFER_KEY_PREFIX}", file=sys.stderr)


if __name__ == "__main__":
    main()
