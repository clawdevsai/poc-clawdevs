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

"""Task synchronization service.

Fetches tasks from GitHub issues and syncs them to the database.
This enables tracking what agents are working on.
"""

import logging
from datetime import datetime, UTC
from typing import Optional
from sqlmodel import select

from app.models import Task, Agent
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


# Map GitHub labels to task labels
LABEL_MAP = {
    "back-end": "back_end",
    "backend": "back_end",
    "front-end": "front_end",
    "frontend": "front_end",
    "mobile": "mobile",
    "tests": "tests",
    "qa": "tests",
    "devops": "devops",
    "sre": "devops",
    "dba": "dba",
    "data": "dba",
    "security": "security",
    "ux": "ux",
    "design": "ux",
}

# Map GitHub issue state to task status
STATUS_MAP = {
    "open": "inbox",
    "in_progress": "in_progress",
    "review": "review",
    "closed": "done",
}


async def sync_tasks_from_github(session, repo: Optional[str] = None) -> None:
    """Sync tasks from GitHub issues to the database.

    Args:
        session: Database session
        repo: GitHub repo in format "owner/repo". If None, uses default from settings.
    """
    if not settings.github_token:
        logger.warning("[task_sync] No GitHub token configured, skipping task sync")
        return

    target_repo = repo or settings.github_default_repository
    if not target_repo:
        logger.warning(
            "[task_sync] No GitHub repository configured, skipping task sync"
        )
        return

    logger.info(f"[task_sync] Syncing tasks from GitHub repo: {target_repo}")

    try:
        import httpx

        async with httpx.AsyncClient() as client:
            # Fetch open issues
            headers = {"Authorization": f"token {settings.github_token}"}
            url = f"https://api.github.com/repos/{target_repo}/issues"
            params: dict[str, str | int] = {
                "state": "all",  # Get both open and closed
                "per_page": 100,
            }

            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()

            issues = response.json()
            logger.info(f"[task_sync] Found {len(issues)} issues in GitHub")

            for issue in issues:
                await _sync_issue_to_task(session, issue, target_repo)

            await session.commit()
            logger.info("[task_sync] Task sync completed")

    except Exception as e:
        logger.error(f"[task_sync] Failed to sync tasks from GitHub: {e}")
        raise


async def _sync_issue_to_task(session, issue: dict, repo: str) -> None:
    """Sync a single GitHub issue to a Task.

    Args:
        session: Database session
        issue: GitHub issue data
        repo: Repository name
    """
    issue_number = issue.get("number")
    if not issue_number:
        return

    # Check if task already exists
    result = await session.exec(
        select(Task).where(Task.github_issue_number == issue_number)
    )
    existing = result.first()

    # Extract task data from issue
    title = issue.get("title", "Untitled")
    description = issue.get("body", "")
    state = issue.get("state", "open")

    # Map status
    status = STATUS_MAP.get(state, "inbox")
    if state == "open":
        # Check labels for in_progress or review status
        labels = [label.get("name", "").lower() for label in issue.get("labels", [])]
        if "in-progress" in labels or "in_progress" in labels:
            status = "in_progress"
        elif "review" in labels:
            status = "review"

    # Map label
    task_label = None
    for gh_label, task_lbl in LABEL_MAP.items():
        if gh_label in [
            label.get("name", "").lower() for label in issue.get("labels", [])
        ]:
            task_label = task_lbl
            break

    # Try to find assigned agent
    assigned_agent_id = None
    assignee = issue.get("assignee")
    if assignee:
        assignee.get("login", "")
        # Try to match by GitHub username (would need to store github_username in Agent model)
        # For now, try to match by name in title/description
        agent_result = await session.exec(select(Agent))
        agents = agent_result.all()
        for agent in agents:
            if (
                agent.slug.lower() in title.lower()
                or agent.slug.lower() in description.lower()
            ):
                assigned_agent_id = agent.id
                break

    # Build GitHub URL
    issue_url = issue.get(
        "html_url", f"https://github.com/{repo}/issues/{issue_number}"
    )

    if existing:
        # Update existing task
        existing.title = title
        existing.description = description
        existing.status = status
        existing.label = task_label or existing.label
        existing.github_issue_url = issue_url
        existing.updated_at = datetime.now(UTC)
        if assigned_agent_id:
            existing.assigned_agent_id = assigned_agent_id
        logger.debug(f"[task_sync] Updated task for issue #{issue_number}")
    else:
        # Create new task
        new_task = Task(
            title=title,
            description=description,
            status=status,
            priority="medium",  # Default priority
            assigned_agent_id=assigned_agent_id,
            github_issue_number=issue_number,
            github_issue_url=issue_url,
            github_repo=repo,
            label=task_label,
        )
        session.add(new_task)
        logger.info(f"[task_sync] Created new task for issue #{issue_number}: {title}")


async def sync_tasks(db_session) -> None:
    """Main entry point for task synchronization.

    Syncs tasks from all configured repositories.
    """
    logger.info("[task_sync] Starting task synchronization")

    # Sync from default repo
    await sync_tasks_from_github(db_session)

    # Could add more repos here if needed
    # await sync_tasks_from_github(db_session, "owner/other-repo")

    logger.info("[task_sync] Task synchronization completed")
