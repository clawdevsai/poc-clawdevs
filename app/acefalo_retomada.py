#!/usr/bin/env python3
"""
Retomada automática após cluster acéfalo (124): checkout limpo, restaura fila (opcional), limpa pausa.
Chamar quando health check estiver estável por 3 ciclos consecutivos.
Ref: docs/06-operacoes.md, docs/issues/124-contingencia-cluster-acefalo.md
"""
import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
from acefalo_redis import get_redis, set_pause_consumption, restore_streams_from_json


REPO_PATH = os.getenv("ACEFALO_REPO_PATH", "")
SNAPSHOT_DIR = os.getenv("ACEFALO_SNAPSHOT_DIR", "/tmp/acefalo_snapshot")
RESTORE_FROM_SNAPSHOT = os.getenv("ACEFALO_RESTORE_FROM_SNAPSHOT", "0") == "1"


def git_checkout_clean(repo_path: str, main_branch: str = "main") -> bool:
    """Volta à branch principal (checkout limpo). Retorna True se OK."""
    if not repo_path or not os.path.isdir(os.path.join(repo_path, ".git")):
        return True
    try:
        subprocess.run(
            ["git", "checkout", main_branch],
            cwd=repo_path,
            check=True,
            capture_output=True,
            timeout=30,
        )
        subprocess.run(
            ["git", "reset", "--hard", "HEAD"],
            cwd=repo_path,
            check=True,
            capture_output=True,
            timeout=30,
        )
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return False


def latest_snapshot_path() -> str:
    """Retorna o path do snapshot mais recente em SNAPSHOT_DIR, ou ''."""
    p = Path(SNAPSHOT_DIR)
    if not p.is_dir():
        return ""
    files = list(p.glob("queue_snapshot_*.json"))
    if not files:
        return ""
    return str(max(files, key=lambda f: f.stat().st_mtime))


def run_retomada(repo_path: str = None, main_branch: str = "main", r=None) -> dict:
    """
    Executa: (1) checkout limpo para main_branch; (2) opcionalmente restaura fila do último snapshot;
             (3) clear cluster:pause_consumption.
    Retorna dict com success e mensagem.
    """
    if r is None:
        r = get_redis()
    repo_path = repo_path or REPO_PATH
    result = {"checkout_ok": True, "restored": False, "pause_cleared": False}

    result["checkout_ok"] = git_checkout_clean(repo_path, main_branch)

    if RESTORE_FROM_SNAPSHOT:
        path = latest_snapshot_path()
        if path:
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                restore_streams_from_json(data, r=r, clear_before_restore=False)
                result["restored"] = True
            except Exception as e:
                result["restore_error"] = str(e)

    set_pause_consumption(False, r=r)
    result["pause_cleared"] = True

    return result


if __name__ == "__main__":
    res = run_retomada()
    print(json.dumps(res, indent=2))
    sys.exit(0 if res.get("checkout_ok") and res.get("pause_cleared") else 1)
