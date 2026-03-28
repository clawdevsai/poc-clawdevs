# Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json
import os
import re
from pathlib import Path
from datetime import datetime, timezone, UTC
from functools import lru_cache
from typing import Any, cast
from app.core.config import get_settings

settings = get_settings()


def _now_utc_naive() -> datetime:
    """Return current UTC time as naive datetime (tzinfo removed)."""
    return datetime.now(UTC).replace(tzinfo=None)


def _to_utc_naive(value: datetime) -> datetime:
    """Normalize datetime values to naive UTC."""
    if value.tzinfo is None:
        return value
    return value.astimezone(UTC).replace(tzinfo=None)


DEFAULT_AGENT_SLUGS = [
    "ceo",
    "po",
    "arquiteto",
    "dev_backend",
    "dev_frontend",
    "dev_mobile",
    "qa_engineer",
    "devops_sre",
    "security_engineer",
    "ux_designer",
    "dba_data_engineer",
    "memory_curator",
]

# Load CRON expressions from environment or use defaults
CRON_MAP = {
    "dev_backend": os.getenv("DEV_BACKEND_CRON_EXPR", "0 */2 * * *"),
    "dev_frontend": os.getenv("DEV_FRONTEND_CRON_EXPR", "15 */2 * * *"),
    "dev_mobile": os.getenv("DEV_MOBILE_CRON_EXPR", "30 */2 * * *"),
    "qa_engineer": os.getenv("QA_CRON_EXPR", "45 */2 * * *"),
    "devops_sre": os.getenv("DEVOPS_SRE_CRON_EXPR", "0 * * * *"),
    "security_engineer": os.getenv("SECURITY_ENGINEER_CRON_EXPR", "0 2 * * *"),
    "ux_designer": os.getenv("UX_DESIGNER_CRON_EXPR", "0 9 * * 1"),
    "dba_data_engineer": os.getenv("DBA_DATA_ENGINEER_CRON_EXPR", "30 9 * * 1"),
    "memory_curator": "0 2 * * *",
}

ROLE_MAP = {
    "ceo": "CEO / Orchestrator",
    "po": "Product Owner",
    "arquiteto": "Architect",
    "dev_backend": "Backend Developer",
    "dev_frontend": "Frontend Developer",
    "dev_mobile": "Mobile Developer",
    "qa_engineer": "QA Engineer",
    "devops_sre": "DevOps / SRE",
    "security_engineer": "Security Engineer",
    "ux_designer": "UX Designer",
    "dba_data_engineer": "DBA / Data Engineer",
    "memory_curator": "Memory Curator",
}

AVATAR_URL_MAP = {
    "ceo": "/avatars/CEO.png",
    "po": "/avatars/PO.png",
    "arquiteto": "/avatars/Architect.png",
    "dev_backend": "/avatars/Developer.png",
    "dev_frontend": "/avatars/Developer.png",
    "dev_mobile": "/avatars/Developer.png",
    "qa_engineer": "/avatars/QA.png",
    "devops_sre": "/avatars/DevOps.png",
    "security_engineer": "/avatars/CyberSec.png",
    "ux_designer": "/avatars/UX.png",
    "dba_data_engineer": "/avatars/DBA.png",
    "memory_curator": "/avatars/Developer.png",
}


def _fallback_display_name(slug: str) -> str:
    return slug.replace("_", " ").replace("-", " ").title()


def _normalize_label(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("_", " ").replace("-", " ")).strip()


def _iter_config_agents() -> list[dict[str, Any]]:
    config = _get_openclaw_config()
    agents_group = config.get("agents", {})
    raw_agents = agents_group.get("list", []) if isinstance(agents_group, dict) else []
    return [cast(dict[str, Any], item) for item in raw_agents if isinstance(item, dict)]


def _discover_agent_slugs() -> list[str]:
    slugs: list[str] = []
    seen: set[str] = set()

    for agent in _iter_config_agents():
        slug = agent.get("id")
        if isinstance(slug, str) and slug and slug not in seen:
            slugs.append(slug)
            seen.add(slug)

    agents_dir = Path(settings.openclaw_data_path) / "agents"
    try:
        if agents_dir.exists():
            for entry in sorted(agents_dir.iterdir(), key=lambda item: item.name):
                if not entry.is_dir():
                    continue
                # Ignore runtime helper folders that are not real agents.
                if not (entry / "sessions").is_dir() and not (entry / "IDENTITY.md").exists():
                    continue
                slug = entry.name.strip()
                if slug and slug not in seen:
                    slugs.append(slug)
                    seen.add(slug)
    except OSError:
        pass

    if not slugs:
        return DEFAULT_AGENT_SLUGS.copy()
    return slugs


def get_discovered_agent_slugs() -> list[str]:
    """Discover agent slugs from OpenClaw config and runtime directories."""
    _get_openclaw_config.cache_clear()
    return _discover_agent_slugs()


@lru_cache(maxsize=1)
def _get_openclaw_config() -> dict[str, Any]:
    """Load OpenClaw configuration from JSON file."""
    config_path = Path(settings.openclaw_data_path) / "openclaw.json"
    try:
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                payload = json.load(f)
                if isinstance(payload, dict):
                    return cast(dict[str, Any], payload)
    except (OSError, json.JSONDecodeError):
        pass
    return {}


def _get_agent_config(slug: str) -> dict[str, Any]:
    """Get agent configuration from openclaw.json."""
    for agent in _iter_config_agents():
        if agent.get("id") == slug:
            return agent
    return {}


def parse_identity(slug: str) -> dict:
    """Try to read IDENTITY.md from the openclaw data path. Fall back to defaults."""
    import logging

    logger = logging.getLogger(__name__)

    base = Path(settings.openclaw_data_path) / "agents" / slug
    identity_file = base / "IDENTITY.md"
    display_name = _fallback_display_name(slug)
    role = ROLE_MAP.get(slug, slug)
    model = None

    # Try to get model from openclaw.json
    try:
        agent_config = _get_agent_config(slug)
        if agent_config:
            if isinstance(agent_config.get("model"), str):
                model = cast(str, agent_config.get("model"))

            config_name = agent_config.get("name")
            if isinstance(config_name, str) and config_name.strip():
                display_name = _normalize_label(config_name)

            config_role = agent_config.get("role")
            if isinstance(config_role, str) and config_role.strip():
                role = _normalize_label(config_role)
    except Exception as e:
        logger.warning(f"Failed to read agent config for {slug}: {e}")

    # Some agent folders/files can be mounted with restrictive ACLs.
    # Startup must not fail if identity metadata cannot be read.
    try:
        if identity_file.exists():
            content = identity_file.read_text(encoding="utf-8")
            name_match = re.search(
                r"(?:Nome|Name)[:\s]+([^\n]+)", content, re.IGNORECASE
            )
            role_match = re.search(
                r"(?:Papel|Role)[:\s]+([^\n]+)", content, re.IGNORECASE
            )
            if name_match:
                display_name = name_match.group(1).strip()
            if role_match:
                role = role_match.group(1).strip()
        else:
            logger.debug(f"IDENTITY.md not found for {slug} at {identity_file}")
    except (OSError, PermissionError) as e:
        logger.warning(f"Failed to read IDENTITY.md for {slug}: {e}")
    except Exception as e:
        logger.warning(f"Unexpected error reading identity for {slug}: {e}")

    logger.debug(
        f"Identity for {slug}: display_name={display_name}, role={role}, model={model}"
    )
    return {"display_name": display_name, "role": role, "model": model}


async def sync_agents(session) -> None:
    """Upsert agents discovered from OpenClaw config/runtime into the panel DB."""
    import logging
    from sqlmodel import delete, select
    from app.models import Agent

    logger = logging.getLogger(__name__)
    created_count = 0
    updated_count = 0
    deleted_count = 0

    try:
        _get_openclaw_config.cache_clear()
        discovered_slugs = _discover_agent_slugs()
        logger.info(f"Starting sync_agents for {len(discovered_slugs)} discovered agents")

        result = await session.exec(select(Agent))
        existing_agents = {agent.slug: agent for agent in result.all()}
        discovered_set = set(discovered_slugs)
        changed = False

        for slug in discovered_slugs:
            try:
                agent = existing_agents.get(slug)
                identity = parse_identity(slug)

                avatar_url = AVATAR_URL_MAP.get(slug, "/avatars/Developer.png")

                if agent is None:
                    agent = Agent(
                        slug=slug,
                        display_name=identity["display_name"],
                        role=identity["role"],
                        current_model=identity.get("model"),
                        avatar_url=avatar_url,
                        cron_expression=CRON_MAP.get(slug),
                    )
                    session.add(agent)
                    created_count += 1
                    changed = True
                    logger.info(
                        f"  ✓ Created agent: {slug} ({identity['display_name']})"
                    )
                else:
                    next_model = (
                        identity.get("model")
                        if isinstance(identity.get("model"), str)
                        else agent.current_model
                    )
                    next_cron_expression = CRON_MAP.get(slug, agent.cron_expression)

                    if (
                        agent.display_name != identity["display_name"]
                        or agent.role != identity["role"]
                        or agent.avatar_url != avatar_url
                        or agent.current_model != next_model
                        or agent.cron_expression != next_cron_expression
                    ):
                        agent.display_name = identity["display_name"]
                        agent.role = identity["role"]
                        agent.avatar_url = avatar_url
                        agent.current_model = next_model
                        agent.cron_expression = next_cron_expression
                        agent.updated_at = _now_utc_naive()
                        updated_count += 1
                        changed = True
                        logger.info(
                            f"  ✓ Updated agent: {slug} ({identity['display_name']})"
                        )
            except Exception as e:
                logger.error(f"Error syncing agent {slug}: {e}", exc_info=True)
                raise

        stale_slugs = sorted(set(existing_agents.keys()) - discovered_set)
        if stale_slugs:
            await session.exec(delete(Agent).where(Agent.slug.in_(stale_slugs)))
            deleted_count = len(stale_slugs)
            changed = True
            logger.info(f"  ✓ Removed stale agents: {', '.join(stale_slugs)}")

        logger.info(
            f"Committing {created_count} new agents, {updated_count} updates, "
            f"{deleted_count} removals..."
        )
        if changed:
            await session.commit()

        # Verify the sync worked
        result = await session.exec(select(Agent))
        final_agents = result.all()
        logger.info(
            "✓ Agent sync completed: "
            f"{created_count} created, {updated_count} updated, {deleted_count} removed"
        )
        logger.info(f"✓ Total agents in database: {len(final_agents)}")
        for agent in final_agents:
            logger.debug(f"  - {agent.slug}: {agent.display_name} ({agent.role})")

    except Exception as e:
        logger.error(f"✗ Failed to sync agents: {e}", exc_info=True)
        raise


def _pick_latest_runtime_entry(
    payload: dict | None,
) -> tuple[dict | None, datetime | None]:
    if not isinstance(payload, dict):
        return None, None
    latest_item: dict | None = None
    latest_ts: int | None = None

    for item in payload.values():
        if not isinstance(item, dict):
            continue
        ts = item.get("updatedAt")
        if isinstance(ts, (int, float)):
            ts_int = int(ts)
            if latest_ts is None or ts_int > latest_ts:
                latest_ts = ts_int
                latest_item = item

    if latest_ts is None:
        return None, None

    dt_utc = datetime.fromtimestamp(latest_ts / 1000, tz=timezone.utc).replace(
        tzinfo=None
    )
    return latest_item, dt_utc


def _status_from_heartbeat(
    last_heartbeat_at: datetime | None, has_active_session: bool = False
) -> str:
    """Determine agent status based on heartbeat and session activity.

    Args:
        last_heartbeat_at: Last known heartbeat timestamp
        has_active_session: Whether agent has an active session (processing)

    Returns:
        Status string: "working", "online", "idle", or "offline"
    """
    if last_heartbeat_at is None:
        return "offline"

    last_heartbeat_at = _to_utc_naive(last_heartbeat_at)

    age_seconds = (_now_utc_naive() - last_heartbeat_at).total_seconds()

    # If actively processing a session, mark as working
    if has_active_session and age_seconds <= 5 * 60:
        return "working"

    if age_seconds <= 5 * 60:
        return "online"
    if age_seconds <= 60 * 60:
        return "idle"
    return "offline"


def _has_active_session(payload: dict | None) -> bool:
    """Check if any session is currently active (processing).

    A session is considered active if:
    - status is "active" OR
    - abortedLastRun is False AND updatedAt is recent (< 5 min)
    """
    if not isinstance(payload, dict):
        return False

    for session_key, session_data in payload.items():
        if not isinstance(session_data, dict):
            continue

        # Check explicit status (but aborted sessions are not active)
        if session_data.get("status") == "active":
            if session_data.get("abortedLastRun", False) is True:
                continue
            return True

        # Check if session is running (not aborted and recent)
        aborted = session_data.get("abortedLastRun", True)
        updated_at = session_data.get("updatedAt")

        if not aborted and isinstance(updated_at, (int, float)):
            # Check if updated in last 5 minutes
            try:
                session_time = datetime.fromtimestamp(
                    updated_at / 1000, tz=timezone.utc
                ).replace(tzinfo=None)
                age_seconds = (_now_utc_naive() - session_time).total_seconds()
                if age_seconds <= 5 * 60:
                    return True
            except (ValueError, OSError, OverflowError):
                pass

    return False


async def sync_agents_runtime(session) -> None:
    """
    Refresh runtime status/model/heartbeat from OpenClaw session artifacts.
    This keeps panel status dynamic without relying on fixed task filenames.
    """
    from sqlmodel import select
    from app.models import Agent

    await sync_agents(session)

    result = await session.exec(select(Agent))
    agents = result.all()
    changed = False

    # Clear cache to get fresh config
    _get_openclaw_config.cache_clear()

    for agent in agents:
        identity = parse_identity(agent.slug)
        expected_avatar_url = AVATAR_URL_MAP.get(agent.slug, "/avatars/Developer.png")
        sessions_file = (
            Path(settings.openclaw_data_path)
            / "agents"
            / agent.slug
            / "sessions"
            / "sessions.json"
        )

        latest_item: dict | None = None
        latest_heartbeat: datetime | None = None
        has_active_session = False
        payload = None

        try:
            if sessions_file.exists():
                payload = json.loads(sessions_file.read_text(encoding="utf-8"))
                if isinstance(payload, dict):
                    latest_item, latest_heartbeat = _pick_latest_runtime_entry(payload)
                    has_active_session = _has_active_session(payload)
        except (OSError, PermissionError, json.JSONDecodeError):
            # Some mounted files can be unreadable under restrictive ACLs.
            pass

        # Get model from openclaw.json config (not from session files)
        agent_config = _get_agent_config(agent.slug)
        next_model = agent_config.get("model")

        next_session_id = (
            latest_item.get("sessionId")
            if isinstance(latest_item, dict)
            and isinstance(latest_item.get("sessionId"), str)
            else None
        )
        next_status = _status_from_heartbeat(latest_heartbeat, has_active_session)

        if (
            agent.last_heartbeat_at != latest_heartbeat
            or agent.openclaw_session_id != next_session_id
            or agent.current_model != next_model
            or agent.status != next_status
            or agent.display_name != identity["display_name"]
            or agent.role != identity["role"]
            or agent.avatar_url != expected_avatar_url
        ):
            agent.last_heartbeat_at = latest_heartbeat
            agent.openclaw_session_id = next_session_id
            agent.current_model = next_model
            agent.status = next_status
            agent.display_name = identity["display_name"]
            agent.role = identity["role"]
            agent.avatar_url = expected_avatar_url
            agent.updated_at = _now_utc_naive()
            changed = True

    if changed:
        await session.commit()
