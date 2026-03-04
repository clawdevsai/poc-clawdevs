# [team-devs-ai] Segurança em runtime: validação pré-execução

**Fase:** 2 — Segurança  
**Labels:** security, runtime

## Descrição

Implementar habilidades de validação em runtime para todos os agentes: antes de executar comandos shell, acessar URLs, manipular paths ou processar conteúdo externo. Mitigar injeção de comando, SSRF, path traversal, injeção de prompt, exposição de API keys e exfiltração.

## Critérios de aceite

- [x] Validação antes de executar comandos: metacaracteres, comandos perigosos, substituição de processo; bloquear e registrar. **Ref:** [14-seguranca-runtime-agentes.md](../14-seguranca-runtime-agentes.md) §1.1; [021-implementacao.md](021-implementacao.md).
- [x] **Comandos npm/pip em sandbox efêmero air-gapped:** somente em container dinâmico sem rede; orquestrador destrói ao término. **Ref:** Doc 14 §1.1; [05-seguranca-e-etica.md](../05-seguranca-e-etica.md); [k8s/sandbox/](../../k8s/sandbox/).
- [x] Validação antes de URLs: bloquear IPs privados, localhost, metadados, .local/.internal (SSRF). **Ref:** Doc 14 §1.2; gateway GET `/check_egress?domain=` (whitelist + reputação).
- [x] Validação de paths: traversal, /etc/passwd, chaves SSH, config credenciais. **Ref:** Doc 14 §1.3.
- [x] Conteúdo externo como DADO; escanear injeção de prompt; reportar CyberSec. **Ref:** Doc 14 §1.4; [prompt_injection_detector.py](../../scripts/prompt_injection_detector.py).
- [x] Detecção de credenciais em saída; redactar; registrar. **Ref:** Doc 14 §1.5.
- [x] Matriz por agente documentada (quem valida o quê). **Ref:** Doc 14 §3; integração TOOLS.md conforme evolução.
- [x] **Quarentena de disco (4 etapas):** diff → assinaturas → SAST (semgrep) → entropia contextual. **Ref:** [21-quarentena-disco-pipeline.md](../21-quarentena-disco-pipeline.md), [quarantine_entropy.py](../../scripts/quarantine_entropy.py), [128-sast-entropia-quarentena.md](128-sast-entropia-quarentena.md).
- [x] **Architect só diffs do PR:** revisão exclusivamente sobre diffs; nunca leitura direta do volume. **Ref:** Doc 14 §3.1; [21-quarentena-disco-pipeline.md](../21-quarentena-disco-pipeline.md).

## Implementação (início Fase 2)

- **Pipeline de quarentena de disco (4 etapas):** Documentado em [21-quarentena-disco-pipeline.md](../21-quarentena-disco-pipeline.md) — ordem diff → assinaturas → SAST (semgrep) → entropia contextual. Script de entropia: [scripts/quarantine_entropy.py](../../scripts/quarantine_entropy.py).
- **Architect só diffs do PR:** Regra explícita em [14-seguranca-runtime-agentes.md](../14-seguranca-runtime-agentes.md) § 3.1 e em [21-quarentena-disco-pipeline.md](../21-quarentena-disco-pipeline.md).
- Validações pré-execução (comandos, URLs, paths, conteúdo) e matriz por agente já estão em [14-seguranca-runtime-agentes.md](../14-seguranca-runtime-agentes.md); integração operacional no orquestrador/skills conforme evolução.

## Referências

- [14-seguranca-runtime-agentes.md](../14-seguranca-runtime-agentes.md)
