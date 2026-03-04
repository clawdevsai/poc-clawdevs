# Quarentena de disco: pipeline em 4 etapas (Fase 2 — 021, 128)

Antes de transferir artefatos do **sandbox efêmero** (instalação npm/pip) para o repositório principal, o orquestrador aplica este pipeline **na ordem**. Ref: [05-seguranca-e-etica.md](05-seguranca-e-etica.md) § 1.3, [14-seguranca-runtime-agentes.md](14-seguranca-runtime-agentes.md) § 3.1, [128-sast-entropia-quarentena.md](issues/128-sast-entropia-quarentena.md).

## Ordem do pipeline

| Etapa | Descrição | Ferramenta / regra |
|-------|-----------|---------------------|
| **1** | **Diff de caminhos** | Script determinístico: apenas arquivos esperados no escopo da biblioteca. Se alteração fora do escopo (ex.: config, arquivo sensível) → rejeitar todo o resultado. |
| **2** | **Matriz de confiança (assinaturas)** | Verificar hash/assinatura do pacote vs registro oficial (npm, PyPI, Google, Vercel, etc.). Se **ok** → dispensar entropia restritiva para esse pacote na etapa 4. |
| **3** | **SAST leve no sandbox** | Executar **semgrep** (ou equivalente) com regras estritas: injeção de rede, eval oculto, exec de shell no pacote. Violação → rejeitar transferência e alerta crítico. Ver [scripts e regras semgrep](#sast-semgrep). |
| **4** | **Entropia contextual** | [scripts/quarantine_entropy.py](../scripts/quarantine_entropy.py): whitelist de extensões (`.map`, `.wasm`, `.min.js`) com tolerância alta; arquivos `.sh` ou texto esperado com entropia alta → rejeitar. Pico em arquivo tolerado → opção de análise dinâmica pelo CyberSec. |

Só após as quatro etapas aprovadas: **aprovar transferência** (ou aprovação temporária + notificação assíncrona no digest). Caso contrário: **rejeitar** e alertar.

## Architect: revisão apenas sobre diffs do PR

O Agente **Architect** deve fazer revisão de código **exclusivamente** sobre **diffs do pull request** em relação à branch principal. **Nunca** ler direto do volume compartilhado para validar código — evita validar artefatos envenenados que contornaram o histórico de commits. Ref: [14-seguranca-runtime-agentes.md](14-seguranca-runtime-agentes.md) § 3.1.

## SAST (semgrep)

- Instalar: `pip install semgrep` ou uso via container no sandbox.
- Regras sugeridas: `p/javascript`, `p/python` com foco em `injection`, `eval`, `exec`; regras custom para padrões de rede/shell no código de dependências.
- Exemplo de invocação (no sandbox, sobre o diretório extraído): `semgrep scan --config auto --strict --error`.

## Scripts de referência

- **Entropia contextual:** [scripts/quarantine_entropy.py](../scripts/quarantine_entropy.py) — extensões com tolerância configurável; saída pass/fail por arquivo ou global.
- **Sandbox de instalação:** [k8s/sandbox/](../k8s/sandbox/) — Job com seccomp (bloqueio de rede); resultado em volume temporário para inspeção pelo pipeline acima.

## Issues

- [021-seguranca-runtime-validacao.md](issues/021-seguranca-runtime-validacao.md)
- [128-sast-entropia-quarentena.md](issues/128-sast-entropia-quarentena.md)
