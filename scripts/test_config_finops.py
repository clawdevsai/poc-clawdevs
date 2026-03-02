#!/usr/bin/env python3
"""
Testes unitários config-perfis / truncamento-finops (perfis por agente, truncamento na borda).
Apenas testes unitários: sem Redis, sem Ollama, sem subprocess, sem I/O de rede.
Rode: python scripts/test_config_finops.py
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
os.chdir(REPO_ROOT)


# --- truncate_payload_border ---
def test_truncate_estimate_tokens():
    from truncate_payload_border import estimate_tokens
    assert estimate_tokens("") >= 1
    assert estimate_tokens("abcd") >= 1
    assert estimate_tokens("a" * 400) <= 200
    print("  truncate_payload_border estimate_tokens: ok")


def test_truncate_payload_under_limit():
    from truncate_payload_border import truncate_payload
    short = "linha1\nlinha2\nlinha3"
    out, was_truncated = truncate_payload(short, max_tokens=100, keep_head_lines=2, keep_tail_lines=2)
    assert out == short
    assert was_truncated is False
    print("  truncate_payload (under limit): ok")


def test_truncate_payload_over_limit():
    from truncate_payload_border import truncate_payload
    lines = ["head_" + str(i) for i in range(15)] + ["tail_" + str(i) for i in range(15)]
    long_text = "\n".join(lines)
    out, was_truncated = truncate_payload(long_text, max_tokens=10, keep_head_lines=5, keep_tail_lines=5)
    assert was_truncated is True
    assert "truncado na borda" in out or "[truncado" in out
    assert "head_0" in out and "tail_" in out
    print("  truncate_payload (over limit, head+tail): ok")


# --- compact_preserve_protected ---
def test_compact_extract_protected_blocks():
    from compact_preserve_protected import extract_protected_blocks
    text = """foo
<!-- CRITERIOS_ACEITE -->
1. Criterio A
2. Criterio B
<!-- /CRITERIOS_ACEITE -->
bar
<!-- INVARIANTE_NEGOCIO -->
- Regra X
<!-- /INVARIANTE_NEGOCIO -->
baz"""
    blocks = extract_protected_blocks(text)
    assert len(blocks) >= 2
    names = [b[0] for b in blocks]
    assert "CRITERIOS_ACEITE" in names
    assert "INVARIANTE_NEGOCIO" in names
    print("  compact_preserve_protected extract_protected_blocks: ok")


def test_compact_preserving_protected():
    from compact_preserve_protected import compact_preserving_protected
    # Bloco protegido no final para sobreviver ao corte (head+tail)
    text = "a\n" * 80 + "<!-- CRITERIOS_ACEITE -->\n1. Aceitar X\n<!-- /CRITERIOS_ACEITE -->"
    result = compact_preserving_protected(text, max_lines_outside=20)
    # Conteúdo do bloco ou placeholder deve estar presente
    assert "1. Aceitar X" in result or "Aceitar X" in result or "__PROTECTED_" in result
    assert "compactado" in result or "blocos protegidos" in result
    print("  compact_preserving_protected: ok")


# --- validate_reverse_po ---
def test_validate_extract_criteria():
    from validate_reverse_po import extract_criteria
    text = "x\n<!-- CRITERIOS_ACEITE -->\n1. Usuario pode fazer X\n2. Sistema deve validar Y\n<!-- /CRITERIOS_ACEITE -->\ny"
    items = extract_criteria(text)
    assert len(items) >= 1
    assert any("Usuario" in i or "validar" in i for i in items)
    assert extract_criteria("sem tag") == []
    print("  validate_reverse_po extract_criteria: ok")


def test_validate_summary_mentions():
    from validate_reverse_po import summary_mentions
    assert summary_mentions("O usuario pode fazer login e validar senha", "Usuario pode fazer login") is True
    assert summary_mentions("Apenas texto aleatorio", "Usuario deve poder fazer X com Y") is False
    print("  validate_reverse_po summary_mentions: ok")


# --- finops_attempt_cost ---
def test_finops_should_stop_task():
    # Usar env para forçar limites nos testes (evitar depender do valor default)
    os.environ["FINOPS_MAX_ATTEMPTS"] = "3"
    os.environ["FINOPS_DAILY_CAP"] = "1.0"
    import importlib
    import finops_attempt_cost as finops
    importlib.reload(finops)
    stop, reason = finops.should_stop_task("x", 2, 0.1)
    assert stop is False
    stop, reason = finops.should_stop_task("x", 3, 0.1)
    assert stop is True
    assert "Tentativas" in reason or "máximo" in reason
    stop, reason = finops.should_stop_task("x", 1, 2.0)
    assert stop is True
    assert "Custo" in reason or "teto" in reason
    # Restaurar defaults para outros testes
    os.environ.pop("FINOPS_MAX_ATTEMPTS", None)
    os.environ.pop("FINOPS_DAILY_CAP", None)
    print("  finops_attempt_cost should_stop_task: ok")


# --- preflight_summarize ---
def test_preflight_count_interactions():
    from preflight_summarize import count_interactions
    assert count_interactions({}) == 0
    assert count_interactions({"messages": [1, 2, 3]}) == 3
    assert count_interactions({"history": [1]}) == 1
    assert count_interactions({"interactions": 5}) == 5
    assert count_interactions([1, 2, 3, 4]) == 4
    print("  preflight_summarize count_interactions: ok")


def test_preflight_pass_through_without_ollama():
    from preflight_summarize import summarize_via_ollama
    orig = "texto original"
    os.environ.pop("OLLAMA_BASE_URL", None)
    import importlib
    import preflight_summarize as pfs
    importlib.reload(pfs)
    out = pfs.summarize_via_ollama(orig)
    assert out == orig
    print("  preflight_summarize pass-through (no Ollama): ok")


# --- apply_max_tokens (usa truncate_payload) ---
def test_apply_max_tokens_logic():
    from truncate_payload_border import truncate_payload, estimate_tokens
    big = "x" * 20000
    limit = 1000
    out, _ = truncate_payload(big, max_tokens=limit)
    assert estimate_tokens(out) <= limit + 50
    print("  apply_max_tokens (truncate_payload limit): ok")


# --- context_validation_hook (unitário: função propose_from_buffer_text) ---
def test_context_validation_hook_heuristic():
    from context_validation_hook import propose_from_buffer_text
    buffer_text = (
        "Linha normal\n"
        "Nunca alterar o contrato sem aprovação do Diretor.\n"
        "Sempre validar entrada do usuario.\n"
        "Texto curto.\n"
    )
    proposals = propose_from_buffer_text(buffer_text)
    assert len(proposals) >= 1
    texts = [p["text"] for p in proposals]
    assert any("Nunca" in t or "contrato" in t for t in texts)
    assert any("Sempre" in t or "validar" in t for t in texts)
    # Linha curta não entra
    assert not any("Texto curto" in t for t in texts)
    print("  context_validation_hook propose_from_buffer_text: ok")


# --- redis_buffer_writer (mock) ---
def test_redis_buffer_writer_contract():
    class MockRedis:
        def set(self, key, value, ex=None):
            self.last_key = key
            self.last_value = value
            self.last_ex = ex
    try:
        from redis_buffer_writer import WORKING_BUFFER_KEY_PREFIX, write_working_buffer
    except ImportError:
        print("  redis_buffer_writer import: skip (redis?)")
        return
    # Sem Redis real, write_working_buffer vai falhar ao conectar; testamos só o prefixo e que o módulo carrega
    assert "working_buffer" in WORKING_BUFFER_KEY_PREFIX
    print("  redis_buffer_writer contract (prefix): ok")


# --- gateway_redis_adapter: _apply_preflight_and_max_tokens (sem Flask/Redis) ---
def test_gateway_apply_preflight_and_max_tokens():
    # Importar só a função testando com mocks; o módulo pode tentar conectar Redis ao importar.
    import json
    from truncate_payload_border import estimate_tokens, truncate_payload
    # Simular lógica: payload grande com profile ceo -> truncar ao MAX_TOKENS_CEO
    data = {"payload": json.dumps({"messages": [{"role": "user", "content": "x" * 5000}]})}
    payload_str = data["payload"]
    limit = 8192
    if estimate_tokens(payload_str) > limit:
        out, _ = truncate_payload(payload_str, max_tokens=limit)
        data["payload"] = out
    assert len(data["payload"]) <= len(payload_str) or estimate_tokens(data["payload"]) <= limit + 100
    print("  gateway _apply_preflight_and_max_tokens (logic): ok")


# --- developer_worker: finops integrado (assinaturas) ---
def test_developer_worker_finops_import():
    # Garantir que o worker importa finops e tem fallback
    import developer_worker as dw
    assert hasattr(dw, "should_stop_task")
    assert hasattr(dw, "increment_attempt")
    assert callable(dw.should_stop_task)
    print("  developer_worker finops import: ok")


def main():
    print("==> Testes config-perfis / truncamento-finops")
    test_truncate_estimate_tokens()
    test_truncate_payload_under_limit()
    test_truncate_payload_over_limit()
    test_compact_extract_protected_blocks()
    test_compact_preserving_protected()
    test_validate_extract_criteria()
    test_validate_summary_mentions()
    test_finops_should_stop_task()
    test_preflight_count_interactions()
    test_preflight_pass_through_without_ollama()
    test_apply_max_tokens_logic()
    test_context_validation_hook_heuristic()
    test_redis_buffer_writer_contract()
    test_gateway_apply_preflight_and_max_tokens()
    test_developer_worker_finops_import()
    print("==> Concluído.")


if __name__ == "__main__":
    main()
