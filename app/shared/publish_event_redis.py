#!/usr/bin/env python3
# Publica um evento em um Redis Stream (018). Uso: testes manuais ou E2E.
# truncamento-finops: truncamento na borda — payloads grandes são truncados antes de enfileirar.
# Ex.: python publish_event_redis.py cmd:strategy directive="Priorizar 2FA" source=ceo
#      python publish_event_redis.py task:backlog issue_id=42 priority=1
# Variáveis: REDIS_HOST, REDIS_PORT, REDIS_PASSWORD; TRUNCATE_BORDER_ENABLED=1 e TRUNCATE_BORDER_MAX_TOKENS (truncamento-finops).
import os
import sys

REDIS_HOST = os.environ.get("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD") or None
TRUNCATE_BORDER_ENABLED = os.environ.get("TRUNCATE_BORDER_ENABLED", "1") == "1"
TRUNCATE_BORDER_MAX_TOKENS = int(os.environ.get("TRUNCATE_BORDER_MAX_TOKENS", "4000"))

# truncamento-finops — truncamento na borda (import opcional)
def _truncate_if_needed(value: str) -> str:
    if not value or not TRUNCATE_BORDER_ENABLED:
        return value
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)
        from truncate_payload_border import truncate_payload, estimate_tokens
        if estimate_tokens(value) <= TRUNCATE_BORDER_MAX_TOKENS:
            return value
        out, _ = truncate_payload(value, max_tokens=TRUNCATE_BORDER_MAX_TOKENS)
        return out
    except Exception:
        return value


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
    # truncamento-finops: truncar valores grandes antes de enfileirar
    for k in list(pairs.keys()):
        v = pairs[k]
        if isinstance(v, str) and len(v) > 500:
            pairs[k] = _truncate_if_needed(v)
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
