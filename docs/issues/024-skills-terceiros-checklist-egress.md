# [team-devs-ai] Skills de terceiros: checklist e egress filtering

**Fase:** 2 — Segurança  
**Labels:** security, skills, network

## Descrição

Aviso e mitigação para skills de terceiros (ex.: Claw Hub): checklist antes de instalar (origem, revisão do SKILL.md, aprovação em dúvida). **Verificação criptográfica na borda:** manifesto SHA-256 (`skillstracelock.json`) obrigatório; roteador OpenClaw rejeita download com hash não batente (sem depender de LLM). **Zero binários:** código de conduta DevOps e Architect — skills apenas em texto claro; rejeitar pré-compilados. Configurar egress filtering (whitelist de rede) para o container OpenClaw. **Desvincular** liberação de rede da autodeclaração da skill: **whitelist global estática** no Gateway (ex.: NPM, GitHub, API OpenAI); domínios fora → bloqueio + alerta crítico Telegram. **Validação determinística de reputação de domínio** (ex.: API VirusTotal) antes de aplicar regra de egress; rejeitar se domínio novo ou má reputação.

## Critérios de aceite

- [ ] Documentação do aviso: skills não verificadas = risco de execução maliciosa (exfiltração, RCE).
- [ ] **Verificação na borda:** skillstracelock.json (SHA-256); rejeição automática de download com hash não batente; não depender de análise semântica do CyberSec para barrar artefatos adulterados.
- [ ] **Zero binários:** regra no código de conduta (DevOps, Architect) — skills só em texto claro; rejeitar binários e pré-compilados.
- [ ] **Whitelist global estática:** Gateway com lista global estática de domínios permitidos (ex.: NPM, GitHub, OpenAI). Se o manifesto da skill pedir domínio **fora** dessa lista → malha **bloqueia por padrão** + **alerta crítico no Telegram**; skill fica sem egress para esse destino.
- [ ] **Validação determinística de reputação de domínio:** antes de aplicar regra de egress para domínio solicitado no manifesto, usar ferramenta **não baseada em LLM** (ex.: script que consulta API VirusTotal ou equivalente); se domínio recém-registrado ou má reputação → **rejeitar** liberação. Skills podem declarar `allowed_domains` no manifesto para documentação; liberação efetiva depende da whitelist global e da verificação de reputação.
- [ ] Checklist de verificação de skill antes de instalar: origem (autor/registry), revisão de SKILL.md (comandos suspeitos, shell, curl/wget), hash, zero binários; em dúvida pedir aprovação ao Diretor.
- [ ] **Skill com manifesto validado + sem binários:** pode ir para **sandbox de execução (quarentena)** em vez de bloquear a sprint aguardando OK do Diretor para cada instalação; manter aprovação explícita para casos de dúvida. Ver [05-seguranca-e-etica.md](../05-seguranca-e-etica.md) e [19-descoberta-instalacao-skills.md](../19-descoberta-instalacao-skills.md).
- [ ] Egress filtering: NetworkPolicy ou Istio/Cilium; **whitelist global estática** no Gateway (não atualização dinâmica a partir do manifesto da skill); bloquear tráfego não autorizado e disparar alerta crítico para domínios fora da lista.
- [ ] Referência a varredura externa (registro de confiança) quando disponível.

## Implementação (início Fase 2)

- **Whitelist global estática:** ConfigMap [k8s/security/egress-whitelist-configmap.yaml](../../k8s/security/egress-whitelist-configmap.yaml); Gateway deve usar essa lista e **não** a autodeclaração da skill.
- **Validação de reputação de domínio:** Script [scripts/check_domain_reputation.py](../../scripts/check_domain_reputation.py). Sem API key (variável `VIRUSTOTAL_API_KEY`), comportamento configurável: `CHECK_DOMAIN_NO_API=block` (rejeitar) ou `allow`. Integração com VirusTotal (ou equivalente) quando a API key for configurada.
- **Checklist de skill:** Documentado em [05-seguranca-e-etica.md](../05-seguranca-e-etica.md) (Skills de terceiros) e [19-descoberta-instalacao-skills.md](../19-descoberta-instalacao-skills.md) — origem, revisão do SKILL.md, hash, zero binários, aprovação em dúvida.

## Referências

- [05-seguranca-e-etica.md](../05-seguranca-e-etica.md) (Skills de terceiros, Filtro de conteúdo)
