#!/usr/bin/env python3
"""Politicas de tentativa e custo do runtime principal."""
from __future__ import annotations

import os

KEY_PREFIX = os.environ.get("KEY_PREFIX_PROJECT", "project:v1")
FINOPS_MAX_ATTEMPTS = int(os.environ.get("FINOPS_MAX_ATTEMPTS", "5"))
FINOPS_DAILY_CAP = float(os.environ.get("FINOPS_DAILY_CAP", "5.0"))


def get_attempt_count(redis_client, issue_id: str) -> int:
    key = f"{KEY_PREFIX}:issue:{issue_id}:attempt_count"
    try:
        return int(redis_client.get(key) or 0)
    except Exception:
        return 0


def increment_attempt(redis_client, issue_id: str) -> int:
    key = f"{KEY_PREFIX}:issue:{issue_id}:attempt_count"
    attempt = redis_client.incr(key)
    redis_client.expire(key, 86400 * 2)
    return attempt


def should_stop_task(issue_id: str, attempt: int, cost_estimate: float) -> tuple[bool, str]:
    if attempt >= FINOPS_MAX_ATTEMPTS:
        return True, f"Tentativas ({attempt}) >= maximo ({FINOPS_MAX_ATTEMPTS}); devolver ao PO."
    effective_cost = cost_estimate * attempt
    if effective_cost >= FINOPS_DAILY_CAP:
        return True, f"Custo efetivo estimado ({effective_cost:.2f}) >= teto diario ({FINOPS_DAILY_CAP}); devolver ao PO."
    return False, ""
