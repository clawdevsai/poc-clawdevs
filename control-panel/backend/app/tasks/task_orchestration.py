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
from app.services.openclaw_client import openclaw_client
from app.services.memory_lifecycle import compact_memory
from app.services.task_contracts import validate_contract
from app.services.task_workflow import (
    FINAL_WORKFLOW_STATES,
    WORKFLOW_COMPLETED,
    WORKFLOW_CONSOLIDATING,
    WORKFLOW_FAILED,
    WORKFLOW_FORWARDED_BY_CEO,
    WORKFLOW_PEER_REVIEW,
    WORKFLOW_PLANNING,
    WORKFLOW_PROCESSING_BY_CEO,
    WORKFLOW_SELF_REVIEW,
    WORKFLOW_EXECUTING,
    get_ceo_agent,
    log_task_event,
)

logger = logging.getLogger(__name__)
MAX_WORKFLOW_ATTEMPTS = 3


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

            if task.workflow_state in FINAL_WORKFLOW_STATES:
                logger.info(
                    "Task %s already processed with state=%s",
                    task_id,
                    task.workflow_state,
                )
                return

            ceo_agent = await get_ceo_agent(session)
            if ceo_agent is None:
                raise RuntimeError("Agent with slug 'ceo' was not found")

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

            await _run_task_pipeline(session, task, target_agent)
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
    raw_output = await _call_ceo_with_timeout(prompt)
    parsed = _parse_json_output(raw_output)

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


def _parse_json_output(raw_output: str) -> dict:
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


async def _call_ceo_with_timeout(prompt: str, timeout: float = 30.0) -> str:
    """Call CEO with timeout protection and fallback to default routing."""
    try:
        return await asyncio.wait_for(
            openclaw_client.run_agent_turn("ceo", prompt),
            timeout=timeout,
        )
    except asyncio.TimeoutError:
        logger.warning("CEO call timed out after %ss, using fallback routing", timeout)
        raise TimeoutError(f"CEO call timed out after {timeout}s")
    except Exception as exc:
        logger.exception("CEO call failed: %s", exc)
        raise


async def _run_loop_step(
    session, *, task: Task, agent_slug: str, contract_name: str, prompt: str
) -> dict:
    raw_output = await openclaw_client.run_agent_turn(agent_slug, prompt)
    parsed = _parse_json_output(raw_output)
    ok, validated, errors = validate_contract(contract_name, parsed)
    if not ok or validated is None:
        raise ValueError("; ".join(errors) if errors else "contract_validation_failed")
    return validated


async def _run_task_pipeline(session, task: Task, target_agent: Agent) -> None:
    if task.workflow_state in FINAL_WORKFLOW_STATES:
        return

    while task.workflow_attempts < MAX_WORKFLOW_ATTEMPTS:
        task.workflow_attempts += 1
        task.workflow_last_error = None
        await session.commit()

        try:
            task.workflow_state = WORKFLOW_PLANNING
            await log_task_event(
                session,
                task_id=task.id,
                event_type="task.planned",
                description="Task em planejamento",
                agent_id=target_agent.id,
                to_agent_slug=target_agent.slug,
                payload={"contract": "plan"},
            )
            await session.commit()

            plan_prompt = (
                f"Task id: {task.id}\\n"
                f"Task title: {task.title}\\n"
                f"Task description: {task.description or ''}\\n"
                "Return JSON only with keys: "
                "task_id, task_title, task_description, plan_steps, risk_notes."
            )
            plan_payload = await _run_loop_step(
                session,
                task=task,
                agent_slug=target_agent.slug,
                contract_name="plan",
                prompt=plan_prompt,
            )

            task.workflow_state = WORKFLOW_EXECUTING
            await log_task_event(
                session,
                task_id=task.id,
                event_type="task.executed",
                description="Task em execução",
                agent_id=target_agent.id,
                to_agent_slug=target_agent.slug,
                payload={"contract": "execute"},
            )
            await session.commit()

            execute_prompt = (
                f"Task id: {task.id}\\n"
                f"Plan steps: {plan_payload.get('plan_steps', [])}\\n"
                "Return JSON only with keys: "
                "task_id, plan_steps, actions, artifacts, evidence, errors."
            )
            execute_payload = await _run_loop_step(
                session,
                task=task,
                agent_slug=target_agent.slug,
                contract_name="execute",
                prompt=execute_prompt,
            )

            task.workflow_state = WORKFLOW_SELF_REVIEW
            await log_task_event(
                session,
                task_id=task.id,
                event_type="task.self_reviewed",
                description="Auto-revisão da task",
                agent_id=target_agent.id,
                to_agent_slug=target_agent.slug,
                payload={"contract": "self_review"},
            )
            await session.commit()

            self_review_prompt = (
                f"Task id: {task.id}\\n"
                f"Actions: {execute_payload.get('actions', [])}\\n"
                f"Evidence: {execute_payload.get('evidence', [])}\\n"
                "Return JSON only with keys: task_id, checks, issues, decision."
            )
            self_review_payload = await _run_loop_step(
                session,
                task=task,
                agent_slug=target_agent.slug,
                contract_name="self_review",
                prompt=self_review_prompt,
            )

            task.workflow_state = WORKFLOW_PEER_REVIEW
            await log_task_event(
                session,
                task_id=task.id,
                event_type="task.peer_reviewed",
                description="Revisão por pares da task",
                agent_id=target_agent.id,
                from_agent_slug=target_agent.slug,
                to_agent_slug="ceo",
                payload={"contract": "peer_review"},
            )
            await session.commit()

            peer_review_prompt = (
                f"Task id: {task.id}\\n"
                f"Self-review decision: {self_review_payload.get('decision')}\\n"
                f"Issues: {self_review_payload.get('issues', [])}\\n"
                "Return JSON only with keys: task_id, reviewer, issues, decision."
            )
            peer_review_payload = await _run_loop_step(
                session,
                task=task,
                agent_slug="ceo",
                contract_name="peer_review",
                prompt=peer_review_prompt,
            )

            task.workflow_state = WORKFLOW_CONSOLIDATING
            await log_task_event(
                session,
                task_id=task.id,
                event_type="task.consolidated",
                description="Consolidação da task",
                agent_id=target_agent.id,
                to_agent_slug=target_agent.slug,
                payload={"contract": "consolidate"},
            )
            await session.commit()

            consolidate_prompt = (
                f"Task id: {task.id}\\n"
                f"Peer review decision: {peer_review_payload.get('decision')}\\n"
                f"Issues: {peer_review_payload.get('issues', [])}\\n"
                "Return JSON only with keys: task_id, summary, artifacts, evidence, next_steps."
            )
            await _run_loop_step(
                session,
                task=task,
                agent_slug=target_agent.slug,
                contract_name="consolidate",
                prompt=consolidate_prompt,
            )

            try:
                await compact_memory(
                    agent_slug=target_agent.slug,
                    task_id=str(task.id),
                    reason="task_completed",
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("Memory compaction failed: %s", exc)

            task.status = "done"
            task.workflow_state = WORKFLOW_COMPLETED
            await session.commit()
            return
        except Exception as exc:  # noqa: BLE001
            task.workflow_last_error = str(exc)[:500]
            if task.workflow_attempts < MAX_WORKFLOW_ATTEMPTS:
                await log_task_event(
                    session,
                    task_id=task.id,
                    event_type="task.replan_requested",
                    description="Replanejamento solicitado após falha",
                    agent_id=target_agent.id,
                    to_agent_slug=target_agent.slug,
                    payload={"error": task.workflow_last_error},
                )
                await session.commit()
                continue

            task.workflow_state = WORKFLOW_FAILED
            await log_task_event(
                session,
                task_id=task.id,
                event_type="task.failed",
                description="Falha no pipeline determinístico",
                agent_id=target_agent.id,
                to_agent_slug=target_agent.slug,
                payload={"error": task.workflow_last_error},
            )
            await session.commit()
            return
