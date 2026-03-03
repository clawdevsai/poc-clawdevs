#!/usr/bin/env python3
"""
PO trigger: consome cmd:strategy (evento do CEO), envia contexto ao agente PO no OpenClaw.
O agente PO (no Gateway) usa ferramentas para ler Memoria, criar issues no GitHub,
gravar project:v1:issue:{id}, publicar em draft.2.issue. Sem LLM neste script (openclaw-first).
Ref: docs/38-redis-streams-estado-global.md, docs/agents-devs/state-machine-issues.md,
     .cursor/rules/openclaw-first.mdc
"""
import json
import os
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from gpu_lock import get_redis

try:
    from issue_state import KEY_PREFIX
except ImportError:
    KEY_PREFIX = os.environ.get("KEY_PREFIX_PROJECT", "project:v1")

try:
    from openclaw_gateway_call import send_to_session
except ImportError:
    def send_to_session(session_key, message, timeout_sec=0):
        return False, "openclaw_gateway_call não disponível"

STREAM_CMD_STRATEGY = os.getenv("STREAM_CMD_STRATEGY", "cmd:strategy")
GROUP = os.getenv("PO_GROUP", "clawdevs")
CONSUMER = os.getenv("POD_NAME", os.getenv("HOSTNAME", "po-1"))
BLOCK_MS = int(os.getenv("PO_BLOCK_MS", "5000"))
STRATEGY_DOC_KEY = os.getenv("STRATEGY_DOC_KEY", f"{KEY_PREFIX}:strategy_doc")
PO_SESSION_KEY = os.getenv("OPENCLAW_PO_SESSION_KEY", "agent:po:main")
GITHUB_REPO = os.getenv("GITHUB_REPO", os.getenv("GH_REPO", ""))


def _payload_to_dict(data) -> dict:
    if isinstance(data, dict):
        return {k: (v.decode() if isinstance(v, bytes) else v) for k, v in data.items()}
    if isinstance(data, (list, tuple)):
        out = {}
        for i in range(0, len(data) - 1, 2):
            k, v = data[i], data[i + 1]
            if isinstance(k, bytes):
                k = k.decode()
            if isinstance(v, bytes):
                v = v.decode()
            out[k] = v
        return out
    return {}


def read_strategy(r, key: str = None) -> str:
    k = key or STRATEGY_DOC_KEY
    raw = r.get(k)
    if raw is None:
        return ""
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8", errors="replace")
    return raw


def process_strategy(r, msg_id: str, payload: dict) -> None:
    directive = (payload.get("directive") or "").strip()
    strategy_key = (payload.get("strategy_doc_key") or "").strip() or STRATEGY_DOC_KEY
    repo = (payload.get("repo") or GITHUB_REPO or "").strip()
    if not directive:
        directive = read_strategy(r, strategy_key or None) or "Implementar conforme documento estratégico na Memoria."
    message = f"""Nova diretriz estratégica (cmd:strategy). Ação: leia o documento em Memoria se necessário, quebre em Épico/Features/Stories, crie as issues no GitHub, grave em project:v1:issue:{{id}} e publique em draft.2.issue para o Arquiteto.

Diretriz: {directive[:8000]}
Repo: {repo or '(não informado)'}
Chave estratégica no Redis: {strategy_key or STRATEGY_DOC_KEY}
"""
    ok, out = send_to_session(PO_SESSION_KEY, message, timeout_sec=0)
    if not ok:
        print(f"[PO] Falha ao enviar ao Gateway: {out}", file=sys.stderr)
        return
    r.xack(STREAM_CMD_STRATEGY, GROUP, msg_id)
    print(f"[PO] XACK {STREAM_CMD_STRATEGY} {GROUP} {msg_id} (mensagem enviada ao agente PO)")


def main() -> None:
    r = get_redis()
    print(f"[PO] Consumindo stream={STREAM_CMD_STRATEGY} group={GROUP} consumer={CONSUMER} (openclaw-first)")

    while True:
        try:
            reply = r.xreadgroup(GROUP, CONSUMER, {STREAM_CMD_STRATEGY: ">"}, block=BLOCK_MS, count=1)
        except Exception as e:
            print(f"[PO] Erro: {e}", file=sys.stderr)
            time.sleep(5)
            continue
        if not reply:
            continue
        for stream, messages in reply:
            stream = stream.decode() if isinstance(stream, bytes) else stream
            for msg_id, data in messages:
                msg_id = msg_id.decode() if isinstance(msg_id, bytes) else msg_id
                payload = _payload_to_dict(data or {})
                try:
                    process_strategy(r, msg_id, payload)
                except Exception as e:
                    print(f"[PO] Erro ao processar {msg_id}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
