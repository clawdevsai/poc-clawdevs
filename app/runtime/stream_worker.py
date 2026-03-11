#!/usr/bin/env python3
"""Loop generico para workers baseados em Redis Streams."""
from __future__ import annotations

import sys
import time
from typing import Any, Callable

from .agent_runtime import AgentResult, GatewayOutput, PreparedRun, RedisClient, StreamAgent
from .logging import log_error, log_event
from .run_context import RunContext

Sender = Callable[[str, str, int], tuple[bool, GatewayOutput]]


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
    )
    ok, output = sender(agent.session_key, instruction, ctx.policy.timeout_sec)
    if not ok:
        raise RuntimeError(str(output))
    result = agent.on_success(redis_client, ctx, output) or AgentResult()
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
    while True:
        try:
            reply = redis_client.xreadgroup(
                agent.consumer_group,
                agent.consumer_name,
                {agent.stream_name: ">"},
                block=agent.policy.block_ms,
                count=1,
            )
        except Exception as error:
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
