#!/usr/bin/env python3
"""
Aprovação por omissão apenas cosmética (Fase 3 — 033).
Regra determinística por extensão de arquivo; timer 6 h; MEMORY.md e lista QA (035).
Uso:
  cosmetic_omission.py is-cosmetic <file1> [file2 ...]
  cosmetic_omission.py start-timer <issue_id> <file1> [file2 ...]
  cosmetic_omission.py check-timers   # chamar por cron; expira timers e grava MEMORY + QA
  cosmetic_omission.py write-qa-file  # gera docs/agents-devs/areas-for-qa-audit.md
Ref: docs/06-operacoes.md, docs/issues/033, 035.
"""
import os
import sys
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orchestration import (
    get_redis,
    is_cosmetic,
    start_cosmetic_timer,
    list_cosmetic_timers,
    clear_cosmetic_timer,
    cosmetic_timer_files_key,
    record_omission_cosmetic,
    write_areas_qa_audit_file,
)


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Uso: cosmetic_omission.py is-cosmetic <f1> [f2 ...] | start-timer <issue_id> <f1> [f2 ...] | check-timers | write-qa-file",
            file=sys.stderr,
        )
        sys.exit(1)
    cmd = sys.argv[1].lower()

    if cmd == "is-cosmetic":
        files = sys.argv[2:]
        if not files:
            print("Passe pelo menos um arquivo.", file=sys.stderr)
            sys.exit(1)
        result = is_cosmetic(files)
        print("yes" if result else "no")
        return

    if cmd == "start-timer":
        if len(sys.argv) < 4:
            print("Uso: start-timer <issue_id> <file1> [file2 ...]", file=sys.stderr)
            sys.exit(1)
        issue_id = sys.argv[2]
        files = sys.argv[3:]
        r = get_redis()
        start_cosmetic_timer(r, issue_id, files)
        print(f"[cosmetic] Timer 6h iniciado para issue {issue_id} ({len(files)} arquivo(s))")
        return

    if cmd == "check-timers":
        r = get_redis()
        now = time.time()
        for issue_id, end_ts in list_cosmetic_timers(r):
            if now >= end_ts:
                files_str = r.get(cosmetic_timer_files_key(issue_id)) or ""
                files = [f.strip() for f in files_str.split("\n") if f.strip()]
                record_omission_cosmetic(r, issue_id, files)
                clear_cosmetic_timer(r, issue_id)
                print(f"[cosmetic] Timer expirado issue {issue_id} — registrado em MEMORY e lista QA")
        return

    if cmd == "write-qa-file":
        r = get_redis()
        write_areas_qa_audit_file(r)
        print("[cosmetic] Escrito docs/agents-devs/areas-for-qa-audit.md")
        return

    print("Comando inválido.", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
