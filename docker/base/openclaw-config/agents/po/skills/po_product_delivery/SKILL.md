<!-- 
  Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.
 -->

---
name: po_product_delivery
description: Product delivery skill for backlog, user stories, sequencing and handoff to the Architect
---

# Product Delivery

Use this skill when an order requires backlog design, feature breakdown, delivery sequencing or acceptance criteria.

Exit checklist:
- problem statement
- target result
- idea file approved at `/data/openclaw/backlog/idea`
- user separate stories at `/data/openclaw/backlog/user_story`
- handoff for Architect with technical drawing and tasks
- tasks prioritized in `/data/openclaw/backlog/tasks`
- acceptance criteria
- risks and dependencies
- files generated in `/data/openclaw/backlog`

---

## User Story Template

Use this template when creating files in `/data/openclaw/backlog/user_story/US-XXX-<slug>.md`.

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