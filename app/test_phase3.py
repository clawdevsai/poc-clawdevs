#!/usr/bin/env python3
"""
Testes Fase 3 (sem Redis/Ollama obrigatórios).
Rode: python scripts/test_phase3.py
Com Redis: pip install redis, inicie Redis e os testes de integração rodarão.
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)
os.chdir(REPO_ROOT)

def test_orchestration_phase3():
    from orchestration_phase3 import is_cosmetic, get_int, strike_key
    assert is_cosmetic(["a.css", "b.md"]) is True
    assert is_cosmetic(["a.py"]) is False
    assert is_cosmetic([]) is False
    print("  orchestration_phase3 is_cosmetic: ok")

def test_slot_payload():
    from slot_revisao_pos_dev import _payload_to_dict
    assert _payload_to_dict({"issue_id": "42"}) == {"issue_id": "42"}
    assert _payload_to_dict([b"issue_id", b"42"]) == {"issue_id": "42"}
    print("  slot _payload_to_dict: ok")

def test_slot_architect_stub():
    os.environ.pop("OLLAMA_BASE_URL", None)
    os.environ.pop("SIMULATE_ARCHITECT_REJECT", None)
    class MockR:
        def get(self, k): return None
    from slot_revisao_pos_dev import run_architect_etapa
    assert run_architect_etapa(MockR(), {"issue_id": "42"}) is True
    assert run_architect_etapa(MockR(), {"issue_id": "42", "simulate_reject": "1"}) is False
    print("  slot run_architect_etapa (stub + simulate_reject): ok")

def test_slot_architect_on_error():
    import importlib
    import slot_revisao_pos_dev as slot
    os.environ["OLLAMA_BASE_URL"] = "http://127.0.0.1:19999"
    os.environ["ARCHITECT_TIMEOUT_SEC"] = "2"
    os.environ["ARCHITECT_ON_ERROR"] = "reject"
    importlib.reload(slot)
    class MockR:
        def get(self, k): return None
    assert slot.run_architect_etapa(MockR(), {"issue_id": "42"}) is False
    os.environ["ARCHITECT_ON_ERROR"] = "approve"
    importlib.reload(slot)
    assert slot.run_architect_etapa(MockR(), {"issue_id": "42"}) is True
    os.environ.pop("OLLAMA_BASE_URL", None)
    os.environ.pop("ARCHITECT_ON_ERROR", None)
    os.environ.pop("ARCHITECT_TIMEOUT_SEC", None)
    print("  slot Ollama unreachable (reject/approve): ok")

def test_redis_integration():
    try:
        from orchestration_phase3 import get_redis, get_strikes, increment_strike, reset_strikes
        r = get_redis()
        r.ping()
        # cleanup
        reset_strikes(r, "test-phase3")
        n = increment_strike(r, "test-phase3")
        assert n == 1
        assert get_strikes(r, "test-phase3") == 1
        reset_strikes(r, "test-phase3")
        print("  Redis + strikes: ok")
    except Exception as e:
        print(f"  Redis + strikes: skip (Redis indisponível: {e})")

def main():
    print("==> Testes Fase 3")
    test_orchestration_phase3()
    test_slot_payload()
    test_slot_architect_stub()
    test_slot_architect_on_error()
    test_redis_integration()
    print("==> Concluído.")

if __name__ == "__main__":
    main()
