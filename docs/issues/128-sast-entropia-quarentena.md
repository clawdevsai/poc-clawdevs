# [team-devs-ai] SAST (semgrep) e checagem de entropia contextual no pipeline de quarentena

**Fase:** 2 — Segurança  
**Labels:** security, quarantine, supply-chain, sast

## Descrição

Integrar ao pipeline de quarentena de dependências (npm/pip) as etapas necessárias antes de transferir artefatos do sandbox para o repositório: **SAST leve** no sandbox (ex.: semgrep com regras estritas) e **analisador de entropia com consciência contextual** nos arquivos do diff. O diff de caminhos sozinho não detecta código malicioso injetado em arquivos legítimos (ex.: index.js envenenado); SAST e entropia fecham o ponto cego. **Risco de falsos positivos:** entropia cega (limite matemático único) bloqueia arquivos legítimos de alto uso (minificados, .wasm, .map); é obrigatório **entropia contextual** e **matriz de confiança (assinaturas)** para evitar paralisia do Developer com pacotes modernos.

## Critérios de aceite

- [x] **Matriz de confiança (assinaturas criptográficas):** Etapa 2 do pipeline; doc 21 descreve verificação hash/assinatura vs registro oficial; se ok → dispensar entropia restritiva na etapa 4. **Ref:** [21-quarentena-disco-pipeline.md](../21-quarentena-disco-pipeline.md); [128-implementacao.md](128-implementacao.md).
- [x] **SAST leve no sandbox:** semgrep sobre arquivos extraídos no sandbox; regras estritas (injeção, eval, shell). Violação → rejeitar + alerta crítico. **Ref:** Doc 21 § SAST; [05-seguranca-e-etica.md](../05-seguranca-e-etica.md) §1.3, [14-seguranca-runtime-agentes.md](../14-seguranca-runtime-agentes.md) §3.1.
- [x] **Analisador de entropia com consciência contextual:** whitelist de extensões com tolerância alta; texto esperado (.sh, etc.) com limite menor. **Ref:** [quarantine_entropy.py](../../scripts/quarantine_entropy.py) — `QUARANTINE_HIGH_ENTROPY_EXT`, `QUARANTINE_MAX_ENTROPY_PLAINTEXT`, `QUARANTINE_MAX_ENTROPY_HIGH`.
- [x] **Análise dinâmica opcional:** Doc 21 e 05 — pico em arquivo tolerado → CyberSec em modo dinâmico isolado para auditoria semântica. **Ref:** [128-implementacao.md](128-implementacao.md).
- [x] Ordem do pipeline: (1) diff, (2) assinaturas, (3) SAST, (4) entropia contextual; só então aprovar. **Ref:** [21-quarentena-disco-pipeline.md](../21-quarentena-disco-pipeline.md).

## Implementação (início Fase 2)

- **Pipeline em 4 etapas e entropia contextual:** Doc [21-quarentena-disco-pipeline.md](../21-quarentena-disco-pipeline.md) — ordem (1) diff de caminhos, (2) assinaturas, (3) SAST leve (semgrep), (4) entropia contextual.
- **Script de entropia:** [scripts/quarantine_entropy.py](../../scripts/quarantine_entropy.py) — whitelist de extensões (`.map`, `.wasm`, `.min.js`, etc.) com tolerância alta; variáveis `QUARANTINE_HIGH_ENTROPY_EXT`, `QUARANTINE_MAX_ENTROPY_PLAINTEXT`, `QUARANTINE_MAX_ENTROPY_HIGH`. Uso: `quarantine_entropy.py <dir>`; exit 0 = passou, 1 = algum arquivo falhou.
- **SAST:** Executar semgrep no sandbox sobre os arquivos extraídos (ex.: `semgrep scan --config auto --strict`); regras estritas para injeção, eval, shell. Matriz de confiança (assinaturas) dispensa entropia restritiva para pacotes oficiais.

## Referências

- [05-seguranca-e-etica.md](../05-seguranca-e-etica.md) (seção 1.3 — Quarentena de disco, Pipeline de quarentena)
- [14-seguranca-runtime-agentes.md](../14-seguranca-runtime-agentes.md) (3.1 — Quarentena de disco)
- [020-zero-trust-fluxo-classificacao.md](020-zero-trust-fluxo-classificacao.md) (Pipeline de quarentena)
- [021-seguranca-runtime-validacao.md](021-seguranca-runtime-validacao.md) (Quarentena de disco)
