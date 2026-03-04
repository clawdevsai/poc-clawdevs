#!/usr/bin/env python3
"""
Gancho de validação de contexto (truncamento-finops). Operado localmente, ANTES da sumarização na nuvem.
Varre o buffer de trabalho em busca de intenções do usuário ou regras informais sem tag.
Se o modelo local identificar algo crítico, propõe extração para SESSION-STATE (arquivo de estado).
Objetivo: preservar valor de negócio sem gastar API; mitigar amnésia funcional.
Ref: docs/issues/041-truncamento-contexto-finops.md, docs/07-configuracao-e-prompts.md (2.2)
Uso: CONTEXT_VALIDATION_HOOK_ENABLED=1 python context_validation_hook.py --buffer-file path/to/buffer.md [--session-state path/to/SESSION-STATE.md]
      Sem LLM: modo stub retorna lista vazia. Com OLLAMA_BASE_URL: opcional chamada a modelo local (implementação futura).
"""
import argparse
import os
import sys

# Se 0, não faz nada (saída vazia)
CONTEXT_VALIDATION_HOOK_ENABLED = os.environ.get("CONTEXT_VALIDATION_HOOK_ENABLED", "1") == "1"
INVARIANT_TAG = os.environ.get("INVARIANT_TAG", "<!-- INVARIANTE_NEGOCIO -->")

# Heurística extraída para testes unitários (sem I/O)
KEYWORDS_REGRA = ("nunca", "sempre", "deve ", "não pode", "obrigatório", "proibido")


def propose_from_buffer_text(buffer_text: str, invariant_tag: str = None) -> list:
    """
    Retorna lista de propostas { "text": linha, "suggested_tag": tag } para linhas que parecem regra.
    Não usa arquivo nem LLM; apenas heurística local.
    """
    tag = invariant_tag if invariant_tag is not None else INVARIANT_TAG
    proposals = []
    for line in buffer_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or tag in line:
            continue
        if any(kw in line.lower() for kw in KEYWORDS_REGRA):
            if len(line) > 20 and len(line) < 500:
                proposals.append({"text": line, "suggested_tag": tag})
    return proposals


def main() -> None:
    ap = argparse.ArgumentParser(description="Gancho validação de contexto (truncamento-finops) — propor extração para SESSION-STATE")
    ap.add_argument("--buffer-file", required=True, help="Arquivo do buffer de trabalho")
    ap.add_argument("--session-state", default="SESSION-STATE.md", help="Arquivo de estado da sessão")
    ap.add_argument("--dry-run", action="store_true", help="Apenas listar propostas, não escrever")
    args = ap.parse_args()

    if not CONTEXT_VALIDATION_HOOK_ENABLED:
        print("[]")
        return

    if not os.path.isfile(args.buffer_file):
        print("[]")
        return

    with open(args.buffer_file, "r", encoding="utf-8", errors="replace") as f:
        buffer_text = f.read()

    proposals = propose_from_buffer_text(buffer_text)

    if args.dry_run:
        for p in proposals:
            print(p["text"][:80] + ("..." if len(p["text"]) > 80 else ""))
        return

    # Saída JSON para orquestrador processar (inserir em SESSION-STATE com tag)
    import json
    print(json.dumps({"proposals": proposals}, ensure_ascii=False))


if __name__ == "__main__":
    main()
