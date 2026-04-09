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

from __future__ import annotations

import asyncio
import logging
from typing import Any
from uuid import UUID

from redis import Redis
from rq import Queue, Retry
from sqlmodel import select

from app.core.config import get_settings
from app.core.database import AsyncSessionLocal
from app.models import ActivityEvent, Agent, Task
from app.services.parallelism_gate import evaluate_parallelism_gate

logger = logging.getLogger(__name__)
settings = get_settings()

WORKFLOW_QUEUED_TO_CEO = "queued_to_ceo"
WORKFLOW_PROCESSING_BY_CEO = "processing_by_ceo"
WORKFLOW_FORWARDED_BY_CEO = "forwarded_by_ceo"
WORKFLOW_PLANNING = "planning"
WORKFLOW_EXECUTING = "executing"
WORKFLOW_SELF_REVIEW = "self_review"
WORKFLOW_PEER_REVIEW = "peer_review"
WORKFLOW_CONSOLIDATING = "consolidating"
WORKFLOW_FAILED = "failed"
WORKFLOW_COMPLETED = "completed"

FINAL_WORKFLOW_STATES = {WORKFLOW_COMPLETED, WORKFLOW_FAILED}
NON_ENQUEUEABLE_STATES = FINAL_WORKFLOW_STATES | {WORKFLOW_PROCESSING_BY_CEO}


async def get_agent_slug_map(session, agent_ids: set[UUID]) -> dict[str, str]:
    if not agent_ids:
        return {}
    result = await session.exec(select(Agent).where(Agent.id.in_(agent_ids)))
    return {str(agent.id): agent.slug for agent in result.all()}


async def get_ceo_agent(session) -> Agent | None:
    result = await session.exec(select(Agent).where(Agent.slug == "ceo"))
    return result.first()


def should_enqueue_task(task: Task) -> bool:
    if task.workflow_state in NON_ENQUEUEABLE_STATES:
        return False
    return True


def task_workflow_job_id(task_id: UUID | str) -> str:
    return f"task-workflow:{task_id}"


def enqueue_task_for_ceo(task_id: UUID) -> tuple[bool, str | None]:
    job_id = task_workflow_job_id(task_id)
    try:
        async def _check_gate() -> tuple[bool, str]:
            async with AsyncSessionLocal() as session:
                result = await session.exec(
                    select(Task).where(Task.status == "in_progress")
                )
                in_progress_count = len(result.all())
                allowed, reason = await evaluate_parallelism_gate(
                    session, in_progress_count
                )
                if not allowed:
                    await log_task_event(
                        session,
                        task_id=task_id,
                        event_type="task.parallelism_blocked",
                        description="Parallelismo bloqueado pelo gate",
                        payload={
                            "reason": reason,
                            "in_progress_count": in_progress_count,
                        },
                    )
                await session.commit()
                return allowed, reason

        allowed, reason = asyncio.run(_check_gate())
        if not allowed:
            return False, reason

        redis_conn = Redis.from_url(settings.redis_url)
        queue = Queue("default", connection=redis_conn)

        existing = queue.fetch_job(job_id)
        if existing and existing.get_status(refresh=True) in {
            "queued",
            "started",
            "scheduled",
            "deferred",
        }:
            return True, None

        queue.enqueue(
            "app.tasks.task_orchestration.process_task_via_ceo",
            str(task_id),
            job_id=job_id,
            retry=Retry(max=3, interval=[30, 120, 300]),
            result_ttl=0,
            failure_ttl=86400,
        )
        return True, None
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to enqueue task workflow for %s: %s", task_id, exc)
        return False, str(exc)


async def log_task_event(
    session,
    *,
    task_id: UUID,
    event_type: str,
    description: str,
    agent_id: UUID | None = None,
    from_agent_slug: str | None = None,
    to_agent_slug: str | None = None,
    payload: dict[str, Any] | None = None,
) -> ActivityEvent:
    event_payload: dict[str, Any] = {"description": description}
    if from_agent_slug:
        event_payload["from_agent_slug"] = from_agent_slug
    if to_agent_slug:
        event_payload["to_agent_slug"] = to_agent_slug
    if payload:
        event_payload.update(payload)

    event = ActivityEvent(
        event_type=event_type,
        agent_id=agent_id,
        entity_type="task",
        entity_id=str(task_id),
        payload=event_payload,
    )
    session.add(event)
    return event
