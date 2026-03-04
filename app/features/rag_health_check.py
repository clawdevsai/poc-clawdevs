#!/usr/bin/env python3
"""
RAG health check determinístico (Fase 3 — 127). Sem LLM.
(1) Datas de indexação dos docs usados pelo PO vs último commit na main.
(2) Estrutura de pastas da épico no disco.
(3) Se houver conflito → forçar atualização da memória local do orquestrador.
Uso: rag_health_check.py [--epic-id ID] [--repo /path]
Ref: docs/issues/127-disjuntor-draft-rejected-rag-health-check.md
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path


def get_last_commit_ts(repo_path: Path) -> float | None:
    try:
        r = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "main"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if r.returncode == 0 and r.stdout.strip():
            return float(r.stdout.strip())
        r = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return float(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip() else None
    except Exception:
        return None


def get_index_ts(index_path: Path) -> float | None:
    if not index_path.exists():
        return None
    try:
        return index_path.stat().st_mtime
    except OSError:
        return None


def check_epic_folders(repo_path: Path, epic_id: str) -> bool:
    """Verifica se estrutura esperada da épico existe (ex.: docs, scripts)."""
    # Placeholder: epic pode ser um subpath; por ora checamos raiz.
    for name in ("docs", "scripts"):
        d = repo_path / name
        if not d.is_dir():
            return False
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description="RAG health check determinístico")
    ap.add_argument("--epic-id", default=os.environ.get("EPIC_ID", ""), help="ID da épico")
    ap.add_argument("--repo", default=os.environ.get("REPO_PATH", "."), help="Caminho do repositório")
    ap.add_argument("--index-file", default=os.environ.get("RAG_INDEX_META", ""), help="Arquivo de metadados de indexação (mtime comparado à main)")
    args = ap.parse_args()
    repo = Path(args.repo).resolve()
    if not (repo / ".git").exists():
        print("[rag_health_check] Repo não encontrado ou não é git.", file=sys.stderr)
        return 2
    last_commit = get_last_commit_ts(repo)
    index_ts = get_index_ts(Path(args.index_file)) if args.index_file else None
    conflict = False
    if last_commit is not None and index_ts is not None and index_ts < last_commit:
        print("[rag_health_check] Conflito: indexação mais antiga que último commit na main.")
        conflict = True
    if not check_epic_folders(repo, args.epic_id):
        print("[rag_health_check] Estrutura de pastas da épico ausente ou incompleta.", file=sys.stderr)
        conflict = True
    if conflict:
        print("force_update")
        return 1
    print("ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
