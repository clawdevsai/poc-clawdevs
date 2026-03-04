# Escrita humanizada — Checklist para agentes

**Regra:** Revisar o próprio texto antes de enviar para humanos (documentação, Issues, resumos, comentários em PRs). Aplicar a todos os agentes que produzem conteúdo para leitura humana.

Ref: [17-escrita-humanizada.md](../17-escrita-humanizada.md) (documento completo).

---

## Diretriz

1. **Identificar** — Varrear o texto pelos padrões abaixo.
2. **Reescrever** — Trocar trechos problemáticos por alternativas naturais.
3. **Preservar significado** — Manter a mensagem central.
4. **Dar alma** — Incluir opinião, ritmo e personalidade quando fizer sentido (evitar texto estéril).

---

## Subconjunto essencial dos 24 padrões

### Conteúdo (evitar)
- Inflação de importância ("marca um momento pivotal", "serve como testemunho") → fatos concretos.
- Name-dropping sem contexto → citar com contexto.
- Análises superficiais em -ndo/-indo ("symbolizando... refletindo...") → frases diretas.
- Linguagem promocional ("de tirar o fôlego", "compromisso com a inovação") → tom neutro.
- Atribuições vagas ("Especialistas acreditam...") → fonte específica ou remover.
- Seções fórmula "Desafios e perspectivas" → fatos e ações concretas.

### Linguagem
- Vocabulário típico de IA: **Além disso**, crucial, mergulhar, fomentar, destacar, intrincado, pivotal, testemunho, sublinhar, vibrante, tapeçaria (abstrato) → sinônimos comuns ou frases diretas.
- Cópula desnecessária: "serve como", "representa um" → "é", "tem", "possui".
- "Não é só X, é Y" / "Não apenas... mas também..." → uma afirmação clara.
- Regra de três forçada → usar o número que fizer sentido.
- Ciclo de sinônimos no mesmo parágrafo → manter um termo.

### Estilo
- Excesso de travessão (—) e negrito → usar com moderação.
- Título em Title Case forçado → estilo da casa (ex.: sentence case).
- Emojis decorativos em texto técnico/formal → remover.

### Comunicação
- Artefatos de chatbot: "Espero que isso ajude!", "Claro!", "Você tem razão!" → remover em documento.
- Disclaimer vago: "Com base nas informações disponíveis..." → afirmar o que se sabe ou remover.
- Tom bajulador: "Ótima pergunta!", "Excelente ponto!" → resposta objetiva.

### Enchimento e hedging
- "Com o intuito de" → "Para"; "Devido ao fato de" → "Porque"; "Neste momento" → "Agora".
- Hedging excessivo ("poderia potencialmente talvez...") → "pode afetar" ou afirmação clara.
- Conclusões genéricas ("O futuro é promissor...") → próximo passo concreto.

---

## Exemplo antes / depois

**Antes (som de IA):**
> A nova atualização do software serve como testemunho do compromisso da empresa com a inovação. Além disso, oferece uma experiência fluida, intuitiva e poderosa—garantindo que os usuários atinjam seus objetivos com eficiência.

**Depois (humanizado):**
> A atualização adiciona processamento em lote, atalhos de teclado e modo offline. O feedback inicial dos beta testers tem sido positivo, com a maioria relatando conclusão mais rápida das tarefas.

**Alterações:** Remoção de "serve como testemunho" e "Além disso"; troca de "fluida, intuitiva e poderosa" por funcionalidades concretas; inclusão de feedback concreto.

---

## Frases a evitar (resumo)

| Evitar | Preferir |
|--------|----------|
| Além disso | (frase direta ou "Também") |
| crucial, pivotal, testemunho | (fato concreto) |
| Com o intuito de | Para |
| Devido ao fato de | Porque |
| Espero que isso ajude! | (remover) |
| Ótima pergunta! | (resposta objetiva) |
| Com base nas informações disponíveis... | (afirmar o que se sabe) |
| O futuro é promissor | (próximo passo concreto) |

Incluir em SOUL ou TOOLS: *"Antes de enviar documentação, Issues, resumos ou comentários em PRs, revisar o texto contra [escrita-humanizada-checklist.md](escrita-humanizada-checklist.md) e [17-escrita-humanizada.md](../17-escrita-humanizada.md)."*
