# [team-devs-ai] API Gateway (Maton) — integração com APIs externas

**Fase:** 9 — Integrações  
**Labels:** integration, security

## Descrição

Conectar a 100+ APIs (Google Workspace, Slack, Notion, HubSpot, Stripe, etc.) via gateway Maton com OAuth gerenciado. Base URL, gestão de conexões, serviços suportados. Uso por CEO, PO, Developer, DevOps após aprovação; Zero Trust; MATON_API_KEY em secrets, nunca em repositório.

## Critérios de aceite

- [ ] Documentação do Maton: base URL, como obter e configurar MATON_API_KEY (secrets do cluster).
- [ ] Gestão de conexões: OAuth por serviço; escopo estritamente as conexões autorizadas pelo usuário.
- [ ] Regra: nunca commitar ou expor MATON_API_KEY; DevOps configura variável no ambiente (secrets).
- [ ] Uso por agentes: CEO, PO, Developer (implementar integrações quando aprovado), DevOps (config); lista de serviços suportados ou link para doc do Maton.
- [ ] Developer: implementar integrações via gateway quando aprovado; nunca expor credenciais de terceiros no código.

## Referências

- [25-api-gateway-integracao-apis.md](../../05-tools-and-skills/25-api-gateway-integracao-apis.md)

## Verificação (Fase 9)

- Documentação base URL e MATON_API_KEY: [25-api-gateway-integracao-apis.md](../../05-tools-and-skills/25-api-gateway-integracao-apis.md). Setup no cluster: [09-setup-e-scripts.md](../../02-infra/09-setup-e-scripts.md) (§ API Gateway Maton).
- Secret K8s: template [secret-maton.example.yaml](../../../k8s/shared/development-team/secret-maton.example.yaml); criar com `kubectl create secret generic clawdevs-maton-secret ...` (nunca commitar valor real).
- envFrom opcional: deployments openclaw (CEO/PO), developer, devops, po referenciam `clawdevs-maton-secret` (optional: true).
- Gestão OAuth: link ctrl.maton.ai e lista de serviços em doc 25. Developer implementa integrações via gateway quando aprovado (doc 02-agentes e 25).
