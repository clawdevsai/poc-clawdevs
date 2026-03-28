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

from unittest.mock import AsyncMock, patch

import pytest
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import ActivityEvent, Agent, Task
from app.tasks import task_orchestration


class _SessionContext:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def __aenter__(self) -> AsyncSession:
        return self._session

    async def __aexit__(self, exc_type, exc, tb) -> bool:
        return False


def _session_factory(session: AsyncSession):
    return _SessionContext(session)


class TestTaskOrchestration:
    @pytest.mark.asyncio
    async def test_process_task_via_ceo_happy_path(self, db_session: AsyncSession):
        ceo = Agent(slug="ceo", display_name="CEO", role="ceo")
        backend = Agent(slug="backend", display_name="Backend", role="developer")
        db_session.add(ceo)
        db_session.add(backend)
        await db_session.commit()
        await db_session.refresh(ceo)
        await db_session.refresh(backend)

        task = Task(
            title="Implement endpoint",
            description="Create CRUD",
            assigned_agent_id=ceo.id,
            workflow_state="queued_to_ceo",
        )
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)

        with patch(
            "app.tasks.task_orchestration.AsyncSessionLocal",
            side_effect=lambda: _session_factory(db_session),
        ):
            with patch(
                "app.tasks.task_orchestration.openclaw_client.run_agent_turn",
                AsyncMock(
                    return_value='{"decision":"forward","target_agent_slug":"backend","summary":"encaminhar para backend"}'
                ),
            ):
                await task_orchestration._process_task_via_ceo(str(task.id))

        await db_session.refresh(task)
        assert task.assigned_agent_id == backend.id
        assert task.status == "in_progress"
        assert task.workflow_state == "forwarded_by_ceo"
        assert task.workflow_attempts == 1
        assert task.workflow_last_error is None

        result = await db_session.exec(
            select(ActivityEvent)
            .where(ActivityEvent.entity_type == "task")
            .where(ActivityEvent.entity_id == str(task.id))
        )
        event_types = {event.event_type for event in result.all()}
        assert "task.sent_to_ceo" in event_types
        assert "task.forwarded" in event_types
        assert "task.processing" in event_types

    @pytest.mark.asyncio
    async def test_process_task_via_ceo_retries_on_gateway_error(
        self, db_session: AsyncSession
    ):
        ceo = Agent(slug="ceo", display_name="CEO", role="ceo")
        backend = Agent(slug="backend", display_name="Backend", role="developer")
        db_session.add(ceo)
        db_session.add(backend)
        await db_session.commit()
        await db_session.refresh(ceo)

        task = Task(
            title="Task with failure",
            assigned_agent_id=ceo.id,
            workflow_state="queued_to_ceo",
        )
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)

        with patch(
            "app.tasks.task_orchestration.AsyncSessionLocal",
            side_effect=lambda: _session_factory(db_session),
        ):
            with patch(
                "app.tasks.task_orchestration.openclaw_client.run_agent_turn",
                AsyncMock(side_effect=RuntimeError("gateway timeout")),
            ):
                with pytest.raises(RuntimeError, match="gateway timeout"):
                    await task_orchestration._process_task_via_ceo(str(task.id))

        await db_session.refresh(task)
        assert task.workflow_state == "failed"
        assert task.workflow_attempts == 1
        assert "gateway timeout" in (task.workflow_last_error or "")

        result = await db_session.exec(
            select(ActivityEvent)
            .where(ActivityEvent.entity_type == "task")
            .where(ActivityEvent.entity_id == str(task.id))
        )
        event_types = {event.event_type for event in result.all()}
        assert "task.failed" in event_types

    @pytest.mark.asyncio
    async def test_process_task_via_ceo_with_invalid_target_slug(
        self, db_session: AsyncSession
    ):
        ceo = Agent(slug="ceo", display_name="CEO", role="ceo")
        backend = Agent(slug="backend", display_name="Backend", role="developer")
        db_session.add(ceo)
        db_session.add(backend)
        await db_session.commit()
        await db_session.refresh(ceo)

        task = Task(
            title="Task invalid route",
            assigned_agent_id=ceo.id,
            workflow_state="queued_to_ceo",
        )
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)

        with patch(
            "app.tasks.task_orchestration.AsyncSessionLocal",
            side_effect=lambda: _session_factory(db_session),
        ):
            with patch(
                "app.tasks.task_orchestration.openclaw_client.run_agent_turn",
                AsyncMock(
                    return_value='{"decision":"forward","target_agent_slug":"ghost","summary":"invalid"}'
                ),
            ):
                with pytest.raises(ValueError, match="Invalid target agent slug"):
                    await task_orchestration._process_task_via_ceo(str(task.id))

        await db_session.refresh(task)
        assert task.workflow_state == "failed"
        assert task.workflow_attempts == 1
        assert "Invalid target agent slug" in (task.workflow_last_error or "")
