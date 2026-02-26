# Frontend design — interfaces distintas e produção

Os agentes do enxame que criam ou revisam frontend (em especial **Developer** e **UX**) aplicam **pensamento de design**, **diretrizes de estética** e o **workflow e padrões de implementação SuperDesign** (layout → tema → animação → código) para entregar interfaces de alta qualidade, memoráveis e livres do "AI slop" genérico. Este documento consolida essas habilidades como capacidade **incorporada** do time (não exige instalação de skill externa).

**Objetivo:** Construir componentes, páginas ou aplicações frontend com código em produção, visualmente marcantes e coerentes com uma direção estética clara.

---

## Visão geral

| Pilar | Objetivo |
|-------|----------|
| **Design thinking** | Entender contexto, propósito e restrições; escolher uma direção estética **ousada** e executá-la com precisão. |
| **Estética de frontend** | Tipografia, cor/tema, motion, composição espacial e detalhes visuais que criem atmosfera e diferenciação. |
| **Anti-genérico** | Evitar fontes, paletas e layouts clichê; cada interface deve ser genuinamente pensada para o contexto. |

---

## 1. Design thinking (antes de codar)

Antes de implementar, definir:

- **Propósito:** Que problema a interface resolve? Quem usa?
- **Tom:** Escolher um extremo coerente: minimalismo brutal, maximalismo, retro-futurista, orgânico/natural, luxo/refinado, lúdico, editorial/revista, brutalista/cru, art déco/geométrico, suave/pastel, industrial/utilitário, etc.
- **Restrições:** Requisitos técnicos (framework, performance, acessibilidade).
- **Diferenciação:** O que torna esta interface **inesquecível**? Qual é o elemento que alguém vai lembrar?

**Regra crítica:** Escolher uma direção conceitual clara e executá-la com precisão. Maximalismo ousado e minimalismo refinado funcionam — o que importa é intencionalidade, não intensidade.

O código resultante deve ser:

- De nível produção e funcional
- Visualmente marcante e memorável
- Coeso, com ponto de vista estético claro
- Refinado em cada detalhe

---

## 2. Diretrizes de estética de frontend

### Tipografia

- Escolher fontes **distintivas**, bonitas e interessantes.
- Evitar genéricos: Arial, Inter, Roboto, system fonts.
- Preferir pares: uma fonte de display marcante + uma fonte de corpo refinada.
- Variação entre projetos: não convergir sempre nas mesmas escolhas (ex.: Space Grotesk).

### Cor e tema

- Compromisso com uma estética coerente.
- Usar variáveis CSS para consistência.
- Paleta com cores dominantes e acentos fortes tende a funcionar melhor que distribuição tímida e uniforme.

### Motion

- Animações para efeitos e microinterações.
- Priorizar CSS puro quando for HTML estático; usar biblioteca Motion (ou equivalente) em React quando disponível.
- Foco em momentos de alto impacto: um carregamento de página bem orquestrado com revelações escalonadas (`animation-delay`) gera mais impacto que microinterações espalhadas.
- Scroll e hover que surpreendam, sem exagero.

### Composição espacial

- Layouts inesperados: assimetria, sobreposição, fluxo diagonal.
- Elementos que quebram a grade; espaço negativo generoso ou densidade controlada.
- Evitar grades e cards previsíveis.

### Fundos e detalhes visuais

- Criar atmosfera e profundidade em vez de fundos sólidos genéricos.
- Efeitos e texturas condizentes com a estética: gradientes mesh, textura de ruído, padrões geométricos, transparências em camadas, sombras marcantes, bordas decorativas, cursores customizados, grão.
- Cada projeto com identidade visual própria.

---

## 3. Workflow e implementação (SuperDesign)

As diretrizes abaixo incorporam o **workflow estruturado** e padrões de implementação do [SuperDesign](https://superdesign.dev), para que Developer e UX tenham um processo reproduzível ao criar ou revisar interfaces.

### 3.1 Workflow em quatro passos

1. **Layout** — Esboçar a estrutura em ASCII (wireframe) antes de codar.
2. **Tema** — Definir cores, fontes, espaçamento e sombras.
3. **Animação** — Planejar microinterações e transições.
4. **Implementação** — Gerar o código (HTML/CSS/JS ou framework).

**Exemplo de wireframe em ASCII:**

```
┌─────────────────────────────────────┐
│         HEADER / NAV BAR            │
├─────────────────────────────────────┤
│            HERO SECTION             │
│         (Title + CTA)               │
├─────────────────────────────────────┤
│   FEATURE   │  FEATURE  │  FEATURE  │
│     CARD    │   CARD    │   CARD    │
├─────────────────────────────────────┤
│            FOOTER                   │
└─────────────────────────────────────┘
```

### 3.2 Regras de tema (cor e tipografia)

- **Cores:** Nunca usar azul genérico tipo Bootstrap (`#007bff`). Preferir `oklch()` para definições modernas e variáveis semânticas (`--primary`, `--secondary`, `--muted`, etc.). Considerar light e dark mode desde o início.
- **Fontes (Google Fonts), referência:** Sans: Inter, Roboto, Poppins, Montserrat, Outfit, Plus Jakarta Sans, DM Sans, Space Grotesk. Mono: JetBrains Mono, Fira Code, Source Code Pro, IBM Plex Mono, Space Mono, Geist Mono. Serif: Merriweather, Playfair Display, Lora, Source Serif Pro, Libre Baskerville. Display: Architects Daughter, Oxanium. Escolher com critério de diferenciação (evitar convergência repetida entre projetos).
- **Espaçamento e sombras:** Escala consistente (base 0.25rem); sombras sutis, evitar drop shadows pesados.

### 3.3 Padrões de tema (referência)

**Modern Dark (estilo Vercel/Linear):** `--background`, `--foreground`, `--primary`, `--muted`, `--border`, `--radius`, `--font-sans` (ex.: Inter). Cores em oklch neutros.

**Neo-Brutalism:** Cores saturadas, `--radius: 0`, sombra sólida (`box-shadow: 4px 4px 0 black`), fontes como DM Sans e Space Mono.

**Glassmorphism:** `background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2); border-radius: 1rem;`

### 3.4 Animações

- **Micro-sintaxe para planejamento:** `button: 150ms [scale 0.95→1]` (press), `hover: 200ms [Y -2px, shadow↗]`, `fadeIn: 400ms ease-out`, `slideIn: 350ms ease-out`.
- **Durações típicas:** Entrada 300–500ms ease-out; hover 150–200ms; clique 100–150ms; transição de página 300–400ms.

### 3.5 Ferramentas e assets de implementação

- **Tailwind CSS:** via CDN em protótipos ou build no projeto.
- **Flowbite (componentes):** CSS e JS via CDN quando for apropriado ao stack.
- **Ícones:** Lucide (ou equivalente) com uso consistente.
- **Imagens:** Usar serviços reais (Unsplash, placehold.co); nunca inventar URLs.

### 3.6 Responsivo e acessibilidade

- **Responsivo:** Mobile-first; breakpoints consistentes (ex.: 768px, 1024px); container com max-width em desktop.
- **Acessibilidade:** HTML semântico (`header`, `main`, `nav`, `section`, `article`); hierarquia de headings (h1→h2→h3); `aria-label` em elementos interativos; contraste mínimo 4.5:1; suporte a navegação por teclado.

### 3.7 Dicas por componente

| Elemento   | Recomendação |
|-----------|----------------|
| Cards     | Sombras sutis, padding consistente (p-4 a p-6), hover com leve elevação. |
| Botões    | Hierarquia clara (primary, secondary, ghost), alvo de toque ≥44px, estados de loading e disabled. |
| Formulários | Labels visíveis, focus visível, validação inline, espaçamento entre campos. |
| Navegação | Header sticky em páginas longas, estado ativo claro, menu mobile acessível. |

### 3.8 Referência rápida

| Aspecto      | Recomendação |
|-------------|---------------|
| Fonte principal | Inter, Outfit, DM Sans (ou distinta conforme direção). |
| Fonte código | JetBrains Mono, Fira Code. |
| Border radius | 0.5rem–1rem (moderno), 0 (brutalist). |
| Sombra       | Sutil, 1–2 camadas no máximo. |
| Espaçamento  | Unidade base 4px (0.25rem). |
| Animação     | 150–400ms, ease-out. |
| Cores        | oklch() quando possível; evitar azul genérico. |

---

## 4. O que NUNCA fazer

- **Estética genérica de IA:** fontes batidas (Inter, Roboto, Arial, system), esquemas de cor clichê (em especial gradientes roxos em fundo branco), layouts e padrões de componente previsíveis.
- **Design sem contexto:** interfaces que poderiam ser de qualquer produto; falta de caráter específico.
- **Convergência repetida:** mesmo conjunto de fontes e estéticas em todo projeto (ex.: sempre Space Grotesk).

Interpretar com criatividade e fazer escolhas inesperadas que pareçam desenhadas de verdade para o contexto. Nenhum design deve ser igual ao outro; variar entre temas claros/escuros, fontes e estéticas.

**Importante:** Ajustar a complexidade da implementação à visão estética. Design maximalista exige código mais elaborado (animações, efeitos). Design minimalista ou refinado exige contenção, precisão e atenção a espaçamento, tipografia e detalhes sutis. A elegância vem de executar bem a visão escolhida.

---

## 5. Quem aplica

| Agente | Aplicação |
|--------|-----------|
| **Developer** | Ao implementar componentes, páginas ou apps frontend: seguir design thinking e diretrizes de estética; código de produção, coerente com a direção escolhida. |
| **UX** | Ao revisar PRs de frontend: validar aderência às diretrizes (tipografia, cor, motion, composição, anti-genérico); sugerir melhorias alinhadas a este doc. |
| **Architect** | Ao definir padrões de UI/frontend no projeto: referenciar este documento para consistência de qualidade visual e manutenibilidade. |

---

## 6. Relação com a documentação

- [02-agentes.md](02-agentes.md) — Definição do Developer e do UX; as responsabilidades de frontend incorporam estas diretrizes.
- [32-ui-ux-pro-max.md](32-ui-ux-pro-max.md) — **UI/UX Pro Max:** triagem (plataforma, stack, objetivo), entregas estruturadas (conceito UI, fluxo UX, design system, plano de implementação), heurísticas por produto/indústria e diretrizes de UX, padrão Master + overrides para design system e padrões de saída. Complementa este doc (23) com fluxo de trabalho e critérios de entrega.
- [soul/UX.md](soul/UX.md) — Alma do agente UX; revisão de frontend e consistência visual alinhadas a este doc.
- [11-ferramentas-browser.md](11-ferramentas-browser.md) — Ferramentas de browser para validação de fluxos e captura de evidências de interface (UX, QA).
- [19-descoberta-instalacao-skills.md](19-descoberta-instalacao-skills.md) — Habilidades de frontend design estão **incorporadas** neste doc (23) e no 32 (UI/UX Pro Max), incluindo workflow e padrões SuperDesign; skills externas de "design" ou "UI" complementam, não substituem, estas diretrizes.

*Padrões de workflow e implementação alinhados ao SuperDesign — https://superdesign.dev*
