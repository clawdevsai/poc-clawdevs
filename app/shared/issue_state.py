#!/usr/bin/env python3
"""Estado de issues do fluxo principal."""
import os

from app.shared.redis_client import get_redis

KEY_PREFIX = os.environ.get("KEY_PREFIX_PROJECT", "project:v1")
STATE_KEY_SUFFIX = ":state"

STATE_BACKLOG = "Backlog"
STATE_REFINAMENTO = "Refinamento"
STATE_READY = "Ready"
STATE_IN_PROGRESS = "InProgress"
STATE_DEPLOYED = "Deployed"
STATE_DONE = "Done"

VALID_STATES = {
    STATE_BACKLOG,
    STATE_REFINAMENTO,
    STATE_READY,
    STATE_IN_PROGRESS,
    STATE_DEPLOYED,
    STATE_DONE,
}

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
    """Alias sem efeitos colaterais extras."""
    return set_issue_state(r, issue_id, new_state, ttl_sec)


if __name__ == "__main__":
    # Teste mínimo: sem Redis não quebra
    import sys
    try:
        r = get_redis()
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
