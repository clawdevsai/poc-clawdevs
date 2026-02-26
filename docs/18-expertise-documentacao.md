# Expertise em documentação

Os agentes do enxame (CEO, PO, DevOps, Architect, Developer, QA, CyberSec, UX) devem **navegar e usar a documentação do projeto com método**: árvore de decisão, busca e descoberta, obtenção do doc correto e citação da fonte. Este documento consolida as habilidades de *documentation expert* aplicadas à pasta `docs/agents-devs` e ao workspace do time.

**Objetivo:** Encontrar rapidamente o documento certo, responder com base em conteúdo atualizado e citar a origem ao responder.

---

## Visão geral

| Habilidade | Objetivo |
|-------------|----------|
| **Árvore de decisão** | Direcionar a pergunta do usuário (ou da própria tarefa) para a categoria/doc certo. |
| **Busca e descoberta** | Localizar docs por palavra-chave, por data de atualização ou por caminho. |
| **Obter e citar** | Ler o doc específico e citar a fonte (arquivo e, quando fizer sentido, URL ou trecho). |

---

## 1. Árvore de decisão

Ao precisar de informação da documentação, classificar a necessidade e ir ao doc correspondente:

- **"Como configuro X?"** → [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md), [09-setup-e-scripts.md](09-setup-e-scripts.md)
  - OpenClaw, provedores, gateway → 07
  - Setup "um clique", scripts, transcrição de áudio → 09

- **"Por que X não funciona?" / troubleshooting** → [06-operacoes.md](06-operacoes.md), [05-seguranca-e-etica.md](05-seguranca-e-etica.md)
  - Primeiros socorros, GPU, cluster, diagnóstico → 06
  - Segurança, skills, tokens, sandbox → 05

- **"Quais são os requisitos de hardware / máquina de referência?"** → [00-objetivo-e-maquina-referencia.md](00-objetivo-e-maquina-referencia.md), [04-infraestrutura.md](04-infraestrutura.md)
  - Specs verificadas (CPU, GPU, RAM, SSD), comandos de verificação e script `verify-machine.sh` → 00
  - Limites 65%, Minikube, YAML, Docker → 04

- **"O que é X?" / conceitos** → [01-visao-e-proposta.md](01-visao-e-proposta.md), [02-agentes.md](02-agentes.md), [03-arquitetura.md](03-arquitetura.md), [04-infraestrutura.md](04-infraestrutura.md)
  - Visão, autonomia, War Room → 01
  - Definição dos nove agentes, permissões, conflitos → 02
  - Redis Streams, GPU Lock, fluxo de eventos → 03
  - Minikube, recursos, YAML, Docker → 04

- **"Como automatizo X?" / crons, heartbeats** → [13-habilidades-proativas.md](13-habilidades-proativas.md), [10-self-improvement-agentes.md](10-self-improvement-agentes.md)
  - Crons autônomo vs promptado, heartbeats → 13
  - Estrutura do workspace, learnings, WAL → 10

- **"Como uso a ferramenta X?"** → [11-ferramentas-browser.md](11-ferramentas-browser.md), [12-ferramenta-summarize.md](12-ferramenta-summarize.md), [20-ferramenta-github-gh.md](20-ferramenta-github-gh.md), [24-busca-web-headless.md](24-busca-web-headless.md), [27-ferramenta-markdown-converter.md](27-ferramenta-markdown-converter.md)
  - Browser (navegação, snapshot, E2E) → 11
  - Summarize (URLs, PDFs, áudio, pipeline) → 12
  - Busca web headless (pesquisa e extração de conteúdo sem browser) → 24
  - Markdown converter (PDF, Word, Excel, etc. → Markdown) → 27

- **"Como busco na web / informação externa?"** → [24-busca-web-headless.md](24-busca-web-headless.md)
  - Pesquisa na web e extração de conteúdo de URL em markdown; implementação via skill do ecossistema.

- **"O que devo fazer em segurança?"** → [05-seguranca-e-etica.md](05-seguranca-e-etica.md), [14-seguranca-runtime-agentes.md](14-seguranca-runtime-agentes.md), [15-seguranca-aplicacao-owasp.md](15-seguranca-aplicacao-owasp.md), [16-ciso-habilidades.md](16-ciso-habilidades.md)
  - Zero Trust, skills, rede, kill switch → 05
  - Validação pré-execução (comandos, URLs, paths) → 14
  - OWASP, auditoria de aplicação → 15
  - CISO: infra, conformidade, incidentes, fornecedores → 16

- **"Como escrevo para humanos?"** → [17-escrita-humanizada.md](17-escrita-humanizada.md)

- **"Como criar frontend/UI distinto?" / design de interface** → [23-frontend-design.md](23-frontend-design.md)
  - Design thinking, estética (tipografia, cor, motion, composição), anti-genérico → 23

- **"Quem é cada agente?" (alma, tom)** → [soul/](soul/) (SOUL de cada agente)

---

## 2. Busca e descoberta

Antes de afirmar que não há informação:

1. **Por palavra-chave:** Buscar no workspace em `docs/agents-devs` (grep ou busca semântica) pelo termo relevante.
2. **Por índice:** Usar o [README.md](README.md) da pasta — tabela de documentos e diagrama de dependência.
3. **Por recência:** Se a dúvida for "o que mudou?" ou "documentação atualizada", verificar histórico (ex.: `git log --oneline -- docs/agents-devs`) ou datas de modificação dos arquivos.

Regra: **não responder "não tenho essa informação"** sem ter buscado na documentação do projeto.

---

## 3. Obter e citar

- **Obter o doc:** Ler o arquivo correspondente (ex.: `docs/agents-devs/07-configuracao-e-prompts.md`) quando a árvore de decisão ou a busca indicar.
- **Citar a fonte:** Ao responder com base na documentação, indicar o documento (e, se útil, a seção ou trecho), por exemplo: *"Conforme [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md), o pipeline de truncamento..."*.
- **Snippets:** Se existirem trechos de configuração prontos (ex.: em docs ou em arquivo de snippets do projeto), preferir referenciá-los e citar a origem em vez de inventar exemplos.

---

## 4. Fluxo de uso

1. **Identificar a necessidade** com a árvore de decisão acima.
2. **Buscar** se não tiver certeza do doc: grep/busca semântica em `docs/agents-devs`.
3. **Ler o doc** indicado (ou o mais relevante).
4. **Responder** com base no conteúdo e **citar o documento**.
5. **Não inventar** configurações ou procedimentos que estejam escritos na documentação — usar o que está escrito.

---

## 5. Relação com a documentação

- [13-habilidades-proativas.md](13-habilidades-proativas.md) — A "Busca unificada" (memória, transcripts, notas) complementa esta expertise: primeiro buscar na doc do projeto (este doc), depois em memória e outros artefatos.
- [10-self-improvement-agentes.md](10-self-improvement-agentes.md) — Estrutura do workspace (AGENTS.md, SOUL.md, TOOLS.md); a navegação em docs integra-se ao uso desses arquivos.
- [02-agentes.md](02-agentes.md) — Definição dos agentes; ao responder sobre papéis, permissões ou conflitos, usar 02 e citar.
- [24-busca-web-headless.md](24-busca-web-headless.md) — Busca web e extração de conteúdo: quando a informação não estiver na doc do projeto, usar busca web headless (pesquisa e extração de URL) para documentação externa, APIs e fatos.
- [README.md](README.md) — Índice principal de `docs/agents-devs`; ponto de partida para navegação.
- [23-frontend-design.md](23-frontend-design.md) — Diretrizes de frontend design para Developer e UX; uso ao responder sobre interfaces, UI e estética de frontend.
