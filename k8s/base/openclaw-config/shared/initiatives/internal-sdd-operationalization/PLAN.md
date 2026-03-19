# PLAN

## Goal
- Tornar o fluxo SDD o caminho padrao de operacao da ClawDevs AI.

## Inputs
- BRIEF
- SPEC
- CLARIFY
- Constitution
- Checklist SDD

## Architecture
- `k8s/base/openclaw-config/shared/` guarda os contratos.
- `k8s/base/openclaw-pod.yaml` distribui os artefatos para os workspaces.
- `k8s/base/kustomization.yaml` expõe os arquivos no configMap.
- `README.md` aponta a entrada oficial do fluxo.
- `Makefile` oferece atalhos para os templates e prompts operacionais.

## Alternatives considered
- Opcao: deixar o fluxo apenas na documentacao.
- Tradeoff: menor trabalho agora, maior risco de uso inconsistente.
- Rejected because: nao cria habito operacional.

## Phases
1. Consolidar templates, checklist e prompts.
2. Expor tudo aos agentes via bootstrap.
3. Criar um exemplo completo para orientar novas iniciativas.

## Risks
- Risco: duplicacao de artefatos e confusao de fonte de verdade.
- Mitigacao: manter o pacote compartilhado e a documentacao principal enxuta.

## Validation
- Renderizacao do kustomize.
- Verificacao do README.
- Verificacao dos atalhos do Makefile.

## Rollback
- Remover os atalhos e referencias novas sem afetar o runtime dos agentes.
