# [team-devs-ai] SAST (semgrep) e checagem de entropia contextual no pipeline de quarentena

**Fase:** 2 — Segurança  
**Labels:** security, quarantine, supply-chain, sast

## Descrição

Integrar ao pipeline de quarentena de dependências (npm/pip) as etapas necessárias antes de transferir artefatos do sandbox para o repositório: **SAST leve** no sandbox (ex.: semgrep com regras estritas) e **analisador de entropia com consciência contextual** nos arquivos do diff. O diff de caminhos sozinho não detecta código malicioso injetado em arquivos legítimos (ex.: index.js envenenado); SAST e entropia fecham o ponto cego. **Risco de falsos positivos:** entropia cega (limite matemático único) bloqueia arquivos legítimos de alto uso (minificados, .wasm, .map); é obrigatório **entropia contextual** e **matriz de confiança (assinaturas)** para evitar paralisia do Developer com pacotes modernos.

## Critérios de aceite

- [ ] **Matriz de confiança (assinaturas criptográficas):** Antes da checagem de entropia, verificar se o **hash/assinatura do pacote** coincide com o **registro oficial** (provedores da matriz: npm, Google, Vercel, etc.). Se **sim**, **aprovar transferência** para esse pacote na etapa de entropia (não bloquear por entropia alta).
- [ ] **SAST leve no sandbox:** executar ferramenta determinística e leve (ex.: **semgrep**) sobre os arquivos extraídos no sandbox, com **regras estritas** (padrões de injeção de rede, eval oculto, execuções de shell indesejadas no pacote). Se violação → **rejeitar** transferência e disparar **alerta crítico**. Ver [05-seguranca-e-etica.md](../05-seguranca-e-etica.md) (seção 1.3) e [14-seguranca-runtime-agentes.md](../14-seguranca-runtime-agentes.md) (3.1).
- [ ] **Analisador de entropia com consciência contextual:** não aplicar um único limite matemático cego. **Whitelist de extensões** (ex.: `.map`, `.wasm`, `.min.js`) com **tolerância de entropia muito maior** que arquivos como `.sh` ou texto legível esperado. Se arquivo que deveria ser texto claro (e não na whitelist) apresentar entropia alta → rejeitar transferência e alertar o Developer.
- [ ] **Análise dinâmica opcional:** Se **pico de entropia** for detectado em arquivo de tipo tolerado (whitelist), orquestrador pode acionar **CyberSec em modo dinâmico isolado** para **auditar semanticamente** o arquivo (minificação padrão vs eval/injeção de shell); decisão final com base nessa auditoria em vez de rejeição imediata.
- [ ] Ordem do pipeline de quarentena: (1) diff de caminhos; (2) verificação de assinaturas (matriz de confiança); (3) SAST leve; (4) checagem de entropia contextual; só então aprovar transferência (ou rejeitar e alertar).

## Implementação (início Fase 2)

- **Pipeline em 4 etapas e entropia contextual:** Doc [21-quarentena-disco-pipeline.md](../21-quarentena-disco-pipeline.md) — ordem (1) diff de caminhos, (2) assinaturas, (3) SAST leve (semgrep), (4) entropia contextual.
- **Script de entropia:** [scripts/quarantine_entropy.py](../../scripts/quarantine_entropy.py) — whitelist de extensões (`.map`, `.wasm`, `.min.js`, etc.) com tolerância alta; variáveis `QUARANTINE_HIGH_ENTROPY_EXT`, `QUARANTINE_MAX_ENTROPY_PLAINTEXT`, `QUARANTINE_MAX_ENTROPY_HIGH`. Uso: `quarantine_entropy.py <dir>`; exit 0 = passou, 1 = algum arquivo falhou.
- **SAST:** Executar semgrep no sandbox sobre os arquivos extraídos (ex.: `semgrep scan --config auto --strict`); regras estritas para injeção, eval, shell. Matriz de confiança (assinaturas) dispensa entropia restritiva para pacotes oficiais.

## Referências

- [05-seguranca-e-etica.md](../05-seguranca-e-etica.md) (seção 1.3 — Quarentena de disco, Pipeline de quarentena)
- [14-seguranca-runtime-agentes.md](../14-seguranca-runtime-agentes.md) (3.1 — Quarentena de disco)
- [020-zero-trust-fluxo-classificacao.md](020-zero-trust-fluxo-classificacao.md) (Pipeline de quarentena)
- [021-seguranca-runtime-validacao.md](021-seguranca-runtime-validacao.md) (Quarentena de disco)
