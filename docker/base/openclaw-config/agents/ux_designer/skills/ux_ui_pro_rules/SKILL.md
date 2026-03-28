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
name: ux_ui_pro_rules
description: Regras profissionais de UI/UX para decisao visual, checklist de qualidade e review de implementacao (somente prompt)
---

# UX_UI_Pro_Rules

Skill complementar para elevar qualidade visual e usabilidade sem depender de scripts externos.
Nao substitui `ux_designer_artifacts`; atua em paralelo como camada de criterio profissional.

## Quando Usar

Use esta skill quando a demanda envolver:
- review de UI/UX de telas ja implementadas;
- melhoria de percepcao de qualidade visual;
- acessibilidade, motion, responsividade, hierarquia visual;
- comparacao de alternativas de interface com foco em custo de implementacao.

## Quando Evitar

Nao usar como skill principal quando a tarefa for:
- gerar artefato UX completo (`UX-XXX.md` com fluxo/wireframe/tokens/spec) do zero;
- trabalho sem impacto visual/interacao (backend, infra, banco).

Nesses casos, priorize `ux_designer_artifacts`.

## Ordem de Revisao (Prioridade)

Execute revisao na ordem abaixo e documente achados por severidade:

1. Acessibilidade (critico):
- contraste minimo WCAG AA;
- foco visivel, navegacao por teclado, rotulos e ARIA;
- nao depender somente de cor para significado.

2. Toque e interacao (critico):
- alvo de toque minimo (44x44 iOS / 48x48 Android);
- feedback claro em clique/toque/estado;
- evitar dependencias de hover em experiencias touch.

3. Performance percebida (alto):
- estados loading/skeleton e feedback de acao;
- evitar layout shift visual;
- reduzir animacoes custosas sem ganho de UX.

4. Layout e responsividade (alto):
- mobile-first e sem scroll horizontal indevido;
- hierarquia e densidade legiveis;
- consistencia entre breakpoints.

5. Tipografia e cor (medio):
- escala tipografica coerente;
- tokens semanticos de cor;
- legibilidade em light/dark mode.

6. Motion e transicoes (medio):
- duracoes coerentes (geralmente 150-300ms);
- animacao com proposito, nao decoracao;
- suporte a reduced motion.

7. Forms e feedback (medio):
- labels explicitos, erros proximos ao campo;
- estados disabled/loading/success/error claros;
- caminho de recuperacao em erro.

8. Navegacao (alto):
- comportamento previsivel de voltar/avancar;
- arquitetura de navegacao simples;
- sem sobrecarga de opcoes primarias.

9. Dados e graficos (baixo a medio):
- leitura facil, legenda e contexto;
- acessibilidade em visualizacao de dados;
- nao depender apenas de cor em categorias.

## Fluxo Somente Prompt

Esta skill nao usa `search.py` nem datasets CSV.

Fluxo recomendado:
1. Ler contexto da feature (US/SPEC/UX atual) no backlog.
2. Fazer pesquisa de referencias confiaveis com:
- `exec("web-search '<query>'")`
- `exec("web-read '<url>'")`
3. Priorizar fontes oficiais (WCAG/W3C, Material, Apple HIG, Nielsen Norman Group).
4. Registrar no `UX-XXX.md`:
- decisoes tomadas;
- tradeoffs;
- referencias com fonte e data;
- checklist de conformidade.

## Checklist de Pre-Entrega (UI/UX)

- [ ] Todos os estados da tela cobertos (empty/loading/success/error)
- [ ] WCAG AA verificado (contraste, foco, labels, teclado)
- [ ] Alvos de toque e feedback de interacao adequados
- [ ] Responsividade validada em mobile e desktop
- [ ] Tipografia e tokens de cor consistentes com design system
- [ ] Motion com intencao e sem degradar performance
- [ ] Formulario/erros com recuperacao clara
- [ ] Navegacao previsivel e sem ambiguidade
- [ ] Decisoes e referencias documentadas no `UX-XXX.md`

## Resultado Esperado

Ao final da revisao/decisao, entregar:
- lista de desvios priorizados (`Critical`, `Minor`, `Suggestion`);
- recomendacoes acionaveis para `dev_frontend`/`dev_mobile`;
- impacto estimado em UX e custo de implementacao;
- status final de aderencia no artefato `UX-XXX.md`.
