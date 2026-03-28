#!/usr/bin/env bash

# Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

set -euo pipefail

ollama serve &

for i in $(seq 1 60); do
  if ollama list >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

if [ "${OLLAMA_AUTO_PULL_MODELS:-false}" = "true" ]; then
  # Em background: nao bloqueia o processo principal; o servidor ja responde ao healthcheck.
  (
    for model in ${OLLAMA_BOOT_MODELS:-}; do
      ollama pull "${model}" || echo "Aviso: pull do modelo ${model} falhou."
    done
  ) &
else
  echo "OLLAMA_AUTO_PULL_MODELS=false: iniciando sem pulls automaticos."
fi

wait
