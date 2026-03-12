#!/usr/bin/env python3
"""Loop generico para workers baseados em Redis Streams."""
from __future__ import annotations

import os
import sys
import time
from typing import Any, Callable

from .agent_runtime import AgentResult, GatewayOutput, PreparedRun, RedisClient, StreamAgent
from .logging import log_error, log_event
from .openclaw_assets import render_openclaw_message
from .openclaw_output import inspect_openclaw_output
from .run_context import RunContext

Sender = Callable[[str, str, int], tuple[bool, GatewayOutput]]
PENDING_MIN_IDLE_MS = max(0, int(os.getenv("STREAM_PENDING_MIN_IDLE_MS", "30000")))
PENDING_CLAIM_COUNT = max(1, int(os.getenv("STREAM_PENDING_CLAIM_COUNT", "10")))


def payload_to_dict(data: Any) -> dict[str, Any]:
    if isinstance(data, dict):
        return {k: (v.decode() if isinstance(v, bytes) else v) for k, v in data.items()}
    if isinstance(data, (list, tuple)):
        out: dict[str, Any] = {}
        for index in range(0, len(data) - 1, 2):
            key = data[index]
            value = data[index + 1]
            if isinstance(key, bytes):
                key = key.decode()
            if isinstance(value, bytes):
                value = value.decode()
            out[str(key)] = value
        return out
    return {}


def process_stream_message(
    redis_client: RedisClient,
    agent: StreamAgent,
    sender: Sender,
    stream_name: str,
    message_id: str,
    raw_data: Any,
) -> AgentResult:
    event = payload_to_dict(raw_data or {})
    ctx = RunContext.from_message(
        stream_name=stream_name,
        message_id=message_id,
        event=event,
        policy=agent.policy,
    )
    log_event(
        "runtime.message_received",
        role=agent.role_name,
        stream=stream_name,
        message_id=message_id,
        run_id=ctx.run_id,
        trace_id=ctx.trace_id,
        issue_id=ctx.issue_id,
        attempt=ctx.attempt,
        event_type=ctx.event_type,
    )
    budget_result = _enforce_execution_budget(redis_client, agent, ctx)
    if budget_result is not None:
        redis_client.xack(agent.stream_name, agent.consumer_group, message_id)
        log_event(
            "runtime.budget_exceeded",
            role=agent.role_name,
            stream=stream_name,
            message_id=message_id,
            run_id=ctx.run_id,
            trace_id=ctx.trace_id,
            issue_id=ctx.issue_id,
            attempt=ctx.attempt,
            status_code=budget_result.status_code,
            event_name=budget_result.event_name,
            reason=budget_result.metadata.get("reason"),
        )
        if budget_result.summary:
            print(budget_result.summary)
        return budget_result
    prepared = _prepare_run(agent, redis_client, ctx)
    if not prepared.should_send:
        result = prepared.result or AgentResult(status="skipped", status_code="skipped", event_name="runtime.skipped")
        if prepared.ack_on_exit:
            redis_client.xack(agent.stream_name, agent.consumer_group, message_id)
        log_event(
            "runtime.message_skipped",
            role=agent.role_name,
            stream=stream_name,
            message_id=message_id,
            run_id=ctx.run_id,
            trace_id=ctx.trace_id,
            issue_id=ctx.issue_id,
            attempt=ctx.attempt,
            status=result.status,
            status_code=result.status_code,
            event_name=result.event_name,
        )
        if result.summary:
            print(result.summary)
        return result
    instruction = prepared.instruction or agent.build_instruction(redis_client, ctx)
    allowed_tools = tuple(getattr(sender, "allowed_tools", ()))
    instruction = render_openclaw_message(agent.role_name, instruction, allowed_tools=allowed_tools)
    log_event(
        "runtime.message_dispatching",
        role=agent.role_name,
        stream=stream_name,
        message_id=message_id,
        run_id=ctx.run_id,
        trace_id=ctx.trace_id,
        issue_id=ctx.issue_id,
        attempt=ctx.attempt,
        timeout_sec=ctx.policy.timeout_sec,
        openclaw_context_applied=True,
        allowed_tools=list(allowed_tools),
    )
    ok, output = sender(agent.session_key, instruction, ctx.policy.timeout_sec)
    if not ok:
        raise RuntimeError(str(output))
    output_inspection = _inspect_output_if_available(agent, ctx, output)
    log_event(
        "runtime.openclaw_output_inspected",
        role=agent.role_name,
        stream=stream_name,
        message_id=message_id,
        run_id=ctx.run_id,
        trace_id=ctx.trace_id,
        schema=output_inspection["schema"],
        valid=output_inspection["valid"],
        missing_fields=list(output_inspection["missing_fields"]),
    )
    result = agent.on_success(redis_client, ctx, output) or AgentResult()
    if output_inspection["checked"] and not output_inspection["valid"]:
        from app.core.orchestration import record_invalid_output

        record_invalid_output(
            redis_client,
            role_name=agent.role_name,
            issue_id=ctx.issue_id,
            schema=output_inspection.get("schema"),
            missing_fields=list(output_inspection.get("missing_fields") or ()),
        )
        result = _mark_invalid_openclaw_output(result, output_inspection)
    redis_client.xack(agent.stream_name, agent.consumer_group, message_id)
    log_event(
        "runtime.message_completed",
        role=agent.role_name,
        stream=stream_name,
        message_id=message_id,
        run_id=ctx.run_id,
        trace_id=ctx.trace_id,
        issue_id=ctx.issue_id,
        attempt=ctx.attempt,
        status=result.status,
        status_code=result.status_code,
        event_name=result.event_name,
        output_schema=output_inspection["schema"],
        output_valid=output_inspection["valid"],
        elapsed_runtime_sec=round(ctx.elapsed_runtime_sec, 6),
    )
    if result.summary:
        print(result.summary)
    return result


def _prepare_run(agent: StreamAgent, redis_client: RedisClient, ctx: RunContext) -> PreparedRun:
    prepared = agent.prepare(redis_client, ctx)
    if isinstance(prepared, PreparedRun):
        return prepared
    if prepared is None:
        return PreparedRun()
    raise TypeError(f"{agent.role_name}.prepare() deve retornar PreparedRun ou None")


def _mark_invalid_openclaw_output(result: AgentResult, inspection: dict[str, Any]) -> AgentResult:
    metadata = dict(result.metadata)
    metadata["output_schema"] = inspection.get("schema")
    metadata["output_valid"] = False
    metadata["missing_fields"] = list(inspection.get("missing_fields") or ())
    return AgentResult(
        status="invalid_output",
        status_code="openclaw_invalid_output",
        event_name="runtime.openclaw_invalid_output",
        summary=result.summary or "Saida do OpenClaw fora do schema esperado",
        metadata=metadata,
    )


def _inspect_output_if_available(agent: StreamAgent, ctx: RunContext, output: GatewayOutput) -> dict[str, Any]:
    if ctx.policy.timeout_sec <= 0:
        return {
            "schema": None,
            "valid": True,
            "missing_fields": (),
            "checked": False,
        }
    inspection = inspect_openclaw_output(agent.role_name, output)
    inspection["checked"] = True
    return inspection


def _enforce_execution_budget(
    redis_client: RedisClient,
    agent: StreamAgent,
    ctx: RunContext,
) -> AgentResult | None:
    if ctx.exceeded_attempt_budget():
        return AgentResult(
            status="budget_exceeded",
            status_code="budget_max_attempts",
            event_name="runtime.budget_max_attempts",
            summary=(
                f"[{agent.role_name}] Budget excedido para {ctx.message_id}: "
                f"attempt={ctx.attempt} max_attempts={ctx.policy.max_attempts}"
            ),
            metadata={"run_id": ctx.run_id, "reason": "max_attempts"},
        )
    if ctx.exceeded_runtime_budget():
        return AgentResult(
            status="budget_exceeded",
            status_code="budget_max_runtime",
            event_name="runtime.budget_max_runtime",
            summary=(
                f"[{agent.role_name}] Budget excedido para {ctx.message_id}: "
                f"elapsed={ctx.elapsed_runtime_sec:.2f}s max_runtime_sec={ctx.policy.max_runtime_sec}"
            ),
            metadata={"run_id": ctx.run_id, "reason": "max_runtime_sec"},
        )
    return None


def run_stream_worker(
    redis_client: RedisClient,
    agent: StreamAgent,
    sender: Sender,
) -> None:
    print(
        f"[{agent.role_name}] Consumindo stream={agent.stream_name} "
        f"group={agent.consumer_group} consumer={agent.consumer_name} (runtime-v1)"
    )
    log_event(
        "runtime.worker_started",
        role=agent.role_name,
        stream=agent.stream_name,
        consumer_group=agent.consumer_group,
        consumer_name=agent.consumer_name,
    )
    _ensure_consumer_group(redis_client, agent)
    pending_start_id = "0-0"
    while True:
        pending_start_id, pending_messages = _claim_pending_messages(
            redis_client,
            agent,
            start_id=pending_start_id,
            min_idle_ms=PENDING_MIN_IDLE_MS,
            count=PENDING_CLAIM_COUNT,
        )
        if pending_messages:
            for normalized_id, raw_data in pending_messages:
                try:
                    process_stream_message(
                        redis_client,
                        agent,
                        sender,
                        agent.stream_name,
                        normalized_id,
                        raw_data,
                    )
                except Exception as error:
                    ctx = None
                    try:
                        ctx = RunContext.from_message(
                            stream_name=agent.stream_name,
                            message_id=normalized_id,
                            event=payload_to_dict(raw_data or {}),
                            policy=agent.policy,
                        )
                    except Exception:
                        pass
                    log_error(
                        "runtime.pending_message_error",
                        role=agent.role_name,
                        stream=agent.stream_name,
                        message_id=normalized_id,
                        run_id=ctx.run_id if ctx else None,
                        trace_id=ctx.trace_id if ctx else None,
                        issue_id=ctx.issue_id if ctx else None,
                        error=str(error),
                    )
                    agent.on_error(redis_client, ctx, error)
            continue
        try:
            reply = redis_client.xreadgroup(
                agent.consumer_group,
                agent.consumer_name,
                {agent.stream_name: ">"},
                block=agent.policy.block_ms,
                count=1,
            )
        except Exception as error:
            if "NOGROUP" in str(error):
                try:
                    _ensure_consumer_group(redis_client, agent)
                except Exception as ensure_error:
                    log_error(
                        "runtime.consumer_group_recreate_error",
                        role=agent.role_name,
                        stream=agent.stream_name,
                        consumer_group=agent.consumer_group,
                        error=str(ensure_error),
                    )
            log_error(
                "runtime.xreadgroup_error",
                role=agent.role_name,
                stream=agent.stream_name,
                consumer_group=agent.consumer_group,
                consumer_name=agent.consumer_name,
                error=str(error),
            )
            print(f"[{agent.role_name}] Erro XREADGROUP: {error}", file=sys.stderr)
            time.sleep(5)
            continue
        if not reply:
            continue
        for stream_name, messages in reply:
            normalized_stream = stream_name if isinstance(stream_name, str) else stream_name.decode()
            for message_id, raw_data in messages:
                normalized_id = message_id if isinstance(message_id, str) else message_id.decode()
                try:
                    process_stream_message(
                        redis_client,
                        agent,
                        sender,
                        normalized_stream,
                        normalized_id,
                        raw_data,
                    )
                except Exception as error:
                    ctx = None
                    try:
                        ctx = RunContext.from_message(
                            stream_name=normalized_stream,
                            message_id=normalized_id,
                            event=payload_to_dict(raw_data or {}),
                            policy=agent.policy,
                        )
                    except Exception:
                        pass
                    log_error(
                        "runtime.message_error",
                        role=agent.role_name,
                        stream=normalized_stream,
                        message_id=normalized_id,
                        run_id=ctx.run_id if ctx else None,
                        trace_id=ctx.trace_id if ctx else None,
                        issue_id=ctx.issue_id if ctx else None,
                        error=str(error),
                    )
                    agent.on_error(redis_client, ctx, error)


def _claim_pending_messages(
    redis_client: RedisClient,
    agent: StreamAgent,
    *,
    start_id: str,
    min_idle_ms: int,
    count: int,
) -> tuple[str, list[tuple[str, Any]]]:
    if min_idle_ms <= 0 or count <= 0:
        return start_id, []
    try:
        claim_result = redis_client.xautoclaim(
            agent.stream_name,
            agent.consumer_group,
            agent.consumer_name,
            min_idle_ms,
            start_id=start_id,
            count=count,
        )
    except AttributeError:
        return start_id, []
    except Exception as error:
        message = str(error).lower()
        if "unknown command" in message or "xautoclaim" in message:
            return start_id, []
        log_error(
            "runtime.xautoclaim_error",
            role=agent.role_name,
            stream=agent.stream_name,
            consumer_group=agent.consumer_group,
            consumer_name=agent.consumer_name,
            error=str(error),
        )
        return start_id, []

    if not claim_result:
        return start_id, []

    next_start = claim_result[0] if len(claim_result) > 0 else start_id
    raw_messages = claim_result[1] if len(claim_result) > 1 else []
    normalized_next = (
        next_start.decode("utf-8", errors="replace") if isinstance(next_start, bytes) else str(next_start or start_id)
    )
    normalized_messages: list[tuple[str, Any]] = []
    for message_id, raw_data in raw_messages or []:
        normalized_id = message_id.decode("utf-8", errors="replace") if isinstance(message_id, bytes) else str(message_id)
        normalized_messages.append((normalized_id, raw_data))
    return normalized_next, normalized_messages


def _ensure_consumer_group(redis_client: RedisClient, agent: StreamAgent) -> None:
    try:
        redis_client.xgroup_create(
            name=agent.stream_name,
            groupname=agent.consumer_group,
            id="0",
            mkstream=True,
        )
        log_event(
            "runtime.consumer_group_created",
            role=agent.role_name,
            stream=agent.stream_name,
            consumer_group=agent.consumer_group,
        )
    except Exception as error:
        if "BUSYGROUP" in str(error):
            return
        raise
