#!/usr/bin/env python3
"""
Utilitários Redis para contingência cluster acéfalo (124).
Chaves: ceo:last_strategy_ts (heartbeat), cluster:pause_consumption, cluster:contingency_acefalo.
Ref: docs/06-operacoes.md, docs/issues/124-contingencia-cluster-acefalo.md
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


KEY_LAST_STRATEGY_TS = "ceo:last_strategy_ts"
KEY_PAUSE_CONSUMPTION = "cluster:pause_consumption"
KEY_CONTINGENCY_ACEFALO = "cluster:contingency_acefalo"


def touch_heartbeat(r=None):
    """Atualiza o timestamp do último comando estratégico (heartbeat). Chamar quando CEO/orquestrador publicar estratégia ou quando health check externo passar."""
    if r is None:
        r = get_redis()
    r.set(KEY_LAST_STRATEGY_TS, str(time.time()))
    return True


def get_last_strategy_ts(r=None):
    """Retorna o timestamp do último heartbeat ou None se nunca atualizado."""
    if r is None:
        r = get_redis()
    s = r.get(KEY_LAST_STRATEGY_TS)
    if s is None:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def is_consumption_paused(r=None):
    """True se o consumo da fila (GPU) deve ser pausado (contingência acéfalo)."""
    if r is None:
        r = get_redis()
    return r.get(KEY_PAUSE_CONSUMPTION) == "1"


def set_pause_consumption(pause: bool, r=None):
    """Define se os consumidores devem pausar (True) ou retomar (False)."""
    if r is None:
        r = get_redis()
    r.set(KEY_PAUSE_CONSUMPTION, "1" if pause else "0")
    r.set(KEY_CONTINGENCY_ACEFALO, "1" if pause else "0")


def export_streams_to_json(r=None, streams=None):
    """Exporta o estado dos streams para uma estrutura dict (salvar como JSON)."""
    if r is None:
        r = get_redis()
    if streams is None:
        streams = ["cmd:strategy", "task:backlog", "draft.2.issue", "draft_rejected", "code:ready"]
    out = {"ts": time.time(), "streams": {}}
    for stream in streams:
        try:
            entries = r.xrange(stream)
            out["streams"][stream] = [
                {"id": eid, "data": data} for eid, data in entries
            ]
        except Exception as e:
            out["streams"][stream] = {"error": str(e)}
    return out


def restore_streams_from_json(data: dict, r=None, clear_before_restore: bool = False):
    """Restaura streams a partir do JSON exportado. Se clear_before_restore, deleta o stream antes (cuidado: perde mensagens atuais)."""
    if r is None:
        r = get_redis()
    for stream, entries in data.get("streams", {}).items():
        if isinstance(entries, dict) and "error" in entries:
            continue
        if clear_before_restore:
            r.delete(stream)
        for item in entries:
            eid = item.get("id")
            payload = item.get("data", {})
            if eid and payload:
                try:
                    r.xadd(stream, payload, id=eid, nomkstream=False)
                except Exception:
                    pass  # duplicate id etc.
    return True
