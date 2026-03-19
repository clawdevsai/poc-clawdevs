# SPEC TEMPLATE

Use este modelo para descrever comportamento externo antes de codificar.
O objetivo e reduzir ambiguidade, alinhar humanos e agentes e manter rastreabilidade entre BRIEF, SPEC, US e TASK.

## 1. Contexto
- Problema que estamos resolvendo
- Quem e afetado
- Porque isso importa agora

## 2. Objetivo
- Resultado esperado em uma frase
- Valor de negocio ou operacional

## 3. Nao objetivos
- O que esta explicitamente fora do escopo

## 4. Escopo funcional
- Fluxos principais
- Fluxos alternativos relevantes
- Casos de erro esperados

## 5. Comportamento
Descreva em linguagem de dominio e, quando util, em formato Given/When/Then.

### Fluxo 1
- Given:
- When:
- Then:

### Fluxo 2
- Given:
- When:
- Then:

## 6. Contratos
- Entradas e saidas
- Regras de validacao
- Precondicoes e poscondicoes
- Invariantes
- Integracoes e limites entre sistemas
- Estado ou sequencia, se aplicavel

## 7. Requisitos nao funcionais
- Performance
- Custo
- Seguranca
- Observabilidade
- Compliance
- Disponibilidade e resiliencia

## 8. Dados
- Dados criados, lidos, atualizados e removidos
- Classificacao de dados sensiveis
- Retencao e auditoria

## 9. Testes e criterio de aceite
- Cenarios de validacao
- Criterios objetivos de aceite
- Sinais de falha

## 10. Rollout
- Plano de entrega
- Migração, se houver
- Rollback, se necessario

## 11. Riscos e decisoes
- Riscos conhecidos
- Decisoes tomadas
- Premissas adotadas

## 12. Rastreabilidade
- BRIEF:
- SPEC:
- US:
- TASK:
- Issues:

## Regra de uso
- Mantenha a spec completa, mas concisa.
- Prefira comportamento observavel a descricoes vagas.
- Refaça a spec antes de refatorar a implementacao quando o comportamento mudar.
