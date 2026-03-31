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
import json
import logging
from uuid import UUID

from sqlmodel import select

from app.core.database import AsyncSessionLocal
from app.models import Agent, Task
from app.services.llm_runtime_client import llm_runtime_client as openclaw_client
from app.services.task_workflow import (
    WORKFLOW_COMPLETED,
    WORKFLOW_FAILED,
    WORKFLOW_FORWARDED_BY_CEO,
    WORKFLOW_PROCESSING_BY_CEO,
    get_ceo_agent,
    log_task_event,
)

logger = logging.getLogger(__name__)


def process_task_via_ceo(task_id: str) -> None:
    """RQ job entrypoint for CEO task orchestration."""
    asyncio.run(_process_task_via_ceo(task_id))


async def _process_task_via_ceo(task_id: str) -> None:
    task_uuid = UUID(task_id)
    try:
        async with AsyncSessionLocal() as session:
            task = await session.get(Task, task_uuid)
            if task is None:
                logger.warning("Task %s not found for orchestration", task_id)
                return

            if task.workflow_state in {WORKFLOW_COMPLETED, WORKFLOW_FORWARDED_BY_CEO}:
                logger.info(
                    "Task %s already processed with state=%s",
                    task_id,
                    task.workflow_state,
                )
                return

            ceo_agent = await get_ceo_agent(session)
            if ceo_agent is None:
                raise RuntimeError("Agent with slug 'ceo' was not found")

            task.workflow_attempts += 1
            task.workflow_state = WORKFLOW_PROCESSING_BY_CEO
            task.workflow_last_error = None
            await log_task_event(
                session,
                task_id=task.id,
                event_type="task.sent_to_ceo",
                description=f"Task enviada para o CEO (tentativa {task.workflow_attempts})",
                agent_id=ceo_agent.id,
                to_agent_slug="ceo",
            )
            await session.commit()

            target_agent, summary = await _ask_ceo_for_routing(session, task)

            from_slug = "ceo"
            to_slug = target_agent.slug
            task.assigned_agent_id = target_agent.id
            task.status = "in_progress"
            task.workflow_state = WORKFLOW_FORWARDED_BY_CEO
            task.workflow_last_error = None

            await log_task_event(
                session,
                task_id=task.id,
                event_type="task.forwarded",
                description=f"CEO encaminhou para {to_slug}",
                agent_id=ceo_agent.id,
                from_agent_slug=from_slug,
                to_agent_slug=to_slug,
                payload={"summary": summary},
            )
            await log_task_event(
                session,
                task_id=task.id,
                event_type="task.processing",
                description=f"Task em processamento por {to_slug}",
                agent_id=target_agent.id,
                to_agent_slug=to_slug,
            )
            await session.commit()
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to process task workflow for task=%s", task_id)
        await _mark_task_failed(task_uuid, str(exc))
        raise


async def _mark_task_failed(task_id: UUID, error_message: str) -> None:
    async with AsyncSessionLocal() as session:
        task = await session.get(Task, task_id)
        if task is None:
            return

        task.workflow_state = WORKFLOW_FAILED
        task.workflow_last_error = error_message[:500]
        await log_task_event(
            session,
            task_id=task.id,
            event_type="task.failed",
            description="Falha ao processar encaminhamento com CEO",
            agent_id=task.assigned_agent_id,
            to_agent_slug="ceo",
            payload={"error": task.workflow_last_error},
        )
        await session.commit()


async def _ask_ceo_for_routing(session, task: Task) -> tuple[Agent, str]:
    agents_result = await session.exec(select(Agent).order_by(Agent.slug))
    all_agents = agents_result.all()
    allowed_targets = [a for a in all_agents if a.slug != "ceo"]
    if not allowed_targets:
        raise RuntimeError("No target agents available for CEO routing")

    allowed_slugs = [a.slug for a in allowed_targets]
    prompt = (
        "Voce eh o CEO de orquestracao de tarefas.\n"
        "Responda APENAS JSON valido com o formato:\n"
        '{"decision":"forward","target_agent_slug":"<slug>","summary":"<texto curto>"}\n'
        f"Agentes validos: {', '.join(allowed_slugs)}\n"
        f"Task title: {task.title}\n"
        f"Task label: {task.label or 'none'}\n"
        f"Task description: {task.description or ''}\n"
        "Escolha o melhor agente para executar a task."
    )
    raw_output = await openclaw_client.run_agent_turn("ceo", prompt)
    parsed = _parse_ceo_json(raw_output)

    decision = str(parsed.get("decision", "")).strip().lower()
    if decision != "forward":
        raise ValueError(f"Unsupported CEO decision: {decision}")

    target_slug = str(parsed.get("target_agent_slug", "")).strip()
    if target_slug not in allowed_slugs:
        raise ValueError(f"Invalid target agent slug from CEO: {target_slug}")

    summary = str(parsed.get("summary", "")).strip() or "Encaminhamento realizado"
    for agent in allowed_targets:
        if agent.slug == target_slug:
            return agent, summary

    raise ValueError(f"Target agent not found: {target_slug}")


def _parse_ceo_json(raw_output: str) -> dict:
    content = raw_output.strip()
    try:
        parsed = json.loads(content)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    start = content.find("{")
    end = content.rfind("}")
    if start == -1 or end <= start:
        raise ValueError("CEO output is not valid JSON")
    parsed = json.loads(content[start : end + 1])
    if not isinstance(parsed, dict):
        raise ValueError("CEO output JSON is not an object")
    return parsed
