#!/usr/bin/env python3
"""Analisador de entropia com consciência contextual (128).
Arquivos na whitelist de extensões (.map, .wasm, .min.js, etc.) têm tolerância alta;
arquivos .sh ou texto esperado com entropia alta falham (possível ofuscação).
"""
from __future__ import annotations

import math
import os
import sys

# Extensões com tolerância de entropia muito maior (minificados, source maps, wasm)
HIGH_ENTROPY_EXTENSIONS = frozenset(
    x.strip().lower()
    for x in os.environ.get("QUARANTINE_HIGH_ENTROPY_EXT", ".map,.wasm,.min.js,.min.css,.bundle.js").split(",")
    if x.strip()
)
# Limite de entropia (bits por byte) para arquivos fora da whitelist (texto esperado)
MAX_ENTROPY_PLAINTEXT = float(os.environ.get("QUARANTINE_MAX_ENTROPY_PLAINTEXT", "5.5"))
# Limite para arquivos na whitelist (quase binário)
MAX_ENTROPY_HIGH_TOLERANCE = float(os.environ.get("QUARANTINE_MAX_ENTROPY_HIGH", "7.9"))


def entropy(data: bytes) -> float:
    """Entropia de Shannon em bits por byte."""
    if not data:
        return 0.0
    freq = {}
    for b in data:
        freq[b] = freq.get(b, 0) + 1
    n = len(data)
    return -sum((c / n) * math.log2(c / n) for c in freq.values())


def get_ext(path: str) -> str:
    base = os.path.basename(path)
    if "." in base:
        return "." + base.rsplit(".", 1)[-1].lower()
    return ""


def check_file(path: str, content: bytes) -> tuple[bool, float, str]:
    """Retorna (passou, entropia, motivo)."""
    ext = get_ext(path)
    high_tolerance = ext in HIGH_ENTROPY_EXTENSIONS
    limit = MAX_ENTROPY_HIGH_TOLERANCE if high_tolerance else MAX_ENTROPY_PLAINTEXT
    e = entropy(content)
    if e <= limit:
        return True, e, ""
    return False, e, f"entropia {e:.2f} > {limit} (high_tolerance={high_tolerance})"


def main() -> int:
    """CLI: quarantine_entropy.py <dir> [dir2 ...]. Exit 0 = todos passaram, 1 = algum falhou."""
    if len(sys.argv) < 2:
        print("Uso: quarantine_entropy.py <diretório> [dir2 ...]", file=sys.stderr)
        return 2
    failed = []
    for d in sys.argv[1:]:
        if not os.path.isdir(d):
            print(f"Diretório não encontrado: {d}", file=sys.stderr)
            failed.append((d, 0.0, "not a directory"))
            continue
        for root, _dirs, files in os.walk(d):
            for f in files:
                path = os.path.join(root, f)
                try:
                    with open(path, "rb") as fp:
                        content = fp.read()
                except OSError as err:
                    failed.append((path, 0.0, str(err)))
                    continue
                ok, e, msg = check_file(path, content)
                if not ok:
                    failed.append((path, e, msg))
    if failed:
        for path, e, msg in failed:
            print(f"FAIL\t{path}\t{msg}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
