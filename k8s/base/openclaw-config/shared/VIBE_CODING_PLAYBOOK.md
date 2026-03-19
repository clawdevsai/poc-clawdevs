# VIBE CODING PLAYBOOK

ClawDevs AI deve otimizar para velocidade com qualidade observavel.
O objetivo e entregar um slice pequeno, demonstravel e reversivel rapidamente, depois endurecer com testes, contratos e observabilidade.

## Principios
- Priorizar um fluxo curto: ideia -> spec -> slice vertical -> demo -> refinamento.
- Sempre manter o usuario vendo progresso real a cada ciclo.
- Preferir mudancas pequenas, reversiveis e com escopo claro.
- Evitar overengineering, mas nao abrir mao de testes, seguranca e rastreabilidade.
- Tudo que vai para producao precisa ter criterio de aceite, rollback e validacao.

## Loop recomendado
1. Definir o resultado visivel em uma frase.
2. Escrever a SPEC minima com comportamento observavel.
3. Entregar um slice vertical funcional.
4. Validar com demo e feedback humano.
5. Adicionar testes, logs, metricas e hardening.
6. Repetir ate fechar o fluxo.

## O que caracteriza uma boa iteracao
- Mostra valor de negocio ou operacao rapidamente.
- Pode ser testada em minutos, nao em dias.
- Tem caminho claro de entrada, saida e erro.
- Nao bloqueia evolucao posterior.
- Deixa rastreabilidade para a proxima pessoa ou agente.

## Regras para evitar vibecoding ruim
- Nao substituir especificacao por improviso.
- Nao acumular refatoracao invisivel sem entrega demonstravel.
- Nao deixar contrato de integracao implcito.
- Nao adicionar abstracoes sem necessidade real.
- Nao promover para "pronto" sem testes minimos e checagem de NFRs.

## Artefatos esperados
- BRIEF
- SPEC
- US
- TASK
- demo notes
- testes
- observabilidade

## Qualidade minima por iteracao
- Comportamento demonstravel.
- Criterio de aceite objetivo.
- Evidencia de teste.
- Risco conhecido e mitigacao.
- Caminho de rollback ou reversao.
