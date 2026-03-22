---
name: po_product_delivery
description: Skill de entrega de produto para backlog, user stories, sequenciamento e handoff ao Arquiteto
---

# Entrega de Produto

Use esta skill quando um pedido exigir desenho de backlog, quebra de features, sequenciamento de entrega ou criterios de aceitacao.

Checklist de saida:
- declaracao do problema
- resultado alvo
- arquivo de ideia aprovado em `/data/openclaw/backlog/idea`
- user stories separadas em `/data/openclaw/backlog/user_story`
- handoff para Arquiteto com desenho tecnico e tasks
- tasks priorizadas em `/data/openclaw/backlog/tasks`
- criterios de aceitacao
- riscos e dependencias
- arquivos gerados em `/data/openclaw/backlog`

---

## Template de User Story

Use este template ao criar arquivos em `/data/openclaw/backlog/user_story/US-XXX-<slug>.md`.

```md
# US-XXX - <Titulo curto>

## Contexto
<Contexto do problema, usuario e situacao atual.>

## Historia do usuario
Como <tipo de usuario>,
quero <acao ou capacidade>,
para <beneficio ou resultado>.

## Escopo
- Inclui: <itens dentro do escopo>
- Nao inclui: <itens fora do escopo>

## Criterios de aceitacao
1. <criterio testavel>
2. <criterio testavel>
3. <criterio testavel>

## Requisitos de UX (se aplicavel)
- <telas, componentes, fluxos>

## Analytics (se aplicavel)
- Eventos: <eventos a instrumentar>
- Funil: <etapas do funil>
- Experimentos: <A/B, feature flag, rollout>

## Dependencias
- <dependencia tecnica, negocio ou time>

## Riscos e mitigacoes
- <risco> -> <mitigacao>

## Metricas de sucesso
- <metrica> com alvo <valor>

## Notas
- <observacoes adicionais>
```
