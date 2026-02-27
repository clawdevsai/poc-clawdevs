# [team-devs-ai] Segurança em runtime: validação pré-execução

**Fase:** 2 — Segurança  
**Labels:** security, runtime

## Descrição

Implementar habilidades de validação em runtime para todos os agentes: antes de executar comandos shell, acessar URLs, manipular paths ou processar conteúdo externo. Mitigar injeção de comando, SSRF, path traversal, injeção de prompt, exposição de API keys e exfiltração.

## Critérios de aceite

- [ ] Validação antes de executar comandos: metacaracteres de shell, comandos perigosos (rm -rf, curl | bash), substituição de processo; bloquear e registrar se ameaça.
- [ ] **Comandos de instalação (npm, pip) e execução de código de terceiros:** somente em **sandbox efêmero air-gapped** (container gerado dinamicamente, sem rede); orquestrador destrói o container ao término. Nunca no container principal do agente.
- [ ] Validação antes de acessar URLs: bloquear IPs privados, localhost, metadados (169.254.169.254), domínios .local/.internal (SSRF).
- [ ] Validação de paths: bloquear traversal (../), acesso a /etc/passwd, chaves SSH, config de credenciais.
- [ ] Conteúdo externo tratado como DADO, nunca como instrução; escanear padrões de injeção de prompt; reportar ao CyberSec em suspeita.
- [ ] Detecção de padrões de credenciais em saída; não repetir em respostas; registrar evento.
- [ ] Matriz por agente documentada (quem valida o quê) e integrada ao workspace (TOOLS.md ou equivalente).
- [ ] **Quarentena de disco:** resultado do sandbox efêmero (instalações npm/pip) só transferido para o repositório após: **(1)** análise determinística de diff de caminhos (apenas arquivos esperados no escopo da biblioteca); **(2)** verificação de **assinaturas criptográficas** (matriz de confiança; se ok, dispensar entropia restritiva para esse pacote); **(3)** **SAST leve (semgrep)** no sandbox com regras estritas; **(4)** **analisador de entropia com consciência contextual** (whitelist de extensões; em pico em arquivo tolerado, opção de análise dinâmica pelo CyberSec). Ver [05-seguranca-e-etica.md](../05-seguranca-e-etica.md), [14-seguranca-runtime-agentes.md](../14-seguranca-runtime-agentes.md) e [128-sast-entropia-quarentena.md](128-sast-entropia-quarentena.md).
- [ ] **Architect (revisão estática):** revisão de código **exclusivamente** sobre **diffs do PR** em relação à branch principal; **nunca** leitura direta do volume compartilhado (evitar validar artefatos envenenados que contornaram o histórico de commits). Ver [14-seguranca-runtime-agentes.md](../14-seguranca-runtime-agentes.md).

## Implementação (início Fase 2)

- **Pipeline de quarentena de disco (4 etapas):** Documentado em [21-quarentena-disco-pipeline.md](../21-quarentena-disco-pipeline.md) — ordem diff → assinaturas → SAST (semgrep) → entropia contextual. Script de entropia: [scripts/quarantine_entropy.py](../../scripts/quarantine_entropy.py).
- **Architect só diffs do PR:** Regra explícita em [14-seguranca-runtime-agentes.md](../14-seguranca-runtime-agentes.md) § 3.1 e em [21-quarentena-disco-pipeline.md](../21-quarentena-disco-pipeline.md).
- Validações pré-execução (comandos, URLs, paths, conteúdo) e matriz por agente já estão em [14-seguranca-runtime-agentes.md](../14-seguranca-runtime-agentes.md); integração operacional no orquestrador/skills conforme evolução.

## Referências

- [14-seguranca-runtime-agentes.md](../14-seguranca-runtime-agentes.md)
