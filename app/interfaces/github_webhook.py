#!/usr/bin/env python3
"""Webhook GitHub para sincronizacao de estado de PR no runtime."""
from __future__ import annotations

import hashlib
import hmac
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from app.core.orchestration import emit_event
from app.shared.issue_state import STATE_DEPLOYED, STATE_IN_REVIEW, set_issue_state
from app.shared.redis_client import get_redis_with_retry

KEY_PREFIX = os.environ.get("KEY_PREFIX_PROJECT", "project:v1")
WEBHOOK_HOST = os.getenv("GITHUB_WEBHOOK_HOST", "0.0.0.0")


def _parse_webhook_port(raw_port: str) -> int:
    value = str(raw_port or "").strip()
    if not value:
        return 8081
    if value.isdigit():
        return int(value)
    if "://" in value:
        candidate = value.rsplit(":", 1)[-1]
        if candidate.isdigit():
            return int(candidate)
    raise ValueError(f"GITHUB_WEBHOOK_PORT invalido: {value}")


WEBHOOK_PORT = _parse_webhook_port(os.getenv("GITHUB_WEBHOOK_PORT", "8081"))
WEBHOOK_PATH = os.getenv("GITHUB_WEBHOOK_PATH", "/webhook/github")
WEBHOOK_SECRET = (os.getenv("GITHUB_WEBHOOK_SECRET") or "").strip()
WEBHOOK_ADMIN_TOKEN = (os.getenv("GITHUB_WEBHOOK_ADMIN_TOKEN") or "").strip()

METRIC_RECEIVED_TOTAL = "received_total"
METRIC_PROCESSED_TOTAL = "processed_total"
METRIC_DUPLICATE_TOTAL = "duplicate_total"
METRIC_INVALID_SIGNATURE_TOTAL = "invalid_signature_total"
METRIC_INVALID_JSON_TOTAL = "invalid_json_total"
METRIC_IGNORED_EVENT_TOTAL = "ignored_event_total"
METRIC_IN_REVIEW_TOTAL = "in_review_total"
METRIC_MERGED_TOTAL = "merged_total"


def _pr_merged_key(issue_id: str) -> str:
    return f"{KEY_PREFIX}:issue:{issue_id}:pr_merged"


def _pr_number_key(issue_id: str) -> str:
    return f"{KEY_PREFIX}:issue:{issue_id}:pr_number"


def _issue_repo_key(issue_id: str) -> str:
    return f"{KEY_PREFIX}:issue:{issue_id}:repo"


def _issue_active_developer_key(issue_id: str) -> str:
    return f"{KEY_PREFIX}:issue:{issue_id}:active_developer"


def _developer_active_issue_key(developer_id: str) -> str:
    return f"{KEY_PREFIX}:developer:{developer_id}:active_issue"


def _repo_pr_issue_key(repo: str, pr: str) -> str:
    safe_repo = repo.replace("/", "__")
    return f"{KEY_PREFIX}:repo:{safe_repo}:pr:{pr}:issue_id"


def _metric_key(name: str) -> str:
    return f"{KEY_PREFIX}:github:webhook:metric:{name}"


def increment_metric(redis_client: Any, name: str) -> int:
    return int(redis_client.incr(_metric_key(name)))


def set_metric(redis_client: Any, name: str, value: str) -> None:
    redis_client.set(_metric_key(name), value)


def collect_metrics(redis_client: Any) -> dict[str, str]:
    names = (
        METRIC_RECEIVED_TOTAL,
        METRIC_PROCESSED_TOTAL,
        METRIC_DUPLICATE_TOTAL,
        METRIC_INVALID_SIGNATURE_TOTAL,
        METRIC_INVALID_JSON_TOTAL,
        METRIC_IGNORED_EVENT_TOTAL,
        METRIC_IN_REVIEW_TOTAL,
        METRIC_MERGED_TOTAL,
        "last_delivery_id",
        "last_event",
        "last_result",
    )
    out: dict[str, str] = {}
    for name in names:
        raw = redis_client.get(_metric_key(name))
        out[name] = str(raw or "")
    return out


def reset_metrics(redis_client: Any) -> None:
    names = (
        METRIC_RECEIVED_TOTAL,
        METRIC_PROCESSED_TOTAL,
        METRIC_DUPLICATE_TOTAL,
        METRIC_INVALID_SIGNATURE_TOTAL,
        METRIC_INVALID_JSON_TOTAL,
        METRIC_IGNORED_EVENT_TOTAL,
        METRIC_IN_REVIEW_TOTAL,
        METRIC_MERGED_TOTAL,
        "last_delivery_id",
        "last_event",
        "last_result",
    )
    for name in names:
        redis_client.delete(_metric_key(name))


def is_reset_authorized(token_header: str, expected_token: str) -> bool:
    if not expected_token:
        return False
    if not token_header:
        return False
    return hmac.compare_digest(token_header, expected_token)


def verify_signature(raw_body: bytes, signature_header: str, secret: str) -> bool:
    if not secret:
        return True
    if not signature_header or "=" not in signature_header:
        return False
    algo, received = signature_header.split("=", 1)
    if algo != "sha256":
        return False
    digest = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(digest, received)


def resolve_issue_id(redis_client: Any, *, repo: str, pr: str, payload: dict[str, Any]) -> str:
    direct = redis_client.get(_repo_pr_issue_key(repo, pr))
    if direct:
        return str(direct).strip()

    body = str((payload.get("pull_request") or {}).get("body") or "")
    marker = "issue_id:"
    idx = body.lower().find(marker)
    if idx >= 0:
        after = body[idx + len(marker):].strip().splitlines()[0].strip()
        if after:
            return after.split()[0].strip()
    return ""


def process_pull_request_event(redis_client: Any, payload: dict[str, Any]) -> dict[str, str]:
    action = str(payload.get("action") or "").strip()
    pull_request = payload.get("pull_request") or {}
    repository = payload.get("repository") or {}
    repo = str(repository.get("full_name") or "").strip()
    pr = str(pull_request.get("number") or payload.get("number") or "").strip()
    if not repo or not pr:
        return {"status": "ignored", "reason": "missing_repo_or_pr"}

    issue_id = resolve_issue_id(redis_client, repo=repo, pr=pr, payload=payload)
    if not issue_id:
        return {"status": "ignored", "reason": "issue_not_mapped", "repo": repo, "pr": pr}

    redis_client.set(_pr_number_key(issue_id), pr)
    redis_client.set(_issue_repo_key(issue_id), repo)
    redis_client.set(_repo_pr_issue_key(repo, pr), issue_id)

    if action in {"opened", "reopened", "synchronize"}:
        set_issue_state(redis_client, issue_id, STATE_IN_REVIEW)
        increment_metric(redis_client, METRIC_IN_REVIEW_TOTAL)
        emit_event(
            redis_client,
            "github_pr_in_review",
            issue_id=issue_id,
            repo=repo,
            pr=pr,
            action=action,
            status_code="github_pr_in_review",
            event_name="orchestration.github_pr_in_review",
        )
        return {"status": "ok", "transition": "in_review", "issue_id": issue_id}

    if action == "closed" and bool(pull_request.get("merged")):
        branch = str((pull_request.get("base") or {}).get("ref") or "")
        redis_client.set(_pr_merged_key(issue_id), "1")
        set_issue_state(redis_client, issue_id, STATE_DEPLOYED)
        increment_metric(redis_client, METRIC_MERGED_TOTAL)
        active_developer = redis_client.get(_issue_active_developer_key(issue_id))
        active_developer = str(active_developer or "").strip()
        if active_developer:
            redis_client.delete(_developer_active_issue_key(active_developer))
            redis_client.delete(_issue_active_developer_key(issue_id))
        redis_client.xadd(
            "event:devops",
            {
                "issue_id": issue_id,
                "branch": branch,
                "repo": repo,
                "pr": pr,
                "reason": "github_webhook_pr_merged",
            },
        )
        emit_event(
            redis_client,
            "github_pr_merged",
            issue_id=issue_id,
            repo=repo,
            pr=pr,
            branch=branch,
            status_code="github_pr_merged",
            event_name="orchestration.github_pr_merged",
        )
        return {"status": "ok", "transition": "merged", "issue_id": issue_id}

    return {"status": "ignored", "reason": f"action_{action}_not_mapped", "issue_id": issue_id}


class GithubWebhookHandler(BaseHTTPRequestHandler):
    redis_client = None

    def do_GET(self):  # noqa: N802
        if self.path == "/healthz":
            try:
                self.redis_client.ping()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'{"ok":true}')
            except Exception:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b'{"ok":false}')
            return
        if self.path == "/metrics":
            payload = collect_metrics(self.redis_client)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(payload).encode("utf-8"))
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):  # noqa: N802
        if self.path == "/metrics/reset":
            token_header = str(self.headers.get("X-Webhook-Admin-Token") or "")
            if not is_reset_authorized(token_header, WEBHOOK_ADMIN_TOKEN):
                self.send_response(401)
                self.end_headers()
                self.wfile.write(b'{"error":"unauthorized"}')
                return
            reset_metrics(self.redis_client)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"status":"metrics_reset"}')
            return
        if self.path != WEBHOOK_PATH:
            self.send_response(404)
            self.end_headers()
            return
        increment_metric(self.redis_client, METRIC_RECEIVED_TOTAL)
        raw_body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
        signature = self.headers.get("X-Hub-Signature-256", "")
        if not verify_signature(raw_body, signature, WEBHOOK_SECRET):
            increment_metric(self.redis_client, METRIC_INVALID_SIGNATURE_TOTAL)
            set_metric(self.redis_client, "last_result", "invalid_signature")
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b'{"error":"invalid_signature"}')
            return
        delivery_id = str(self.headers.get("X-GitHub-Delivery") or "").strip()
        if delivery_id:
            dedupe_key = f"{KEY_PREFIX}:github:webhook:delivery:{delivery_id}"
            if not self.redis_client.set(dedupe_key, "1", nx=True, ex=60 * 60 * 24):
                increment_metric(self.redis_client, METRIC_DUPLICATE_TOTAL)
                set_metric(self.redis_client, "last_delivery_id", delivery_id)
                set_metric(self.redis_client, "last_result", "duplicate_delivery")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'{"status":"duplicate_delivery"}')
                return
            set_metric(self.redis_client, "last_delivery_id", delivery_id)
        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except Exception:
            increment_metric(self.redis_client, METRIC_INVALID_JSON_TOTAL)
            set_metric(self.redis_client, "last_result", "invalid_json")
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'{"error":"invalid_json"}')
            return

        event_name = str(self.headers.get("X-GitHub-Event") or "")
        set_metric(self.redis_client, "last_event", event_name)
        if event_name != "pull_request":
            increment_metric(self.redis_client, METRIC_IGNORED_EVENT_TOTAL)
            set_metric(self.redis_client, "last_result", "ignored_event")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"status":"ignored_event"}')
            return

        result = process_pull_request_event(self.redis_client, payload)
        increment_metric(self.redis_client, METRIC_PROCESSED_TOTAL)
        set_metric(self.redis_client, "last_result", str(result.get("status") or "ok"))
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps(result).encode("utf-8"))

    def log_message(self, format, *args):  # noqa: A003
        return


def main() -> int:
    redis_client = get_redis_with_retry()
    GithubWebhookHandler.redis_client = redis_client
    server = ThreadingHTTPServer((WEBHOOK_HOST, WEBHOOK_PORT), GithubWebhookHandler)
    print(f"[github-webhook] listening on {WEBHOOK_HOST}:{WEBHOOK_PORT}{WEBHOOK_PATH}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
