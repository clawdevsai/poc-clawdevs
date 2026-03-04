# Fase 7 — Ferramentas: escopo e ordem

**Fase:** 7 (070–089)  
**Objetivo:** Browser (agent-browser), summarize, gh CLI, markdown converter (markitdown), Ollama (skill), OpenCode Controller.

## Issues da fase

| # | Issue | Título | Ref doc |
|---|-------|--------|---------|
| 070 | [070-ferramentas-browser-agent-browser.md](070-ferramentas-browser-agent-browser.md) | Ferramentas de browser (agent-browser) | [11-ferramentas-browser.md](../11-ferramentas-browser.md) ✅ |
| 071 | [071-ferramenta-summarize.md](071-ferramenta-summarize.md) | Ferramenta summarize | [12-ferramenta-summarize.md](../12-ferramenta-summarize.md) ✅ |
| 072 | [072-ferramenta-github-gh-cli.md](072-ferramenta-github-gh-cli.md) | Ferramenta GitHub (gh CLI) | [20-ferramenta-github-gh.md](../20-ferramenta-github-gh.md) ✅ |
| 073 | [073-ferramenta-markdown-converter.md](073-ferramenta-markdown-converter.md) | Ferramenta Markdown Converter (markitdown) | [27-ferramenta-markdown-converter.md](../27-ferramenta-markdown-converter.md) ✅ |
| 074 | [074-ollama-local-skill.md](074-ollama-local-skill.md) | Ollama Local (skill) | [31-ollama-local.md](../31-ollama-local.md) + [scripts/ollama.py](../../scripts/ollama.py) ✅ |
| 075 | [075-opencode-controller.md](075-opencode-controller.md) | OpenCode Controller | [33-opencode-controller.md](../33-opencode-controller.md) ✅ |

## Ordem sugerida

1. **070** — agent-browser: instalação, comandos, uso QA/UX, boas práticas e segurança (doc 11).
2. **071** — summarize: CLI/skill, flags, pipeline de truncamento, exceção invariantes/microADR (doc 12).
3. **072** — gh CLI: auth, comandos (issue, pr, checks, run, api), matriz por agente, segurança (doc 20).
4. **073** — markitdown: instalação, formatos, uso CEO/PO/Developer/Architect, microADR, expertise doc (doc 27).
5. **074** — Ollama local como skill (doc 31).
6. **075** — OpenCode Controller (conforme doc/issue).

## Segurança transversal

- **URLs e recursos externos:** Validar antes de executar (Zero Trust). Ref: [05-seguranca-e-etica.md](../05-seguranca-e-etica.md), [14-seguranca-runtime-agentes.md](../14-seguranca-runtime-agentes.md).
- **Tokens:** Nunca expor em chat, logs ou repositório (gh, summarize, APIs).

## Referência consolidada

Mapeamento issues → docs e scripts: [ferramentas-fase7-referencia.md](../agents-devs/ferramentas-fase7-referencia.md).
