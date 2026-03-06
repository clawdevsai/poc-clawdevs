#!/usr/bin/env python3
"""
Disjuntor draft_rejected (127). Rastreia rejeições por épico no Redis;
ao atingir 3 consecutivas na mesma épico: congela, executa RAG health check, descongela.
Ref: docs/issues/127-disjuntor-draft-rejected-rag-health-check.md, docs/38-redis-streams-estado-global.md
"""
import os
import subprocess
import sys
import time

REDIS_HOST = os.environ.get("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD") or None
KEY_PREFIX = os.environ.get("KEY_PREFIX_PROJECT", "project:v1")
STREAM_REJECTED = "draft_rejected"
GROUP = os.environ.get("DISJUNTOR_CONSUMER_GROUP", "disjuntor")
CONSUMER = os.environ.get("DISJUNTOR_CONSUMER_NAME", "disjuntor-1")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RAG_SCRIPT = os.path.join(SCRIPT_DIR, "rag_health_check.py")
INTERVAL_MS = int(os.environ.get("DISJUNTOR_POLL_MS", "5000"))
FROZEN_TTL = int(os.environ.get("DISJUNTOR_FROZEN_TTL", "300"))


def key_consecutive(epic_id: str) -> str:
    return f"{KEY_PREFIX}:orchestrator:draft_rejected_consecutive:{epic_id}"


def key_frozen(epic_id: str) -> str:
    return f"{KEY_PREFIX}:orchestrator:epic_frozen:{epic_id}"


def get_redis():
    try:
        import redis
        return redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            decode_responses=True,
        )
    except ImportError:
        raise RuntimeError("Instale redis: pip install redis")


def ensure_consumer_group(r, stream: str, group: str) -> None:
    try:
        r.xgroup_create(stream, group, id="$", mkstream=True)
    except Exception as e:
        if "BUSYGROUP" not in str(e):
            raise


def run_rag_health_check(epic_id: str, repo_path: str) -> bool:
    env = os.environ.copy()
    env["EPIC_ID"] = epic_id
    env["REPO_PATH"] = repo_path or "."
    try:
        r = subprocess.run(
            [sys.executable, RAG_SCRIPT, "--epic-id", epic_id, "--repo", repo_path or "."],
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=SCRIPT_DIR,
        )
        return r.returncode == 0
    except Exception as e:
        print(f"[disjuntor] RAG health check falhou: {e}", file=sys.stderr)
        return False


def process_message(r, msg_id: str, fields: dict) -> None:
    issue_id = fields.get("issue_id") or fields.get("id") or ""
    epic_id = fields.get("epic_id") or issue_id
    if not epic_id:
        return
    key_c = key_consecutive(epic_id)
    key_f = key_frozen(epic_id)
    count = int(r.incr(key_c))
    r.expire(key_c, 86400)
    if count < 3:
        return
    print(f"[disjuntor] 3 rejeições consecutivas na épico {epic_id} — congelando e executando RAG health check.")
    r.set(key_f, "1", ex=FROZEN_TTL)
    repo_path = os.environ.get("REPO_PATH", ".")
    run_rag_health_check(epic_id, repo_path)
    r.delete(key_f)
    r.delete(key_c)
    print(f"[disjuntor] Épico {epic_id} descongelada; contexto saneado. Contagem resetada.")


def main() -> None:
    r = get_redis()
    ensure_consumer_group(r, STREAM_REJECTED, GROUP)
    print(f"[disjuntor] Consumindo {STREAM_REJECTED} (group={GROUP}, consumer={CONSUMER})")
    while True:
        try:
            msgs = r.xreadgroup(
                GROUP, CONSUMER, {STREAM_REJECTED: ">"},
                count=10, block=INTERVAL_MS
            )
            for stream_name, stream_msgs in msgs or []:
                for msg_id, fields in stream_msgs:
                    if isinstance(fields, list):
                        fields = dict(zip(fields[::2], fields[1::2]))
                    process_message(r, msg_id, fields)
                    r.xack(STREAM_REJECTED, GROUP, msg_id)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[disjuntor] Erro: {e}", file=sys.stderr)
        time.sleep(0.5)


if __name__ == "__main__":
    main()
