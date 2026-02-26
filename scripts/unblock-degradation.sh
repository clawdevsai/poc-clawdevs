#!/usr/bin/env bash
# scripts/unblock-degradation.sh — ClawDevs
# Script de desbloqueio explícito do freio de mão (orçamento de degradação).
# SOMENTE o Diretor deve executar este script após revisar MEMORY.md e config.
# Nenhum agente pode reativar a esteira por conta própria.
#
# Referência: docs/issues/017-autonomia-nivel-4-matriz-escalonamento.md
#             docs/06-operacoes.md (Workflow de recuperação pós-degradação)
#
# USO: ./scripts/unblock-degradation.sh [--confirm]

set -euo pipefail

RED="\033[0;31m"; GREEN="\033[0;32m"; YELLOW="\033[1;33m"; RESET="\033[0m"

echo -e "${YELLOW}╔══════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${YELLOW}║  ClawDevs — Desbloqueio do Freio de Mão (Esteira Pausada)    ║${RESET}"
echo -e "${YELLOW}╚══════════════════════════════════════════════════════════════╝${RESET}"
echo ""
echo -e "${RED}ATENÇÃO: Este script desbloqueia a esteira de desenvolvimento.${RESET}"
echo "Antes de continuar, verifique:"
echo "  1. MEMORY.md foi revisado"
echo "  2. Configurações de limiares foram ajustadas"
echo "  3. O relatório de degradação foi analisado"
echo ""

REDIS_POD=$(kubectl get pods -n ai-agents -l app=redis -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [[ -z "$REDIS_POD" ]]; then
    echo -e "${RED}ERRO: Pod Redis não encontrado. Verifique o cluster.${RESET}"
    exit 1
fi

BRAKE_STATUS=$(kubectl exec -n ai-agents "$REDIS_POD" -- redis-cli get "degradation:emergency_brake_active" 2>/dev/null || echo "null")
if [[ "$BRAKE_STATUS" == "null" || -z "$BRAKE_STATUS" ]]; then
    echo -e "${GREEN}Freio de mão não está ativo no momento.${RESET}"
    exit 0
fi

echo -e "${YELLOW}Freio de mão ATIVO. Deseja desbloquear? [Digite 'CONFIRMO' para continuar]:${RESET} "
read -r CONFIRMATION
if [[ "$CONFIRMATION" != "CONFIRMO" ]]; then
    echo "Operação cancelada."
    exit 0
fi

# Desbloquear
kubectl exec -n ai-agents "$REDIS_POD" -- redis-cli del "degradation:emergency_brake_active"

# Resetar contadores de degradação para novo sprint
kubectl exec -n ai-agents "$REDIS_POD" -- redis-cli del "degradation:fifth_strike_count"
kubectl exec -n ai-agents "$REDIS_POD" -- redis-cli del "degradation:cosmetic_approval_count"
kubectl exec -n ai-agents "$REDIS_POD" -- redis-cli del "degradation:sprint_total"

echo -e "${GREEN}Freio de mão removido. Esteira desbloqueada.${RESET}"
echo "  - Contadores de degradação resetados para novo sprint"
echo "  - Monitor os eventos nas próximas horas"
echo ""
echo "  kubectl logs -f -n ai-agents -l app=agent-devops"
