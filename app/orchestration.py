#!/usr/bin/env python3
"""
Chaves e helpers: five strikes por issue, aprovação por omissão cosmética,
orçamento de degradação, loop de consenso, QA auditor.
Ref: docs/06-operacoes.md, docs/issues/032–036.
"""
import os
import time
from pathlib import Path

KEY_PREFIX = os.environ.get("KEY_PREFIX_PROJECT", "project:v1")

# --- Strikes (032) ---
def strike_key(issue_id: str) -> str:
    return f"{KEY_PREFIX}:issue:{issue_id}:strikes"
def architect_fallback_patch_key(issue_id: str) -> str:
    return f"{KEY_PREFIX}:issue:{issue_id}:architect_fallback_patch"
def cloud_arbitrage_solution_key(issue_id: str) -> str:
    return f"{KEY_PREFIX}:issue:{issue_id}:cloud_arbitrage_solution"

# --- Degradação (orquestrador) ---
KEY_FIVE_STRIKES = f"{KEY_PREFIX}:orchestrator:five_strikes_count"
KEY_OMISSION_COUNT = f"{KEY_PREFIX}:orchestrator:omission_cosmetic_count"
KEY_SPRINT_TASKS = f"{KEY_PREFIX}:orchestrator:sprint_task_count"
KEY_PAUSE_DEGRADATION = "orchestration:pause_degradation"

# --- Loop de consenso (034) ---
KEY_CONSENSUS_IN_PROGRESS = f"{KEY_PREFIX}:orchestrator:consensus_loop_in_progress"
KEY_CONSENSUS_PILOT_RESULT = f"{KEY_PREFIX}:orchestrator:consensus_pilot_result"  # success | fail
KEY_CONSENSUS_PROPOSAL = f"{KEY_PREFIX}:orchestrator:consensus_proposal"  # texto da proposta QA+Architect

# --- Cosmético (033): timer 6h ---
COSMETIC_TIMER_HOURS = float(os.environ.get("COSMETIC_TIMER_HOURS", "6"))
COSMETIC_EXTENSIONS = frozenset(
    os.environ.get("COSMETIC_EXTENSIONS", ".css,.scss,.less,.md,.html,.htm,.svg,.json").lower().split(",")
)
# Arquivos .html/.htm considerados cosméticos só se não forem template com lógica (heurística: sem script tag?)
def cosmetic_timer_key(issue_id: str) -> str:
    return f"{KEY_PREFIX}:issue:{issue_id}:cosmetic_timer_end"
def cosmetic_timer_files_key(issue_id: str) -> str:
    return f"{KEY_PREFIX}:issue:{issue_id}:cosmetic_timer_files"

# --- QA auditor (035): set de issue_ids que tiveram aprovação por omissão ---
KEY_QA_AUDIT_ISSUES = f"{KEY_PREFIX}:orchestrator:qa_audit_issues"  # SET
def qa_audit_detail_key(issue_id: str) -> str:
    return f"{KEY_PREFIX}:orchestrator:qa_audit_detail:{issue_id}"  # HASH: files, date

# --- Streams / eventos ---
STREAM_ORCHESTRATOR_EVENTS = os.environ.get("STREAM_ORCHESTRATOR_EVENTS", "orchestrator:events")
STREAM_DIGEST = os.environ.get("STREAM_DIGEST", "digest:daily")

# --- Paths ---
DEGRADATION_REPORT_DIR = os.environ.get("DEGRADATION_REPORT_DIR", "docs/agents-devs")
MEMORY_MD_PATH = os.environ.get("MEMORY_MD_PATH", "docs/agents-devs/MEMORY.md")
AREAS_QA_AUDIT_PATH = os.environ.get("AREAS_QA_AUDIT_PATH", "docs/agents-devs/areas-for-qa-audit.md")


def get_redis():
    try:
        import redis
        return redis.Redis(
            host=os.environ.get("REDIS_HOST", "127.0.0.1"),
            port=int(os.environ.get("REDIS_PORT", "6379")),
            password=os.environ.get("REDIS_PASSWORD") or None,
            decode_responses=True,
        )
    except ImportError:
        raise RuntimeError("Instale redis: pip install redis")


def get_int(r, key: str, default: int = 0) -> int:
    val = r.get(key)
    if val is None:
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


# --- Strikes ---
def get_strikes(r, issue_id: str) -> int:
    return get_int(r, strike_key(issue_id))


def increment_strike(r, issue_id: str) -> int:
    """Incrementa contagem de strikes da issue. Retorna nova contagem."""
    k = strike_key(issue_id)
    n = r.incr(k)
    return n


def reset_strikes(r, issue_id: str) -> None:
    r.delete(strike_key(issue_id))


def record_architect_rejection(r, issue_id: str) -> int:
    """
    Registra rejeição do Architect (slot revisão ou pipeline). Incrementa strike;
    ao 2º emite trigger_architect_fallback; ao 5º incrementa orçamento de degradação e emite issue_back_to_po.
    Retorna a nova contagem de strikes.
    """
    n = increment_strike(r, issue_id)
    if n == 2:
        emit_event(r, "trigger_architect_fallback", issue_id=issue_id)
        emit_digest(r, "strike_2_architect_fallback", issue_id=issue_id)
    elif n >= 5:
        r.incr(KEY_FIVE_STRIKES)
        emit_event(r, "issue_back_to_po", issue_id=issue_id, reason="fifth_strike")
        emit_digest(
            r,
            "strike_5_back_to_po",
            issue_id=issue_id,
            five_strikes_total=str(r.get(KEY_FIVE_STRIKES) or "0"),
        )
    return n


# --- Cosmético determinístico (033) ---
def is_cosmetic(file_paths: list[str]) -> bool:
    """
    Classificação determinística: True apenas se todos os arquivos
    têm extensão considerada cosmética (.css, .scss, .md, .html, etc.).
    Sem LLM.
    """
    if not file_paths:
        return False
    for p in file_paths:
        path = p.strip().lower()
        if not path:
            continue
        ext = path[path.rfind("."):] if "." in path else ""
        if ext not in COSMETIC_EXTENSIONS:
            return False
    return True


def start_cosmetic_timer(r, issue_id: str, files: list[str]) -> None:
    """Registra fim do timer (timestamp) e lista de arquivos. Timer = COSMETIC_TIMER_HOURS."""
    end_ts = time.time() + COSMETIC_TIMER_HOURS * 3600
    r.set(cosmetic_timer_key(issue_id), str(end_ts))
    r.set(cosmetic_timer_files_key(issue_id), "\n".join(files))


def get_cosmetic_timer_end(r, issue_id: str) -> float | None:
    val = r.get(cosmetic_timer_key(issue_id))
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def clear_cosmetic_timer(r, issue_id: str) -> None:
    r.delete(cosmetic_timer_key(issue_id))
    r.delete(cosmetic_timer_files_key(issue_id))


def list_cosmetic_timers(r) -> list[tuple[str, float]]:
    """Retorna [(issue_id, end_ts), ...] para todas as issues com timer ativo."""
    pattern = f"{KEY_PREFIX}:issue:*:cosmetic_timer_end"
    keys = list(r.scan_iter(match=pattern))
    out = []
    for k in keys:
        # k = project:v1:issue:42:cosmetic_timer_end
        parts = k.split(":")
        if len(parts) >= 4:
            issue_id = parts[-2]
        else:
            issue_id = k.replace(f"{KEY_PREFIX}:issue:", "").replace(":cosmetic_timer_end", "")
        val = r.get(k)
        if val is not None:
            try:
                out.append((issue_id, float(val)))
            except (ValueError, TypeError):
                pass
    return out


# --- Aprovação por omissão: registrar em MEMORY e lista QA (033, 035) ---
def record_omission_cosmetic(r, issue_id: str, files: list[str], decision: str = "rota_conservadora") -> None:
    """Incrementa contador global, grava MEMORY.md e adiciona à lista de auditoria QA."""
    r.incr(KEY_OMISSION_COUNT)
    _append_memory_md(issue_id, files, decision)
    add_to_qa_audit(r, issue_id, files)


def _append_memory_md(issue_id: str, files: list[str], decision: str) -> None:
    path = Path(MEMORY_MD_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    from datetime import datetime
    line = f"- **{datetime.utcnow().isoformat()}Z** — issue `{issue_id}` — aprovação por omissão cosmética — decisão: {decision} — arquivos: {', '.join(files)}\n"
    with open(path, "a", encoding="utf-8") as f:
        f.write(line)


def add_to_qa_audit(r, issue_id: str, files: list[str]) -> None:
    """Adiciona issue à lista de auditoria QA (Redis SET + detalhe em HASH)."""
    r.sadd(KEY_QA_AUDIT_ISSUES, issue_id)
    from datetime import datetime
    r.hset(qa_audit_detail_key(issue_id), mapping={
        "files": "\n".join(files),
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
    })


def get_qa_audit_issues(r) -> list[str]:
    return list(r.smembers(KEY_QA_AUDIT_ISSUES))


def get_qa_audit_detail(r, issue_id: str) -> dict:
    return r.hgetall(qa_audit_detail_key(issue_id)) or {}


def write_areas_qa_audit_file(r, path: str | None = None) -> None:
    """Escreve docs/agents-devs/areas-for-qa-audit.md a partir do Redis."""
    path = path or AREAS_QA_AUDIT_PATH
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    issues = get_qa_audit_issues(r)
    lines = [
        "# Áreas para auditoria QA (aprovadas por omissão cosmética)",
        "",
        "Gerado automaticamente. QA deve priorizar testes exploratórios nestas áreas.",
        "",
        "| Issue | Arquivos | Data |",
        "|-------|----------|------|",
    ]
    for iid in sorted(issues):
        detail = get_qa_audit_detail(r, iid)
        files = detail.get("files", "")
        date = detail.get("date", "")
        files_display = (files[:80] + "…") if len(files) > 80 else (files or "—")
        lines.append(f"| {iid} | {files_display} | {date} |")
    p.write_text("\n".join(lines), encoding="utf-8")


# --- Eventos no stream (para 2º strike, 5º strike, consensus_loop) ---
def emit_event(r, event_type: str, **fields) -> str | None:
    try:
        payload = {"type": event_type, **{k: str(v) for k, v in fields.items()}}
        return r.xadd(STREAM_ORCHESTRATOR_EVENTS, payload)
    except Exception:
        return None


def emit_digest(r, event_type: str, **fields) -> str | None:
    try:
        payload = {"type": event_type, **{k: str(v) for k, v in fields.items()}}
        return r.xadd(STREAM_DIGEST, payload)
    except Exception:
        return None
