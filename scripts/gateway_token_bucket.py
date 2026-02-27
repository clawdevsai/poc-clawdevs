#!/usr/bin/env python3
"""
Token bucket para eventos de estratégia e degradação por eficiência (Fase 2 — 126).
O Gateway/orquestrador chama este script (ou importa) para decidir se permite publicar
em cmd:strategy ou se deve rotear CEO para modelo local.
Ref: docs/07-configuracao-e-prompts.md, docs/issues/126-token-bucket-degradacao-eficiencia.md
"""
import os
import sys
import time

REDIS_HOST = os.environ.get("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD") or None
# Máximo de eventos de estratégia por hora (janela deslizante ou fixa)
TOKEN_BUCKET_MAX_PER_HOUR = int(os.environ.get("TOKEN_BUCKET_MAX_PER_HOUR", "5"))
# Razão mínima (po_approved / ceo_ideas) para não degradar CEO para local
EFFICIENCY_RATIO_MIN = float(os.environ.get("EFFICIENCY_RATIO_MIN", "0.2"))
KEY_STRATEGY_COUNT = os.environ.get("KEY_STRATEGY_COUNT", "gateway:strategy_events_count")
KEY_CEO_IDEAS = os.environ.get("KEY_CEO_IDEAS", "gateway:ceo_ideas_count")
KEY_PO_APPROVED = os.environ.get("KEY_PO_APPROVED", "gateway:po_approved_count")
WINDOW_SEC = int(os.environ.get("TOKEN_BUCKET_WINDOW_SEC", "3600"))  # janela em segundos (1 h)


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


def check_token_bucket(r) -> bool:
    """Retorna True se pode emitir evento de estratégia (dentro do limite). Não consome token; chamar record após publicar."""
    now = int(time.time())
    window_start = now - WINDOW_SEC
    key = f"{KEY_STRATEGY_COUNT}:hour"
    r.zremrangebyscore(key, 0, window_start)
    count = r.zcard(key)
    return count < TOKEN_BUCKET_MAX_PER_HOUR


def record_strategy_event(r) -> None:
    """Registra um evento de estratégia (chamar após o Gateway publicar em cmd:strategy)."""
    now = int(time.time())
    key = f"{KEY_STRATEGY_COUNT}:hour"
    r.zadd(key, {f"{now}:{os.getpid()}": now})
    r.expire(key, WINDOW_SEC + 60)


def should_degrade_ceo_to_local(r) -> bool:
    """True se a razão PO aprovadas / CEO ideias estiver abaixo do limiar (forçar CEO em local)."""
    ceo = int(r.get(KEY_CEO_IDEAS) or 0)
    po = int(r.get(KEY_PO_APPROVED) or 0)
    if ceo <= 0:
        return False
    ratio = po / ceo
    return ratio < EFFICIENCY_RATIO_MIN


def main() -> int:
    """CLI: check_bucket | record | check_degrade. Exit 0 = allow, 1 = deny/degrade."""
    if len(sys.argv) < 2:
        print("Uso: gateway_token_bucket.py check_bucket | record | check_degrade", file=sys.stderr)
        return 2
    r = get_redis()
    cmd = sys.argv[1].lower()
    if cmd == "check_bucket":
        return 0 if check_token_bucket(r) else 1
    if cmd == "record":
        record_strategy_event(r)
        return 0
    if cmd == "check_degrade":
        return 1 if should_degrade_ceo_to_local(r) else 0
    print(f"Comando desconhecido: {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
