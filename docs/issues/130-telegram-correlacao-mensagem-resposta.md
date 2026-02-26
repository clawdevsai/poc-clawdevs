# [team-devs-ai] Telegram: correlacionar resposta à mensagem de origem (evitar cross-reply)

**Fase:** 4 — Configuração  
**Labels:** config, telegram, openclaw

## Descrição

Garantir que, quando o bot responder no Telegram, a resposta seja **sempre** associada à mensagem do usuário que a provocou. Evitar que a resposta gerada para a mensagem A seja enviada como resposta à mensagem B (cross-reply).

## Critérios de aceite

- [ ] Requisito documentado em [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) (Canais) e [37-deploy-fase0-telegram-ceo-ollama.md](../37-deploy-fase0-telegram-ceo-ollama.md).
- [ ] Verificar na documentação do OpenClaw (docs.openclaw.ai) se existe:
  - Opção de processamento **sequencial por chat** (uma mensagem por vez por conversa), ou
  - Uso de `reply_to_message_id` (ou equivalente) ao enviar a resposta.
- [ ] Se houver parâmetros de config relevantes (ex.: `channels.telegram.serializedPerChat`, `replyToMessageId`), adicionar a `k8s/openclaw/configmap.yaml` e `config/openclaw/openclaw.local.json5` e documentar.
- [ ] Se não houver suporte no OpenClaw, registrar no upstream ou contornar com fila serializada por chat no gateway.

## Referências

- [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) (seção 4. Canais de comunicação)
- [37-deploy-fase0-telegram-ceo-ollama.md](../37-deploy-fase0-telegram-ceo-ollama.md)
- [OpenClaw — Telegram](https://docs.openclaw.ai/channels/telegram)
