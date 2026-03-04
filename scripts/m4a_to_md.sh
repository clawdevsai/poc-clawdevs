#!/usr/bin/env bash
# Wrapper para transcrição M4A → MD (009). Chama app/features/m4a_to_md.py.
# Uso: ./scripts/m4a_to_md.sh arquivo.m4a [ -o saida.md ] [ -m base ] [ -d auto|cuda|cpu ]
# Ref: docs/02-infra/09-setup-e-scripts.md, docs/08-technical-notes/issues/009-transcricao-audio-m4a-to-md.md
set -e
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 "$REPO_ROOT/app/features/m4a_to_md.py" "$@"
