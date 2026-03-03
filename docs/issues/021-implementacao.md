# Segurança runtime: validação pré-execução (021) — Implementação

Mapeamento dos critérios da issue 021 para documentação e scripts existentes no repositório.

| Critério | Onde está | Observação |
|----------|-----------|------------|
| **Validação antes de comandos** | [14-seguranca-runtime-agentes.md](../14-seguranca-runtime-agentes.md) §1.1 — metacaracteres, comandos perigosos, substituição de processo; bloquear e registrar | Regras e matriz por agente no doc 14 |
| **Comandos npm/pip em sandbox air-gapped** | Doc 14 §1.1; [05-seguranca-e-etica.md](../05-seguranca-e-etica.md); [k8s/sandbox/](../../k8s/sandbox/) (Job + seccomp) | Container efêmero sem rede; orquestrador destrói ao término |
| **Validação antes de URLs (SSRF)** | Doc 14 §1.2 — IPs privados, localhost, 169.254, .local/.internal | Gateway: [gateway_redis_adapter.py](../../scripts/gateway_redis_adapter.py) GET `/check_egress?domain=` (whitelist + reputação) |
| **Validação de paths** | Doc 14 §1.3 — traversal, /etc/passwd, chaves SSH, config credenciais | Bloquear e registrar |
| **Conteúdo externo como DADO; injeção de prompt** | Doc 14 §1.4; [prompt_injection_detector.py](../../scripts/prompt_injection_detector.py) — `detect(text)`, padrões, reportar CyberSec | Ref. issue 026 |
| **Detecção credenciais em saída** | Doc 14 §1.5 — padrões de API keys; redactar/bloquear; registrar | |
| **Matriz por agente** | Doc 14 §3 — tabela "Quem aplica o quê"; integração TOOLS.md/workspace conforme evolução | |
| **Quarentena de disco (4 etapas)** | [21-quarentena-disco-pipeline.md](../21-quarentena-disco-pipeline.md); [quarantine_entropy.py](../../scripts/quarantine_entropy.py); [128-sast-entropia-quarentena.md](128-sast-entropia-quarentena.md) | Diff → assinaturas → SAST (semgrep) → entropia contextual |
| **Architect só diffs do PR** | Doc 14 §3.1; [21-quarentena-disco-pipeline.md](../21-quarentena-disco-pipeline.md) | Revisão exclusivamente sobre diffs; nunca leitura direta do volume compartilhado |

**Integração operacional:** Validações aplicadas pelo orquestrador/skills conforme evolução; documentação e scripts de referência disponíveis no repo.

Ref: [021-seguranca-runtime-validacao.md](021-seguranca-runtime-validacao.md).
