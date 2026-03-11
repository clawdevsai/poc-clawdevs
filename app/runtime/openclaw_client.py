#!/usr/bin/env python3
"""Cliente minimo para envio de mensagens ao OpenClaw Gateway via CLI."""
from __future__ import annotations

import json
import os
import subprocess

from .agent_runtime import GatewayOutput

TOOL_OPENCLAW_SESSIONS_SEND = "openclaw.sessions.send"

OPENCLAW_CLI = os.getenv("OPENCLAW_CLI_PATH", "openclaw")
GATEWAY_WS = (os.getenv("OPENCLAW_GATEWAY_WS") or "").strip().rstrip("/")
GATEWAY_TOKEN = (os.getenv("OPENCLAW_GATEWAY_TOKEN") or "").strip() or None


def gateway_call(method: str, params: dict, timeout_sec: int = 60) -> tuple[bool, GatewayOutput]:
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
) -> tuple[bool, GatewayOutput]:
    params = {
        "sessionKey": session_key,
        "message": message,
    }
    if timeout_sec > 0:
        params["timeoutSeconds"] = timeout_sec
    return gateway_call("sessions.send", params, timeout_sec=max(90, timeout_sec + 30))
