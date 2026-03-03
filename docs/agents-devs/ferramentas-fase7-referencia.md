# Ferramentas (Fase 7) — Referência no repositório

Mapeamento das issues 070–075 para documentação e uso no ecossistema.

---

## 070 — Ferramentas de browser (agent-browser)

| Critério | Onde está |
|----------|------------|
| Instalação e dependências | [11-ferramentas-browser.md](../11-ferramentas-browser.md) § Instalação (npm, from source) |
| Comandos principais (navegação, snapshot, click, type, etc.) | Doc 11 § Fluxo básico, Comandos por categoria (Navegação, Snapshot, Interações, Obter informação, Estado e espera, Screenshot/PDF/vídeo) |
| Uso por QA (E2E, validação UI) e UX (fluxos, evidências) | Doc 11 § Integração com o enxame (QA, Developer, UX) |
| Boas práticas e segurança (Zero Trust, URLs validadas) | Doc 11 § Boas práticas para agentes; segurança: [14-seguranca-runtime-agentes.md](../14-seguranca-runtime-agentes.md), [05-seguranca-e-etica.md](../05-seguranca-e-etica.md) — validar URLs antes de abrir |

---

## 071 — Ferramenta summarize

| Critério | Onde está |
|----------|------------|
| Ferramenta para sumarizar URLs, PDFs, imagens, áudio, YouTube | [12-ferramenta-summarize.md](../12-ferramenta-summarize.md) § Instalação, Quick start |
| Flags e opções (idioma, tamanho máximo) | Doc 12 § Flags úteis (`--length`, `--max-output-tokens`, `--json`, `--youtube`, etc.) |
| Integração com pipeline de truncamento | Doc 12 § Uso no ecossistema, Pre-flight obrigatório; [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) |
| Exceção: invariantes/microADR não passam ao summarize | Doc 12 § Regra de ouro — exceções à sumarização; [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) §2.3 |
| Uso por CEO e PO (resumos executivos) | Doc 12 § CEO/PO |

---

## 072 — Ferramenta GitHub (gh CLI)

| Critério | Onde está |
|----------|------------|
| gh instalado e autenticado; --repo quando fora do repo | [20-ferramenta-github-gh.md](../20-ferramenta-github-gh.md) § Requisito |
| Comandos: gh issue, gh pr, gh pr checks, gh run list/view, gh api | Doc 20 § Pull Requests (checks, run list, run view, log-failed), API |
| Matriz de uso por agente (PO, Developer, Architect, DevOps, QA, CyberSec) | Doc 20 § Quem pode usar (tabela) |
| Segurança: nunca expor tokens; validação em runtime | Doc 20 § Segurança; [05-seguranca-e-etica.md](../05-seguranca-e-etica.md), [14-seguranca-runtime-agentes.md](../14-seguranca-runtime-agentes.md) |

---

## 073 — Ferramenta Markdown Converter (markitdown)

| Critério | Onde está |
|----------|------------|
| Instalação e uso de uvx markitdown | [27-ferramenta-markdown-converter.md](../27-ferramenta-markdown-converter.md) § Instalação, Uso básico |
| Formatos: PDF, Word, PowerPoint, Excel, HTML, imagens, áudio, ZIP, YouTube, EPub | Doc 27 § Formatos suportados |
| Uso por CEO, PO, Developer e pipeline de pré-processamento | Doc 27 § Uso no ecossistema de agentes |
| Architect e microADR (markitdown ou saída formatada; anexar ao Warm Store) | Doc 27 § Architect — microADR; [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) §2.3 |
| Integração com expertise em documentação (18) | Doc 27 § Expertise em documentação |

---

## 074 — Ollama Local (skill)

| Critério | Onde está |
|----------|------------|
| Gestão de modelos: listar, pull, remover | [31-ollama-local.md](../31-ollama-local.md) § Referência rápida; [scripts/ollama.py](../../scripts/ollama.py) (`list`, `pull`, `rm`, `show`) |
| Uso: chat, completions, embeddings, tool-use | Doc 31 § Referência rápida (chat, generate, embed), § Tool-use; script [ollama.py](../../scripts/ollama.py); tool-use (ollama_tools quando disponível no skill) |
| Seleção de modelos por agente; troubleshooting (porta, GPU, OOM) | Doc 31 § Seleção de modelos, § Troubleshooting |
| Integração com GPU Lock: agentes adquirem lock antes de chamar Ollama | Doc 31 § Segurança e alinhamento (Integração com GPU Lock); [gpu_lock.py](../../scripts/gpu_lock.py) |

---

## 075 — OpenCode Controller

| Critério | Onde está |
|----------|------------|
| Pré-voo: confirmar provedor e autenticação com usuário | [33-opencode-controller.md](../33-opencode-controller.md) § Pré-voo |
| Gestão de sessões: reutilizar sessão atual; /sessions; nunca criar nova sem aprovação | Doc 33 § Gestão de sessões |
| Controle de agente: /agents; iniciar em Plan; alternar para Build quando plano aprovado | Doc 33 § Controle de agente (modo Plan/Build) |
| Seleção de modelo: /models; auth → link ao usuário, aguardar confirmação | Doc 33 § Seleção de modelo |
| Comportamento em Plan: analisar tarefa, propor plano, perguntas, revisar; não gerar código em Plan | Doc 33 § Comportamento no modo Plan |
| Comportamento em Build: implementar conforme plano; tratar perguntas e falhas | Doc 33 § Comportamento no modo Build, § Tratamento de perguntas, § Falhas comuns |
| Documentação para CEO/PO e Developer sobre quando e como usar o OpenCode | Doc 33 § Quem usa, § Fluxo padrão, § Comandos principais, § Prompts típicos |
