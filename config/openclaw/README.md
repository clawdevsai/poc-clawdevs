# Config OpenClaw (uso fora do K8s)

Configuração para rodar o OpenClaw **no host**: Telegram (bot) + Ollama no cluster via port-forward.

## Telegram + Ollama (script pronto)

- **Config:** `openclaw.local.json5` — gateway local, canal Telegram, provedor Ollama em `http://127.0.0.1:11434/v1`.
- **Script:** `scripts/run-openclaw-telegram-ollama.sh` — faz port-forward do `svc/ollama-service` para 11434 e inicia `openclaw gateway`.

Uso:

1. No cluster: `make up` (namespace ai-agents, redis, ollama, openclaw).
2. No host: defina `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID` (ou `.env` na raiz) e execute:
   ```bash
   ./scripts/run-openclaw-telegram-ollama.sh
   ```
3. Envie uma mensagem ao **ClawDev bot** no Telegram; a resposta sai do LLM Ollama (ex.: phi3:mini). Se não tiver puxado o modelo: `kubectl exec -n ai-agents deploy/ollama-gpu -- ollama pull phi3:mini`.

Sem `TELEGRAM_CHAT_ID`: o script usa `dmPolicy: pairing`; aprove o primeiro DM com `openclaw pairing approve telegram <CODE>`.

Ref: [openclaw-sub-agents-architecture.md](../../docs/openclaw-sub-agents-architecture.md)
