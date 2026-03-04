#!/usr/bin/env python3
"""
Publicador de eventos para o Kanban board.
Os workers importam este módulo para notificar mudanças de estado no stream kanban:events.
O Kanban API consome este stream via SSE para atualizar o frontend em tempo real.
Ref: docs/agents-devs/state-machine-issues.md
"""
import os
import time

STREAM_KANBAN_EVENTS = os.environ.get("STREAM_KANBAN_EVENTS", "kanban:events")
# Limitar o stream a ~1000 entradas para não estourar memória
KANBAN_STREAM_MAXLEN = int(os.environ.get("KANBAN_STREAM_MAXLEN", "1000"))


def publish_kanban_event(
    r,
    issue_id: str,
    old_state: str,
    new_state: str,
    agent: str = "unknown",
    extra: dict | None = None,
) -> str | None:
    """
    Publica evento de transição de estado no stream kanban:events.
    Retorna o ID da mensagem ou None em caso de erro.

    Args:
        r: cliente Redis
        issue_id: ID da issue
        old_state: estado anterior (pode ser vazio se criação)
        new_state: novo estado
        agent: nome do agente que fez a transição
        extra: campos adicionais opcionais
    """
    if not issue_id or not new_state:
        return None
    payload = {
        "issue_id": str(issue_id),
        "from_state": str(old_state or ""),
        "to_state": str(new_state),
        "agent": str(agent),
        "ts": str(int(time.time() * 1000)),
    }
    if extra and isinstance(extra, dict):
        for k, v in extra.items():
            payload[k] = str(v)
    try:
        return r.xadd(
            STREAM_KANBAN_EVENTS,
            payload,
            maxlen=KANBAN_STREAM_MAXLEN,
            approximate=True,
        )
    except Exception:
        return None


def publish_kanban_issue_created(
    r,
    issue_id: str,
    title: str,
    agent: str = "director",
) -> str | None:
    """Atalho: publica evento de criação de issue."""
    return publish_kanban_event(
        r,
        issue_id=issue_id,
        old_state="",
        new_state="Backlog",
        agent=agent,
        extra={"action": "created", "title": title},
    )
