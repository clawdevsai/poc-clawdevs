#!/usr/bin/env bash
# Wrapper para transcrição M4A → MD (009). Chama app/features/m4a_to_md.py.
# Uso: ./scripts/transcription/m4a_to_md.sh arquivo.m4a [ -o saida.md ] [ -m base ] [ -d auto|cuda|cpu ]
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
exec python3 "$REPO_ROOT/app/features/m4a_to_md.py" "$@"
