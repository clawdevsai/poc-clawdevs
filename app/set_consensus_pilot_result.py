#!/usr/bin/env python3
"""
Define o resultado do pilot do loop de consenso (Fase 3 — 034).
Chamado pelo subfluxo QA+Architect após testar ajuste em uma tarefa.
Uso: set_consensus_pilot_result.py success | fail
Ref: docs/06-operacoes.md (Loop de consenso automatizado)
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orchestration_phase3 import get_redis, KEY_CONSENSUS_PILOT_RESULT

def main():
    if len(sys.argv) < 2 or sys.argv[1].lower() not in ("success", "fail"):
        print("Uso: set_consensus_pilot_result.py success | fail", file=sys.stderr)
        sys.exit(1)
    r = get_redis()
    r.set(KEY_CONSENSUS_PILOT_RESULT, sys.argv[1].lower())
    print(f"[orchestrator] Consensus pilot result = {sys.argv[1].lower()}")

if __name__ == "__main__":
    main()
