# Skills de terceiros: checklist e egress (024) — Implementação

**Documentação do aviso:** Skills não verificadas = risco (exfiltração, RCE). Ref: [05-seguranca-e-etica.md](../05-seguranca-e-etica.md) (Skills de terceiros), [19-descoberta-instalacao-skills.md](../19-descoberta-instalacao-skills.md).

**Verificação na borda (skillstracelock.json, SHA-256):** Doc 19 §4 — manifesto SHA-256 obrigatório; roteador/borda rejeita download com hash não batente. Não depender de LLM para barrar artefatos adulterados. Ref: 05, 19.

**Zero binários:** Regra em 05 e 19 — skills só em texto claro; rejeitar binários e pré-compilados; Architect analisa estaticamente.

**Whitelist global estática:** [k8s/security/egress-whitelist-configmap.yaml](../../k8s/security/egress-whitelist-configmap.yaml) — `ALLOWED_DOMAINS`. Gateway [gateway_redis_adapter.py](../../scripts/gateway_redis_adapter.py) usa essa lista (não autodeclaração da skill); GET `/check_egress?domain=` — fora da lista → 403 + alerta. Ref: [validacao-fase2-completa.md](validacao-fase2-completa.md).

**Validação de reputação de domínio:** [scripts/check_domain_reputation.py](../../scripts/check_domain_reputation.py) — CLI `check_domain_reputation.py <domain>`; exit 0 = allow, 1 = block. Variável `VIRUSTOTAL_API_KEY`; sem API key: `CHECK_DOMAIN_NO_API=block` ou `allow`. Gateway pode chamar antes de liberar egress. Ref: 024 issue, validacao-fase2-completa.

**Checklist antes de instalar:** Doc 19 — origem (autor/registry), revisão do SKILL.md (comandos suspeitos, shell, curl/wget), hash, zero binários; em dúvida pedir aprovação ao Diretor.

**Skill validada → sandbox de execução (quarentena):** Doc 05 e 19 — manifesto validado + sem binários pode ir para sandbox de quarentena em vez de bloquear sprint; aprovação explícita para dúvida.

**Egress filtering:** NetworkPolicy/Istio conforme infra; whitelist global no Gateway (egress-whitelist-configmap); tráfego não autorizado bloqueado; alerta crítico para domínios fora.

Ref: [024-skills-terceiros-checklist-egress.md](024-skills-terceiros-checklist-egress.md).
