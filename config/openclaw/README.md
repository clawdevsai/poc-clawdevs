# Config OpenClaw (uso fora do K8s)

Configuração para rodar o OpenClaw **no host**: Telegram (só CEO) + Slack opcional (todos os agentes) + Ollama no cluster via port-forward.

## Regras de canal

- **Telegram:** somente o **agente CEO** conversa com o Diretor. Canal exclusivo CEO ↔ Diretor.
- **Slack:** **todos os agentes** podem conversar (CEO, PO, DevOps, Architect, etc.). Quando os agentes discutirem soluções entre si no Slack, é **obrigatório** usar **Ollama (LLM local com GPU)**.
- **Política rigorosa:** agentes diferentes do CEO não podem acessar outra plataforma além do Slack; apenas o CEO usa Telegram (e Slack).
- **Workspace único:** todos os agentes compartilham o mesmo workspace (ex.: `config/openclaw/workspace-ceo`).

## Modelo menor para conversa apenas no Slack

Para **só conversa no Slack** (menos VRAM, resposta mais rápida), a config local usa o **menor LLM local** disponível no Ollama. Padrão: **`ollama/qwen2.5:3b`** (Qwen 2.5 3B). Alternativas igualmente leves:

- **`ollama/qwen2.5:3b`** — 3B parâmetros, ~2 GB, bom para chat.
- **`ollama/stewyphoenix19/phi3-mini_v1:latest`** (Phi-3 Mini) — ~3.8B, ~2 GB.
- **`ollama/ministral-3:3b`** — 3B, se já estiver no cluster.

Trocar: em `openclaw.local.json5`, altere `agents.defaults.model` e os `model` em cada item de `agents.list` para o ID do modelo desejado (ex.: `ollama/stewyphoenix19/phi3-mini_v1:latest`). No K8s, o ConfigMap `openclaw-config` define os modelos por agente; para Slack-only pode padronizar todos em um único modelo pequeno.

## Telegram + Ollama (script pronto)

- **Config:** `openclaw.local.json5` — gateway local, canal Telegram, canal Slack (opcional), provedor Ollama em `http://127.0.0.1:11434/v1`.
- **Script:** `scripts/run-openclaw-telegram-ollama.sh` — faz port-forward do `svc/ollama-service` para 11434 e inicia `openclaw gateway`. Se `SLACK_APP_TOKEN` e `SLACK_BOT_TOKEN` estiverem no `.env`, o Slack é habilitado automaticamente.

Uso:

1. No cluster: `make up` (namespace ai-agents, redis, ollama, openclaw).
2. No host: defina `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID` (ou `.env` na raiz). Para Slack: `SLACK_APP_TOKEN`, `SLACK_BOT_TOKEN` e opcionalmente `SLACK_DIRECTOR_USER_ID` (ver [docs OpenClaw Slack](https://docs.openclaw.ai/channels/slack)).
3. Execute:
   ```bash
   ./scripts/run-openclaw-telegram-ollama.sh
   ```
4. Envie uma mensagem ao **ClawDev bot** no Telegram (ou no Slack, se habilitado); a resposta sai do LLM Ollama.

Sem `TELEGRAM_CHAT_ID`: o script usa `dmPolicy: pairing`; aprove o primeiro DM com `openclaw pairing approve telegram <CODE>`.  
Sem `SLACK_DIRECTOR_USER_ID`: use `openclaw pairing approve slack <CODE>` no primeiro DM no Slack.

## Como conversar com o PO (ou outro agente) no Slack

No **DM com o ClawdevsAI** (ou em canal onde o app está), você conversa com o bot; o gateway pode rotear para o **CEO** primeiro. Para envolver o **Product Owner (PO)** ou outro agente:

1. **Pedir ao CEO para falar com o PO** — Exemplos:
   - *"Quero falar com o PO"*
   - *"Pergunte ao Product Owner: qual o status do backlog?"*
   - *"Fale com o PO sobre prioridades desta semana"*
   O CEO pode delegar ao PO via sub-agents e trazer a resposta de volta.

2. **Pedir direto ao PO por texto** — Exemplos:
   - *"PO: quais as próximas entregas?"*
   - *"Product Owner, qual a prioridade do épico X?"*
   Assim o modelo (e o gateway) podem interpretar e rotear ao agente PO.

3. **Outros agentes** — O mesmo vale para DevOps, Architect, Developer, QA, CyberSec, UX, DBA. Ex.: *"DevOps: o cluster está estável?"*, *"QA: quais testes cobrem o módulo Y?"*.

O app **ClawdevsAI** no Slack é o mesmo para todos; a escolha do agente é pelo conteúdo da mensagem (e, quando houver, por menção ou comando específico do OpenClaw — ver [docs OpenClaw Slack](https://docs.openclaw.ai/channels/slack)).

## App vs usuário: com quem falar? Preciso criar um usuário por agente?

**Fale com o app (ClawdevsAI), não com usuários separados.**  
Você **não** precisa criar um usuário no Slack para cada agente (CEO, PO, DevOps, etc.). Existe **um único app** no Slack — o **ClawdevsAI** — que representa o gateway OpenClaw. Todos os agentes (CEO, PO, DevOps, Architect, Developer, QA, CyberSec, UX, DBA) “falam” por esse mesmo app. Você conversa em **DM com o app** ou **em um canal** onde o app foi adicionado; o gateway decide qual agente responde ou participa da discussão.

**Resumo:** um app, uma identidade no Slack; vários agentes na config do OpenClaw, todos por trás desse app.

## O que falta para a conversa funcionar no Slack

1. **Gateway rodando** — `./scripts/run-openclaw-telegram-ollama.sh` (com `SLACK_APP_TOKEN` e `SLACK_BOT_TOKEN` no `.env`).
2. **Quem pode mandar DM** — Se usar allowlist: coloque o seu Slack User ID (ex.: do Diego) em `SLACK_ALLOWED_USER_IDS` no `.env`, ou deixe allowlist vazia e use **pairing**: no primeiro DM, no terminal rode `openclaw pairing approve slack <CODE>`.
3. **App no canal** — Para os agentes participarem de discussões em canal (#all-clawdevsai, #new-channel, etc.), **convide o app ClawdevsAI para o canal** (no canal: Integrações → Adicionar apps → ClawdevsAI). Assim o app recebe mensagens do canal e pode responder ou fazer os agentes discutirem entre si.

## Agentes discutindo entre si no Slack

Para os **agentes comunicarem e discutirem via Slack**:

1. **Convide o app ClawdevsAI para o canal** onde a discussão deve acontecer (ex.: #all-clawdevsai). Sem o app no canal, ele não vê nem responde mensagens de lá.
2. No canal, **mencione o app ou escreva a pergunta** (ex.: *“@ClawdevsAI PO e DevOps: alinhem a entrega da próxima sprint”* ou *“Quero que CEO, PO e Architect discutam a arquitetura do módulo X”*). O gateway pode acionar vários agentes (sub-agents) e as respostas ou a discussão aparecem no canal.
3. Em **DM com o app**, você já pode pedir que um agente fale com outro (ex.: *“Pergunte ao PO e traga a resposta”*); a “discussão” entre agentes ocorre no backend e a resposta consolidada vem pelo mesmo app.

Ref: [openclaw-sub-agents-architecture.md](../../docs/openclaw-sub-agents-architecture.md)
