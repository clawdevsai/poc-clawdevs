# SPEC

## Behavior
- Ao iniciar uma iniciativa, o CEO consolida a demanda em BRIEF e SPEC inicial.
- Se houver ambiguidade, o fluxo produz CLARIFY antes de PLAN.
- O PO refina a SPEC em FEATURE e USER STORY.
- O Arquiteto converte a SPEC em PLAN, TASK e critérios de validacao.
- O Dev_Backend implementa somente o comportamento especificado.

## Contracts
- BRIEF define contexto, valor, escopo e restricoes.
- SPEC define comportamento observavel, contratos, NFRs e criterios de aceite.
- CLARIFY registra ambiguidade, decisoes e assumptions.
- PLAN define arquitetura, fases, riscos e validacao.
- TASK define execucao pequena e rastreavel.
- VALIDATE confirma prontidao e evidencia.

## Acceptance criteria
1. Dado uma demanda nova, quando o CEO iniciar a operacao, entao existe BRIEF e SPEC inicial.
2. Dado uma ambiguidade, quando o fluxo encontrar um gap, entao CLARIFY acontece antes de PLAN.
3. Dado uma TASK pronta, quando o Dev_Backend executar, entao a entrega segue rastreabilidade ate a SPEC.

## NFRs
- Baixa friccao para uso humano e por agentes.
- Rastreabilidade completa entre artefatos.
- Repetibilidade em novas iniciativas.

## Invariants
- Nao implementar sem SPEC suficiente.
- Nao fechar etapa sem checklist.
- Nao deixar plan desatualizado quando a SPEC mudar.
