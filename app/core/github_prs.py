#!/usr/bin/env python3
"""Consulta status de merge de PR no GitHub com cache curto."""
from __future__ import annotations

import json
import os
import urllib.request
from typing import Callable

KEY_PREFIX = os.environ.get("KEY_PREFIX_PROJECT", "project:v1")
PR_MERGE_CACHE_TTL_SEC = int(os.getenv("PR_MERGE_CACHE_TTL_SEC", "60"))


def _github_token() -> str:
    return (os.getenv("GITHUB_TOKEN") or "").strip()


def _cache_key(issue_id: str) -> str:
    return f"{KEY_PREFIX}:issue:{issue_id}:github_pr_merged_cache"


def _request_json(url: str, headers: dict[str, str]) -> dict:
    request = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload if isinstance(payload, dict) else {}


def check_pr_merged_status(
    redis_client,
    *,
    issue_id: str,
    repo: str,
    pr: str,
    request_fn: Callable[[str, dict[str, str]], dict] | None = None,
) -> bool:
    if not issue_id or not repo or not pr:
        return False

    cached = redis_client.get(_cache_key(issue_id))
    if isinstance(cached, bytes):
        cached = cached.decode("utf-8", errors="replace")
    if str(cached or "").strip() in {"1", "0"}:
        return str(cached) == "1"

    token = _github_token()
    if not token:
        return False

    url = f"https://api.github.com/repos/{repo}/pulls/{pr}"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "clawdevs-pr-merge-check",
    }
    try:
        payload = (request_fn or _request_json)(url, headers)
        merged = bool(payload.get("merged"))
        redis_client.set(_cache_key(issue_id), "1" if merged else "0", ex=PR_MERGE_CACHE_TTL_SEC)
        return merged
    except Exception:
        return False
