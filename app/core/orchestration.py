#!/usr/bin/env python3
"""Modulo unico de governanca do runtime principal."""
import os
import time
from datetime import datetime
from pathlib import Path

from app.runtime import EventEnvelope, log_error, log_event
from app.shared.issue_state import STATE_BACKLOG, set_issue_state
from app.shared.redis_client import get_redis

KEY_PREFIX = os.environ.get("KEY_PREFIX_PROJECT", "project:v1")


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or not str(raw).strip():
        return default
    try:
        return int(str(raw).strip())
    except (ValueError, TypeError):
        return default


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None or not str(raw).strip():
        return default
    try:
        return float(str(raw).strip())
    except (ValueError, TypeError):
        return default

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
KEY_INVALID_OUTPUT_COUNT = f"{KEY_PREFIX}:orchestrator:invalid_output_count"
INVALID_OUTPUT_THRESHOLD = _env_int("INVALID_OUTPUT_THRESHOLD", 3)

# --- Loop de consenso (034) ---
KEY_CONSENSUS_IN_PROGRESS = f"{KEY_PREFIX}:orchestrator:consensus_loop_in_progress"
KEY_CONSENSUS_PILOT_RESULT = f"{KEY_PREFIX}:orchestrator:consensus_pilot_result"  # success | fail
KEY_CONSENSUS_PROPOSAL = f"{KEY_PREFIX}:orchestrator:consensus_proposal"  # texto da proposta QA+Architect

# --- Cosmético (033): timer 6h ---
COSMETIC_TIMER_HOURS = _env_float("COSMETIC_TIMER_HOURS", 6.0)
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
DEGRADATION_REPORT_DIR = os.environ.get("DEGRADATION_REPORT_DIR", "docs")
MEMORY_MD_PATH = os.environ.get("MEMORY_MD_PATH", "docs/MEMORY.md")
AREAS_QA_AUDIT_PATH = os.environ.get("AREAS_QA_AUDIT_PATH", "docs/areas-for-qa-audit.md")

DEGRADATION_THRESHOLD_PCT = _env_float("DEGRADATION_THRESHOLD_PCT", 12.0)
CONSENSUS_LOOP_TIMEOUT_SEC = _env_int("CONSENSUS_LOOP_TIMEOUT_SEC", 3600)
INTERVAL_SEC = _env_int("ORCHESTRATOR_INTERVAL_SEC", 60)


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


def record_invalid_output(r, *, role_name: str, issue_id: str | None, schema: str | None, missing_fields: list[str]) -> int:
    total = r.incr(KEY_INVALID_OUTPUT_COUNT)
    role_key = f"{KEY_PREFIX}:orchestrator:invalid_output:role:{role_name}"
    role_total = r.incr(role_key)
    issue_total = 0
    if issue_id:
        issue_key = f"{KEY_PREFIX}:issue:{issue_id}:invalid_output_count"
        issue_total = r.incr(issue_key)
    emit_event(
        r,
        "openclaw_invalid_output",
        issue_id=issue_id or "",
        role_name=role_name,
        schema=schema or "",
        missing_fields=",".join(missing_fields),
        total=total,
        role_total=role_total,
        issue_total=issue_total,
        status_code="openclaw_invalid_output",
        event_name="orchestration.openclaw_invalid_output",
    )
    if issue_id and issue_total >= INVALID_OUTPUT_THRESHOLD:
        increment_strike(r, issue_id)
        set_issue_state(r, issue_id, STATE_BACKLOG)
        emit_event(
            r,
            "openclaw_invalid_output_threshold",
            issue_id=issue_id,
            role_name=role_name,
            schema=schema or "",
            issue_total=issue_total,
            threshold=INVALID_OUTPUT_THRESHOLD,
            status_code="openclaw_invalid_output_threshold",
            event_name="orchestration.openclaw_invalid_output_threshold",
        )
        emit_event(
            r,
            "issue_back_to_po",
            issue_id=issue_id,
            role_name=role_name,
            reason="openclaw_invalid_output_threshold",
            issue_total=issue_total,
            threshold=INVALID_OUTPUT_THRESHOLD,
            target_state=STATE_BACKLOG,
            status_code="issue_back_to_po",
            event_name="orchestration.issue_back_to_po",
        )
    return total


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
    line = f"- **{datetime.utcnow().isoformat()}Z** — issue `{issue_id}` — aprovação por omissão cosmética — decisão: {decision} — arquivos: {', '.join(files)}\n"
    with open(path, "a", encoding="utf-8") as f:
        f.write(line)


def add_to_qa_audit(r, issue_id: str, files: list[str]) -> None:
    """Adiciona issue à lista de auditoria QA (Redis SET + detalhe em HASH)."""
    r.sadd(KEY_QA_AUDIT_ISSUES, issue_id)
    r.hset(qa_audit_detail_key(issue_id), mapping={
        "files": "\n".join(files),
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
    })


def get_qa_audit_issues(r) -> list[str]:
    return list(r.smembers(KEY_QA_AUDIT_ISSUES))


def get_qa_audit_detail(r, issue_id: str) -> dict:
    return r.hgetall(qa_audit_detail_key(issue_id)) or {}


def write_areas_qa_audit_file(r, path: str | None = None) -> None:
    """Gera arquivo markdown com áreas para auditoria de QA a partir do Redis."""
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
        envelope = EventEnvelope.from_payload(
            {
                "type": event_type,
                "status_code": fields.get("status_code") or event_type,
                "event_name": fields.get("event_name") or f"orchestration.{event_type}",
                **fields,
            }
        )
        log_event(
            "orchestration.event_emitted",
            stream=STREAM_ORCHESTRATOR_EVENTS,
            event_type=event_type,
            status_code=envelope.payload.get("status_code"),
            event_name=envelope.payload.get("event_name"),
            run_id=envelope.run_id,
            trace_id=envelope.trace_id,
            issue_id=envelope.issue_id,
            attempt=envelope.attempt,
        )
        return r.xadd(STREAM_ORCHESTRATOR_EVENTS, envelope.to_payload())
    except Exception:
        return None


def emit_digest(r, event_type: str, **fields) -> str | None:
    try:
        envelope = EventEnvelope.from_payload(
            {
                "type": event_type,
                "status_code": fields.get("status_code") or event_type,
                "event_name": fields.get("event_name") or f"orchestration.{event_type}",
                **fields,
            }
        )
        log_event(
            "orchestration.digest_emitted",
            stream=STREAM_DIGEST,
            event_type=event_type,
            status_code=envelope.payload.get("status_code"),
            event_name=envelope.payload.get("event_name"),
            run_id=envelope.run_id,
            trace_id=envelope.trace_id,
            issue_id=envelope.issue_id,
            attempt=envelope.attempt,
        )
        return r.xadd(STREAM_DIGEST, envelope.to_payload())
    except Exception:
        return None


def write_degradation_report(five: int, omission: int, sprint_total: int, pct: float) -> Path:
    report_dir = Path(DEGRADATION_REPORT_DIR)
    report_dir.mkdir(parents=True, exist_ok=True)
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    report_path = report_dir / f"degradation-report-{date_str}.md"
    body = f"""# Relatorio de degradacao - {date_str}

Esteira pausada por orcamento de degradacao.

- tarefas na rota de fuga: {five + omission}
- total de tarefas do sprint: {sprint_total}
- percentual na rota de fuga: {pct:.1f}%
- quinto strike: {five}
- aprovacao por omissao cosmetica: {omission}
"""
    report_path.write_text(body, encoding="utf-8")
    return report_path


def _consensus_timed_out(r) -> bool:
    started = r.get(f"{KEY_CONSENSUS_IN_PROGRESS}:started_at")
    if not started:
        return True
    try:
        return (time.time() - float(started)) >= CONSENSUS_LOOP_TIMEOUT_SEC
    except (ValueError, TypeError):
        return True


def run_degradation_cycle(r) -> str:
    five = get_int(r, KEY_FIVE_STRIKES)
    omission = get_int(r, KEY_OMISSION_COUNT)
    sprint_total = get_int(r, KEY_SPRINT_TASKS, default=1)
    if sprint_total <= 0:
        return "idle"

    route_fuge = five + omission
    pct = 100.0 * route_fuge / sprint_total
    log_event(
        "orchestration.degradation_evaluated",
        five_strikes=five,
        omission_count=omission,
        sprint_total=sprint_total,
        degradation_pct=round(pct, 2),
    )

    if pct < DEGRADATION_THRESHOLD_PCT:
        r.delete(KEY_PAUSE_DEGRADATION)
        return "healthy"

    consensus_in_progress = r.get(KEY_CONSENSUS_IN_PROGRESS)
    pilot_result = (r.get(KEY_CONSENSUS_PILOT_RESULT) or "").strip().lower()

    if pilot_result == "success":
        r.delete(KEY_CONSENSUS_IN_PROGRESS)
        r.delete(KEY_CONSENSUS_PILOT_RESULT)
        r.delete(KEY_PAUSE_DEGRADATION)
        emit_digest(r, "consensus_pilot_success", pct=str(round(pct, 1)))
        return "consensus_success"

    if pilot_result == "fail" or (consensus_in_progress and _consensus_timed_out(r)):
        r.delete(KEY_CONSENSUS_IN_PROGRESS)
        r.delete(KEY_CONSENSUS_PILOT_RESULT)
        r.set(KEY_PAUSE_DEGRADATION, "1", ex=86400)
        emit_digest(
            r,
            "degradation_threshold",
            pct=str(round(pct, 1)),
            five_strikes=str(five),
            omission_cosmetic=str(omission),
            sprint_tasks=str(sprint_total),
        )
        write_degradation_report(five, omission, sprint_total, pct)
        return "paused"

    if not consensus_in_progress:
        r.set(KEY_CONSENSUS_IN_PROGRESS, "1", ex=CONSENSUS_LOOP_TIMEOUT_SEC)
        r.set(f"{KEY_CONSENSUS_IN_PROGRESS}:started_at", str(time.time()), ex=CONSENSUS_LOOP_TIMEOUT_SEC)
        emit_digest(
            r,
            "consensus_loop_requested",
            pct=str(round(pct, 1)),
            five_strikes=str(five),
            omission_cosmetic=str(omission),
            sprint_tasks=str(sprint_total),
        )
        emit_event(
            r,
            "consensus_loop_requested",
            pct=str(round(pct, 1)),
            five_strikes=str(five),
            omission_cosmetic=str(omission),
            sprint_tasks=str(sprint_total),
        )
        return "consensus_requested"

    return "waiting_consensus"


def main() -> None:
    redis_client = get_redis()
    print(f"[orchestration] threshold={DEGRADATION_THRESHOLD_PCT}% interval={INTERVAL_SEC}s")
    log_event(
        "orchestration.worker_started",
        threshold_pct=DEGRADATION_THRESHOLD_PCT,
        interval_sec=INTERVAL_SEC,
    )
    while True:
        try:
            run_degradation_cycle(redis_client)
        except Exception as error:
            log_error("orchestration.loop_error", error=str(error))
            print(f"[orchestration] Erro: {error}")
        time.sleep(INTERVAL_SEC)


if __name__ == "__main__":
    main()
