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

# O que a aplicação ClawDevs AI faz

## Visão geral

O repositório **clawdevs-ai** define um stack em Docker Compose que sobe:

1. **Ollama** — API de modelos em `http://ollama:11434`, com modelos cloud configurados no bootstrap do container Ollama.
2. **OpenClaw** — gateway multi-agente num container Debian: instala o CLI via `install.sh`, gera `openclaw.json` e executa `openclaw gateway` na porta **18789** (probe e Service). Estado persistente em PVC `openclaw-data` montado em `/data/openclaw`.
3. **SearXNG** — busca interna no cluster; o bootstrap do OpenClaw expõe o comando `web-search` que chama `http://searxng:8080`.
4. **Painel de controle** — UI e API (`container/base/control-panel/`): acompanha agentes, sessões e filas; sobe junto com `make stack-apply` / `make clawdevs-up` (inclui `panel-db-migrate` no fluxo `clawdevs-up`).
5. **Ferramentas no container OpenClaw** — `gh` autenticado com `GIT_TOKEN`, `web-search` (SearXNG), `web-read` (Jina Reader em `https://r.jina.ai/...`), scripts `claw-repo-discover`, `claw-repo-ensure`, `claw-repo-switch` em `/data/openclaw/bin` e em `/usr/local/bin`.

O **StatefulSet** `clawdevs-ai` (container `openclaw`) é o núcleo: um time de agentes (CEO, PO, Arquiteto, Dev_Backend, Dev_Frontend, Dev_Mobile, QA_Engineer, DevOps_SRE, Security_Engineer, UX_Designer, DBA_Data_Engineer, Memory_Curator) com workspaces sob `/data/openclaw/workspace-*`, regras em `AGENTS.md` copiadas do ConfigMap `openclaw-agent-config`, e modelo padrão apontando para provedores Ollama no `openclaw.json`.

## Comportamento principal

- **Spec-Driven Development (SDD)** — templates e constitution em `container/base/openclaw-config/shared/`; artefatos esperados em `/data/openclaw/backlog/` (briefs, specs, tasks, user_story, implementation, status, etc.).
- **Delegação entre agentes** — `openclaw.json` habilita `agentToAgent` entre os IDs listados; CEO costuma orquestrar; executor técnico (ex.: Dev_Backend) trabalha a partir de TASK/issue conforme `AGENTS.md`.
- **Telegram** — binding padrão: agente **ceo** no canal Telegram (bot `TELEGRAM_BOT_TOKEN_CEO`, allowlist `TELEGRAM_CHAT_ID_CEO`). Mensagens de grupo fora da política containerem ser negadas pelas regras de `session.sendPolicy`.
- **GitHub** — contexto ativo em `/data/openclaw/contexts/active_repository.env` (`ACTIVE_GIT_REPOSITORY`, branch, org). Fallback de repo no bootstrap se `GIT_DEFAULT_REPOSITORY` não existir na org.
- **Crons nativos (gateway)** — variáveis `*_CRON_ENABLED`, `*_CRON_EXPR`, fuso `America/Sao_Paulo` no manifest disparam ciclos que invocam agentes (ex.: filas por label no GitHub). Valores efetivos estão no `openclaw-container.yaml` (ex.: dev_backend `0 * * * *`, dev_frontend `15 * * * *`, memory_curator `0 2 * * *`, etc.).
- **Roteador de erros** — com `AGENT_ERROR_ROUTER_ENABLED=true`, um loop observa sessões dos agentes e envia alerta ao CEO via `openclaw agent --agent ceo --message ...`.
- **Git hooks globais** — bloqueiam commit/push direto em `main`/`master` (caminho configurado para hooks em `/data/openclaw/git-hooks`).

## O que você containere fazer (exemplos)

### Operar o cluster

```bash
make preflight
make clawdevs-up
```

O `make clawdevs-up` / `make stack-apply` já inclui `openclaw-apply-gpu` (manifest em `container/overlays/gpu`). Para GPU só no Ollama em cenários manuais: `make openclaw-apply-gpu` ou fluxo `gpu-migrate-apply` (ver `docs/README.md`).

### Acessar o gateway e o painel na máquina local

```bash
docker-compose --context=clawdevs-ai port-forward service/clawdevs-ai 18789:18789
```

Ou, para expor gateway + API + frontend do painel de uma vez (Windows/Linux conforme `Makefile`):

```bash
make services-expose
```

Autenticação HTTP do gateway usa o token `OPENCLAW_GATEWAY_TOKEN` do `container/.env` (Bearer nas APIs do OpenClaw, conforme documentação do produto).

NodePort do Service (quando útil no Docker): **31879** → 18789.

### Abrir dashboard OpenClaw dentro do container

```bash
make openclaw-dashboard
```

(executa `openclaw dashboard --no-open` no container.)

### Entrar no container e usar ferramentas de bootstrap

```bash
docker-compose --context=clawdevs-ai exec -it statefulset/clawdevs-ai -c openclaw -- bash
```

```bash
claw-repo-discover
claw-repo-discover billing
claw-repo-switch minha-org/meu-repo develop
claw-repo-ensure minha-org/novo-repo --create
```

```bash
web-search licença MIT diferença Apache
web-read https://docs.github.com/en/rest
```

### Conversar com o CEO pelo Telegram

1. Preencher `TELEGRAM_BOT_TOKEN_CEO` e `TELEGRAM_CHAT_ID_CEO` no `container/.env`.
2. Aplicar o stack; o bot só aceita DMs/grupos allowlisted com esse chat id.
3. Enviar mensagem ao bot — o agente default do binding é o **ceo** (orquestração, BRIEF/SPEC, delegação ao PO/Arquiteto conforme regras).

### Integrar fila GitHub → Dev_Backend (exemplo)

1. Garantir contexto: `claw-repo-switch org/repo` ou `GIT_DEFAULT_REPOSITORY` correto.
2. Criar issue no repositório ativo com label **`back_end`** (e sem conflito com outras trilhas, conforme `AGENTS.md` do dev_backend).
3. No horário do cron do agente (ver env no `openclaw-container.yaml`), o ciclo containere acionar o agente para pegar a issue; delegação imediata também containere vir do Arquiteto na mesma sessão.

### Logs e diagnóstico

```bash
make openclaw-logs
```

Bootstrap: `/data/openclaw/backlog/status/openclaw-bootstrap.log` (e `openclaw-gateway-last.log` em cópia após saída do gateway). Com `DEBUG_LOG_ENABLED=true` no secret, mais verbosidade e espelhamento de sessões no log.

### Persistência

- Dados OpenClaw: PVC `openclaw-data`.
- Modelos Ollama: PVC `ollama-data`.

## Agentes

Resumo por agente: [agentes/README.md](./agentes/README.md). Contrato completo: `container/base/openclaw-config/<id>/AGENTS.md`.
