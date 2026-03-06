#!/usr/bin/env python3
"""
Matriz de confiança: verificação de pacote por nome@versão e hash (128 evolução).
Se o pacote estiver na whitelist e o hash coincidir, dispensar entropia restritiva no pipeline de quarentena.
Ref: docs/44-fase2-seguranca-automacao.md § 2.2, docs/issues/128-sast-entropia-quarentena.md
"""
from __future__ import annotations

import os
import sys

# Formato: um por linha: name@version=sha256:hex ou name@version (só nome/versão)
# Ou caminho para arquivo com o mesmo formato
TRUSTED_PACKAGES_ENV = os.environ.get("TRUSTED_PACKAGES", "")
TRUSTED_PACKAGES_FILE = os.environ.get("TRUSTED_PACKAGES_FILE", "")


def _load_trusted() -> dict[str, str]:
    """Retorna dict name@version -> hash (ou '' se só nome@version)."""
    out = {}
    raw = TRUSTED_PACKAGES_ENV.strip()
    if TRUSTED_PACKAGES_FILE and os.path.isfile(TRUSTED_PACKAGES_FILE):
        with open(TRUSTED_PACKAGES_FILE, "r", encoding="utf-8", errors="replace") as f:
            raw = raw + "\n" + f.read()
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, hash_val = line.split("=", 1)
            out[key.strip().lower()] = hash_val.strip()
        else:
            out[line.lower()] = ""
    return out


_TRUSTED = None


def get_trusted() -> dict[str, str]:
    global _TRUSTED
    if _TRUSTED is None:
        _TRUSTED = _load_trusted()
    return _TRUSTED


def is_trusted(package: str, version: str, expected_hash: str = "") -> tuple[bool, str]:
    """
    Retorna (trusted, reason). package e version podem ser "name" e "1.0.0" ou "name@1.0.0".
    Se expected_hash for fornecido, exige que a entrada na whitelist tenha o mesmo hash.
    """
    key = f"{package}@{version}".lower() if version else package.lower()
    if "@" in package and not version:
        key = package.lower()
    trusted_map = get_trusted()
    if key in trusted_map:
        listed_hash = trusted_map[key]
        if expected_hash and listed_hash:
            if listed_hash.lower() == expected_hash.lower():
                return True, "hash_match"
            return False, "hash_mismatch"
        if expected_hash and not listed_hash:
            return False, "no_listed_hash"
        return True, "whitelist"
    return False, "not_in_whitelist"


def main() -> int:
    """CLI: trusted_package_verify.py <package> [version] [hash]. Exit 0 = trusted, 1 = not trusted, 2 = usage."""
    if len(sys.argv) < 2:
        print("Uso: trusted_package_verify.py <package> [version] [expected_hash]", file=sys.stderr)
        return 2
    pkg = sys.argv[1]
    ver = sys.argv[2] if len(sys.argv) > 2 else ""
    h = sys.argv[3] if len(sys.argv) > 3 else ""
    if "@" in pkg and not ver:
        parts = pkg.split("@", 1)
        pkg, ver = parts[0], parts[1]
    trusted, reason = is_trusted(pkg, ver, h)
    if trusted:
        print(f"TRUSTED\t{reason}")
        return 0
    print(f"NOT_TRUSTED\t{reason}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
