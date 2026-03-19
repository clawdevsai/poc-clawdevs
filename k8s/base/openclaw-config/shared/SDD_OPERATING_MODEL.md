# SDD OPERATING MODEL

ClawDevs AI aplica Spec-Driven Development em dois niveis:

1. **Internamente**: na propria plataforma, nos agentes, no bootstrap, na infraestrutura e nas automacoes do repo.
2. **Nos projetos**: em qualquer entrega feita para clientes, produtos ou times internos.

## Regra central
- A SPEC define o comportamento pretendido.
- O codigo e a implementacao executavel dessa SPEC.
- Mudancas sem SPEC clara nao devem seguir para implementacao.

## Fonte de verdade
- Para comportamento e contrato, a fonte de verdade e a SPEC aprovada.
- Para execucao, runtime e automacao, o codigo precisa refletir a SPEC.
- Para negocio e prioridade, o BRIEF e a SPEC precisam permanecer alinhados.

## Como aplicar internamente
- Toda melhoria da plataforma ClawDevs AI começa com BRIEF ou demanda equivalente.
- Em seguida, escrever SPEC com comportamento observavel e criterio de aceite.
- Depois, quebrar em US e TASK para execucao.
- Se a mudanca afetar agentes, bootstrap, manifests ou automacoes, o mesmo fluxo continua valendo.

## Como aplicar nos projetos
- Toda feature de projeto tambem segue BRIEF -> SPEC -> US -> TASK.
- A SPEC deve cobrir contratos, NFRs, integracoes e riscos.
- O trabalho deve sair em slices pequenos, demonstraveis e reversiveis.
- Depois da primeira entrega visivel, endurecer com testes, observabilidade e rollback.

## Resultado esperado
- Menos ambiguidade.
- Menos retrabalho.
- Mais previsibilidade.
- Melhor rastreabilidade entre o que foi pedido, especificado e entregue.
