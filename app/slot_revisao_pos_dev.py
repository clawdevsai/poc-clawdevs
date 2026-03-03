#!/usr/bin/env python3
"""
Slot único "Revisão pós-Dev" (openclaw-first). Consome code:ready, envia a cada um dos 6 papéis
(Architect, QA, CyberSec, DBA, UX, PO) via OpenClaw Gateway; persiste review por papel;
quando todos aprovam → Approved, merge (gh pr merge), event:devops. Sem LLM neste script.
Ref: docs/39-consumer-groups-pipeline-revisao.md, docs/agents-devs/state-machine-issues.md,
     .cursor/rules/openclaw-first.mdc
"""
import json
import os
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from gpu_lock import GPULock, get_redis

try:
    from acefalo_redis import is_consumption_paused
except ImportError:
    def is_consumption_paused(r=None):
        return False

try:
    from orchestration import record_architect_rejection
except ImportError:
    def record_architect_rejection(r, issue_id: str) -> int:
        return 0
try:
    from architect_fallback import run_fallback as run_architect_fallback
except ImportError:
    def run_architect_fallback(r, issue_id: str, reason: str = "", branch: str = "", title: str = ""):
        return None

try:
    from microadr_generate import generate_and_store_microadr
except ImportError:
    def generate_and_store_microadr(issue_id, branch, title, decision, related_pr=None):
        return None, None

KEY_PREFIX = os.getenv("KEY_PREFIX_PROJECT", "project:v1")
try:
    from issue_state import set_issue_state, STATE_IN_REVIEW, STATE_APPROVED, STATE_MERGED
except ImportError:
    STATE_IN_REVIEW = "InReview"
    STATE_APPROVED = "Approved"
    STATE_MERGED = "Merged"
    def set_issue_state(r, issue_id: str, state: str, ttl_sec=None) -> bool:
        r.set(f"{KEY_PREFIX}:issue:{issue_id}:state", state)
        return True

try:
    from openclaw_gateway_call import send_to_session
except ImportError:
    def send_to_session(session_key, message, timeout_sec=0):
        return False, "openclaw_gateway_call não disponível"

REVIEW_ROLES = ["architect", "qa", "cybersec", "dba", "ux", "po"]
GITHUB_REPO = os.getenv("GITHUB_REPO", os.getenv("GH_REPO", ""))
STREAM_CODE_READY = os.getenv("STREAM_CODE_READY", "code:ready")
GROUP_REVISAO = os.getenv("CONSUMER_GROUP_REVISAO", "revisao-pos-dev")
CONSUMER_NAME = os.getenv("POD_NAME", os.getenv("HOSTNAME", "slot-1"))
BLOCK_MS = int(os.getenv("SLOT_BLOCK_MS", "5000"))
REVIEW_TIMEOUT_SEC = int(os.getenv("SLOT_REVIEW_TIMEOUT_SEC", "120"))
SIMULATE_REJECT = os.getenv("SIMULATE_ARCHITECT_REJECT", "").strip().lower() in ("1", "true", "yes")


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


def _get_issue_context(r, issue_id: str, max_chars: int = 4000) -> str:
    if not issue_id:
        return ""
    key = f"{KEY_PREFIX}:issue:{issue_id}"
    try:
        raw = r.get(key)
        if raw is None:
            return ""
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", errors="replace")
        return (raw[:max_chars] + "…") if len(raw) > max_chars else raw
    except Exception:
        return ""


def _review_key(issue_id: str, role: str) -> str:
    return f"{KEY_PREFIX}:issue:{issue_id}:review:{role}"


def _session_key(role: str) -> str:
    return os.getenv(f"OPENCLAW_{role.upper()}_SESSION_KEY", f"agent:{role}:main")


def run_review_step(role: str, r, payload: dict) -> tuple[bool, str]:
    """
    Envia revisão ao agente do papel no OpenClaw; espera resposta e interpreta APPROVED/REJECTED.
    Retorna (aprovado, motivo_rejeicao).
    """
    issue_id = (payload.get("issue_id") or payload.get("issue") or payload.get("task_id") or "").strip()
    if SIMULATE_REJECT and role == "architect":
        print("  [Architect] Simulação de rejeição (SIMULATE_ARCHITECT_REJECT).")
        return (False, "simulate_reject")

    issue_ctx = _get_issue_context(r, issue_id)
    branch = payload.get("branch", "")
    title = payload.get("title", "")

    message = f"""Code review (papel: {role}). Issue: {issue_id}. Branch: {branch or '(não informada)'}. Título: {title or '(vazio)'}.

Contexto da issue (especificação/critérios):
{issue_ctx or '(nenhum contexto no Redis)'}

O código desta tarefa está pronto para revisão. Responda em exatamente uma linha começando por APPROVED ou REJECTED: (ou REJEITADO:). Exemplo: REJECTED: falta cobertura de testes."""
    session_key = _session_key(role)
    ok, out = send_to_session(session_key, message, timeout_sec=REVIEW_TIMEOUT_SEC)
    if not ok:
        print(f"  [{role}] Falha ao chamar Gateway: {out}", file=sys.stderr)
        return (False, str(out)[:200])
    reply_text = ""
    if isinstance(out, dict):
        reply_text = out.get("reply") or out.get("content") or out.get("payload", {}).get("reply") or json.dumps(out)
    else:
        reply_text = str(out)
    content_upper = reply_text.strip().upper()
    first_line = (reply_text.strip().split("\n")[0] or "")[:200]
    rejected = "REJECTED" in content_upper or "REJEITADO" in content_upper
    if rejected:
        print(f"  [{role}] Resposta: rejeitado — {first_line[:120]}")
        return (False, first_line)
    print(f"  [{role}] Resposta: aprovado — {first_line[:80]}")
    return (True, "")


def do_merge(r, issue_id: str, payload: dict) -> bool:
    """Executa merge do PR (gh pr merge). Retorna True se merge feito."""
    import subprocess
    branch = (payload.get("branch") or "").strip()
    repo = (GITHUB_REPO or os.getenv("GITHUB_REPO", "")).strip()
    if not repo or not branch:
        print("[Slot] Merge: GITHUB_REPO ou branch não informado.", file=sys.stderr)
        return False
    try:
        env = {**os.environ, "GH_TOKEN": os.environ.get("GH_TOKEN", os.environ.get("GITHUB_TOKEN", ""))}
        out = subprocess.run(
            ["gh", "pr", "list", "--repo", repo, "--head", branch, "--json", "number", "-q", ".[0].number"],
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )
        if out.returncode != 0 or not out.stdout or not out.stdout.strip():
            print(f"[Slot] Merge: PR não encontrado para branch={branch}", file=sys.stderr)
            return False
        pr_num = out.stdout.strip()
        m = subprocess.run(
            ["gh", "pr", "merge", pr_num, "--repo", repo, "--merge"],
            capture_output=True,
            text=True,
            timeout=60,
            env=env,
        )
        if m.returncode != 0:
            print(f"[Slot] Merge falhou: {m.stderr or m.stdout}", file=sys.stderr)
            return False
        set_issue_state(r, issue_id, STATE_MERGED)
        print(f"[Slot] PR {pr_num} merged. Estado → Merged.")
        try:
            r.xadd(
                os.getenv("STREAM_EVENT_DEVOPS", "event:devops"),
                {"issue_id": issue_id, "branch": branch, "repo": repo, "pr": pr_num, "ts": str(int(time.time()))},
            )
        except Exception:
            pass
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
        print(f"[Slot] Erro ao fazer merge: {e}", file=sys.stderr)
        return False


def processar_mensagem(r, stream: str, msg_id: str, data: dict) -> None:
    payload = _payload_to_dict(data or {})
    issue_id = (payload.get("issue_id") or payload.get("issue") or payload.get("task_id") or "").strip()
    print(f"[Slot] Processando {msg_id} stream={stream} issue_id={issue_id!r} (openclaw-first)")

    reason = ""
    with GPULock():
        all_approved = True
        for role in REVIEW_ROLES:
            approved, reason = run_review_step(role, r, payload)
            value = "rejected" if not approved else "approved"
            if issue_id:
                r.set(_review_key(issue_id, role), value)
            if not approved:
                all_approved = False
                print(f"[Slot] {role} rejeitou: {reason[:100]}")
                if role == "architect" and issue_id:
                    n = record_architect_rejection(r, issue_id)
                    if n == 2:
                        try:
                            run_architect_fallback(
                                r, issue_id,
                                rejection_reason=reason,
                                branch=payload.get("branch", ""),
                                title=payload.get("title", ""),
                            )
                        except Exception as e:
                            print(f"[Slot] Fallback Architect: {e}", file=sys.stderr)
                break
        if not all_approved:
            try:
                from orchestration import emit_event
                emit_event(r, "review_rejected", issue_id=issue_id or "", reason=reason[:200])
            except Exception:
                pass
            r.xack(stream, GROUP_REVISAO, msg_id)
            return
        if issue_id:
            set_issue_state(r, issue_id, STATE_APPROVED)
            try:
                _, key = generate_and_store_microadr(
                    issue_id,
                    payload.get("branch", ""),
                    payload.get("title", "Code review aprovado"),
                    "Aprovado por todos os 6 papéis (Architect, QA, CyberSec, DBA, UX, PO).",
                    payload.get("pr"),
                )
                if key:
                    print(f"[Slot] MicroADR registrado para issue {issue_id} em {key}.")
            except Exception as e:
                print(f"[Slot] Falha ao gerar microADR: {e}", file=sys.stderr)
            do_merge(r, issue_id, payload)
    r.xack(stream, GROUP_REVISAO, msg_id)
    print(f"[Slot] XACK {stream} {GROUP_REVISAO} {msg_id}")


def get_redis_with_retry(max_attempts=30, delay_sec=10):
    for attempt in range(1, max_attempts + 1):
        try:
            r = get_redis()
            r.ping()
            return r
        except Exception as e:
            print(f"[Slot] Redis indisponível (tentativa {attempt}/{max_attempts}): {e}", file=sys.stderr)
            if attempt == max_attempts:
                raise
            time.sleep(delay_sec)
    raise RuntimeError("Redis não disponível após retries")


def main() -> None:
    r = get_redis_with_retry()
    print(f"[Slot] Consumindo stream={STREAM_CODE_READY} group={GROUP_REVISAO} consumer={CONSUMER_NAME} (openclaw-first)")

    while True:
        try:
            if is_consumption_paused(r=r):
                time.sleep(60)
                continue
            reply = r.xreadgroup(
                GROUP_REVISAO,
                CONSUMER_NAME,
                {STREAM_CODE_READY: ">"},
                block=BLOCK_MS,
                count=1,
            )
        except Exception as e:
            print(f"[Slot] Erro de conexão Redis (reconectando em 15s): {e}", file=sys.stderr)
            time.sleep(15)
            try:
                r = get_redis_with_retry(max_attempts=3, delay_sec=5)
            except Exception:
                time.sleep(15)
            continue
        if not reply:
            continue
        for stream, messages in reply:
            stream = stream if isinstance(stream, str) else stream.decode()
            for msg_id, data in messages:
                msg_id = msg_id if isinstance(msg_id, str) else msg_id.decode()
                data = data or {}
                try:
                    processar_mensagem(r, stream, msg_id, data)
                except Exception as e:
                    print(f"[Slot] Erro ao processar {msg_id}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
