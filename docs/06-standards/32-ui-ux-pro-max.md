# UI/UX Pro Max — inteligência de design e entrega estruturada

Os agentes do enxame que trabalham com UI/UX (em especial **Developer** e **UX**) aplicam um fluxo estruturado de **triagem**, **entregas concretas** e **padrões de saída** para produzir interfaces polidas com mínimo ida-e-volta. Este documento consolida essas habilidades como capacidade **incorporada** do time (não exige skill externa).

**Objetivo:** Entregar direção visual, fluxos de UX, design system e plano de implementação de forma concreta e reproduzível, alinhado a [23-frontend-design.md](23-frontend-design.md).

---

## 1. Triagem (antes de produzir)

Perguntar apenas o necessário para evitar trabalho errado:

| Dimensão | Perguntas |
|----------|-----------|
| **Plataforma** | Web / iOS / Android / desktop? |
| **Stack** (se houver código) | React/Next/Vue/Svelte, CSS/Tailwind, biblioteca de componentes? |
| **Objetivo e restrições** | Conversão, velocidade, vibe da marca, nível de acessibilidade (ex.: WCAG AA)? |
| **O que já existe** | Screenshot, Figma, repositório, URL, jornada do usuário? |

Se o pedido cobrir design + UX + código + design system, tratar como **quatro entregas** e produzir nessa ordem.

---

## 2. Entregas (escolher o que couber)

Sempre ser concreto: nomear componentes, estados, espaçamento, tipografia e interações.

| Entrega | Conteúdo |
|---------|----------|
| **Conceito de UI + layout** | Direção visual clara, grid, tipografia, sistema de cores, telas/seções principais. |
| **Fluxo de UX** | Jornada do usuário, caminhos críticos, estados de erro/vazio/carregamento, edge cases. |
| **Design system** | Tokens (cor, tipografia, espaçamento, radius, sombra), regras de componentes, notas de acessibilidade. |
| **Plano de implementação** | Edições em nível de arquivo, quebra de componentes e critérios de aceite. |

---

## 3. Inteligência de design (heurísticas)

Usar **heurísticas por tipo de produto e contexto** ao definir padrões e evitar anti-padrões.

### 3.1 Por tipo de produto / indústria

- **SaaS:** Hero + Features + CTA; glassmorphism ou flat; azul de confiança + acento; animações sutis (200–250ms). Evitar animação excessiva e dark mode por padrão sem necessidade.
- **E-commerce:** Showcase rico; cores de marca + verde de sucesso; hover em cards (200ms). Evitar páginas só texto e flat sem profundidade.
- **Healthcare / governo:** Foco em prova social ou minimal direto; acessível (WCAG AAA quando aplicável); azul calmo, tipografia legível (16px+). Evitar neon, motion pesado e gradientes roxo/rosa genéricos.
- **Fintech / banking:** Confiança e autoridade; minimalismo; navy + azul + dourado; transições suaves. Evitar design lúdico e indicadores de segurança ausentes.
- **Beauty / spa / wellness:** Hero + prova social; soft pastels (rosa, sage, creme) + acentos dourados; sombras suaves, transições 200–300ms. Evitar neon e dark mode por padrão.
- **Landing B2B / startup:** Hero-cêntrico ou foco em conversão; motion ou blocos vibrantes; CTA claro, social proof. Evitar layout estático e mobile ruim.

Ajustar sempre ao contexto: se o usuário pedir "tudo" (design + UX + código + design system), entregar nessa ordem e com nível de detalhe coerente.

### 3.2 Diretrizes de UX (resumo)

- **Navegação:** scroll suave, estado ativo visível, breadcrumbs em hierarquias profundas.
- **Animação:** 150–300ms para microinterações; respeitar `prefers-reduced-motion`; evitar animação infinita em elementos decorativos.
- **Layout:** escala de z-index definida; reservar espaço para conteúdo assíncrono (evitar layout shift); containers com max-width para texto.
- **Toque (mobile):** alvos ≥ 44px; espaçamento entre alvos; evitar gestos que conflitam com o sistema.
- **Interação:** estados de foco visíveis, hover, active, disabled, loading; feedback de erro e sucesso; confirmação em ações destrutivas.
- **Acessibilidade:** contraste ≥ 4.5:1; não depender só de cor; alt em imagens; hierarquia de headings; aria-label em botões só ícone; navegação por teclado.
- **Formulários:** label visível, validação inline/blur, erro próximo ao campo, indicador de obrigatório, feedback de envio.
- **Feedback:** loading (> 300ms), empty state com ação, recuperação de erro com próximo passo, toasts com auto-dismiss.

---

## 4. Design system (padrão Master + overrides)

Quando for persistir o design system no projeto:

- **MASTER:** arquivo global (ex.: `design-system/MASTER.md`) com regras de tokens, componentes e acessibilidade.
- **Overrides por página:** arquivos em `design-system/pages/<página>.md` que sobrescrevem o Master para aquela tela.
- **Consulta:** ao implementar uma página, verificar primeiro o override da página; se não existir, usar só o Master.

Incluir sempre: escala de espaçamento, escala de tipo, 2–3 pares de fontes, tokens de cor, estados de componente (default, hover, active, disabled, loading, error).

---

## 5. Script opcional (gerador de design system)

Se no ambiente existir um script de geração de design system (ex.: `design_system.py` com domínios product, style, color, landing, typography, ux e stacks), usá-lo para:

- Gerar recomendação completa com `--design-system` e query (tipo de produto + indústria + palavras-chave).
- Persistir com `--persist` e, se aplicável, overrides por página com `--page <nome>`.
- Consultar domínios específicos (style, chart, ux, typography, landing) quando precisar de mais detalhes.
- Obter diretrizes por stack (html-tailwind, react, nextjs, vue, svelte, etc.); padrão html-tailwind quando não especificado.

Preferir tokens e variáveis em ASCII quando o projeto ainda não usar Unicode.

---

## 6. Padrões de saída

- **Tokens:** default em ASCII; variáveis semânticas (`--primary`, `--secondary`, `--muted`, etc.).
- **Incluir:** escala de espaçamento, escala de tipo, 2–3 pares de fontes, tokens de cor, estados de componentes.
- **Cobrir sempre:** estados vazio, carregamento e erro; navegação por teclado; estados de foco; contraste.

---

## 7. Quem aplica

| Agente | Aplicação |
|--------|-----------|
| **Developer** | Ao implementar UI: seguir triagem, entregas e padrões de saída; usar design system do projeto (MASTER + overrides) e heurísticas por produto. |
| **UX** | Ao revisar ou especificar: validar triagem, fluxos de UX, design system e aderência às diretrizes de acessibilidade e feedback; sugerir uso do script de design system quando disponível. |
| **Architect** | Ao definir padrões de UI no projeto: referenciar este doc e o 23 para consistência e manutenção. |

---

## 8. Relação com a documentação

- [23-frontend-design.md](23-frontend-design.md) — Design thinking, estética e workflow SuperDesign (layout → tema → animação → implementação); este doc (32) adiciona triagem, entregas estruturadas e heurísticas de produto/UX.
- [02-agentes.md](02-agentes.md) — Definição dos papéis Developer e UX.
- [soul/UX.md](soul/UX.md) e [soul/Developer.md](soul/Developer.md) — Alma e tom dos agentes que aplicam estas habilidades.
- [11-ferramentas-browser.md](11-ferramentas-browser.md) — Validação de fluxos e captura de evidências de interface.
