# Busca web headless e extração de conteúdo

Os agentes do enxame podem usar **busca na web sem browser** (headless) e **extração de conteúdo** de páginas para markdown. Útil para pesquisar documentação, referências de API, fatos atuais ou obter o conteúdo legível de uma URL sem abrir um browser. A implementação pode ser fornecida por uma **skill do ecossistema** ou por **MCP** (ex.: **Exa Web Search** — busca neural web, código e empresas via mcporter; ver [30-exa-web-search.md](30-exa-web-search.md)); instalação/habilitação conforme [19-descoberta-instalacao-skills.md](19-descoberta-instalacao-skills.md) e Zero Trust em [05-seguranca-e-etica.md](05-seguranca-e-etica.md).

**Objetivo:** Pesquisar na web e extrair conteúdo de páginas em texto/markdown, leve e sem depender de automação de browser (ver [11-ferramentas-browser.md](11-ferramentas-browser.md) para interação visual).

---

## Habilidades cobertas

| Habilidade | Descrição | Quando usar |
|------------|-----------|-------------|
| **Busca web** | Pesquisar na web e obter resultados (título, link, snippet). | Documentação, APIs, fatos, informação atual. |
| **Extração de conteúdo** | Buscar uma URL e extrair o conteúdo principal da página em markdown. | Ler artigo, doc externa ou página específica sem browser. |

---

## Quando usar

- Procurar documentação oficial ou referências de API na web.
- Verificar fatos ou informação atual (datas, versões, boas práticas).
- Obter o conteúdo legível de uma URL já conhecida (extração para markdown).
- Qualquer tarefa que exija **pesquisa na web** sem interação visual (formulários, cliques).

Quando for necessário **navegar, clicar ou preencher formulários**, usar as ferramentas de browser ([11-ferramentas-browser.md](11-ferramentas-browser.md)).

---

## Forma de uso típica (quando a skill estiver instalada)

Padrão genérico (a skill instalada pode expor comandos semelhantes):

- **Busca:** comando que recebe uma query e opcionalmente número de resultados e flag para incluir conteúdo das páginas.
- **Extração:** comando que recebe uma URL e devolve o conteúdo principal em markdown.

Exemplo de formato de saída da busca:

```
--- Result 1 ---
Title: Título da página
Link: https://exemplo.com/pagina
Snippet: Descrição do resultado
Content: (se solicitado) Conteúdo em markdown extraído da página...
```

---

## Segurança e Zero Trust

- **URLs:** Validar antes de acessar (lista permitida, domínios conhecidos, sem SSRF); ver [14-seguranca-runtime-agentes.md](14-seguranca-runtime-agentes.md).
- **Credenciais:** Se a skill exigir chave de API (ex.: `BRAVE_API_KEY`), nunca expor em chat, logs ou repositório; usar variáveis de ambiente no ambiente do agente.
- **Instalação:** A skill que fornece essa capacidade é de terceiros; instalar somente após checklist de [05-seguranca-e-etica.md](05-seguranca-e-etica.md) e aprovação do Diretor ([19-descoberta-instalacao-skills.md](19-descoberta-instalacao-skills.md)).

---

## Quem pode usar

| Agente | Acesso à internet | Pode usar busca web headless |
|--------|-------------------|------------------------------|
| **CEO** | Sim | Sim (pesquisa, tendências, benchmarking). |
| **PO** | Não (apenas GitHub open source) | Não — informação externa via CEO ou documentação interna. |
| **DevOps/SRE** | Sim | Sim (docs de infra, APIs, cloud). |
| **Architect** | Sim | Sim (arquitetura, boas práticas, ADRs). |
| **Developer** | Repositórios provisionados | Sim se houver permissão de rede para busca (ex.: docs de libs); caso contrário, usar doc do projeto ([18-expertise-documentacao.md](18-expertise-documentacao.md)). |
| **QA** | Conforme política | Sim quando permitido (docs de ferramentas, reprodutibilidade). |
| **CyberSec** | Sim | Sim (ameaças, CVEs, boas práticas de segurança). |
| **UX** | Sim | Sim (tendências, usabilidade, acessibilidade). |

---

## Relação com a documentação

- [30-exa-web-search.md](30-exa-web-search.md) — **Exa Web Search:** implementação via MCP (mcporter): busca web, contexto de código (GitHub/Stack Overflow) e pesquisa de empresas; sem API key no conjunto básico.
- [19-descoberta-instalacao-skills.md](19-descoberta-instalacao-skills.md) — Descobrir e propor skills/MCPs que forneçam busca web headless (ex.: brave-search, Exa); instalação/habilitação só após aprovação.
- [18-expertise-documentacao.md](18-expertise-documentacao.md) — Primeiro buscar na documentação do projeto; busca web para informação **externa** ao repositório.
- [11-ferramentas-browser.md](11-ferramentas-browser.md) — Para interação visual (navegar, clicar, preencher), usar browser; para só pesquisar ou extrair conteúdo, usar esta habilidade.
- [12-ferramenta-summarize.md](12-ferramenta-summarize.md) — Summarize para **resumir** URLs/PDFs/áudio com modelo de IA; busca web headless para **pesquisar** e **extrair** conteúdo bruto em markdown.
- [05-seguranca-e-etica.md](05-seguranca-e-etica.md) — Zero Trust, classificação de URLs e regras para skills de terceiros.
- [14-seguranca-runtime-agentes.md](14-seguranca-runtime-agentes.md) — Validação pré-execução de comandos e URLs.
