#!/usr/bin/env python3
"""Criacao de issues no GitHub com controle simples de idempotencia por issue_id."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Callable

KEY_PREFIX = os.environ.get("KEY_PREFIX_PROJECT", "project:v1")


def _github_token() -> str:
    return (os.getenv("GITHUB_TOKEN") or "").strip()


def _github_issue_number_key(issue_id: str) -> str:
    return f"{KEY_PREFIX}:issue:{issue_id}:github_issue_number"


def _github_issue_url_key(issue_id: str) -> str:
    return f"{KEY_PREFIX}:issue:{issue_id}:github_issue_url"


def _github_sync_status_key(issue_id: str) -> str:
    return f"{KEY_PREFIX}:issue:{issue_id}:github_sync_status"


def _issue_repo_key(issue_id: str) -> str:
    return f"{KEY_PREFIX}:issue:{issue_id}:repo"


def _post_issue_request(
    url: str,
    headers: dict[str, str],
    payload: dict[str, Any],
) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers=headers,
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        if response.status >= 300:
            raise RuntimeError(f"github_issue_http_{response.status}")
        raw = response.read().decode("utf-8", errors="replace")
    return json.loads(raw) if raw else {}


def ensure_github_issue_for_runtime_issue(
    redis_client: Any,
    *,
    issue_id: str,
    repo: str,
    title: str,
    body: str,
    request_fn: Callable[[str, dict[str, str], dict[str, Any]], dict[str, Any]] | None = None,
) -> dict[str, str]:
    issue_id = str(issue_id or "").strip()
    repo = str(repo or "").strip()
    if not issue_id or not repo:
        redis_client.set(_github_sync_status_key(issue_id), "skipped_missing_issue_or_repo")
        return {"status": "skipped_missing_issue_or_repo", "issue_id": issue_id}

    existing_number = redis_client.get(_github_issue_number_key(issue_id))
    existing_url = redis_client.get(_github_issue_url_key(issue_id))
    if existing_number:
        redis_client.set(_github_sync_status_key(issue_id), "already_synced")
        redis_client.set(_issue_repo_key(issue_id), repo)
        return {
            "status": "already_synced",
            "issue_id": issue_id,
            "number": str(existing_number),
            "url": str(existing_url or ""),
        }

    token = _github_token()
    if not token:
        redis_client.set(_github_sync_status_key(issue_id), "skipped_not_configured")
        redis_client.set(_issue_repo_key(issue_id), repo)
        return {"status": "skipped_not_configured", "issue_id": issue_id}

    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "clawdevs-po-runtime",
        "Content-Type": "application/json",
    }
    payload = {"title": title or issue_id, "body": body or ""}
    request_fn = request_fn or _post_issue_request
    try:
        response = request_fn(url, headers, payload)
    except (urllib.error.URLError, RuntimeError, ValueError) as error:
        redis_client.set(_github_sync_status_key(issue_id), f"error:{error}")
        redis_client.set(_issue_repo_key(issue_id), repo)
        return {"status": "error", "issue_id": issue_id, "reason": str(error)}

    number = str(response.get("number") or "").strip()
    html_url = str(response.get("html_url") or "").strip()
    if not number:
        redis_client.set(_github_sync_status_key(issue_id), "error:missing_number")
        redis_client.set(_issue_repo_key(issue_id), repo)
        return {"status": "error", "issue_id": issue_id, "reason": "missing_number"}

    redis_client.set(_github_issue_number_key(issue_id), number)
    redis_client.set(_github_issue_url_key(issue_id), html_url)
    redis_client.set(_github_sync_status_key(issue_id), "synced")
    redis_client.set(_issue_repo_key(issue_id), repo)
    return {"status": "synced", "issue_id": issue_id, "number": number, "url": html_url}
