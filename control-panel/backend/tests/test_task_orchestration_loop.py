import json

import pytest
from sqlmodel import select

from app.models import ActivityEvent, Agent, Task
from app.tasks import task_orchestration


@pytest.mark.asyncio
async def test_task_pipeline_completes(db_session, monkeypatch):
    responses = [
        {"task_id": "1", "task_title": "t", "task_description": "d", "plan_steps": ["s"], "risk_notes": []},
        {"task_id": "1", "plan_steps": ["s"], "actions": ["a"], "artifacts": [], "evidence": [], "errors": []},
        {"task_id": "1", "checks": ["c"], "issues": [], "decision": "pass"},
        {"task_id": "1", "reviewer": "ceo", "issues": [], "decision": "pass"},
        {"task_id": "1", "summary": "sum", "artifacts": [], "evidence": [], "next_steps": []},
    ]

    async def fake_run_agent_turn(agent_slug, message, session_key=None, timeout=60.0):
        return json.dumps(responses.pop(0))

    monkeypatch.setattr(task_orchestration.openclaw_client, "run_agent_turn", fake_run_agent_turn)

    agent = Agent(slug="builder", display_name="Builder", role="executor")
    db_session.add(agent)
    await db_session.commit()
    await db_session.refresh(agent)

    task = Task(title="Test", description="desc")
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    await task_orchestration._run_task_pipeline(db_session, task, agent)

    assert task.workflow_state == task_orchestration.WORKFLOW_COMPLETED
    assert task.status == "done"


@pytest.mark.asyncio
async def test_invalid_contract_triggers_replan(db_session, monkeypatch):
    responses = [
        "{invalid-json}",
        {"task_id": "1", "task_title": "t", "task_description": "d", "plan_steps": ["s"], "risk_notes": []},
        {"task_id": "1", "plan_steps": ["s"], "actions": ["a"], "artifacts": [], "evidence": [], "errors": []},
        {"task_id": "1", "checks": ["c"], "issues": [], "decision": "pass"},
        {"task_id": "1", "reviewer": "ceo", "issues": [], "decision": "pass"},
        {"task_id": "1", "summary": "sum", "artifacts": [], "evidence": [], "next_steps": []},
    ]

    async def fake_run_agent_turn(agent_slug, message, session_key=None, timeout=60.0):
        value = responses.pop(0)
        if isinstance(value, str):
            return value
        return json.dumps(value)

    monkeypatch.setattr(task_orchestration.openclaw_client, "run_agent_turn", fake_run_agent_turn)

    agent = Agent(slug="builder", display_name="Builder", role="executor")
    db_session.add(agent)
    await db_session.commit()
    await db_session.refresh(agent)

    task = Task(title="Test", description="desc")
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    await task_orchestration._run_task_pipeline(db_session, task, agent)

    assert task.workflow_attempts == 2

    result = await db_session.exec(
        select(ActivityEvent).where(ActivityEvent.event_type == "task.replan_requested")
    )
    assert result.first() is not None
