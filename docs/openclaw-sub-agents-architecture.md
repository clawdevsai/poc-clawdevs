# Arquitetura ClawDevs: OpenClaw + Sub-agents + Kubernetes

Este documento descreve a **arquitetura de referência** para colocar o ecossistema ClawDevs em funcionamento usando **OpenClaw com sub-agents** ([Sub-Agents — OpenClaw](https://docs.openclaw.ai/tools/subagents)), integrado a **Kubernetes** (pods Ollama-GPU, Redis, OpenClaw) e **Telegram** como interface do Diretor com o CEO.

## Visão geral

```
                    ┌─────────────────────────────────────────────────────────┐
                    │                    Diretor (humano)                      │
                    └───────────────────────────┬─────────────────────────────┘
                                                │ Telegram
                                                ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│  Pod: openclaw                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐  │
│  │  OpenClaw Gateway                                                            │  │
│  │  • Canal: Telegram (bot token + allowFrom = chat Diretor)                     │  │
│  │  • Agente principal: CEO (único que recebe mensagens do Telegram)            │  │
│  │  • Sub-agents: PO, DevOps, Architect, Developer, QA, CyberSec, UX, DBA       │  │
│  │    → spawnados via sessions_spawn quando o CEO delega                        │  │
│  └─────────────────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────┬───────────────────────────────────────┘
                    │                         │
                    │ HTTP (Ollama API)       │ TCP (Redis)
                    ▼                         ▼
┌─────────────────────────────┐   ┌─────────────────────────────┐
│  Pod: ollama-gpu            │   │  Pod: redis-stream         │
│  • Serviço de inferência    │   │  • Estado global / streams  │
│  • Um modelo leve para teste│   │  • Eventos entre agentes    │
│  • Ex.: phi3:mini ou similar│   │  • (opcional na Fase 0)    │
└─────────────────────────────┘   └─────────────────────────────┘
```

## Decisões de desenho

### 1. OpenClaw como orquestrador único no pod

- **Um único processo OpenClaw** (gateway) no cluster recebe mensagens do Telegram e roteia para o agente **CEO**.
- O CEO é o **único agente com canal Telegram**; os demais são **sub-agents** acionados via `sessions_spawn` quando o CEO delega (pesquisa, backlog, revisão, etc.).
- Alinhado à doc: [02-agentes.md](02-agentes.md) (CEO como interface com o Diretor), [Sub-Agents](https://docs.openclaw.ai/tools/subagents) (sessions_spawn, announce de volta ao requester).

### 2. Um único modelo local para teste inicial

- **Todos os agentes** (CEO e sub-agents) usam o **mesmo LLM local** no início: menor consumo de VRAM e validação rápida do fluxo.
- Modelo sugerido: **phi3:mini** ou **qwen2.5:3b** (ou o menor que rodar estável no Ollama-GPU).
- Configuração: provedor `ollama` no OpenClaw apontando para o **Service** do pod Ollama no K8s (ex.: `http://ollama-service.ai-agents.svc.cluster.local:11434`).
- Formato do modelo no OpenClaw: `ollama/phi3:mini` (conforme [31-ollama-local.md](31-ollama-local.md)).

### 3. Redis para estado e eventos (fase posterior)

- Na **Fase 0** (entrega mínima): CEO via Telegram + Ollama já funciona **sem** Redis.
- Quando for implementar o fluxo completo (backlog, draft.2.issue, GPU Lock, etc.), o OpenClaw ou um sidecar pode publicar/consumir **Redis Streams**; o pod `redis-stream` fica disponível desde o início.

### 4. Segurança: credenciais fora do código

- **Telegram Bot Token** e **Chat ID** do Diretor vêm de **variáveis de ambiente** ou **Kubernetes Secrets**; nunca commitados no repositório.
- Se o token foi exposto em chat ou em arquivo, **revogar no BotFather** e gerar um novo.

## Fluxo mínimo (Fase 0)

1. Diretor envia mensagem no Telegram para o bot.
2. OpenClaw recebe, roteia para o agente **CEO**.
3. CEO usa o modelo **Ollama** (serviço no cluster) para gerar a resposta.
4. Resposta é enviada de volta ao Telegram.
5. (Opcional) CEO pode usar `sessions_spawn` para delegar uma tarefa a um sub-agent (ex.: PO ou Developer); ao terminar, o sub-agent anuncia o resultado no chat do CEO e o CEO responde ao Diretor.

## Referências

- [Sub-Agents — OpenClaw](https://docs.openclaw.ai/tools/subagents)
- [Telegram — OpenClaw](https://docs.openclaw.ai/channels/telegram)
- [31-ollama-local.md](31-ollama-local.md) (formato ollama/<modelo>)
- [09-setup-e-scripts.md](09-setup-e-scripts.md) (config OpenClaw + Telegram)
- [02-agentes.md](02-agentes.md) (definição CEO e sub-agents)
