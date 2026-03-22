import re
from pathlib import Path
from typing import Optional
from app.core.config import get_settings

settings = get_settings()

AGENT_SLUGS = [
    "ceo", "po", "arquiteto", "dev_backend", "dev_frontend",
    "dev_mobile", "qa_engineer", "devops_sre", "security_engineer",
    "ux_designer", "dba_data_engineer", "memory_curator",
]

CRON_MAP = {
    "dev_backend": "0 * * * *",
    "dev_frontend": "0 * * * *",
    "dev_mobile": "0 * * * *",
    "qa_engineer": "0 */6 * * *",
    "devops_sre": "0 */6 * * *",
    "security_engineer": "0 */6 * * *",
    "ux_designer": "0 */6 * * *",
    "dba_data_engineer": "0 */6 * * *",
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

DISPLAY_NAME_MAP = {
    "ceo": "Victor",
    "memory_curator": "Mnemon",
    "dev_backend": "Mateus",
}


def parse_identity(slug: str) -> dict:
    """Try to read IDENTITY.md from the openclaw data path. Fall back to defaults."""
    base = Path(settings.openclaw_data_path) / "agents" / slug
    identity_file = base / "IDENTITY.md"
    display_name = DISPLAY_NAME_MAP.get(slug, slug.replace("_", " ").title())
    role = ROLE_MAP.get(slug, slug)

    if identity_file.exists():
        try:
            content = identity_file.read_text(encoding="utf-8")
            name_match = re.search(r"(?:Nome|Name)[:\s]+([^\n]+)", content, re.IGNORECASE)
            role_match = re.search(r"(?:Papel|Role)[:\s]+([^\n]+)", content, re.IGNORECASE)
            if name_match:
                display_name = name_match.group(1).strip()
            if role_match:
                role = role_match.group(1).strip()
        except Exception:
            pass

    return {"display_name": display_name, "role": role}


async def sync_agents(session) -> None:
    """Upsert all 12 agents from config. Called at startup."""
    from sqlmodel import select
    from app.models import Agent

    for slug in AGENT_SLUGS:
        result = await session.exec(select(Agent).where(Agent.slug == slug))
        agent = result.first()
        identity = parse_identity(slug)

        if agent is None:
            agent = Agent(
                slug=slug,
                display_name=identity["display_name"],
                role=identity["role"],
                avatar_url=f"/static/avatars/{slug}.png",
                cron_expression=CRON_MAP.get(slug),
            )
            session.add(agent)
        else:
            agent.display_name = identity["display_name"]
            agent.role = identity["role"]

    await session.commit()
