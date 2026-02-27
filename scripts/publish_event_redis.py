#!/usr/bin/env python3
# Publica um evento em um Redis Stream (Fase 1 — 018). Uso: testes manuais ou E2E.
# Ex.: python publish_event_redis.py cmd:strategy directive="Priorizar 2FA" source=ceo
#      python publish_event_redis.py task:backlog issue_id=42 priority=1
# Variáveis de ambiente: REDIS_HOST (default 127.0.0.1), REDIS_PORT (default 6379), REDIS_PASSWORD (opcional).
import os
import sys

REDIS_HOST = os.environ.get("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD") or None


def main():
    if len(sys.argv) < 3:
        print(
            "Uso: publish_event_redis.py <stream> <key>=<value> [key2=value2 ...]\n"
            "Ex.: publish_event_redis.py cmd:strategy directive=\"Priorizar 2FA\" source=ceo\n"
            "     publish_event_redis.py task:backlog issue_id=42",
            file=sys.stderr,
        )
        sys.exit(1)
    stream = sys.argv[1]
    pairs = {}
    for arg in sys.argv[2:]:
        if "=" in arg:
            k, v = arg.split("=", 1)
            pairs[k.strip()] = v.strip().strip('"').strip("'")
        else:
            pairs[arg] = "1"
    if not pairs:
        print("Forneça ao menos um par key=value.", file=sys.stderr)
        sys.exit(1)
    try:
        import redis
    except ImportError:
        print("Instale redis: pip install redis", file=sys.stderr)
        sys.exit(1)
    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=True,
    )
    msg_id = r.xadd(stream, pairs)
    print(f"Publicado em {stream}: {msg_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
