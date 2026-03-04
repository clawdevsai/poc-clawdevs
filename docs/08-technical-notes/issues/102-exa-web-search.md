# [team-devs-ai] Exa Web Search (MCP)

**Fase:** 9 — Integrações  
**Labels:** tooling, search

## Descrição

Busca neural (web, código GitHub/Stack Overflow, pesquisa de empresas) via MCP Exa (mcporter). Setup, ferramentas principais e avançadas, segurança e quem pode usar. Pode ser usado sem API key em alguns contextos (verificar doc do MCP).

## Critérios de aceite

- [ ] Setup do MCP Exa documentado (configuração no OpenClaw ou ambiente).
- [ ] Ferramentas principais: busca web, contexto de código (GitHub, Stack Overflow), pesquisa de empresas.
- [ ] Segurança: validação de queries e resultados; quem pode usar (agentes com acesso à internet) documentado.
- [ ] Integração com 24-busca-web-headless e 30-exa: quando usar Exa vs headless documentado.

## Referências

- [30-exa-web-search.md](../../05-tools-and-skills/30-exa-web-search.md)

## Verificação (Fase 9)

- Setup MCP Exa: [30-exa-web-search.md](../../05-tools-and-skills/30-exa-web-search.md) (§ Setup mcporter). Ferramentas principais: § Ferramentas principais (web_search_exa, get_code_context_exa, company_research_exa).
- Segurança e quem pode usar: § Segurança e Zero Trust, § Quem pode usar no doc 30.
- Exa vs headless: § "Exa vs busca web headless (doc 24)" no doc 30.
