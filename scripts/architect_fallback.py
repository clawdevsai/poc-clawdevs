#!/usr/bin/env python3
"""
Fase 3 — 032: Fallback Architect no 2º strike.
Ao receber trigger_architect_fallback (ou ao ser chamado com issue_id + rejection_reason),
chama o Architect com "prompt de compromisso": gerar código/patch que tornaria o PR aprovável.
Armazena resultado em Redis (project:v1:issue:{id}:architect_fallback_patch) para o Developer aplicar.
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

from orchestration_phase3 import get_redis, architect_fallback_patch_key

try:
    from slack_notify import send_slack
except ImportError:
    def send_slack(*a, **k):
        pass

KEY_PREFIX = os.environ.get("KEY_PREFIX_PROJECT", "project:v1")
OLLAMA_BASE_URL = (os.environ.get("OLLAMA_BASE_URL") or "").strip().rstrip("/")
ARCHITECT_MODEL = os.environ.get("ARCHITECT_MODEL", "glm-5:cloud")
ARCHITECT_FALLBACK_TIMEOUT = int(os.environ.get("ARCHITECT_FALLBACK_TIMEOUT_SEC", "180"))


def _get_issue_context(r, issue_id: str, max_chars: int = 6000) -> str:
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


def run_fallback(r, issue_id: str, rejection_reason: str = "", branch: str = "", title: str = "") -> str | None:
    """
    Chama o Architect com prompt de compromisso. Retorna o patch/código gerado ou None em falha.
    Também grava em Redis em architect_fallback_patch_key(issue_id).
    """
    if not OLLAMA_BASE_URL:
        return None
    issue_ctx = _get_issue_context(r, issue_id)
    reason = (rejection_reason or "Rejeição pelo Architect (razão não informada).").strip()[:500]

    system_prompt = """Você é o Architect (Arquiteto de Software). Esta tarefa recebeu 2 rejeições no code review.
Sua tarefa agora é de COMPROMISSO: gerar o código ou patch (unified diff) MÍNIMO que tornaria este PR aprovável.
Respeite SOLID, testes e ADRs. Responda APENAS com o código ou o patch (diff), sem explicação longa.
Se for patch, use formato unified diff (começando por --- ou diff -u)."""

    user_content = f"""Issue id: {issue_id}. Branch: {branch or '(não informada)'}. Título: {title or '(vazio)'}.

Motivo da última rejeição: {reason}

Contexto da issue (especificação/critérios de aceite):
{issue_ctx or '(nenhum contexto no Redis)'}

Gere o código ou patch mínimo que tornaria este PR aprovável. Output apenas código/diff."""

    body = {
        "model": ARCHITECT_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "stream": False,
    }
    url = f"{OLLAMA_BASE_URL}/api/chat"
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=ARCHITECT_FALLBACK_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[architect_fallback] Erro Ollama: {e}", file=sys.stderr)
        return None

    content = ""
    try:
        content = (data.get("message") or {}).get("content") or ""
    except Exception:
        pass
    if isinstance(content, bytes):
        content = content.decode("utf-8", errors="replace")
    content = content.strip()
    if not content:
        return None

    key = architect_fallback_patch_key(issue_id)
    try:
        r.set(key, content, ex=86400 * 7)  # 7 dias
    except Exception:
        pass
    try:
        send_slack(f"*ClawDevs — Fallback Architect (2º strike)*\nIssue `{issue_id}`: patch de compromisso gerado. Ver Redis key `{key}`.")
    except Exception:
        pass
    return content


def main():
    if len(sys.argv) < 2:
        print("Uso: architect_fallback.py <issue_id> [rejection_reason]", file=sys.stderr)
        sys.exit(1)
    issue_id = sys.argv[1].strip()
    reason = " ".join(sys.argv[2:]).strip() if len(sys.argv) > 2 else ""
    r = get_redis()
    out = run_fallback(r, issue_id, rejection_reason=reason)
    if out:
        print(out[:2000] + ("…" if len(out) > 2000 else ""))
        sys.exit(0)
    sys.exit(1)


if __name__ == "__main__":
    main()
