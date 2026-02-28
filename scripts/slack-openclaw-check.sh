#!/usr/bin/env bash
# Verifica por que o Slack não responde com o OpenClaw no cluster.
# Uso: ./scripts/slack-openclaw-check.sh
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

echo "==> Checklist: Slack não responde (OpenClaw no K8s)"
echo ""

# 1) Secret tem tokens?
echo "1. Secret openclaw-telegram tem SLACK_APP_TOKEN e SLACK_BOT_TOKEN?"
if ! kubectl get secret openclaw-telegram -n ai-agents &>/dev/null; then
  echo "   ERRO: Secret openclaw-telegram não existe."
  echo "   Faça: ./scripts/k8s-openclaw-secret-from-env.sh"
  echo "   (Isso copia SLACK_* do .env para o Secret.)"
  exit 1
fi
HAS_APP=$(kubectl get secret openclaw-telegram -n ai-agents -o jsonpath='{.data.SLACK_APP_TOKEN}' 2>/dev/null | wc -c)
HAS_BOT=$(kubectl get secret openclaw-telegram -n ai-agents -o jsonpath='{.data.SLACK_BOT_TOKEN}' 2>/dev/null | wc -c)
if [[ "${HAS_APP:-0}" -lt 10 || "${HAS_BOT:-0}" -lt 10 ]]; then
  echo "   ERRO: Secret não tem SLACK_APP_TOKEN e/ou SLACK_BOT_TOKEN."
  echo "   O pod NÃO lê o .env do seu PC; os tokens precisam estar no Secret."
  echo "   Faça: ./scripts/k8s-openclaw-secret-from-env.sh"
  echo "   Depois: kubectl rollout restart deployment/openclaw -n ai-agents"
  exit 1
fi
echo "   OK: Secret tem os dois tokens."
echo ""

# 2) Pod rodando?
echo "2. Pod openclaw está rodando?"
if ! kubectl get deployment openclaw -n ai-agents &>/dev/null; then
  echo "   ERRO: deployment openclaw não existe. Rode: make up"
  exit 1
fi
READY=$(kubectl get deployment openclaw -n ai-agents -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
if [[ "${READY:-0}" -lt 1 ]]; then
  echo "   AVISO: Nenhum pod ready. Verifique: kubectl get pods -n ai-agents -l app=openclaw"
  echo "   Logs: kubectl logs -n ai-agents -l app=openclaw -f --tail=100"
else
  echo "   OK: Pod ready."
fi
echo ""

# 3) Config dentro do pod: Slack enabled?
echo "3. Slack habilitado na config do pod? (slack.enabled = true)"
POD=$(kubectl get pods -n ai-agents -l app=openclaw -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || true)
if [[ -n "$POD" ]]; then
  # No bloco slack, procurar "enabled": true (pode estar algumas linhas depois de "slack")
  if kubectl exec -n ai-agents "$POD" -c gateway -- cat /tmp/openclaw.json 2>/dev/null | grep -A20 '"slack"' | grep -q '"enabled": true'; then
    echo "   OK: slack.enabled = true no pod."
  else
    echo "   ERRO: slack.enabled não está true no pod."
    echo "   O entrypoint só habilita Slack quando SLACK_APP_TOKEN e SLACK_BOT_TOKEN existem no ambiente do container."
    echo "   Confirme que o Secret tem as chaves e reinicie: kubectl rollout restart deployment/openclaw -n ai-agents"
  fi
else
  echo "   (Pod não encontrado; pulando verificação da config.)"
fi
echo ""

echo "4. No Slack:"
echo "   - Convide o app ClawdevsAI para o canal (#all-clawdevsai: Integrações → Adicionar apps → ClawdevsAI)."
echo "   - Em canal, MENCIONE o app: @ClawdevsAI e depois a mensagem (ex.: \"@ClawdevsAI Oi\")."
echo "   - Em DM com o app, seu User ID deve estar em SLACK_DIRECTOR_USER_ID ou SLACK_ALLOWED_USER_IDS no .env (e no Secret)."
echo ""
echo "5. Ver logs do gateway em tempo real:"
echo "   kubectl logs -n ai-agents -l app=openclaw -f --tail=50"
echo ""
