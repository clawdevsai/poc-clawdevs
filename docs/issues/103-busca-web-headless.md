# [team-devs-ai] Busca web headless (pesquisa e extração em markdown)

**Fase:** 9 — Integrações  
**Labels:** tooling, search, security

## Descrição

Pesquisa na web e extração de conteúdo de páginas em markdown sem browser. Quando usar, segurança (URLs validadas, Zero Trust) e quem pode usar. Implementação via skill ou MCP do ecossistema.

## Critérios de aceite

- [ ] Ferramenta ou skill que permite pesquisa web e extração de conteúdo de páginas em markdown (sem abrir browser completo).
- [ ] Quando usar documentado (ex.: pesquisa de documentação, notícias, dados públicos).
- [ ] Segurança: validar URLs antes de acessar (SSRF, lista de permissões); alinhado a 14-seguranca-runtime e 05-seguranca.
- [ ] Quem pode usar: agentes com permissão de internet (CEO, DevOps, CyberSec, etc.) conforme doc 02-agentes.

## Referências

- [24-busca-web-headless.md](../24-busca-web-headless.md)
