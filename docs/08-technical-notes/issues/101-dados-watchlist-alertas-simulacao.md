# [team-devs-ai] Dados, watchlist, alertas e simulação

**Fase:** 9 — Integrações  
**Labels:** integration, data

## Descrição

Consultas a APIs de dados (leitura), watchlist, alertas (threshold/cron), calendário/prazos, momentum/digests, simulação local (paper). Categorias de habilidades para skills; uso por CEO, PO, DevOps e outros conforme tarefa.

## Critérios de aceite

- [ ] Categorias documentadas: leitura de APIs de dados, watchlist, alertas (threshold e cron), calendário/prazos, digests, simulação local (paper).
- [ ] Uso por agente: CEO, PO, DevOps e outros conforme necessidade da tarefa (documentado).
- [ ] Quando implementar como skill vs usar API direta: diretriz ou exemplos.
- [ ] Segurança: apenas leitura e dados aprovados; sem expor credenciais.

## Referências

- [26-dados-watchlist-alertas-simulacao.md](../../07-operations/26-dados-watchlist-alertas-simulacao.md)

## Verificação (Fase 9)

- Categorias e uso por agente: [26-dados-watchlist-alertas-simulacao.md](../../07-operations/26-dados-watchlist-alertas-simulacao.md) (§ Visão geral, § Quem pode usar — CEO, PO, DevOps, outros).
- Skill vs API direta: § "Skill vs API direta" no doc 26. Segurança: §1 (leitura apenas, validar URL), §2–6 (paths locais, sem credenciais).
