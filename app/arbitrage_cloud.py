#!/usr/bin/env python3
"""
Fase 3 — 032: Arbitragem na nuvem no 5º strike.
Empacota contexto da issue (Redis) e envia para modelo superior (OpenRouter ou Gemini).
Se sucesso: grava solução em Redis (project:v1:issue:{id}:cloud_arbitrage_solution).
Se falha: não altera fluxo (issue já foi emitida issue_back_to_po).
Ref: docs/issues/032-five-strikes-fallback-arbitragem.md
"""
import json
import os
import sys
import urllib.error
import urllib.request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from orchestration_phase3 import get_redis, cloud_arbitrage_solution_key

KEY_PREFIX = os.environ.get("KEY_PREFIX_PROJECT", "project:v1")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "").strip()
OPENROUTER_MODEL = os.environ.get("OPENROUTER_ARBITRAGE_MODEL", "openai/gpt-4o-mini")
GOOGLE_AI_KEY = os.environ.get("GOOGLE_AI_KEY", "").strip()
ARBITRAGE_TIMEOUT = int(os.environ.get("ARBITRAGE_CLOUD_TIMEOUT_SEC", "120"))


def _get_issue_context(r, issue_id: str, max_chars: int = 8000) -> str:
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


def _call_openrouter(context: str, issue_id: str) -> str | None:
    if not OPENROUTER_API_KEY:
        return None
    url = "https://openrouter.ai/api/v1/chat/completions"
    body = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "Você é um arbitro técnico. Esta issue teve 5 rejeições do Architect. Gere uma solução concreta: código ou patch (unified diff) que atenda aos critérios. Seja direto: apenas código/patch.",
            },
            {
                "role": "user",
                "content": f"Issue id: {issue_id}.\n\nContexto (especificação e critérios):\n{context}\n\nGere a solução (código ou patch) que resolveria esta issue.",
            },
        ],
        "max_tokens": 4096,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=ARBITRAGE_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None
    try:
        content = (data.get("choices") or [{}])[0].get("message", {}).get("content") or ""
    except Exception:
        return None
    return content.strip() or None


def _call_gemini(context: str, issue_id: str) -> str | None:
    if not GOOGLE_AI_KEY:
        return None
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_AI_KEY}"
    body = {
        "contents": [{
            "parts": [{
                "text": f"Você é um arbitro técnico. Issue {issue_id} teve 5 rejeições do Architect. Gere solução concreta: código ou patch (unified diff). Seja direto.\n\nContexto:\n{context}\n\nSolução (código ou patch):"
            }]
        }],
        "generationConfig": {"maxOutputTokens": 4096},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=ARBITRAGE_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None
    try:
        parts = (data.get("candidates") or [{}])[0].get("content", {}).get("parts") or []
        text = (parts[0].get("text") or "").strip()
        return text or None
    except Exception:
        return None


def run(r, issue_id: str) -> bool:
    """
    Tenta arbitragem na nuvem. Retorna True se obteve solução e gravou em Redis.
    """
    if not issue_id:
        return False
    context = _get_issue_context(r, issue_id)
    if not context:
        return False
    solution = None
    if OPENROUTER_API_KEY:
        solution = _call_openrouter(context, issue_id)
    if solution is None and GOOGLE_AI_KEY:
        solution = _call_gemini(context, issue_id)
    if not solution:
        return False
    key = cloud_arbitrage_solution_key(issue_id)
    try:
        r.set(key, solution, ex=86400 * 7)
    except Exception:
        return False
    return True


def main():
    if len(sys.argv) < 2:
        print("Uso: arbitrage_cloud.py <issue_id>", file=sys.stderr)
        sys.exit(1)
    issue_id = sys.argv[1].strip()
    r = get_redis()
    ok = run(r, issue_id)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
