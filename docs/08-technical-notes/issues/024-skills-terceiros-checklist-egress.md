# [team-devs-ai] Skills de terceiros: checklist e egress filtering

**Fase:** 2 — Segurança  
**Labels:** security, skills, network

## Descrição

Aviso e mitigação para skills de terceiros (ex.: Claw Hub): checklist antes de instalar (origem, revisão do SKILL.md, aprovação em dúvida). **Verificação criptográfica na borda:** manifesto SHA-256 (`skillstracelock.json`) obrigatório; roteador OpenClaw rejeita download com hash não batente (sem depender de LLM). **Zero binários:** código de conduta DevOps e Architect — skills apenas em texto claro; rejeitar pré-compilados. Configurar egress filtering (whitelist de rede) para o container OpenClaw. **Desvincular** liberação de rede da autodeclaração da skill: **whitelist global estática** no Gateway (ex.: NPM, GitHub, API OpenAI); domínios fora → bloqueio + alerta crítico Telegram. **Validação determinística de reputação de domínio** (ex.: API VirusTotal) antes de aplicar regra de egress; rejeitar se domínio novo ou má reputação.

## Critérios de aceite

- [x] Documentação do aviso: skills não verificadas = risco (exfiltração, RCE). **Ref:** [05-seguranca-e-etica.md](../05-seguranca-e-etica.md), [19-descoberta-instalacao-skills.md](../19-descoberta-instalacao-skills.md); [024-implementacao.md](024-implementacao.md).
- [x] **Verificação na borda:** skillstracelock.json (SHA-256); rejeição automática de download com hash não batente. **Ref:** Doc 19 §4; 05.
- [x] **Zero binários:** skills só em texto claro; rejeitar binários e pré-compilados. **Ref:** Doc 05, 19.
- [x] **Whitelist global estática:** ConfigMap egress-whitelist (`ALLOWED_DOMAINS`); Gateway usa essa lista; GET `/check_egress?domain=` — fora da lista → 403 + alerta. **Ref:** [egress-whitelist-configmap.yaml](../../k8s/security/egress-whitelist-configmap.yaml), [gateway_redis_adapter.py](../../scripts/gateway_redis_adapter.py).
- [x] **Validação determinística de reputação de domínio:** script [check_domain_reputation.py](../../scripts/check_domain_reputation.py); Gateway pode usar antes de liberar egress; VirusTotal quando `VIRUSTOTAL_API_KEY` configurada. **Ref:** [024-implementacao.md](024-implementacao.md), validacao-fase2-completa.
- [x] Checklist antes de instalar: origem, revisão SKILL.md, hash, zero binários; em dúvida aprovação Diretor. **Ref:** Doc 19.
- [x] **Skill validada + sem binários:** pode ir para sandbox de quarentena; aprovação explícita para dúvida. **Ref:** Doc 05, 19.
- [x] Egress filtering: whitelist global no Gateway (egress-whitelist-configmap); tráfego não autorizado bloqueado; alerta para domínios fora. **Ref:** k8s/security, gateway adapter.
- [x] Referência a varredura externa (registro de confiança) quando disponível. **Ref:** Doc 05, 19.

## Implementação (início Fase 2)

- **Whitelist global estática:** ConfigMap [k8s/security/egress-whitelist-configmap.yaml](../../k8s/security/egress-whitelist-configmap.yaml); Gateway deve usar essa lista e **não** a autodeclaração da skill.
- **Validação de reputação de domínio:** Script [scripts/check_domain_reputation.py](../../scripts/check_domain_reputation.py). Sem API key (variável `VIRUSTOTAL_API_KEY`), comportamento configurável: `CHECK_DOMAIN_NO_API=block` (rejeitar) ou `allow`. Integração com VirusTotal (ou equivalente) quando a API key for configurada.
- **Checklist de skill:** Documentado em [05-seguranca-e-etica.md](../05-seguranca-e-etica.md) (Skills de terceiros) e [19-descoberta-instalacao-skills.md](../19-descoberta-instalacao-skills.md) — origem, revisão do SKILL.md, hash, zero binários, aprovação em dúvida.

## Referências

- [05-seguranca-e-etica.md](../05-seguranca-e-etica.md) (Skills de terceiros, Filtro de conteúdo)
