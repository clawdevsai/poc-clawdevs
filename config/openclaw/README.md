# Config OpenClaw (uso fora do K8s)

Configuração para rodar o OpenClaw **no host**: **Slack = todos os agentes** (padrão); **Telegram = apenas CEO** (Diretor ↔ CEO). Ollama no cluster via port-forward.

## Regras de canal

- **Slack (padrão):** **todos os agentes** conversam no Slack (CEO, PO, DevOps, Architect, etc.) — DM e canais (ex. #all-clawdevsai). Discussões entre agentes no Slack usam **Ollama (LLM local com GPU)**.
- **Telegram (apenas CEO):** somente o **agente CEO** conversa com o Diretor pelo Telegram. Canal exclusivo CEO ↔ Diretor.
- **Política:** agentes que não são o CEO **só** usam Slack; o CEO usa Telegram e Slack.
- **Workspace único:** todos os agentes compartilham o mesmo workspace (ex.: `config/openclaw/workspace-ceo`).

## Modelo para discussões no Slack

Para **discussões no Slack** (conversas e tema para análise no #all-clawdevsai), todos os agentes usam **`ollama/ministral-3:3b-cloud`** (Ministral 3 3B Cloud). Configurado em `agents.defaults.model` e em cada `agents.list[].model` (local e K8s).

Para trocar: em `openclaw.local.json5` altere `agents.defaults.model` e os `model` em cada item de `agents.list`. No K8s, o ConfigMap `openclaw-config` define os modelos por agente. Alternativas no Ollama: `ollama/qwen2.5:3b`, `ollama/ministral-3:3b`, `ollama/glm-5:cloud`.

## Telegram + Ollama (script pronto)

- **Config:** `openclaw.local.json5` — gateway local, canal Telegram, canal Slack (opcional), provedor Ollama em `http://127.0.0.1:11434/v1`.
- **Script:** `scripts/run-openclaw-telegram-slack-ollama.sh` — faz port-forward do `svc/ollama-service` para 11434 e inicia `openclaw gateway`. Se `SLACK_APP_TOKEN` e `SLACK_BOT_TOKEN` estiverem no `.env`, o Slack é habilitado automaticamente.

Uso:

1. No cluster: `make up` (namespace ai-agents, redis, ollama, openclaw).
2. No host: defina `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID` (ou `.env` na raiz). Para Slack: `SLACK_APP_TOKEN`, `SLACK_BOT_TOKEN` e opcionalmente `SLACK_DIRECTOR_USER_ID` (ver [docs OpenClaw Slack](https://docs.openclaw.ai/channels/slack)).
3. Execute:
   ```bash
   ./scripts/run-openclaw-telegram-slack-ollama.sh
   ```
4. Envie uma mensagem ao **ClawDev bot** no Telegram (ou no Slack, se habilitado); a resposta sai do LLM Ollama.

Sem `TELEGRAM_CHAT_ID`: o script usa `dmPolicy: pairing`; aprove o primeiro DM com `openclaw pairing approve telegram <CODE>`.  
Sem `SLACK_DIRECTOR_USER_ID`: use `openclaw pairing approve slack <CODE>` no primeiro DM no Slack.

## Como conversar com o PO (ou outro agente) no Slack

O gateway OpenClaw está conectado a **um único app Slack** (o app **ClawdevsAI** / CEO). Para o PO ou outro agente responder no canal **#all-clawdevsai**, você precisa **mencionar esse app** e pedir o agente no texto. Se você criar um app separado para o PO em api.slack.com e mencionar @PO, esse app **não** recebe eventos no gateway (só um app conectado por vez).

**No canal #all-clawdevsai (ou DM com o ClawdevsAI):**

1. **Mencione o app conectado** — Ex.: *"@ClawdevsAI PO: Ola PO esta me ouvindo?"* ou *"@ClawdevsAI PO: quais as próximas entregas?"*
   O gateway (conectado ao app ClawdevsAI) recebe a mensagem e pode rotear ao agente PO pelo conteúdo.

2. **Pedir ao CEO para falar com o PO** — Ex.: *"@ClawdevsAI Quero falar com o PO"*, *"Pergunte ao Product Owner: qual o status do backlog?"*
   O CEO pode delegar ao PO via sub-agents e trazer a resposta de volta.

3. **Pedir direto por texto (já no contexto do app)** — Em DM com o ClawdevsAI: *"PO: quais as próximas entregas?"*, *"Product Owner, qual a prioridade do épico X?"*

4. **Outros agentes** — Mesmo padrão: *"@ClawdevsAI DevOps: o cluster está estável?"*, *"@ClawdevsAI QA: quais testes cobrem o módulo Y?"*.

**Resumo:** Use **@ClawdevsAI** (o app que está conectado ao gateway) e no texto indique o agente (PO:, DevOps:, etc.). O app **ClawdevsAI** no Slack é o mesmo para todos; a escolha do agente é pelo conteúdo da mensagem (ver [docs OpenClaw Slack](https://docs.openclaw.ai/channels/slack)).

## App vs usuário: com quem falar? Preciso criar um usuário por agente?

**Fale com o app (ClawdevsAI), não com usuários separados.**  
Você **não** precisa criar um usuário no Slack para cada agente (CEO, PO, DevOps, etc.). Existe **um único app** no Slack — o **ClawdevsAI** — que representa o gateway OpenClaw. Todos os agentes (CEO, PO, DevOps, Architect, Developer, QA, CyberSec, UX, DBA) “falam” por esse mesmo app. Você conversa em **DM com o app** ou **em um canal** onde o app foi adicionado; o gateway decide qual agente responde ou participa da discussão.

**Resumo:** um app, uma identidade no Slack; vários agentes na config do OpenClaw, todos por trás desse app.

## O que falta para a conversa funcionar no Slack

1. **Gateway rodando** — Local: `./scripts/run-openclaw-telegram-slack-ollama.sh` (com `SLACK_APP_TOKEN` e `SLACK_BOT_TOKEN` no `.env`). **No K8s:** os tokens precisam estar no **Secret** do cluster, não só no `.env`: rode `./scripts/k8s-openclaw-secret-from-env.sh` e depois `kubectl rollout restart deployment/openclaw -n ai-agents`. Sem isso, nada acontece no Slack.
2. **Quem pode mandar DM** — Se usar allowlist: coloque o seu Slack User ID (ex.: do Diego) em `SLACK_ALLOWED_USER_IDS` no `.env`, ou deixe allowlist vazia e use **pairing**: no primeiro DM, no terminal rode `openclaw pairing approve slack <CODE>`.
3. **App no canal** — Para os agentes participarem de discussões em canal (#all-clawdevsai, #new-channel, etc.), **convide o app ClawdevsAI para o canal** (no canal: Integrações → Adicionar apps → ClawdevsAI). Assim o app recebe mensagens do canal e pode responder ou fazer os agentes discutirem entre si.
4. **Mencione o app em canal** — Em canais, o Slack costuma exigir **@menção** do app. Escreva por exemplo: *"@ClawdevsAI Oi"* ou *"@ClawdevsAI Tema: analisar migração para K8s"*.

### Slack não responde? (checklist)

Rode o diagnóstico: **`./scripts/slack-openclaw-check.sh`**. Em resumo:

- **K8s:** o pod **não** lê o `.env` do seu PC. É preciso enviar os tokens para o cluster: `./scripts/k8s-openclaw-secret-from-env.sh` e `kubectl rollout restart deployment/openclaw -n ai-agents`.
- **Canal:** o app está no canal? (Integrações → Adicionar apps → ClawdevsAI.)
- **Menção:** em canal, use **@ClawdevsAI** no início da mensagem (é o app conectado ao gateway). Se você mencionar **@PO** (app separado do PO), o gateway não recebe — só o app ClawdevsAI/CEO está conectado. Para falar com o PO: *"@ClawdevsAI PO: sua mensagem"*.
- **Logs:** `kubectl logs -n ai-agents -l app=openclaw -f --tail=100` para ver se o gateway conectou ao Slack (Socket Mode) e se está recebendo eventos.

### PO não responde? (causa e solução)

**Causa:** Quando você escreve **"@PO esta me ouvindo"**, a menção **@PO** é do **app do PO** (outro app no Slack). O gateway OpenClaw está conectado apenas ao app **ClawdevsAI** (CEO). Eventos do app PO não chegam a nenhum processo — por isso o PO “não ouve”.

**Solução (multi-account — @PO direto):** O gateway pode conectar o app PO. Faça: (1) No .env preencha `PO_SLACK_APP_TOKEN` e `PO_SLACK_BOT_TOKEN`; (2) Rode `./scripts/k8s-openclaw-secret-from-env.sh` e `kubectl rollout restart deployment/openclaw -n ai-agents`; (3) No Slack convide o app **PO** para #all-clawdevsai. O binding roteia @PO para o agente PO.

**Alternativa (um app):** Use **@ClawdevsAI PO: esta me ouvindo?** — o CEO delega ao PO. Se aparecer `missing_scope` nos logs, adicione no app ClawdevsAI os scopes `channels:read` e `users:read`.

## Agentes discutindo entre si no Slack

Para os **agentes comunicarem e discutirem via Slack**:

1. **Convide o app ClawdevsAI para o canal** onde a discussão deve acontecer (ex.: #all-clawdevsai). Sem o app no canal, ele não vê nem responde mensagens de lá.
2. No canal, **mencione o app ou escreva a pergunta** (ex.: *“@ClawdevsAI PO e DevOps: alinhem a entrega da próxima sprint”* ou *“Quero que CEO, PO e Architect discutam a arquitetura do módulo X”*). O gateway pode acionar vários agentes (sub-agents) e as respostas ou a discussão aparecem no canal.
3. Em **DM com o app**, você já pode pedir que um agente fale com outro (ex.: *“Pergunte ao PO e traga a resposta”*); a “discussão” entre agentes ocorre no backend e a resposta consolidada vem pelo mesmo app.

Ref: [openclaw-sub-agents-architecture.md](../../docs/openclaw-sub-agents-architecture.md)

## Fluxo #all-clawdevsai: tema para análise (Diretor → rodada → aprovação)

No canal **#all-clawdevsai** o Diretor pode **colocar um tema para analisar**. O fluxo é:

1. **Diretor** posta no #all-clawdevsai o tema (ex.: *"Tema: migrar o módulo X para K8s"*). Pode mencionar @ClawdevsAI.
2. **Agentes** discutem **um por vez** no canal, cada um na sua especialidade (DevOps → Architect → Developer → QA → CyberSec → UX → DBA → PO → CEO).
3. **PO e CEO** decidem a recomendação; o **CEO** pergunta ao Diretor no canal: *"Aprovamos [resumo]. Quer que eu inicie essa tarefa?"*
4. **Diretor** responde no Slack (ex.: *"Sim, pode iniciar"*).
5. O **fluxo normal** segue (backlog, issues, desenvolvimento conforme já documentado).

Config: o canal #all-clawdevsai está na allowlist do Slack (`groupPolicy: allowlist`, `channels.CDAHISCLSQKC`). Detalhes: [43-fluxo-slack-all-clawdevsai-tema-analise.md](../../docs/43-fluxo-slack-all-clawdevsai-tema-analise.md).
