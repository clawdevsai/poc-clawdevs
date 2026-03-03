---
trigger: always_on
glob:
description: Maximizar uso do OpenClaw; não reinventar a roda; codificar só quando não houver solução no OpenClaw
---

# OpenClaw First — Não reinventar a roda

Este projeto **aproveita ao máximo a tecnologia OpenClaw**. Não duplicar ou reimplementar o que o OpenClaw já oferece. **Apagar código custom e desenvolver somente quando realmente não existir solução no OpenClaw.**

## Princípio

- **Preferir sempre**: configuração, bindings, multi-agent, providers, session, memory, compaction, streaming e ferramentas nativas do OpenClaw.
- **Evitar**: reimplementar agent loop, sessões, memória, system prompt, workspace, OAuth, retry ou mensageria própria.
- **Consultar a documentação** antes de escrever código novo: https://docs.openclaw.ai/ (índice: https://docs.openclaw.ai/llms.txt).

## O que o OpenClaw já cobre (usar em vez de código próprio)

| Necessidade | Onde no OpenClaw | Ação |
|-------------|------------------|------|
| Arquitetura / Gateway | [Architecture](https://docs.openclaw.ai/concepts/architecture), [Pi Integration](https://docs.openclaw.ai/pi) | Usar um Gateway por host; WebSocket, eventos, protocolo tipado. |
| Agentes / agent loop | [Agent](https://docs.openclaw.ai/concepts/agent), [Agent loop](https://docs.openclaw.ai/concepts/agent-loop) | Usar runtime embarcado (pi), workspace, bootstrap files, tools built-in. |
| System prompt / contexto | [System prompt](https://docs.openclaw.ai/concepts/system-prompt), [Context](https://docs.openclaw.ai/concepts/context) | USER.md, IDENTITY.md, SOUL.md, AGENTS.md, TOOLS.md; customização por canal. |
| Workspace do agente | [Agent workspace](https://docs.openclaw.ai/concepts/agent-workspace) | `agents.defaults.workspace`, sandbox por agente. |
| Bootstrapping | [Bootstrapping](https://docs.openclaw.ai/start/bootstrapping) | Ritual first-run; não recriar. |
| Sessões | [Session](https://docs.openclaw.ai/concepts/session), [Session pruning](https://docs.openclaw.ai/concepts/session-pruning), [Session tool](https://docs.openclaw.ai/concepts/session-tool) | dmScope, mainKey, reset, maintenance, store no gateway. |
| Memória e compaction | [Memory](https://docs.openclaw.ai/concepts/memory), [Compaction](https://docs.openclaw.ai/concepts/compaction) | Notas duráveis, flush pré-compaction, política de pruning. |
| Multi-agent / roteamento | [Multi-agent](https://docs.openclaw.ai/concepts/multi-agent) | `agents.list`, `bindings`, accountId, peer, guildId; um "cérebro" por agente. |
| Providers / modelos | [Providers](https://docs.openclaw.ai/providers), [Ollama](https://docs.openclaw.ai/providers/ollama) | `provider/model`, auth via `openclaw onboard`, failover. |
| OAuth | [OAuth](https://docs.openclaw.ai/concepts/oauth) | Fluxos suportados pelo OpenClaw; não reimplementar. |
| Mensagens / streaming | [Messages](https://docs.openclaw.ai/concepts/messages), [Streaming](https://docs.openclaw.ai/concepts/streaming) | Block streaming, chunking, coalesce; eventos do gateway. |
| Retry | [Retry](https://docs.openclaw.ai/concepts/retry) | Políticas nativas; não adicionar retry custom sem checar docs. |
| Presence | [Presence](https://docs.openclaw.ai/concepts/presence) | Eventos e estado do gateway. |

## Checklist antes de implementar

1. **Pesquisar na documentação**: docs.openclaw.ai (concepts, gateway, providers, channels).
2. **Verificar config**: `openclaw.json` / JSON5 — agents, bindings, session, channels, tools.
3. **Verificar CLI**: `openclaw agents`, `openclaw channels`, `openclaw sessions`, `openclaw gateway`.
4. **Só então** implementar código novo se não houver opção configurável ou extensão documentada.

## Escopo do projeto (clawdevs)

- Integrar com o **Gateway OpenClaw** existente (config, bindings, multi-agent).
- Usar **workspace**, **AGENTS.md/SOUL.md/USER.md** e **skills** do OpenClaw.
- Usar **session store**, **compaction** e **memory** do OpenClaw; não manter estado paralelo.
- Usar **providers** (ex.: Ollama) via config OpenClaw; não criar clientes LLM próprios para o que o OpenClaw já faz.
- Qualquer worker/script que "converse" com o agente deve usar o **protocolo do Gateway** (WS/API) ou CLI, não reimplementar o agent loop.

## Exemplos

- **Ruim**: Criar um "session manager" próprio que persiste histórico.
- **Bom**: Usar `session.dmScope`, `session.maintenance`, store do gateway e `openclaw sessions`.
- **Ruim**: Implementar retry manual em chamadas ao modelo.
- **Bom**: Usar política de retry do OpenClaw e failover de providers.
- **Ruim**: Novo "orchestrator" que dispara múltiplos agentes por conta própria.
- **Bom**: Múltiplos agentes via `agents.list` + `bindings` e, se necessário, ferramentas que chamem o gateway (ex.: session spawn / gateway tool).

## Referências rápidas

- Índice: https://docs.openclaw.ai/llms.txt
- Arquitetura: https://docs.openclaw.ai/concepts/architecture
- Agent: https://docs.openclaw.ai/concepts/agent
- Multi-agent: https://docs.openclaw.ai/concepts/multi-agent
- Session: https://docs.openclaw.ai/concepts/session
- Providers: https://docs.openclaw.ai/providers
- Pi (embed): https://docs.openclaw.ai/pi
