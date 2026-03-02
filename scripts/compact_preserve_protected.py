#!/usr/bin/env python3
"""
truncamento-finops: Compactação de buffer preservando blocos protegidos (CRITERIOS_ACEITE e INVARIANTE_NEGOCIO).
O script de limpeza/compacted do DevOps deve usar regex para NUNCA apagar linhas dentro dessas tags.
Ref: docs/07-configuracao-e-prompts.md (2.2 e 2.3), docs/issues/041-truncamento-contexto-finops.md
Uso: python compact_preserve_protected.py < input.md > output.md
      ou --extract: apenas extrai os blocos protegidos (para validação reversa PO).
"""
import argparse
import re
import sys

# Tags do ConfigMap finops-config (config-perfis / truncamento-finops) — podem ser overriden por env
CRITERIOS_TAG = "<!-- CRITERIOS_ACEITE -->"
CRITERIOS_END = "<!-- /CRITERIOS_ACEITE -->"
INVARIANT_TAG = "<!-- INVARIANTE_NEGOCIO -->"
INVARIANT_END = "<!-- /INVARIANTE_NEGOCIO -->"


def extract_protected_blocks(text: str) -> list[tuple[str, str]]:
    """Retorna lista de (nome_bloco, conteúdo)."""
    blocks = []
    for name, start, end in [
        ("CRITERIOS_ACEITE", CRITERIOS_TAG, CRITERIOS_END),
        ("INVARIANTE_NEGOCIO", INVARIANT_TAG, INVARIANT_END),
    ]:
        pattern = re.escape(start) + r"(.*?)" + re.escape(end)
        for m in re.finditer(pattern, text, re.DOTALL):
            blocks.append((name, m.group(1).strip()))
    return blocks


def compact_preserving_protected(text: str, max_lines_outside: int = 50) -> str:
    """
    Mantém todos os blocos protegidos intactos; reduz o restante a no máximo max_lines_outside linhas.
    """
    blocks = extract_protected_blocks(text)
    # Remover blocos protegidos do texto e guardar placeholders
    remaining = text
    placeholders = []
    for name, block in blocks:
        start = CRITERIOS_TAG if name == "CRITERIOS_ACEITE" else INVARIANT_TAG
        end = CRITERIOS_END if name == "CRITERIOS_ACEITE" else INVARIANT_END
        pattern = re.escape(start) + r".*?" + re.escape(end)
        placeholder = f"\n\n__PROTECTED_{name}_{len(placeholders)}__\n\n"
        placeholders.append((placeholder, start + "\n" + block + "\n" + end))
        remaining = re.sub(pattern, placeholder, remaining, count=1, flags=re.DOTALL)

    lines = remaining.splitlines()
    if len(lines) <= max_lines_outside:
        result = remaining
    else:
        head = max_lines_outside // 2
        tail = max_lines_outside - head
        result = "\n".join(lines[:head]) + "\n\n... [compactado - blocos protegidos preservados abaixo] ...\n\n" + "\n".join(lines[-tail:])

    for placeholder, block_content in placeholders:
        result = result.replace(placeholder, block_content)
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description="Compactar buffer preservando blocos CRITERIOS_ACEITE e INVARIANTE_NEGOCIO")
    ap.add_argument("--extract", action="store_true", help="Apenas extrair blocos protegidos (um por linha, formato nome:conteúdo)")
    ap.add_argument("--max-lines", type=int, default=50, help="Máx. linhas fora dos blocos no output compactado")
    args = ap.parse_args()

    text = sys.stdin.read()
    blocks = extract_protected_blocks(text)
    if args.extract:
        for name, content in blocks:
            print(f"--- {name} ---")
            print(content)
            print()
        return
    result = compact_preserving_protected(text, max_lines_outside=args.max_lines)
    print(result, end="")


if __name__ == "__main__":
    main()
