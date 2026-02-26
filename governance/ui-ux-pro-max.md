# 💎 ui-ux-pro-max — Design System e Triagem Estruturada

**Objetivo:** Estabelecer um processo de design de alto nível, com triagem prévia, entregas estruturadas e um Design System (Master + Overrides) que permita escalabilidade sem perder a identidade visual.  
**Quando usar:** No início de novos projetos frontend ou na reformulação de sistemas existentes.  
**Referência:** `docs/32-ui-ux-pro-max.md`

---

## ─── 1. Triagem (O "Para Quem" e "Para Quê") ──────────────

Antes de desenhar, o agente UX/Developer deve responder:

1. **Plataforma:** Web, Mobile App, Desktop PWA?
2. **Stack:** React, Next.js, HTML Puro, Dashboard?
3. **Objetivo:** Vendas (conversão), Ferramenta (eficiência), Conteúdo (leitura)?
4. **Indústria:** Fintech (segurança/sobriedade), E-commerce (vibração/desejo), DevTool (densidade/funcionalidade).

---

## ─── 2. Entregas Estruturadas ────────────────────────────

Uma entrega "Pro Max" contém (nesta ordem):

| Artefato | Descrição |
|----------|-----------|
| **Conceito UI** | Moodboard, paleta de cores primária/acentos, tipografia base. |
| **Fluxo UX** | Diagrama de estados (User Flow), transições críticas, tratamento de erros. |
| **Design System** | Biblioteca de componentes reutilizáveis (botões, inputs, cards). |
| **Plano de Implementação** | Ordem técnica: Setup → Layout Global → Componentes → Páginas → Polimento. |

---

## ─── 3. Design System (Master + Overrides) ────────────────

O enxame utiliza uma abordagem de **Tokens de Design** para garantir consistência.

### Padrão Master (Core)
Onde as regras globais são definidas:
- `tokens.css`: Variáveis de cor, espaçamento, sombras e fontes.
- `base-components.css`: Estilos para botões e inputs fundamentais.

### Overrides (Especificidade)
Onde o design se adapta ao contexto:
- `theme-dark.css` / `theme-light.css`.
- Overrides por "indústria" (ex.: `industry-fintech.css` altera acentos para tons de verde/cinza).

---

## ─── 4. Padrões de Saída (Ready for Build) ───────────────

Todo componente criado deve declarar:
- **States:** Default, Hover, Active, Focus, Disabled, Loading.
- **Tokens:** Qual variável CSS utiliza (ex.: `--color-primary-600`).
- **Acessibilidade:** Tags ARIA e ordem de TabIndex.

---

## ─── 5. Heurísticas de Ouro ──────────────────────────────

1. **Visibilidade do status:** O usuário sempre sabe o que está acontecendo (loaders, toasts).
2. **Consistência:** Um botão "Salvar" deve ter o mesmo comportamento em todo o app.
3. **Prevenção de erros:** Interfaces que impedem o erro antes que ele aconteça.
4. **Minimalismo:** Eliminar qualquer elemento que não contribua para a tarefa.

---

## Uso por agente

| Agente | Responsabilidade |
|--------|------------------|
| **UX** | Conduz a triagem, define os fluxos e cria os tokens base. |
| **Developer** | Segue fielmente os tokens e os padrões de estados na implementação. |
| **QA** | Valida se os overrides não quebraram a consistência Master. |
| **CEO/PO** | Revisam se o conceito UI está alinhado à estratégia de mercado. |
