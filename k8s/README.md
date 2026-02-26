# Kubernetes — ClawDevs

Ordem sugerida de apply (Fase 0):

```bash
kubectl apply -f namespace.yaml
kubectl apply -f redis/deployment.yaml
kubectl apply -f ollama/deployment.yaml
# Criar secret Telegram (nunca commitar):
# kubectl create secret generic openclaw-telegram -n ai-agents --from-literal=TELEGRAM_BOT_TOKEN='...' --from-literal=TELEGRAM_CHAT_ID='...'
kubectl apply -f openclaw/configmap.yaml
kubectl apply -f openclaw/deployment.yaml
```

- **Ollama:** após o pod estar `Running`, puxar o modelo (ex.: `phi3:mini`) via port-forward ou exec.
- **OpenClaw:** a imagem padrão do deployment é placeholder; substituir por imagem que execute `openclaw gateway`. Ver [37-deploy-fase0-telegram-ceo-ollama.md](../docs/37-deploy-fase0-telegram-ceo-ollama.md).

Ref: [openclaw-sub-agents-architecture.md](../docs/openclaw-sub-agents-architecture.md).
