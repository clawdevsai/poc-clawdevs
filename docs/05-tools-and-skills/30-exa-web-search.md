# Exa Web Search (busca neural web, código e empresas)

Os agentes do enxame podem usar **busca neural na web**, **contexto de código** (GitHub, Stack Overflow) e **pesquisa de empresas** via **Exa MCP**, sem necessidade de API key. Implementação concreta das habilidades de busca web headless descritas em [24-busca-web-headless.md](24-busca-web-headless.md), com ferramentas adicionais para código e business intelligence.

**Objetivo:** Pesquisar na web (notícias, fatos, tendências), obter exemplos e documentação de código, e pesquisar empresas — tudo via Exa MCP (mcporter), leve e sem browser.

---

## Habilidades cobertas

| Habilidade | Ferramenta Exa | Descrição |
|------------|----------------|-----------|
| **Busca web** | `web_search_exa` | Pesquisa na web (notícias, fatos, informação atual). Parâmetros: `query`, `numResults`, `type` (auto/fast/deep). |
| **Contexto de código** | `get_code_context_exa` | Busca exemplos e documentação em GitHub, Stack Overflow. Parâmetros: `query`, `tokensNum` (1000–50000). |
| **Pesquisa de empresas** | `company_research_exa` | Pesquisa de empresas (notícias, negócios, funding). Parâmetros: `companyName`, `numResults`. |
| **Extração de página** | (avançado) `crawling_exa` | Extrair conteúdo de uma URL (requer config exa-full). |
| **Busca avançada** | (avançado) `web_search_advanced_exa`, `deep_search_exa` | Filtros por domínio/data, expansão de query (config exa-full). |
| **Pesquisa de pessoas** | (avançado) `people_search_exa` | Perfis profissionais (config exa-full). |
| **Deep Researcher** | (avançado) `deep_researcher_start` / `deep_researcher_check` | Agente de pesquisa em profundidade (config exa-full). |

---

## Setup (mcporter)

A capacidade é fornecida pelo **MCP Exa**, configurado via `mcporter` (não via Skills CLI). Não é necessária API key para o conjunto básico.

**Verificar se Exa está configurado:**

```bash
mcporter list exa
```

**Se não estiver listado:**

```bash
mcporter config add exa https://mcp.exa.ai/mcp
```

**Ferramentas avançadas (opcional):** Para habilitar `deep_search_exa`, `crawling_exa`, `people_search_exa`, `deep_researcher_*`, usar uma config com todas as tools:

```bash
mcporter config add exa-full "https://mcp.exa.ai/mcp?tools=web_search_exa,web_search_advanced_exa,get_code_context_exa,deep_search_exa,crawling_exa,company_research_exa,people_search_exa,deep_researcher_start,deep_researcher_check"
```

Uso: `mcporter call 'exa-full.deep_search_exa(...)'` etc.

---

## Ferramentas principais (uso típico)

### web_search_exa

Busca na web para notícias, fatos ou pesquisa geral.

```bash
mcporter call 'exa.web_search_exa(query: "latest AI news 2026", numResults: 5)'
mcporter call 'exa.web_search_exa(query: "best practices API design", type: "deep", numResults: 8)'
```

- **type:** `"auto"` (padrão), `"fast"` (rápido), `"deep"` (mais completo).

### get_code_context_exa

Busca exemplos e documentação em repositórios e Stack Overflow.

```bash
mcporter call 'exa.get_code_context_exa(query: "React hooks examples", tokensNum: 3000)'
mcporter call 'exa.get_code_context_exa(query: "Next.js 14 app router auth middleware", tokensNum: 5000)'
```

- **tokensNum:** 1000–50000 (padrão 5000). Menor = focado; maior = mais contexto.

### company_research_exa

Pesquisa de empresas (notícias, negócios, funding).

```bash
mcporter call 'exa.company_research_exa(companyName: "Anthropic", numResults: 3)'
mcporter call 'exa.company_research_exa(companyName: "NVIDIA", numResults: 5)'
```

---

## Quando usar

- **web_search_exa:** Documentação externa, notícias, fatos atuais, tendências, benchmarking — quando a informação não está na doc do projeto ([18-expertise-documentacao.md](18-expertise-documentacao.md)).
- **get_code_context_exa:** Exemplos de código, tutoriais, soluções em GitHub/Stack Overflow, referência de APIs e SDKs.
- **company_research_exa:** Due diligence, tendências de mercado, notícias sobre empresas (CEO, PO, CyberSec).

Quando for necessário **navegar, clicar ou preencher formulários**, usar as ferramentas de browser ([11-ferramentas-browser.md](11-ferramentas-browser.md)).

---

## Segurança e Zero Trust

- **URLs e conteúdo:** Validar uso de resultados (evitar SSRF, domínios maliciosos); ver [14-seguranca-runtime-agentes.md](14-seguranca-runtime-agentes.md).
- **Credenciais:** A configuração básica do Exa MCP não exige API key; se no futuro for usada chave, nunca expor em chat, logs ou repositório — variáveis de ambiente no ambiente do agente.
- **Origen do MCP:** Exa é serviço de terceiros; habilitar somente após alinhamento com [05-seguranca-e-etica.md](05-seguranca-e-etica.md) e aprovação do Diretor. A descoberta de skills/MCPs segue [19-descoberta-instalacao-skills.md](19-descoberta-instalacao-skills.md) em espírito (propor → verificar → aprovar).

---

## Quem pode usar

| Agente | Busca web | Código (get_code_context) | Empresas (company_research) |
|--------|-----------|----------------------------|-----------------------------|
| **CEO** | Sim (tendências, benchmarking) | Conforme necessidade | Sim (mercado, empresas) |
| **PO** | Não (info externa via CEO/doc interna) | Não | Não |
| **DevOps/SRE** | Sim (docs de infra, APIs) | Sim (scripts, APIs, cloud) | Conforme tarefa |
| **Architect** | Sim (arquitetura, ADRs) | Sim (padrões, libs) | Conforme tarefa |
| **Developer** | Sim se rede permitir (docs de libs) | Sim (exemplos, docs, Stack Overflow) | Raro |
| **QA** | Conforme política (docs, reprodutibilidade) | Sim (ferramentas, exemplos) | Raro |
| **CyberSec** | Sim (ameaças, CVEs) | Sim (segurança, exploits conhecidos) | Sim (fornecedores, riscos) |
| **UX** | Sim (tendências, acessibilidade) | Conforme necessidade | Conforme tarefa |

---

## Relação com a documentação

- [24-busca-web-headless.md](24-busca-web-headless.md) — Habilidades genéricas de busca web headless e extração; Exa é uma implementação concreta (via MCP).
- [19-descoberta-instalacao-skills.md](19-descoberta-instalacao-skills.md) — Descoberta e instalação de skills; MCPs como Exa podem ser propostos e habilitados após checklist e aprovação (mcporter em vez de npx skills).
- [18-expertise-documentacao.md](18-expertise-documentacao.md) — Primeiro usar a documentação do projeto; Exa para informação **externa** ao repositório.
- [11-ferramentas-browser.md](11-ferramentas-browser.md) — Para interação visual (navegar, clicar), usar browser; para pesquisa e contexto, Exa.
- [05-seguranca-e-etica.md](05-seguranca-e-etica.md) — Zero Trust e regras para serviços de terceiros.
- [14-seguranca-runtime-agentes.md](14-seguranca-runtime-agentes.md) — Validação pré-execução de comandos e uso de resultados externos.
