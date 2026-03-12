#!/usr/bin/env python3
"""Cliente minimo para envio de mensagens ao OpenClaw Gateway via CLI."""
from __future__ import annotations

import json
import os
import subprocess
from uuid import uuid4

from .agent_runtime import GatewayOutput
from .openclaw_session import OpenClawSessionConfig

TOOL_OPENCLAW_SESSIONS_SEND = "openclaw.sessions.send"

OPENCLAW_CLI = os.getenv("OPENCLAW_CLI_PATH", "openclaw")
GATEWAY_WS = (os.getenv("OPENCLAW_GATEWAY_WS") or "").strip().rstrip("/")
GATEWAY_TOKEN = (os.getenv("OPENCLAW_GATEWAY_TOKEN") or "").strip() or None


def gateway_call(
    method: str,
    params: dict,
    timeout_sec: int = 60,
    *,
    expect_final: bool = False,
    call_timeout_ms: int | None = None,
) -> tuple[bool, GatewayOutput]:
    if not GATEWAY_WS:
        return False, "OPENCLAW_GATEWAY_WS nao definido"
    params_json = json.dumps(params, ensure_ascii=False)
    cmd = [
        OPENCLAW_CLI,
        "gateway",
        "call",
        method,
        "--url",
        GATEWAY_WS,
        "--params",
        params_json,
        "--json",
    ]
    if expect_final:
        cmd.append("--expect-final")
    if call_timeout_ms is not None and call_timeout_ms > 0:
        cmd.extend(["--timeout", str(int(call_timeout_ms))])
    if GATEWAY_TOKEN:
        cmd.extend(["--token", GATEWAY_TOKEN])
    try:
        out = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_sec + 10,
            env=os.environ,
        )
        if out.returncode != 0:
            return False, (out.stderr or out.stdout or "unknown error").strip()
        if not (out.stdout or "").strip():
            return True, {}
        try:
            return True, json.loads(out.stdout)
        except json.JSONDecodeError:
            return True, {"raw": out.stdout.strip()}
    except FileNotFoundError:
        return False, f"openclaw CLI nao encontrado (PATH ou OPENCLAW_CLI_PATH={OPENCLAW_CLI})"
    except subprocess.TimeoutExpired:
        return False, "timeout"
    except Exception as error:
        return False, str(error)


def send_to_session(
    session_key: str,
    message: str,
    timeout_sec: int = 0,
    session_config: OpenClawSessionConfig | None = None,
) -> tuple[bool, GatewayOutput]:
    # OpenClaw 2026.x moved session send to the "agent" gateway method.
    # Keep the runtime contract stable and adapt here.
    params = {
        "sessionKey": session_key,
        "message": message,
        "deliver": False,
        "idempotencyKey": str(uuid4()),
    }
    expect_final = timeout_sec > 0
    call_timeout_ms = max(1000, timeout_sec * 1000) if expect_final else None
    # session_config is currently resolved by gateway-side defaults.
    _ = session_config
    return gateway_call(
        "agent",
        params,
        timeout_sec=max(90, timeout_sec + 30),
        expect_final=expect_final,
        call_timeout_ms=call_timeout_ms,
    )
