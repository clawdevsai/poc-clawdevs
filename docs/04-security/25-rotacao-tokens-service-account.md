# Rotação de tokens e service account do roteador (Fase 2 — 025)

Mitigações para reduzir exposição a **RCE** e **exfiltração**: rotação de tokens do Gateway e roteador com **service account zerada**. Ref: [05-seguranca-e-etica.md](05-seguranca-e-etica.md), [024-skills-terceiros-checklist-egress.md](issues/024-skills-terceiros-checklist-egress.md).

---

## Service account dedicada (implementado)

- **Artefato:** [k8s/management-team/openclaw/serviceaccount.yaml](../k8s/management-team/openclaw/serviceaccount.yaml) — ServiceAccount `openclaw-router` no namespace `ai-agents`.
- **Uso:** O Deployment do OpenClaw ([deployment.yaml](../k8s/management-team/openclaw/deployment.yaml)) referencia `serviceAccountName: openclaw-router`.
- **Privilégios:** Nenhum Role ou ClusterRole vinculado; o pod nasce sem permissões de API além do padrão do cluster (acesso mínimo). Rede interna/externa controlada por NetworkPolicy e egress whitelist (issue 024).
- **Aplicar:** O `serviceaccount.yaml` deve ser aplicado antes ou junto do deployment: `kubectl apply -f k8s/management-team/openclaw/serviceaccount.yaml`.

---

## Rotação de tokens

- **Objetivo:** Reduzir janela de impacto se um token for comprometido; rotação em intervalo configurável (ex.: 2–3 min).
- **Mecanismo:** Depende do suporte do Gateway OpenClaw (renovação automática ou endpoint de rotação). Opções:
  1. **CronJob no cluster:** Job que a cada N minutos invoca um script ou API interna que renova o token e atualiza o secret usado pelo pod; o deployment pode ser reiniciado ou o secret montado como env pode ser atualizado (ex.: reload do processo).
  2. **Serviço sidecar ou externo:** Serviço que obtém novo token do provedor (ex.: Telegram Bot API) e escreve no Kubernetes Secret ou em arquivo montado; o gateway lê o token atualizado.
- **Documentação de ativação:** Para ativar rotação automática, configurar o intervalo (ex.: variável `TOKEN_ROTATION_INTERVAL_MIN`) e garantir que o secret `openclaw-telegram` (ou equivalente) seja atualizado sem reinício prolongado do pod. Implementação de referência pode ser um CronJob que chama `scripts/rotate_gateway_token.sh` (stub: documentar o contrato; implementação concreta depende do provedor de identidade).
- **Riscos mitigados:** Token roubado tem validade curta; reduz superfície de ataque para zero-click e exfiltração.

---

## Sandbox do roteador

- **Arquitetura opcional:** Colocar o **roteador de mensagens** (componente que recebe Telegram e despacha para agentes) em pod separado, efêmero ou com ciclo de vida curto, **sem privilégios** e em nó separado do que executa código sensível (Developer, builds). Assim, um comprometimento do roteador não expõe diretamente o volume de código ou credenciais do time técnico.
- **Estado atual:** O gateway OpenClaw (CEO/PO) roda em um deployment único; a **service account zerada** já reduz o impacto. Evolução futura: split do componente de roteamento em deployment dedicado com resource limits e NetworkPolicy restritiva.

---

## Referências

- [025-rotacao-tokens-sandbox-roteador.md](issues/025-rotacao-tokens-sandbox-roteador.md) — critérios de aceite da issue.
- [024-skills-terceiros-checklist-egress.md](issues/024-skills-terceiros-checklist-egress.md) — manifesto com domínios e malha dinâmica (Istio/Cilium).
