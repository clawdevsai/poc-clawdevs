#!/usr/bin/env python3
"""Publicacao de comentarios de review no GitHub."""
from __future__ import annotations

import json
import os
import urllib.request
from typing import Callable

KEY_PREFIX = os.environ.get("KEY_PREFIX_PROJECT", "project:v1")


def _github_token() -> str:
    return (os.getenv("GITHUB_TOKEN") or "").strip()


def _comment_key(issue_id: str, review_round: str, scope: str) -> str:
    return f"{KEY_PREFIX}:issue:{issue_id}:review:{review_round}:github_comment:{scope}"


def _post_comment_request(url: str, headers: dict[str, str], payload: dict[str, str]) -> None:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers=headers,
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        if response.status >= 300:
            raise RuntimeError(f"github_comment_http_{response.status}")


def publish_role_review_comment(
    redis_client,
    *,
    issue_id: str,
    review_round: str,
    role: str,
    decision: str,
    summary: str,
    repo: str,
    pr: str,
    request_fn: Callable[[str, dict[str, str], dict[str, str]], None] | None = None,
) -> str:
    role_scope = role.lower()
    key = _comment_key(issue_id, review_round, role_scope)
    if not issue_id or not review_round or not role_scope:
        return "ignored"
    token = _github_token()
    if not repo or not pr or not token:
        return "skipped_not_configured"
    if not redis_client.set(key, "posting", nx=True, ex=60 * 60 * 24):
        return "already_posted"

    url = f"https://api.github.com/repos/{repo}/issues/{pr}/comments"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "clawdevs-review-consensus",
        "Content-Type": "application/json",
    }
    body = {
        "body": (
            f"[{role}] Review round {review_round}\n"
            f"- Issue: {issue_id}\n"
            f"- Decision: {decision}\n"
            f"- Summary: {summary or 'n/a'}"
        )
    }
    try:
        (request_fn or _post_comment_request)(url, headers, body)
        redis_client.set(key, "posted", ex=60 * 60 * 24)
        return "posted"
    except Exception:
        redis_client.delete(key)
        return "error"


def publish_consensus_comment(
    redis_client,
    *,
    issue_id: str,
    review_round: str,
    repo: str,
    pr: str,
    outcome: str,
    decisions_by_role: dict[str, dict[str, str]],
    request_fn: Callable[[str, dict[str, str], dict[str, str]], None] | None = None,
) -> str:
    key = _comment_key(issue_id, review_round, "consensus")
    if not issue_id or not review_round:
        return "ignored"
    token = _github_token()
    if not repo or not pr or not token:
        return "skipped_not_configured"
    if not redis_client.set(key, "posting", nx=True, ex=60 * 60 * 24):
        return "already_posted"

    lines = []
    for role in ("QA", "DBA", "CyberSec"):
        data = decisions_by_role.get(role, {})
        lines.append(f"- {role}: {data.get('decision', 'unknown')} ({data.get('summary', 'n/a')})")
    body = {
        "body": (
            f"[Consensus] Review round {review_round}\n"
            f"- Issue: {issue_id}\n"
            f"- Outcome: {outcome}\n"
            f"- Decisions:\n" + "\n".join(lines)
        )
    }
    url = f"https://api.github.com/repos/{repo}/issues/{pr}/comments"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "clawdevs-review-consensus",
        "Content-Type": "application/json",
    }
    try:
        (request_fn or _post_comment_request)(url, headers, body)
        redis_client.set(key, "posted", ex=60 * 60 * 24)
        return "posted"
    except Exception:
        redis_client.delete(key)
        return "error"
