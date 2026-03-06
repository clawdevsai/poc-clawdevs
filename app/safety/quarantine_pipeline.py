#!/usr/bin/env python3
"""
Pipeline de quarentena automatizado (128 evolução).
Ordem: (1) opcional matriz de confiança para pacotes listados; (2) SAST semgrep; (3) entropia contextual.
Exit 0 = passou; 1 = falhou; 2 = uso.
Ref: docs/44-fase2-seguranca-automacao.md § 2.2, docs/21-quarentena-disco-pipeline.md
"""
from __future__ import annotations

import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

RUN_SAST = os.environ.get("QUARANTINE_RUN_SAST", "1") == "1"
RUN_ENTROPY = os.environ.get("QUARANTINE_RUN_ENTROPY", "1") != "0"


def run_sast(dir_path: str) -> tuple[bool, str]:
    """Executa semgrep --config auto --strict. Retorna (ok, msg)."""
    try:
        r = subprocess.run(
            ["semgrep", "scan", "--config", "auto", "--strict", "--quiet", "--error", dir_path],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=dir_path,
        )
        if r.returncode != 0:
            return False, (r.stderr or r.stdout or "semgrep found issues")[:500]
        return True, ""
    except FileNotFoundError:
        return True, "semgrep not installed, skip"
    except subprocess.TimeoutExpired:
        return False, "semgrep timeout"
    except Exception as e:
        return False, str(e)


def run_entropy(dir_path: str) -> tuple[bool, str]:
    """Executa quarantine_entropy.py. Retorna (ok, msg)."""
    try:
        from quarantine_entropy import main as entropy_main
    except ImportError:
        # CLI
        r = subprocess.run(
            [sys.executable, os.path.join(SCRIPT_DIR, "quarantine_entropy.py"), dir_path],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if r.returncode != 0:
            return False, (r.stderr or r.stdout or "entropy check failed")[:500]
        return True, ""
    old_argv = sys.argv
    sys.argv = ["quarantine_entropy.py", dir_path]
    try:
        code = entropy_main()
        return code == 0, "" if code == 0 else "entropy check failed"
    finally:
        sys.argv = old_argv


def main() -> int:
    if len(sys.argv) < 2:
        print("Uso: quarantine_pipeline.py <diretório_sandbox> [--skip-sast] [--skip-entropy]", file=sys.stderr)
        return 2
    dir_path = os.path.abspath(sys.argv[1])
    if not os.path.isdir(dir_path):
        print(f"Diretório não encontrado: {dir_path}", file=sys.stderr)
        return 2
    skip_sast = "--skip-sast" in sys.argv or not RUN_SAST
    skip_entropy = "--skip-entropy" in sys.argv or not RUN_ENTROPY

    if RUN_SAST and not skip_sast:
        ok, msg = run_sast(dir_path)
        if not ok and "not installed" not in msg.lower():
            print(f"SAST falhou: {msg}", file=sys.stderr)
            return 1
    if RUN_ENTROPY and not skip_entropy:
        ok, msg = run_entropy(dir_path)
        if not ok:
            print(f"Entropia falhou: {msg}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
