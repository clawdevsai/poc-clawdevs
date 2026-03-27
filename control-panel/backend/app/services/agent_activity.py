from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import get_settings

settings = get_settings()

IGNORED_ACTIVITY_TEXTS = {
    "NO_REPLY",
    "HEARTBEAT_OK",
    "PONG",
    "OK",
}


def get_agent_current_activity(
    agent_slug: str,
) -> tuple[str | None, str | None, datetime | None]:
    """Return short/full human-readable activity text for the latest agent session."""
    sessions_path = (
        Path(settings.openclaw_data_path) / "agents" / agent_slug / "sessions" / "sessions.json"
    )
    if not sessions_path.exists():
        return None, None, None

    try:
        with open(sessions_path, "r", encoding="utf-8") as f:
            sessions = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None, None, None

    if not isinstance(sessions, dict) or not sessions:
        return None, None, None

    latest = _pick_latest_session(sessions)
    if not latest:
        return None, None, None

    updated_at = _parse_timestamp(latest.get("updatedAt"))
    session_file = _resolve_session_file(agent_slug, latest)
    if not session_file or not session_file.exists():
        return None, None, updated_at

    full_text, role = _extract_last_meaningful_text(session_file)
    if not full_text:
        return None, None, updated_at

    full_label = full_text if role == "assistant" else f"User: {full_text}"
    compact = " ".join(full_label.split())
    summary = compact if len(compact) <= 260 else compact[:257] + "..."
    return summary, full_label, updated_at


def _pick_latest_session(sessions: dict) -> dict | None:
    def score(item: dict) -> float:
        ts = item.get("updatedAt")
        if isinstance(ts, (int, float)):
            return float(ts)
        if isinstance(ts, str):
            try:
                return float(ts)
            except ValueError:
                return 0.0
        return 0.0

    candidates = [v for v in sessions.values() if isinstance(v, dict)]
    if not candidates:
        return None
    return max(candidates, key=score)


def _resolve_session_file(agent_slug: str, session_obj: dict) -> Path | None:
    session_file = session_obj.get("sessionFile")
    if isinstance(session_file, str) and session_file:
        if session_file.startswith("/"):
            return Path(session_file)
        return Path(settings.openclaw_data_path) / session_file

    session_id = session_obj.get("sessionId")
    if isinstance(session_id, str) and session_id:
        return (
            Path(settings.openclaw_data_path)
            / "agents"
            / agent_slug
            / "sessions"
            / f"{session_id}.jsonl"
        )
    return None


def _extract_last_meaningful_text(session_file: Path) -> tuple[str | None, str | None]:
    try:
        with open(session_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError:
        return None, None

    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        if not isinstance(event, dict) or event.get("type") != "message":
            continue
        msg = event.get("message")
        if not isinstance(msg, dict):
            continue

        role = str(msg.get("role", "")).lower()
        if role not in {"assistant", "user"}:
            continue

        text = _extract_text_content(msg.get("content"))
        if not text:
            continue
        full_text = text.strip()
        if full_text.upper() in IGNORED_ACTIVITY_TEXTS:
            continue
        return full_text, role

    return None, None


def _extract_text_content(content: object) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
                continue
            if not isinstance(item, dict):
                continue
            if item.get("type") == "text" and isinstance(item.get("text"), str):
                parts.append(item["text"])
        return "\n".join(p.strip() for p in parts if p and p.strip()).strip()
    return ""


def _parse_timestamp(value: object) -> datetime | None:
    if isinstance(value, (int, float)):
        ts = float(value)
        if ts > 946684800000:
            ts = ts / 1000
        return datetime.fromtimestamp(ts, timezone.utc)
    if isinstance(value, str):
        try:
            ts = float(value)
            if ts > 946684800000:
                ts = ts / 1000
            return datetime.fromtimestamp(ts, timezone.utc)
        except ValueError:
            return None
    return None
