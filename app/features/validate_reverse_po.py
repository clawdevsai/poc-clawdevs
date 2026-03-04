#!/usr/bin/env python3
"""
Validação reversa (PO) — truncamento-finops. Compara o resumo gerado com os critérios de aceite originais.
Se o resumo omitir um critério fundamental, retorna falha (exit 1); PO deve rejeitar o truncamento.
Uso: python validate_reverse_po.py --summary summary.md --criteria issue.md
      ou: python validate_reverse_po.py --summary summary.md --criteria-stdin < issue.md
Saída: exit 0 se OK, 1 se algum critério foi omitido; mensagens em stderr.
"""
import argparse
import re
import sys

CRITERIOS_TAG = "<!-- CRITERIOS_ACEITE -->"
CRITERIOS_END = "<!-- /CRITERIOS_ACEITE -->"


def extract_criteria(text: str) -> list[str]:
    """Extrai itens do bloco CRITERIOS_ACEITE (linhas que parecem 1., 2., - item)."""
    pattern = re.escape(CRITERIOS_TAG) + r"(.*?)" + re.escape(CRITERIOS_END)
    m = re.search(pattern, text, re.DOTALL)
    if not m:
        return []
    block = m.group(1).strip()
    items = []
    for line in block.splitlines():
        line = line.strip()
        if not line:
            continue
        # Remover marcador (1., 2., -)
        line = re.sub(r"^[\d]+[.)]\s*", "", line)
        line = re.sub(r"^-\s*", "", line)
        if len(line) > 10:
            items.append(line)
    return items


def summary_mentions(summary: str, criterion: str) -> bool:
    """Heurística: o resumo menciona o critério? (palavras-chave ou substring)."""
    summary_lower = summary.lower()
    # Pegar primeiras 5–7 palavras do critério como semente
    words = [w for w in criterion.lower().split() if len(w) > 2][:7]
    if not words:
        return True
    # Pelo menos 2 palavras do critério devem aparecer no resumo
    return sum(1 for w in words if w in summary_lower) >= min(2, len(words))


def main() -> None:
    ap = argparse.ArgumentParser(description="Validação reversa PO (truncamento-finops)")
    ap.add_argument("--summary", required=True, help="Arquivo com o resumo gerado")
    ap.add_argument("--criteria", help="Arquivo com critérios de aceite (bloco CRITERIOS_ACEITE)")
    ap.add_argument("--criteria-stdin", action="store_true", help="Ler critérios de stdin")
    args = ap.parse_args()
    with open(args.summary, "r", encoding="utf-8", errors="replace") as f:
        summary = f.read()
    if args.criteria_stdin:
        criteria_text = sys.stdin.read()
    elif args.criteria:
        with open(args.criteria, "r", encoding="utf-8", errors="replace") as f:
            criteria_text = f.read()
    else:
        print("Forneça --criteria ou --criteria-stdin.", file=sys.stderr)
        sys.exit(2)
    criteria_list = extract_criteria(criteria_text)
    if not criteria_list:
        print("Nenhum critério encontrado (tag CRITERIOS_ACEITE).", file=sys.stderr)
        sys.exit(0)
    missing = []
    for c in criteria_list:
        if not summary_mentions(summary, c):
            missing.append(c[:80] + ("..." if len(c) > 80 else ""))
    if missing:
        print("Validação reversa: FALHOU — resumo omite critérios:", file=sys.stderr)
        for m in missing:
            print(f"  - {m}", file=sys.stderr)
        sys.exit(1)
    print("Validação reversa: OK — resumo cobre os critérios.", file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
