#!/usr/bin/env python3
"""
Aplica limite de max tokens por request (truncamento-finops). Para uso antes de enviar payload à nuvem.
Lê MAX_TOKENS_PER_REQUEST do env (ou --max-tokens); trunca o payload para caber no limite.
Uso: MAX_TOKENS_PER_REQUEST_CEO=8192 python apply_max_tokens.py [--profile ceo|po|default] < payload.txt
      ou: python apply_max_tokens.py --max-tokens 4096 < payload.txt
Saída: payload truncado em stdout.
"""
import argparse
import os
import sys

# Usar mesma lógica do truncate_payload_border
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
try:
    from truncate_payload_border import truncate_payload
except ImportError:
    def truncate_payload(payload, max_tokens=4096, keep_head_lines=20, keep_tail_lines=30):
        return (payload, False)


def main() -> None:
    ap = argparse.ArgumentParser(description="Aplicar max tokens ao payload (truncamento-finops)")
    ap.add_argument("--profile", choices=["ceo", "po", "default"], default="default", help="Perfil (lê env MAX_TOKENS_PER_REQUEST_CEO etc.)")
    ap.add_argument("--max-tokens", type=int, default=0, help="Override: limite de tokens")
    args = ap.parse_args()
    if args.max_tokens > 0:
        max_tokens = args.max_tokens
    else:
        if args.profile == "ceo":
            max_tokens = int(os.environ.get("MAX_TOKENS_PER_REQUEST_CEO", "8192"))
        elif args.profile == "po":
            max_tokens = int(os.environ.get("MAX_TOKENS_PER_REQUEST_PO", "8192"))
        else:
            max_tokens = int(os.environ.get("MAX_TOKENS_PER_REQUEST_CLOUD_DEFAULT", "4096"))
    payload = sys.stdin.read()
    out, _ = truncate_payload(payload, max_tokens=max_tokens)
    print(out, end="")


if __name__ == "__main__":
    main()
