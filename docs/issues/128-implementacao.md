# SAST e entropia contextual na quarentena (128) — Implementação

**Pipeline em 4 etapas:** Ordem documentada em [21-quarentena-disco-pipeline.md](../21-quarentena-disco-pipeline.md): (1) diff de caminhos, (2) matriz de confiança (assinaturas), (3) SAST leve (semgrep), (4) entropia contextual. Só então aprovar transferência.

**Matriz de confiança (assinaturas):** Etapa 2 do pipeline; doc 21 descreve verificação hash/assinatura vs registro oficial (npm, PyPI, etc.). Se ok → dispensar entropia restritiva na etapa 4. Implementação operacional no orquestrador/sandbox conforme integração.

**SAST leve no sandbox:** Doc 21 § SAST (semgrep): executar `semgrep scan --config auto --strict` sobre arquivos extraídos no sandbox; regras para injeção, eval, exec de shell. Violação → rejeitar transferência e alerta crítico. Ref: [05-seguranca-e-etica.md](../05-seguranca-e-etica.md) §1.3, [14-seguranca-runtime-agentes.md](../14-seguranca-runtime-agentes.md) §3.1.

**Entropia contextual:** [scripts/quarantine_entropy.py](../../scripts/quarantine_entropy.py) — whitelist de extensões (`.map`, `.wasm`, `.min.js`, etc.) com tolerância alta (`QUARANTINE_MAX_ENTROPY_HIGH`); arquivos fora da whitelist (ex.: `.sh`, texto esperado) com limite `QUARANTINE_MAX_ENTROPY_PLAINTEXT`. Pico em arquivo tolerado → opção de análise dinâmica pelo CyberSec (doc 21, 05).

**Análise dinâmica opcional:** Documentado em doc 21 e 05: se pico de entropia em arquivo de tipo tolerado, orquestrador pode acionar CyberSec em modo dinâmico isolado para auditoria semântica.

Ref: [128-sast-entropia-quarentena.md](128-sast-entropia-quarentena.md).
