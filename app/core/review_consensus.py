#!/usr/bin/env python3
"""Consenso de review entre QA, DBA e CyberSec."""
from __future__ import annotations

import json
import os
from typing import Any

from app.core.github_reviews import publish_consensus_comment, publish_role_review_comment
from app.core.orchestration import emit_event
from app.runtime.openclaw_output import normalize_openclaw_output
from app.shared.issue_state import STATE_BACKLOG, set_issue_state

KEY_PREFIX = os.environ.get("KEY_PREFIX_PROJECT", "project:v1")
REQUIRED_REVIEW_ROLES = ("QA", "DBA", "CyberSec")


def _decision_key(issue_id: str, review_round: str, role: str) -> str:
    return f"{KEY_PREFIX}:issue:{issue_id}:review:{review_round}:decision:{role.lower()}"


def _finalized_key(issue_id: str, review_round: str) -> str:
    return f"{KEY_PREFIX}:issue:{issue_id}:review:{review_round}:finalized"


def _parse_decision(send_output: dict | str) -> tuple[str, str]:
    normalized = normalize_openclaw_output(send_output)
    status = str(normalized.get("status") or "").strip().lower()
    decision = str(normalized.get("decision") or "").strip().lower()
    summary = str(normalized.get("summary") or "").strip() or str(send_output)[:300]
    approved_tokens = {"approved", "approve_for_merge", "approve_merge"}
    is_approved = status in approved_tokens or decision in approved_tokens
    return ("approved" if is_approved else "blocked", summary)


def _load_role_decision(redis_client: Any, issue_id: str, review_round: str, role: str) -> dict[str, str] | None:
    raw = redis_client.get(_decision_key(issue_id, review_round, role))
    if not raw:
        return None
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8", errors="replace")
    try:
        payload = json.loads(str(raw))
    except Exception:
        return None
    if not isinstance(payload, dict):
        return None
    return {
        "decision": str(payload.get("decision") or "").strip().lower(),
        "summary": str(payload.get("summary") or "").strip(),
    }


def record_review_decision(
    redis_client: Any,
    *,
    issue_id: str,
    review_round: str,
    role: str,
    send_output: dict | str,
    repo: str,
    pr: str,
) -> None:
    decision, summary = _parse_decision(send_output)
    payload = {"decision": decision, "summary": summary}
    redis_client.set(_decision_key(issue_id, review_round, role), json.dumps(payload), ex=60 * 60 * 24)
    publish_role_review_comment(
        redis_client,
        issue_id=issue_id,
        review_round=review_round,
        role=role,
        decision=decision,
        summary=summary,
        repo=repo,
        pr=pr,
    )


def finalize_round_if_ready(
    redis_client: Any,
    *,
    issue_id: str,
    review_round: str,
    branch: str,
    repo: str,
    pr: str,
) -> str:
    if not issue_id or not review_round:
        return "ignored"

    decisions: dict[str, dict[str, str]] = {}
    for role in REQUIRED_REVIEW_ROLES:
        decision = _load_role_decision(redis_client, issue_id, review_round, role)
        if decision is None:
            return "pending"
        decisions[role] = decision

    lock_key = _finalized_key(issue_id, review_round)
    locked = redis_client.set(lock_key, "1", nx=True, ex=60 * 60 * 24)
    if not locked:
        return "already_finalized"

    blocked_roles = [role for role, data in decisions.items() if data["decision"] != "approved"]
    if blocked_roles:
        publish_consensus_comment(
            redis_client,
            issue_id=issue_id,
            review_round=review_round,
            repo=repo,
            pr=pr,
            outcome="blocked",
            decisions_by_role=decisions,
        )
        set_issue_state(redis_client, issue_id, STATE_BACKLOG)
        redis_client.xadd(
            "task:backlog",
            {
                "issue_id": issue_id,
                "branch": branch,
                "repo": repo,
                "pr": pr,
                "round": review_round,
                "reason": "review_blocked",
                "blocked_roles": ",".join(blocked_roles),
            },
        )
        emit_event(
            redis_client,
            "review_consensus_blocked",
            issue_id=issue_id,
            branch=branch,
            repo=repo,
            pr=pr,
            round=review_round,
            blocked_roles=",".join(blocked_roles),
            status_code="review_consensus_blocked",
            event_name="orchestration.review_consensus_blocked",
        )
        return "blocked"

    publish_consensus_comment(
        redis_client,
        issue_id=issue_id,
        review_round=review_round,
        repo=repo,
        pr=pr,
        outcome="approved",
        decisions_by_role=decisions,
    )
    redis_client.xadd(
        "event:devops",
        {
            "issue_id": issue_id,
            "branch": branch,
            "repo": repo,
            "pr": pr,
            "round": review_round,
            "reason": "review_consensus_approved",
        },
    )
    emit_event(
        redis_client,
        "review_consensus_approved",
        issue_id=issue_id,
        branch=branch,
        repo=repo,
        pr=pr,
        round=review_round,
        status_code="review_consensus_approved",
        event_name="orchestration.review_consensus_approved",
    )
    return "approved"
