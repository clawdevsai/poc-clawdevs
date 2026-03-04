#!/usr/bin/env bash
# Wrapper: delega para transcription/m4a_to_md.sh.
# Uso: ./scripts/m4a_to_md.sh arquivo.m4a [ -o saida.md ] ...
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/transcription/m4a_to_md.sh" "$@"
