<!-- 
  Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.
 -->

# OpenClaw Runtime Image

Imagem otimizada para o `StatefulSet` do OpenClaw, com dependências e OpenClaw pré-instalados.

## Build local

```bash
docker build \
  --build-arg OPENCLAW_VERSION=2026.3.24 \
  -t clawdevsai/openclaw-runtime:2026.3.24 \
  -t clawdevsai/openclaw-runtime:latest \
  -f docker/clawdevs-openclaw/Dockerfile .
```

## Push Docker Hub

```bash
docker login -u clawdevsAI

docker push clawdevsai/openclaw-runtime:2026.3.24
docker push clawdevsai/openclaw-runtime:latest
```

## Uso na Stack Local

A stack local usa `make up` (docker run) e monta scripts/config de `docker/base/`.
O container inicia via `ENTRYPOINT` (`/usr/local/bin/openclaw-entrypoint.sh`) e executa, em ordem,
os scripts `docker/base/bootstrap-scripts/00-env.sh` ate `11-start-gateway.sh`.

## Skills por agente (layout OpenClaw)

No volume `OPENCLAW_STATE_DIR` (por padrão `/data/openclaw`), cada agente usa:

- **`/data/openclaw/workspace-<id>/skills/`** — skills específicas do agente (maior precedência).
- **`/data/openclaw/workspace-<id>/.agents/skills/`** — skills compartilhadas do projeto (`openclaw-config/agents/shared/skills/` no host).

O workspace compartilhado `backlog/implementation` replica `skills/` e `.agents/skills/` para o mesmo padrão. Referência: [OpenClaw — Skills](https://docs.openclaw.ai/tools/skills).
