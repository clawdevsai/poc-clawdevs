# SDD CHECKLIST

Use este checklist antes de passar uma mudanca adiante.

## Constitution
- [ ] A mudanca esta alinhada com a constitution do repositorio.
- [ ] O objetivo foi escrito de forma curta e observavel.

## Brief
- [ ] O problema e o valor esperado estao claros.
- [ ] O escopo e o nao-escopo estao definidos.
- [ ] Os riscos principais foram identificados.

## Spec
- [ ] A SPEC descreve comportamento observavel.
- [ ] Contratos, invariantes e NFRs estao explicitos.
- [ ] Criterios de aceite sao testaveis.

## Clarify
- [ ] As ambiguidades foram resolvidas.
- [ ] As suposicoes foram registradas.
- [ ] O que ficou em aberto foi declarado.

## Plan
- [ ] Existe um plano tecnico coerente com a SPEC.
- [ ] As decisoes arquiteturais estao justificadas.
- [ ] O impacto em custo, seguranca e operacao foi considerado.

## Tasks
- [ ] As tasks sao pequenas e executaveis.
- [ ] A rastreabilidade para SPEC e BRIEF esta mantida.
- [ ] A ordem de implementacao reduz risco.

## Implement
- [ ] O slice funcional minimo e demonstravel existe.
- [ ] Testes cobrem os cenarios da SPEC.
- [ ] Logs, metricas e rollback foram considerados.

## Validate
- [ ] CI ou validacao local passou.
- [ ] A demo confirmou o comportamento esperado.
- [ ] O artefato pode seguir para a proxima etapa sem ambiguidade.
