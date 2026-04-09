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

"""
Failure Detection & Self-Healing Service

Monitors task failures and automatically escalates to senior agents
when thresholds are met. Implements exponential backoff retry logic
and domain-specific escalation routing.
"""

import logging
from datetime import datetime, timedelta, UTC
from typing import Optional
from uuid import UUID

from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.task import Task
from app.models.agent import Agent
from app.models.activity_event import ActivityEvent
from app.models.constants import get_escalation_agent

logger = logging.getLogger(__name__)

# Senior escalation agents (can handle escalations)
SENIOR_AGENTS = {
    "arquiteto": {"can_escalate": True, "max_escalations": 10, "fallback_to": "ceo"},
    "ceo": {"can_escalate": True, "max_escalations": 5, "fallback_to": None},
}


class FailureDetector:
    """Detects and responds to repeated task failures."""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.failure_threshold = 3  # Escalate after 3 consecutive failures
        self.backoff_base = 1.5  # Exponential backoff multiplier

    async def record_failure(
        self,
        task_id: UUID,
        error_message: str,
        error_type: str = "execution_error",
    ) -> None:
        """Record a failure and check if escalation is needed."""
        task = (
            await self.db_session.exec(select(Task).where(Task.id == task_id))
        ).first()
        if not task:
            logger.warning(f"Task {task_id} not found for failure recording")
            return

        # Update failure tracking
        task.failure_count += 1
        task.consecutive_failures += 1
        task.last_error = error_message
        task.error_reason = error_type
        task.last_failed_at = datetime.now(UTC).replace(tzinfo=None)
        task.updated_at = datetime.now(UTC).replace(tzinfo=None)

        # Create activity event for failure
        await self._create_failure_event(task_id, error_type, error_message)

        logger.info(
            f"Task {task_id} failed (attempt {task.failure_count}): {error_type}"
        )

        # Check if escalation is needed
        if task.consecutive_failures >= self.failure_threshold:
            await self.escalate_task(task_id, error_type, error_message)

        self.db_session.add(task)
        await self.db_session.commit()

    async def escalate_task(
        self,
        task_id: UUID,
        error_type: str,
        error_message: str,
    ) -> None:
        """Escalate a failed task to appropriate senior agent."""
        task = (
            await self.db_session.exec(select(Task).where(Task.id == task_id))
        ).first()
        if not task:
            logger.warning(f"Cannot escalate: task {task_id} not found")
            return

        if task.escalated_to_agent_id:
            logger.info(
                f"Task {task_id} already escalated, skipping duplicate escalation"
            )
            return

        # Determine escalation target based on task label
        escalation_agent_slug = self._get_escalation_target(task.label)

        # Find the escalation agent
        escalation_agent = (
            await self.db_session.exec(
                select(Agent).where(Agent.slug == escalation_agent_slug)
            )
        ).first()

        if not escalation_agent:
            # Fallback to Arquiteto if domain-specific agent not found
            escalation_agent = (
                await self.db_session.exec(
                    select(Agent).where(Agent.slug == "arquiteto")
                )
            ).first()

        if not escalation_agent:
            logger.error("No escalation agent available (Arquiteto not found)")
            return

        # Check if agent can handle escalations
        if not escalation_agent.can_escalate:
            logger.warning(
                f"Agent {escalation_agent_slug} cannot escalate. "
                "Using fallback agent (Arquiteto)"
            )
            escalation_agent = (
                await self.db_session.exec(
                    select(Agent).where(Agent.slug == "arquiteto")
                )
            ).first()

        if escalation_agent and escalation_agent.can_escalate:
            # Check escalation limit
            if (
                escalation_agent.max_escalations > 0
                and escalation_agent.escalations_handled
                >= escalation_agent.max_escalations
            ):
                logger.warning(
                    f"Agent {escalation_agent.slug} has reached max escalations. "
                    "Cannot escalate further."
                )
                return

            # Perform escalation
            task.escalated_to_agent_id = escalation_agent.id
            task.escalation_reason = (
                f"Failed {task.consecutive_failures}x: {error_type}"
            )
            task.escalated_at = datetime.now(UTC).replace(tzinfo=None)
            escalation_agent.escalations_handled += 1

            await self._create_escalation_event(
                task_id,
                escalation_agent.id,
                task.escalation_reason,
            )

            logger.info(
                f"Task {task_id} escalated to {escalation_agent.slug} "
                f"(reason: {error_type})"
            )

            self.db_session.add(task)
            self.db_session.add(escalation_agent)
            await self.db_session.commit()

    async def apply_exponential_backoff(self, task_id: UUID, attempt: int) -> timedelta:
        """Calculate exponential backoff for retry."""
        delay_seconds = int(self.backoff_base ** (attempt - 1))
        # Cap at 5 minutes
        delay_seconds = min(delay_seconds, 300)
        return timedelta(seconds=delay_seconds)

    async def reset_consecutive_failures(self, task_id: UUID) -> None:
        """Reset consecutive failure count on successful execution."""
        task = (
            await self.db_session.exec(select(Task).where(Task.id == task_id))
        ).first()
        if task:
            task.consecutive_failures = 0
            task.updated_at = datetime.now(UTC).replace(tzinfo=None)
            self.db_session.add(task)
            await self.db_session.commit()
            logger.info(f"Reset consecutive failures for task {task_id}")

    def _get_escalation_target(self, label: Optional[str]) -> str:
        """Get domain-specific escalation agent."""
        if label:
            return get_escalation_agent(label)
        return "arquiteto"  # Default fallback

    async def _create_failure_event(
        self,
        task_id: UUID,
        error_type: str,
        error_message: str,
    ) -> None:
        """Create activity event for task failure."""
        event = ActivityEvent(
            event_type="task_failed",
            entity_type="task",
            entity_id=str(task_id),
            payload={
                "error_type": error_type,
                "error_message": error_message,
                "timestamp": datetime.now(UTC).replace(tzinfo=None).isoformat(),
            },
        )
        self.db_session.add(event)
        await self.db_session.commit()

    async def _create_escalation_event(
        self,
        task_id: UUID,
        agent_id: UUID,
        reason: str,
    ) -> None:
        """Create activity event for escalation."""
        event = ActivityEvent(
            event_type="task_escalated",
            entity_type="task",
            entity_id=str(task_id),
            payload={
                "escalated_to_agent_id": str(agent_id),
                "reason": reason,
                "timestamp": datetime.now(UTC).replace(tzinfo=None).isoformat(),
            },
        )
        self.db_session.add(event)
        await self.db_session.commit()

    async def get_task_health(self, task_id: UUID) -> dict:
        """Get health status of a task."""
        task = (
            await self.db_session.exec(select(Task).where(Task.id == task_id))
        ).first()
        if not task:
            return {"status": "unknown", "message": "Task not found"}

        health_status = "healthy"
        if task.consecutive_failures >= self.failure_threshold:
            health_status = "failed"
        elif task.consecutive_failures > 0:
            health_status = "unhealthy"

        return {
            "task_id": str(task_id),
            "status": health_status,
            "failure_count": task.failure_count,
            "consecutive_failures": task.consecutive_failures,
            "last_error": task.last_error,
            "last_failed_at": (
                task.last_failed_at.isoformat() if task.last_failed_at else None
            ),
            "escalated_to_agent_id": (
                str(task.escalated_to_agent_id) if task.escalated_to_agent_id else None
            ),
            "escalation_reason": task.escalation_reason,
        }

    async def get_failure_detail(self, task_id: UUID) -> dict | None:
        """Get latest failure detail for a task."""
        task = (
            await self.db_session.exec(select(Task).where(Task.id == task_id))
        ).first()
        if not task:
            return None

        event = (
            await self.db_session.exec(
                select(ActivityEvent)
                .where(ActivityEvent.entity_type == "task")
                .where(ActivityEvent.entity_id == str(task_id))
                .where(col(ActivityEvent.event_type).in_(["task_failed", "task.failed"]))
                .order_by(col(ActivityEvent.created_at).desc())
            )
        ).first()

        message = task.last_error
        stack_trace = None
        evidence: list[str] = []
        if event and isinstance(event.payload, dict):
            payload = event.payload
            message = (
                payload.get("error_message")
                or payload.get("message")
                or message
            )
            stack_trace = payload.get("stack_trace") or payload.get("trace")
            raw_evidence = payload.get("evidence") or payload.get("artifacts")
            if isinstance(raw_evidence, list):
                evidence = [str(item) for item in raw_evidence]
            elif isinstance(raw_evidence, str):
                evidence = [raw_evidence]

        return {
            "message": message,
            "stack_trace": stack_trace,
            "evidence": evidence,
        }
