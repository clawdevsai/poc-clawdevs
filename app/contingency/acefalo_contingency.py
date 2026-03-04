#!/usr/bin/env python3
"""
Ação imediata de contingência cluster acéfalo (124): branch efêmera, persistência da fila, pausa.
DevOps local é acionado (via evento Redis ou chamada deste script).
Ref: docs/06-operacoes.md, docs/issues/124-contingencia-cluster-acefalo.md
"""
import json
import os
import subprocess
import time
from pathlib import Path

# Importar após possível ajuste de path
import sys
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
from acefalo_redis import get_redis, set_pause_consumption, export_streams_to_json


REPO_PATH = os.getenv("ACEFALO_REPO_PATH", "")
SNAPSHOT_DIR = os.getenv("ACEFALO_SNAPSHOT_DIR", "/tmp/acefalo_snapshot")
STREAMS = ["cmd:strategy", "task:backlog", "draft.2.issue", "draft_rejected", "code:ready"]


def git_create_recovery_branch(repo_path: str) -> str:
    """Cria branch efêmera recovery-failsafe-YYYYMMDD-HHMMSS com commit do estado atual. Retorna o nome da branch."""
    if not repo_path or not os.path.isdir(os.path.join(repo_path, ".git")):
        return ""
    branch_name = f"recovery-failsafe-{time.strftime('%Y%m%d-%H%M%S')}"
    try:
        subprocess.run(
            ["git", "add", "-A"],
            cwd=repo_path,
            check=True,
            capture_output=True,
            timeout=30,
        )
        subprocess.run(
            ["git", "commit", "-m", f"contingency-acefalo checkpoint {branch_name}"],
            cwd=repo_path,
            capture_output=True,
            timeout=30,
        )
        subprocess.run(
            ["git", "checkout", "-b", branch_name],
            cwd=repo_path,
            check=True,
            capture_output=True,
            timeout=30,
        )
        return branch_name
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def persist_queue_to_file(r=None) -> str:
    """Exporta fila Redis para JSON em SNAPSHOT_DIR. Retorna caminho do arquivo."""
    Path(SNAPSHOT_DIR).mkdir(parents=True, exist_ok=True)
    data = export_streams_to_json(r=r, streams=STREAMS)
    path = os.path.join(SNAPSHOT_DIR, f"queue_snapshot_{int(time.time())}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return path


def run_contingency(repo_path: str = None, r=None) -> dict:
    """
    Executa: (1) commit em branch efêmera se repo_path tiver .git;
             (2) persiste fila em JSON;
             (3) pausa consumo (cluster:pause_consumption = 1).
    Retorna dict com branch, snapshot_path e status.
    """
    if r is None:
        r = get_redis()
    repo_path = repo_path or REPO_PATH
    result = {"branch": "", "snapshot_path": "", "pause_set": False}

    branch = git_create_recovery_branch(repo_path)
    result["branch"] = branch

    snapshot_path = persist_queue_to_file(r=r)
    result["snapshot_path"] = snapshot_path

    set_pause_consumption(True, r=r)
    result["pause_set"] = True

    return result
