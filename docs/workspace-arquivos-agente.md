# Objetivo dos arquivos no workspace do agente

Objetivo de cada arquivo no workspace (como neste repositório), alinhado à documentação OpenClaw e ao que `k8s/base/openclaw-pod.yaml` faz.

## Onde a OpenClaw define isso

- **Mapa dos arquivos do workspace:** [Agent workspace](https://docs.openclaw.ai/concepts/agent-workspace) — lista `AGENTS.md`, `SOUL.md`, `USER.md`, `IDENTITY.md`, `TOOLS.md`, `HEARTBEAT.md`, `BOOT.md`, `BOOTSTRAP.md`, etc.
- **Como entram no prompt:** [System prompt](https://docs.openclaw.ai/concepts/system-prompt) — injeção dos “bootstrap files” no contexto (limites `bootstrapMaxChars` / `bootstrapTotalMaxChars`); subagentes só recebem `AGENTS.md` e `TOOLS.md`.
- **RPC adapters:** [RPC](https://docs.openclaw.ai/reference/rpc) — integração de canais externos via JSON-RPC (ex.: daemon HTTP do Signal, `imsg` por stdio). Não é o mesmo conjunto de arquivos do workspace; é outra camada (CLI/provedor ↔ gateway).

## Objetivo de cada arquivo

| Arquivo | Objetivo |
|---------|----------|
| `AGENTS.md` | Instruções operacionais: missão, capabilities, regras, matriz de responsabilidade, constraints. Carregado no início da sessão; neste manifest recebe substituição de placeholders (`__GITHUB_ORG__`, repo ativo, etc.). [Agent workspace](https://docs.openclaw.ai/concepts/agent-workspace) |
| `BOOT.md` | Checklist opcional de arranque: ordem de carregamento (`IDENTITY` → `AGENTS` → …), healthchecks, variáveis. Na OpenClaw: em restart do gateway quando hooks internos habilitados; deve ser curto. [Agent workspace](https://docs.openclaw.ai/concepts/agent-workspace) |
| `BOOTSTRAP.md` | Ritual de primeira execução / contexto inicial. Na OpenClaw costuma ser one-shot e apagado depois; no pod, só o workspace do **CEO** remove `BOOTSTRAP.md` após o bootstrap (`rm -f .../workspace-ceo/BOOTSTRAP.md` em `openclaw-pod.yaml`); os outros agentes mantêm o arquivo copiado do ConfigMap. |
| `HEARTBEAT.md` | Lista curta para execuções periódicas (heartbeat), para poupar tokens. Ex.: sessões, filas, limites de research, GitHub, pipeline docs/issue. [Agent workspace](https://docs.openclaw.ai/concepts/agent-workspace); ver também [Cron vs Heartbeat](https://docs.openclaw.ai/automation/cron-vs-heartbeat) no [índice llms.txt](https://docs.openclaw.ai/llms.txt). |
| `IDENTITY.md` | Nome, papel, vibe, emoji, restrições de identidade imutáveis (anti–prompt injection de “mude quem você é”). [Agent workspace](https://docs.openclaw.ai/concepts/agent-workspace) |
| `INPUT_SCHEMA.json` | **Extensão ClawDevs:** contrato JSON Schema para `intent`, `source`, `payload` (e similares), referenciado nas regras de `AGENTS.md`. Não consta no mapa padrão do workspace na doc OpenClaw. |
| `SECURITY_TEST_CASES.md` | **Extensão ClawDevs:** casos de teste (injeção de prompt, path traversal, `gh` com repo errado, etc.) para validar comportamento de segurança esperado. |
| `SKILL.md` | Skill no workspace (OpenClaw também suporta `skills/`). O system prompt pode listar skills elegíveis e o modelo carrega com `read` o `SKILL.md` indicado. [System prompt → Skills](https://docs.openclaw.ai/concepts/system-prompt) |
| `SOUL.md` | Postura, valores não negociáveis, limites rígidos, tom — “personalidade + guardrails” persistentes. [Agent workspace](https://docs.openclaw.ai/concepts/agent-workspace) |
| `TOOLS.md` | Orientação: uso de `read` / `write` / `exec`, convenções (`gh`, `web-search`, `web-read`), rate limits, labels GitHub. **Não** liga ou desliga ferramentas; isso vem do gateway / `openclaw.json`. [Agent workspace](https://docs.openclaw.ai/concepts/agent-workspace) |
| `USER.md` | Quem é o usuário principal para o agente (ex.: PO), fuso, escalação. No CEO, `DIRECTORS_NAME` é injetado via `sed` a partir do Secret. [Agent workspace](https://docs.openclaw.ai/concepts/agent-workspace) |
| `MEMORY.md` | Memória de longo prazo do agente (quando habilitada em `AGENTS.md`): padrões e aprendizados por agente em `/data/openclaw/memory/<id>/MEMORY.md`; memória compartilhada em `/data/openclaw/memory/shared/SHARED_MEMORY.md` (escrita pelo Memory Curator). |

## Resumo prático

- **OpenClaw:** workspace = “casa” do agente; arquivos padrão entram no Project Context (com truncagem). **RPC** = adaptadores de **canais**, não substituem estes `.md`.
- **ClawDevs:** `INPUT_SCHEMA.json` e `SECURITY_TEST_CASES.md` reforçam contrato e testes de segurança além do mapa básico da doc OpenClaw.

**Fonte no repo:** `k8s/base/openclaw-config/<agente>/` (via ConfigMap `openclaw-agent-config`); destino em runtime: `/data/openclaw/workspace-<agente>/`.
