#!/usr/bin/env python3
"""
Truncamento na borda (truncamento-finops). Aplica limite de tokens ao payload ANTES de enfileirar no Redis.
Mantém cabeçalho e causa raiz (final); remove miolo de logs/stack trace. Não usa LLM.
Ref: docs/issues/041-truncamento-contexto-finops.md, docs/07-configuracao-e-prompts.md
Uso: echo "<payload>" | python truncate_payload_border.py [--max-tokens 4000] [--head 20] [--tail 30]
      ou: python truncate_payload_border.py --stdin < arquivo.txt
Saída: payload truncado em stdout (ou JSON com key "truncated_payload" se --json).
"""
import argparse
import json
import os
import sys

# Aproximação: ~4 chars por token para inglês/código; configurável
CHARS_PER_TOKEN = int(os.environ.get("TRUNCATE_CHARS_PER_TOKEN", "4"))
DEFAULT_MAX_TOKENS = int(os.environ.get("TRUNCATE_BORDER_MAX_TOKENS", "4000"))
DEFAULT_HEAD = int(os.environ.get("TRUNCATE_BORDER_KEEP_HEAD_LINES", "20"))
DEFAULT_TAIL = int(os.environ.get("TRUNCATE_BORDER_KEEP_TAIL_LINES", "30"))


def estimate_tokens(text: str) -> int:
    """Estimativa de tokens por caracteres (evita depender de tiktoken no borda)."""
    return max(1, len(text) // CHARS_PER_TOKEN)


def truncate_payload(
    payload: str,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    keep_head_lines: int = DEFAULT_HEAD,
    keep_tail_lines: int = DEFAULT_TAIL,
) -> tuple[str, bool]:
    """
    Trunca payload mantendo as primeiras keep_head_lines e as últimas keep_tail_lines.
    Se estiver dentro do limite, retorna (payload, False). Caso contrário (truncated, True).
    """
    if not payload:
        return payload, False
    current = estimate_tokens(payload)
    if current <= max_tokens:
        return payload, False
    lines = payload.splitlines()
    if len(lines) <= keep_head_lines + keep_tail_lines:
        # Cortar por caracteres
        max_chars = max_tokens * CHARS_PER_TOKEN
        head_chars = (keep_head_lines * 50)  # aprox
        tail_chars = (keep_tail_lines * 50)
        if len(payload) <= max_chars:
            return payload, False
        head = payload[:head_chars]
        tail = payload[-tail_chars:]
        sep = "\n... [truncado na borda - miolo removido] ...\n"
        return head + sep + tail, True
    head_lines = lines[:keep_head_lines]
    tail_lines = lines[-keep_tail_lines:]
    truncated = "\n".join(head_lines) + "\n... [truncado na borda - miolo removido] ...\n" + "\n".join(tail_lines)
    return truncated, True


def main() -> None:
    ap = argparse.ArgumentParser(description="Truncamento na borda (truncamento-finops) — limite de tokens antes de enfileirar")
    ap.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS, help="Limite de tokens")
    ap.add_argument("--head", type=int, default=DEFAULT_HEAD, help="Linhas a manter no início")
    ap.add_argument("--tail", type=int, default=DEFAULT_TAIL, help="Linhas a manter no final")
    ap.add_argument("--stdin", action="store_true", help="Ler payload de stdin (default se não houver arquivo)")
    ap.add_argument("--json", action="store_true", help="Saída JSON com truncated_payload e was_truncated")
    ap.add_argument("file", nargs="?", help="Arquivo com payload (ou stdin)")
    args = ap.parse_args()

    if args.file:
        with open(args.file, "r", encoding="utf-8", errors="replace") as f:
            payload = f.read()
    else:
        payload = sys.stdin.read()

    out, was_truncated = truncate_payload(
        payload,
        max_tokens=args.max_tokens,
        keep_head_lines=args.head,
        keep_tail_lines=args.tail,
    )
    if args.json:
        print(json.dumps({"truncated_payload": out, "was_truncated": was_truncated}, ensure_ascii=False))
    else:
        print(out, end="" if out and not out.endswith("\n") else "")


if __name__ == "__main__":
    main()
