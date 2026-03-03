#!/usr/bin/env python3
"""
Pre-flight Summarize (truncamento-finops). Para payloads com mais de N interações destinados à nuvem,
o orquestrador deve interceptar, chamar modelo local para resumir e substituir o histórico pelo resumo.
Uso: PREFLIGHT_SUMMARIZE_MIN_INTERACTIONS=3 OLLAMA_BASE_URL=http://... python preflight_summarize.py [--interactions 4] < payload.json
      ou: echo '{"messages":[...]}' | python preflight_summarize.py
Saída: payload com histórico substituído por resumo (se interactions > min), ou payload original.
Se OLLAMA_BASE_URL não estiver definido, retorna payload como-is (modo pass-through).
"""
import json
import os
import sys
import urllib.error
import urllib.request

MIN_INTERACTIONS = int(os.environ.get("PREFLIGHT_SUMMARIZE_MIN_INTERACTIONS", "3"))
OLLAMA_BASE_URL = (os.environ.get("OLLAMA_BASE_URL") or "").strip().rstrip("/")
PREFLIGHT_MODEL = os.environ.get("PREFLIGHT_SUMMARIZE_MODEL", "llama3:8b")
PREFLIGHT_TIMEOUT = int(os.environ.get("PREFLIGHT_SUMMARIZE_TIMEOUT", "60"))


def count_interactions(payload) -> int:
    """Conta interações (mensagens ou itens em lista) no payload."""
    if isinstance(payload, dict):
        if "messages" in payload:
            return len(payload.get("messages", []))
        if "history" in payload:
            return len(payload.get("history", []))
        if "interactions" in payload:
            return int(payload.get("interactions", 0))
    if isinstance(payload, list):
        return len(payload)
    return 0


def summarize_via_ollama(text: str) -> str:
    """Chama Ollama para gerar resumo executivo denso do texto."""
    if not OLLAMA_BASE_URL or not text.strip():
        return text
    body = {
        "model": PREFLIGHT_MODEL,
        "prompt": f"Resuma o seguinte em um único parágrafo executivo denso (máx. 300 palavras), preservando decisões e critérios de aceite:\n\n{text[:12000]}",
        "stream": False,
    }
    req = urllib.request.Request(
        f"{OLLAMA_BASE_URL}/api/generate",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=PREFLIGHT_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return (data.get("response") or text).strip()
    except Exception:
        return text


def main() -> None:
    if not sys.stdin.isatty():
        payload_str = sys.stdin.read()
    else:
        print("Uso: pipe do payload JSON para stdin ou --file <path>", file=sys.stderr)
        sys.exit(2)
    try:
        payload = json.loads(payload_str)
    except json.JSONDecodeError:
        print(payload_str, end="")
        return
    n = count_interactions(payload)
    if n <= MIN_INTERACTIONS or not OLLAMA_BASE_URL:
        print(json.dumps(payload, ensure_ascii=False), end="")
        return
    # Construir texto a resumir a partir de messages/history
    parts = []
    if isinstance(payload, dict) and "messages" in payload:
        for m in payload["messages"]:
            if isinstance(m, dict):
                role = m.get("role", "")
                content = m.get("content", "")
                parts.append(f"[{role}]: {content[:2000]}")
            else:
                parts.append(str(m)[:2000])
    elif isinstance(payload, dict) and "history" in payload:
        for h in payload["history"]:
            parts.append(str(h)[:2000])
    else:
        parts.append(payload_str[:12000])
    text_to_summarize = "\n\n".join(parts)
    summary = summarize_via_ollama(text_to_summarize)
    if isinstance(payload, dict):
        if "messages" in payload:
            payload["messages"] = [{"role": "system", "content": f"[Resumo pré-envio à nuvem — {n} interações]: {summary}"}]
        if "history" in payload:
            payload["history"] = [summary]
        payload["_preflight_summarized"] = True
        payload["_preflight_interaction_count"] = n
    print(json.dumps(payload, ensure_ascii=False), end="")


if __name__ == "__main__":
    main()
