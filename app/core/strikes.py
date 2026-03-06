#!/usr/bin/env python3
"""
Five strikes por issue (032).
Contagem em Redis; ao 2º strike emite evento trigger_architect_fallback;
ao 5º strike incrementa orçamento de degradação e emite issue_back_to_po (ou trigger_arbitrage).
Uso: strikes.py increment <issue_id> | get <issue_id> | reset <issue_id>
Ref: docs/06-operacoes.md, docs/issues/032-five-strikes-fallback-arbitragem.md
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orchestration import (
    get_redis,
    get_strikes,
    increment_strike,
    reset_strikes,
    KEY_FIVE_STRIKES,
    emit_event,
    emit_digest,
)


def main() -> None:
    if len(sys.argv) < 2:
        print("Uso: strikes.py increment <issue_id> | get <issue_id> | reset <issue_id>", file=sys.stderr)
        sys.exit(1)
    cmd = sys.argv[1].lower()
    issue_id = sys.argv[2] if len(sys.argv) > 2 else ""

    r = get_redis()

    if cmd == "get":
        if not issue_id:
            print("strikes.py get <issue_id>", file=sys.stderr)
            sys.exit(1)
        n = get_strikes(r, issue_id)
        print(n)
        return

    if cmd == "reset":
        if not issue_id:
            print("strikes.py reset <issue_id>", file=sys.stderr)
            sys.exit(1)
        reset_strikes(r, issue_id)
        print(f"[strikes] Reset issue {issue_id}")
        return

    if cmd == "increment":
        if not issue_id:
            print("strikes.py increment <issue_id>", file=sys.stderr)
            sys.exit(1)
        n = increment_strike(r, issue_id)
        print(f"[strikes] Issue {issue_id} agora com {n} strike(s)")

        if n == 2:
            eid = emit_event(r, "trigger_architect_fallback", issue_id=issue_id)
            if eid:
                print(f"[strikes] Evento trigger_architect_fallback emitido: {eid}")
            emit_digest(r, "strike_2_architect_fallback", issue_id=issue_id)

        elif n >= 5:
            r.incr(KEY_FIVE_STRIKES)
            eid = emit_event(r, "issue_back_to_po", issue_id=issue_id, reason="fifth_strike")
            if eid:
                print(f"[strikes] Evento issue_back_to_po emitido: {eid}")
            emit_digest(
                r,
                "strike_5_back_to_po",
                issue_id=issue_id,
                five_strikes_total=str(r.get(KEY_FIVE_STRIKES) or "0"),
            )
            print("[strikes] 5º strike: contador global de degradação incrementado; issue volta ao PO.")
        return

    print("Comando inválido. Use: increment | get | reset", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
