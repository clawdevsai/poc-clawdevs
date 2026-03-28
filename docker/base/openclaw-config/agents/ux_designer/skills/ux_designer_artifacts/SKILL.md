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
name: ux_designer_artifacts
description: UX design skill for wireframes, user flows, design tokens and visual artifacts
---

# UX_Designer Skills

Use this document as a single skill to guide the creation of UX artifacts.

---

## Create Complete UX Artifact

Use this skill when you receive a User Story with a PO UI component.

Workflow:
1. Read US-XXX.md and SPEC-XXX.md to understand the purpose and acceptance criteria.
2. Search UX references for the product domain (minimum 3 references).
3. Map user flow with Mermaid: happy path, error states, edge cases.
4. Create wireframe in Markdown per screen: layout, components, states (empty/loading/error/success).
5. Define relevant design tokens: colors, typography, spacing, breakpoints.
6. Specify core components: props, variants, responsive behavior, WCAG AA accessibility.
7. Persist UX-XXX-<slug>.md in `/data/openclaw/backlog/ux/`.
8. Report to PO with artifact link and summary of design decisions.

---

## UX-XXX.md Artifact Structure

```markdown
# UX-XXX — <título da feature>

## Objective
<user experience objective>

## Persona Primária
<persona, contexto de uso, dispositivo>

## User Flow
```mermaid
TD flowchart
  A[Input] --> B[Main Action] --> C[Success Status]
  B --> D[Error status]
```

## Wireframes

### Tela: <nome>
[Layout ASCII/Markdown com anotações]
**Estados:** empty | loading | success | error
**Acessibilidade:** aria-label, role, contraste mínimo 4.5:1

## Design Tokens
| Token | Valor | Uso |
|-------|-------|-----|
| color-primary | #... | CTA principal |

## Componentes
### <NomeComponente>
- Props: ...
- Variantes: ...
- Responsivo: mobile-first, breakpoints sm/md/lg
- WCAG: role, aria-*, contraste

## Referências
- [Fonte 1](url) — <o que foi adaptado>

## UX Acceptance Criteria
- [ ] User flow implementado conforme diagrama
- [ ] Todos os estados de tela cobertos
- [ ] WCAG AA validated
- [ ] Design tokens aplicados corretamente
```