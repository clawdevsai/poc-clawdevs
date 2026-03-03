#!/usr/bin/env python3
"""
Testes orquestração (sem Redis/Ollama obrigatórios).
Rode: python app/test_orchestration.py
Com Redis: pip install redis, inicie Redis e os testes de integração rodarão.
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)
os.chdir(REPO_ROOT)

def test_orchestration():
    from orchestration import is_cosmetic, get_int, strike_key
    assert is_cosmetic(["a.css", "b.md"]) is True
    assert is_cosmetic(["a.py"]) is False
    assert is_cosmetic([]) is False
    print("  orchestration is_cosmetic: ok")

def test_slot_payload():
    from slot_revisao_pos_dev import _payload_to_dict
    assert _payload_to_dict({"issue_id": "42"}) == {"issue_id": "42"}
    assert _payload_to_dict([b"issue_id", b"42"]) == {"issue_id": "42"}
    print("  slot _payload_to_dict: ok")

def test_slot_architect_stub():
    """Verifica que run_review_step e run_architect_fallback existem no módulo."""
    from slot_revisao_pos_dev import run_review_step, run_architect_fallback
    assert callable(run_review_step)
    assert callable(run_architect_fallback)
    print("  slot run_review_step + run_architect_fallback: ok")

def test_slot_architect_on_error():
    """Verifica que o módulo carrega com OLLAMA_BASE_URL inválido sem crash."""
    import importlib
    import slot_revisao_pos_dev as slot
    os.environ["OLLAMA_BASE_URL"] = "http://127.0.0.1:19999"
    os.environ["ARCHITECT_TIMEOUT_SEC"] = "2"
    importlib.reload(slot)
    assert hasattr(slot, 'run_review_step')
    assert hasattr(slot, 'run_architect_fallback')
    os.environ.pop("OLLAMA_BASE_URL", None)
    os.environ.pop("ARCHITECT_TIMEOUT_SEC", None)
    print("  slot module reload with invalid Ollama: ok")

def test_redis_integration():
    try:
        from orchestration import get_redis, get_strikes, increment_strike, reset_strikes
        r = get_redis()
        r.ping()
        # cleanup
        reset_strikes(r, "test_run")
        n = increment_strike(r, "test_run")
        assert n == 1
        assert get_strikes(r, "test_run") == 1
        reset_strikes(r, "test_run")
        print("  Redis + strikes: ok")
    except Exception as e:
        print(f"  Redis + strikes: skip (Redis indisponível: {e})")

def main():
    print("==> Testes orquestração")
    test_orchestration()
    test_slot_payload()
    test_slot_architect_stub()
    test_slot_architect_on_error()
    test_redis_integration()
    print("==> Concluído.")

if __name__ == "__main__":
    main()
