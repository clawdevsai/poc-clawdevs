#!/usr/bin/env bash
# Verifica se o agente DevOps está configurado para responder no Slack (conta devops no gateway).
# Uso: ./scripts/ops/slack-devops-check.sh
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SECRET_SCRIPT="$REPO_ROOT/scripts/cluster/secrets-from-env.sh"
cd "$REPO_ROOT"

echo "==> Checklist: DevOps não responde no Slack"
echo ""

echo "1. Secret openclaw-telegram tem tokens do DevOps (DEVOPS_SLACK_APP_TOKEN e DEVOPS_SLACK_BOT_TOKEN)?"
if ! kubectl get secret openclaw-telegram -n ai-agents &>/dev/null; then
  echo "   ERRO: Secret openclaw-telegram não existe. Rode: $SECRET_SCRIPT"
  exit 1
fi
HAS_APP=$(kubectl get secret openclaw-telegram -n ai-agents -o jsonpath='{.data.DEVOPS_SLACK_APP_TOKEN}' 2>/dev/null | wc -c)
HAS_BOT=$(kubectl get secret openclaw-telegram -n ai-agents -o jsonpath='{.data.DEVOPS_SLACK_BOT_TOKEN}' 2>/dev/null | wc -c)
if [[ "${HAS_APP:-0}" -lt 10 || "${HAS_BOT:-0}" -lt 10 ]]; then
  echo "   ERRO: Secret não tem DEVOPS_SLACK_APP_TOKEN e/ou DEVOPS_SLACK_BOT_TOKEN."
  echo "   No .env defina DEVOPS_SLACK_APP_TOKEN e DEVOPS_SLACK_BOT_TOKEN (app do DevOps em api.slack.com/apps)."
  echo "   Depois: $SECRET_SCRIPT  &&  kubectl rollout restart deployment/openclaw -n ai-agents"
  exit 1
fi
echo "   OK: Secret tem os tokens do DevOps."
echo ""

echo "2. Pod tem conta 'devops' na config do Slack?"
POD=$(kubectl get pods -n ai-agents -l app=openclaw -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || true)
if [[ -z "$POD" ]]; then
  echo "   AVISO: Pod openclaw não encontrado. Rode: make up"
  exit 1
fi
if kubectl exec -n ai-agents "$POD" -c gateway -- cat /tmp/openclaw.json 2>/dev/null | grep -q '"devops"'; then
  if kubectl exec -n ai-agents "$POD" -c gateway -- cat /tmp/openclaw.json 2>/dev/null | grep -A1 '"accounts"' | grep -q '"devops"'; then
    echo "   OK: Config do pod tem accounts.devops."
  else
    echo "   OK: Config menciona devops (bindings ou accounts)."
  fi
else
  echo "   ERRO: Config do pod NÃO tem conta 'devops'. O gateway não vai rotear mensagens do app DevOps para o agente."
  echo "   Confirme no .env: DEVOPS_SLACK_APP_TOKEN e DEVOPS_SLACK_BOT_TOKEN; rode $SECRET_SCRIPT e kubectl rollout restart deployment/openclaw -n ai-agents"
  exit 1
fi
echo ""

echo "3. Provider [devops] nos logs (últimas linhas)?"
if kubectl logs -n ai-agents deploy/openclaw -c gateway --tail=80 2>/dev/null | grep -q '\[devops\]'; then
  echo "   OK: [slack] [devops] starting provider apareceu nos logs."
else
  echo "   AVISO: Nenhuma linha [devops] nos últimos 80 logs. Pode ser que o pod tenha reiniciado há pouco."
fi
echo ""

echo "4. Próximos passos se ainda não responder:"
echo "   - App do DevOps está no canal? (Integrações do canal → Adicionar apps → app do DevOps)"
echo "   - Ao mencionar, use @ e selecione o BOT do DevOps no autocomplete (não só o texto @DevOps)."
echo "   - Scopes do app: chat:write, channels:read, channels:history, app_mentions:read; evento app_mention."
echo "   - Doc: docs/08-technical-notes/devops-nao-responde-slack.md"
echo ""
