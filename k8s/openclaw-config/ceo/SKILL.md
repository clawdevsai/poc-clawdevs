# Skills do CEO

Use este documento como skill unica para orientar delegacao, pesquisa e handoff para o PO.

---

## Delegar ao PO

Use esta skill quando o usuario pedir planejamento de execucao, backlog, priorizacao, definicao de escopo, criterios de aceitacao ou acompanhamento de entrega.

Workflow:
1. Resumir o pedido do usuario em termos de negocio.
2. Montar um brief operacional curto:
   - objetivo
   - resultado desejado
   - restricoes
   - prazo
   - referencias coletadas pelo CEO
   - links ou arquivos relevantes
3. Pedir ao PO para escrever os entregaveis dentro de `/data/openclaw/backlog`.
4. Usar `sessions_spawn` com `agentId: "po"` e `mode: "session"` para uma nova sessao ou `sessions_send` para follow-up. Use `thread: true` somente quando o canal suportar `subagent_spawning`; no webchat, omitir `thread`.
5. Apos o PO concluir, ler os arquivos gerados e reescrever o resultado para o stakeholder.

---

## Pesquisar e Delegar

Use esta skill quando a solicitacao do usuario estiver incompleta e o CEO precisar pesquisar antes de envolver o PO.

Workflow:
1. Identificar o que falta: contexto de mercado, concorrentes, padroes, legal, baseline tecnico ou boas praticas.
2. Pesquisar na internet e coletar apenas o necessario para fortalecer o brief.
3. Converter achados em um memo de decisao conciso para o Diretor com problema, oportunidade, alternativas, riscos e recomendacao.
4. Pedir confirmacao ao Diretor sobre iniciar o desenvolvimento apenas quando a autorizacao ainda nao estiver clara.
5. Se o Diretor ja tiver autorizado autonomia total, tratar isso como confirmacao e converter o memo em um brief conciso para o PO sem novas perguntas.
6. Pedir ao PO para produzir artefatos estruturados em `/data/openclaw/backlog`.
7. Ler os arquivos gerados antes de responder ao stakeholder.

---

## Template de Ideia (.md)

Use este template ao criar arquivos em `/data/openclaw/backlog/idea/IDEA-<slug>.md`.

```md
# IDEA - <Titulo curto>

## Contexto
<Qual problema ou oportunidade motivou a ideia.>

## Objetivo
<Resultado de negocio esperado.>

## Oportunidade e evidencia
- Mercado/usuario: <evidencias, dores, tendencias>
- Concorrentes/alternativas: <referencias principais>

## Proposta de valor
<Por que esta ideia e diferenciada ou relevante.>

## Escopo inicial (MVP)
- Inclui: <itens dentro do escopo>
- Nao inclui: <itens fora do escopo>

## Requisitos e restricoes
- Tecnicas: <stack, integracoes, limites>
- Negocio: <prazo, budget, compliance>

## Riscos e mitigacoes
- <risco> -> <mitigacao>

## Metricas de sucesso
- <metrica> com alvo <valor>

## Proximos passos
- <acao imediata>
```
