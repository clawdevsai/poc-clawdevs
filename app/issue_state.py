#!/usr/bin/env python3
"""
Módulo compartilhado para estado de issues (state diagram).
Chave: project:v1:issue:{id}:state com valores Backlog, Refinamento, Ready,
InProgress, InReview, Approved, Merged, Deployed, Monitoring, Done.
Ref: docs/agents-devs/state-machine-issues.md, docs/38-redis-streams-estado-global.md
"""
import os

KEY_PREFIX = os.environ.get("KEY_PREFIX_PROJECT", "project:v1")
STATE_KEY_SUFFIX = ":state"

# Estados da máquina (state diagram)
STATE_BACKLOG = "Backlog"
STATE_REFINAMENTO = "Refinamento"
STATE_READY = "Ready"
STATE_IN_PROGRESS = "InProgress"
STATE_IN_REVIEW = "InReview"
STATE_APPROVED = "Approved"
STATE_MERGED = "Merged"
STATE_DEPLOYED = "Deployed"
STATE_MONITORING = "Monitoring"
STATE_DONE = "Done"
STATE_NEW = "New"
STATE_SHORTLISTED = "Shortlisted"
STATE_INTERVIEWED = "Interviewed"

VALID_STATES = {
    STATE_BACKLOG,
    STATE_REFINAMENTO,
    STATE_READY,
    STATE_IN_PROGRESS,
    STATE_IN_REVIEW,
    STATE_APPROVED,
    STATE_MERGED,
    STATE_DEPLOYED,
    STATE_MONITORING,
    STATE_DONE,
    STATE_NEW,
    STATE_SHORTLISTED,
    STATE_INTERVIEWED,
}


def _get_redis():
    try:
        import redis
        host = os.environ.get("REDIS_HOST", "redis-service.ai-agents.svc.cluster.local")
        port = int(os.environ.get("REDIS_PORT", "6379"))
        return redis.Redis(host=host, port=port, db=0, decode_responses=True)
    except ImportError:
        raise RuntimeError("Instale redis: pip install redis")


def _state_key(issue_id: str) -> str:
    return f"{KEY_PREFIX}:issue:{issue_id}{STATE_KEY_SUFFIX}"


def set_issue_state(r, issue_id: str, state: str, ttl_sec: int | None = None) -> bool:
    """
    Define o estado da issue. Retorna True se gravado.
    r: cliente Redis; issue_id: id da issue; state: um de VALID_STATES; ttl_sec: opcional.
    """
    if not issue_id or not state:
        return False
    if state not in VALID_STATES:
        return False
    key = _state_key(issue_id)
    if ttl_sec is not None:
        r.setex(key, ttl_sec, state)
    else:
        r.set(key, state)
    return True


def get_issue_state(r, issue_id: str) -> str | None:
    """Retorna o estado atual da issue ou None se não existir."""
    if not issue_id:
        return None
    key = _state_key(issue_id)
    return r.get(key)


def transition(r, issue_id: str, new_state: str, ttl_sec: int | None = None, agent: str = "agent") -> bool:
    """
    Alias para set_issue_state (transição de estado).
    Agora também publica evento no Kanban se o publicador estiver disponível.
    """
    old_state = get_issue_state(r, issue_id)
    ok = set_issue_state(r, issue_id, new_state, ttl_sec)
    if ok:
        try:
            from kanban_event_publisher import publish_kanban_event
            publish_kanban_event(r, issue_id, old_state, new_state, agent)
        except ImportError:
            pass
    return ok


if __name__ == "__main__":
    # Teste mínimo: sem Redis não quebra
    import sys
    try:
        r = _get_redis()
        r.ping()
    except Exception as e:
        print(f"Redis não disponível: {e}", file=sys.stderr)
        sys.exit(0)
    ok = set_issue_state(r, "test-1", STATE_BACKLOG)
    print(f"set_issue_state(test-1, Backlog) -> {ok}")
    s = get_issue_state(r, "test-1")
    print(f"get_issue_state(test-1) -> {s!r}")
    r.delete(_state_key("test-1"))
    print("issue_state: ok")
