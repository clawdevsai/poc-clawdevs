#!/usr/bin/env python3
"""
Chamada ao OpenClaw Gateway via CLI (protocolo WS).
Triggers usam isto para enviar mensagens a agentes sem reimplementar o agent loop.
Requer: openclaw no PATH ou OPENCLAW_CLI_PATH; OPENCLAW_GATEWAY_WS (ex.: ws://openclaw.ai-agents.svc:18789).
Ref: docs.openclaw.ai/gateway/protocol, .cursor/rules/openclaw-first.mdc
"""
import json
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

OPENCLAW_CLI = os.getenv("OPENCLAW_CLI_PATH", "openclaw")
GATEWAY_WS = (os.getenv("OPENCLAW_GATEWAY_WS") or "").strip().rstrip("/")
GATEWAY_TOKEN = (os.getenv("OPENCLAW_GATEWAY_TOKEN") or "").strip() or None


def gateway_call(method: str, params: dict, timeout_sec: int = 60) -> tuple[bool, dict | str]:
    """
    Chama um método RPC do Gateway via CLI.
    Retorna (ok, payload_dict ou mensagem de erro).
    """
    if not GATEWAY_WS:
        return False, "OPENCLAW_GATEWAY_WS não definido"
    params_json = json.dumps(params, ensure_ascii=False)
    cmd = [
        OPENCLAW_CLI,
        "gateway",
        "call",
        method,
        "--url", GATEWAY_WS,
        "--params", params_json,
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
        return False, f"openclaw CLI não encontrado (PATH ou OPENCLAW_CLI_PATH={OPENCLAW_CLI})"
    except subprocess.TimeoutExpired:
        return False, "timeout"
    except Exception as e:
        return False, str(e)


def send_to_session(
    session_key: str,
    message: str,
    timeout_sec: int = 0,
) -> tuple[bool, dict | str]:
    """
    Envia mensagem à sessão do agente (sessions.send).
    timeout_sec=0: fire-and-forget; >0: espera até N segundos pela conclusão.
    """
    params = {
        "sessionKey": session_key,
        "message": message,
    }
    if timeout_sec > 0:
        params["timeoutSeconds"] = timeout_sec
    return gateway_call("sessions.send", params, timeout_sec=max(90, timeout_sec + 30))
