# Escrita humanizada (Humanizer)

Os agentes do enxame aplicam **escrita humanizada** ao produzir texto para humanos: documentação, resumos executivos, Issues, comentários em PRs e qualquer conteúdo que será lido por pessoas. O objetivo é remover sinais de texto gerado por IA e dar **voz e alma** ao que escrevem.

**Referência de origem:** Padrões baseados no guia [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), mantido pelo WikiProject AI Cleanup — observações de milhares de instâncias de texto gerado por IA.

**Ideia central:** *"LLMs usam algoritmos estatísticos para adivinhar o que vem a seguir. O resultado tende ao mais estatisticamente provável que se aplica ao maior número de casos."* Escrever de forma humanizada é fugir desse padrão: específico, com opinião e ritmo variado.

---

## Quem aplica

| Agente | Onde aplicar |
|--------|----------------|
| **CEO** | Resumos executivos, documentação estratégica, comunicações ao Diretor. |
| **PO** | Descrição de Issues, critérios de aceite, comentários no backlog. |
| **Architect** | Comentários em PRs, ADRs, documentação de arquitetura. |
| **Developer** | Comentários em código e PRs, documentação técnica e README. |
| **QA** | Relatórios de bug, descrição de Issues, evidências de teste. |
| **CyberSec** | Relatórios de auditoria, descrição de vulnerabilidades, recomendações. |
| **UX** | Descrições de fluxos, feedback de usabilidade, documentação de padrões. |
| **DevOps** | Documentação de infra, runbooks, mensagens de commit quando descritivas. |

Todos os agentes que produzem texto para leitura humana devem revisar o próprio texto contra os padrões abaixo antes de enviar.

---

## Processo

1. **Identificar** — Varrear o texto pelos padrões listados abaixo.
2. **Reescrever** — Trocar trechos problemáticos por alternativas naturais.
3. **Preservar significado** — Manter a mensagem central.
4. **Manter o tom** — Formal, casual ou técnico conforme o contexto.
5. **Dar alma** — Não só remover padrões; incluir opinião, ritmo e personalidade quando fizer sentido.

### Formato de saída

- Texto reescrito.
- Opcional: resumo breve das alterações (ex.: "Removido 'além disso' e 'testemunho'; trocado por frases diretas.").

---

## Alma e voz (evitar escrita “sem alma”)

Evitar padrões de IA é metade do trabalho. Texto estéril, sem voz, também soa artificial.

### Sinais de escrita sem alma

- Todas as frases com o mesmo tamanho e estrutura.
- Nenhuma opinião, só relato neutro.
- Nenhum reconhecimento de incerteza ou sentimentos mistos.
- Nenhuma primeira pessoa quando for apropriado.
- Sem humor, sem aresta, sem personalidade.
- Leitura de comunicado de imprensa ou verbete genérico.

### Como dar voz

- **Ter opinião.** Não só reportar — reagir. "Não sei bem o que achar disso" soa mais humano que listar prós e contras de forma neutra.
- **Variar o ritmo.** Frases curtas e diretas; depois frases mais longas. Alternar.
- **Reconhecer complexidade.** "Isso é impressionante, mas também um pouco inquietante" soa mais humano que "Isso é impressionante."
- **Usar "eu" quando couber.** Primeira pessoa não é pouco profissional — é honesta. "Eu continuo voltando a..." ou "O que me chama atenção é..." indica alguém pensando.
- **Deixar um pouco de “desordem”.** Estrutura perfeita demais parece algorítmica. Digressões, parênteses e meias-ideias são humanos.
- **Ser específico em sentimentos.** Não "isso é preocupante", mas "há algo inquietante em X quando Y."

---

## Padrões a detectar e corrigir

### Conteúdo

1. **Inflação de importância** — "marca um momento pivotal...", "serve como testemunho..." → substituir por fatos concretos.
2. **Name-dropping de notoriedade** — listar fontes sem contexto → citar com contexto (ex.: "Em entrevista de 2024 ao X, disse que...").
3. **Análises superficiais em -ndo/-indo** — "symbolizando... refletindo... garantindo..." → frases diretas com sujeito e verbo.
4. **Linguagem promocional** — "aninhado em...", "de tirar o fôlego", "compromisso com a inovação" → tom neutro e factual.
5. **Atribuições vagas** — "Especialistas acreditam...", "Relatórios do setor..." → fonte específica ou remover.
6. **Seções fórmula "Desafios e perspectivas"** — "Apesar dos desafios... continua a prosperar" → fatos e ações concretas.

### Linguagem e gramática

7. **Vocabulário típico de IA** — Além disso, crucial, mergulhar, fomentar, destacar, intrincado, paisagem (abstrato), pivotal, testemunho, sublinhar, vibrante, tapeçaria (abstrato) → sinônimos mais comuns ou frases diretas.
8. **Evitar "é"/"são" (cópula)** — "serve como", "representa um", "dispõe de" → "é", "tem", "possui" quando couber.
9. **Paralelismos negativos** — "Não é só X, é Y" / "Não apenas... mas também..." → uma afirmação clara.
10. **Regra de três forçada** — agrupar sempre em três itens → usar o número que fizer sentido.
11. **Ciclo de sinônimos** — "protagonista... personagem principal... figura central... herói" no mesmo parágrafo → manter um termo.
12. **Falsos intervalos** — "de X a Y" em escalas não mensuráveis → enumeração ou descrição direta.

### Estilo

13. **Excesso de travessão (—)** — substituir por vírgula ou ponto quando possível.
14. **Excesso de negrito** — usar com moderação; remover quando for só enfeite.
15. **Listas com cabeçalho inline** — "**Experiência do usuário:** A experiência..." → texto corrido ou lista simples.
16. **Título em Title Case** — "Strategic Negotiations And Global Partnerships" → "Strategic negotiations and global partnerships" (ou estilo da casa).
17. **Emojis decorativos** — remover em texto técnico/formal; usar só quando fizer parte do padrão de comunicação.
18. **Aspas curvas** — "..." → "..." (aspas retas) quando for convenção do projeto.

### Comunicação

19. **Artefatos de chatbot** — "Espero que isso ajude!", "Claro!", "Você tem razão!" → remover de conteúdo que vira documento.
20. **Disclaimer de corte de conhecimento** — "Com base nas informações disponíveis...", "Enquanto detalhes são escassos..." → afirmar o que se sabe ou remover.
21. **Tom bajulador** — "Ótima pergunta!", "Excelente ponto!" → resposta objetiva ao conteúdo.

### Enchimento e hedging

22. **Frases de enchimento** — "Com o intuito de" → "Para"; "Devido ao fato de" → "Porque"; "Neste momento" → "Agora"; "No caso de você precisar" → "Se você precisar".
23. **Hedging excessivo** — "poderia potencialmente talvez ser argumentado que..." → "pode afetar" ou afirmação clara.
24. **Conclusões genéricas positivas** — "O futuro é promissor...", "Tempos emocionantes pela frente..." → próximo passo concreto ou fato.

---

## Exemplo completo

**Antes (som de IA):**
> A nova atualização do software serve como testemunho do compromisso da empresa com a inovação. Além disso, oferece uma experiência fluida, intuitiva e poderosa—garantindo que os usuários atinjam seus objetivos com eficiência.

**Depois (humanizado):**
> A atualização adiciona processamento em lote, atalhos de teclado e modo offline. O feedback inicial dos beta testers tem sido positivo, com a maioria relatando conclusão mais rápida das tarefas.

**Alterações:** Remoção de "serve como testemunho" e "Além disso"; troca de "fluida, intuitiva e poderosa" e do travessão por frases diretas; inclusão de funcionalidades e feedback concretos.

---

## Referências

- [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
- [Wikipedia: WikiProject AI Cleanup](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_AI_Cleanup)

---

## Relação com a documentação

- [02-agentes.md](02-agentes.md) — Definição dos nove agentes; a escrita humanizada aplica-se a todos ao produzirem texto para humanos.
- [13-habilidades-proativas.md](13-habilidades-proativas.md) — Habilidades proativas, persistentes e de autoaprimoramento; a revisão do próprio texto (humanizar) é parte do comportamento de qualidade antes de entregar.
- [soul/](soul/) — Identidade e tom de cada agente; a "alma" na escrita deve ser coerente com o SOUL do agente (CEO direto, PO pragmático, etc.).
