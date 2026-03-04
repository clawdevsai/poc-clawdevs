# Nomes próprios dos agentes

Cada agente tem um **nome próprio** (exibido no Slack e na UI). O `id` continua sendo o identificador técnico; o `name` é o nome da persona.

| id | Nome | Papel |
|----|------|--------|
| ceo | Rafael | CEO |
| po | Marina | Product Owner |
| devops | Sérgio | DevOps/SRE |
| architect | Vera | Architect |
| developer | Leo | Developer |
| qa | Renata | QA |
| cybersec | Jade | CyberSec |
| ux | Luna | UX |
| dba | Dante | DBA |
| governance_proposer | Letícia | Governance Proposer |

Configuração: `k8s/management-team/openclaw/configmap.yaml` (agents.list), `k8s/development-team/*/config/configmap.yaml`, `k8s/governance-team/configmap.yaml`.
