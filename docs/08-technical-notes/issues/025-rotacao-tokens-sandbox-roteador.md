# [team-devs-ai] Rotação de tokens e sandbox do roteador OpenClaw

**Fase:** 2 — Segurança  
**Labels:** security, hardening

## Descrição

Mitigações para reduzir exposição a RCE e exfiltração: rotação automática de tokens do Gateway do OpenClaw (ex.: a cada 2–3 min) e roteador de mensagens em sandbox efêmero sem privilégios, separado do nó principal. **Service account dedicada** ao pod do roteador com privilégios zerados; isolamento dinâmico de rede via manifesto de skills (ver issue 024).

## Critérios de aceite

- [ ] Rotação de tokens: mecanismo (cron ou serviço) que rotaciona tokens do Gateway em intervalo configurável (ex.: 2–3 min); documentação de como ativar.
- [ ] Sandbox do roteador: opção ou arquitetura para colocar o roteador de mensagens do OpenClaw em ambiente efêmero, sem privilégios e separado do nó que lida com código sensível.
- [ ] **Service account dedicada:** definir no Kubernetes uma service account exclusiva para o pod do roteador OpenClaw, com **privilégios absolutamente zerados** (nascida "cega" para rede interna; para externa, só o permitido pela malha). Sem Role/ClusterRole desnecessários.
- [ ] Referência à issue 024 para manifesto com domínios por skill e atualização dinâmica da malha (Istio/Cilium), fechando brechas de túnel DNS.
- [ ] Documentação de riscos (RCE, zero-click) e como essas mitigações reduzem a janela de impacto.

## Referências

- [05-seguranca-e-etica.md](../05-seguranca-e-etica.md) (Mitigações, service account, túnel DNS)
- [024-skills-terceiros-checklist-egress.md](024-skills-terceiros-checklist-egress.md) (manifesto com domínios, malha dinâmica)
