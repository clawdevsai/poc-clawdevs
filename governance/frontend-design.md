# 🎨 frontend-design — Diretrizes e Workflow SuperDesign

**Objetivo:** Criar interfaces distintas, modernas e vibrantes que gerem o efeito "WOW". Evitar o genérico e focar em estética premium, acessibilidade e performance.  
**Quando usar:** Quando o Developer ou UX estiverem criando, revisando ou aprimorando aplicações web e dashboards.  
**Referência:** `docs/23-frontend-design.md`

---

## ─── 1. Pilares da Estética ClawDevs ───────────────────────

### 🚫 Anti-Genérico (The Death of Boring UI)
- Nada de cores puras (`#FF0000`, `#0000FF`). Use paletas curadas (HSL).
- Nada de sombras duras. Use sombras suaves e difusas (estilo glassmorphism).
- Nada de layouts "bloco fixo". Use fluidez, grids dinâmicos e assimetria controlada.

### 💎 Premium Aesthetics
- **Tipografia:** Use fontes modernas (Google Fonts: *Outfit*, *Inter*, *Roboto Mono* para código).
- **Cores:** Temas escuros profundos (#0A0A0A) com acentos vibrantes (Neon Indigo, Cyber Red, Matrix Green).
- **Material:** Vidro fosco (backdrop-blur), bordas sutis com gradiente.
- **Micro-animações:** Hover suave, transições de estado, skeleton screens elegantes.

---

## ─── 2. Workflow SuperDesign (4 Passos) ───────────────────

### Passo 1: Layout (A Estrutura)
- Defina o grid (CSS Grid/Flexbox).
- Priorize hierarquia visual: o que o usuário deve ver primeiro?
- Design Mobile-First (essencial).

### Passo 2: Tema (A Alma)
- Aplique o sistema de cores (Tokens CSS).
- Tipografia: Escalas claras (Heading 1, 2, Body, Small).
- Defina o raio das bordas (rounded-xl ou rounded-2xl para aspecto moderno).

### Passo 3: Animação (O Movimento)
- Use transições CSS para `opacity`, `transform` e `background-color`.
- Tempo padrão: `200ms ease-in-out` ou `300ms cubic-bezier(...)`.
- Não exagere: a animação deve auxiliar a compreensão, não distrair.

### Passo 4: Implementação (O Código)
- **Framework:** Preferir Vanilla + TailwindCSS (se solicitado) ou CSS puro.
- **Componentes:** Use Lucide-React (ícones), Flowbite (UI components base).
- **Semântica:** HTML5 correto (main, section, article, nav).

---

## ─── 3. Stack Técnica Recomendada ─────────────────────────

| Tecnologia | Requisito |
|------------|-----------|
| **Styling** | Vanilla CSS ou TailwindCSS v3.x |
| **Icons** | Lucide Icons (precisos e modernos) |
| **Fonts** | Google Fonts (Inter / Outfit) |
| **Patterns** | BEM (para CSS regular) |
| **Validation** | Lighthouse Score p90+ |

---

## ─── 4. Checklist de UX/Acessibilidade ─────────────────────

- [ ] **Contraste:** Texto legível em todos os temas (WCAG AA).
- [ ] **Target Size:** Botões interativos com min. 44x44px em mobile.
- [ ] **Responsivo:** Funciona de 320px a 2560px.
- [ ] **Feedback:** Estado de Loading/Error/Success visualmente claro.
- [ ] **Performance:** Imagens otimizadas (WebP) e zero layout shift (CLS).

---

## Integração por agente

| Agente | Responsabilidade |
|--------|------------------|
| **UX** | Criar o conceito, definir a "alma" e as heurísticas de uso. |
| **Developer** | Implementar o código limpo seguindo o SuperDesign. |
| **QA** | Validar fidelidade visual, acessibilidade e performance (Lighthouse). |
| **Architect** | Validar a estrutura de componentes e escalonabilidade do CSS. |
