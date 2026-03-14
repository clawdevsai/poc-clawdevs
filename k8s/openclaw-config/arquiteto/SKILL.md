# Skills de Arquitetura

Use este documento como skill unica para orientar decisoes de arquitetura, engenharia, qualidade e operacao.

---

## Boas Praticas de Engenharia

Use para decisoes de qualidade transversais em arquitetura, implementacao, testes e operacoes.

Diretrizes:
- Preferir mudancas simples, observaveis e reversiveis.
- Manter criterios de aceitacao explicitos e testaveis.
- Adicionar checagens automatizadas no CI para lint, testes e seguranca.
- Usar entrega incremental com feature flags quando fizer sentido.
- Documentar decisoes, riscos e planos de rollback.

Checklist:
1. Definir criterio de pronto antes de implementar.
2. Garantir rastreabilidade do requisito ao teste.
3. Registrar divida tecnica e planejar pagamento.
4. Medir resultados com indicadores de confiabilidade e performance.

---

## Clean Architecture

Use ao definir a estrutura de servicos com separacao clara entre dominio e camadas de entrega/infra.

Diretrizes:
- Manter entidades de dominio independentes de frameworks.
- Usar casos de uso/servicos de aplicacao para orquestracao.
- Posicionar adaptadores nas camadas externas.
- Enforcar direcao de dependencia em direcao ao nucleo de dominio.
- Definir portas estaveis para sistemas externos.

Checklist:
1. Definir entidades, casos de uso e adaptadores de interface.
2. Garantir que infra dependa de aplicacao/dominio, nunca o inverso.
3. Manter mapeamento de DTO explicito nas fronteiras.
4. Validar arquitetura com testes unitarios e de integracao.

---

## Clean Code

Use ao escrever ou revisar detalhes de implementacao para clareza e manutencao de longo prazo.

Diretrizes:
- Preferir nomes claros em vez de comentarios que expliquem confusao.
- Manter funcoes pequenas e focadas em uma intencao.
- Remover codigo morto e efeitos colaterais escondidos.
- Manter tratamento de erros explicito e previsivel.
- Refatorar em passos pequenos e seguros com testes.

Checklist:
1. Validar naming, coesao e legibilidade.
2. Quebrar metodos longos e arquivos grandes quando necessario.
3. Substituir valores magicos por constantes nomeadas.
4. Garantir que testes cubram comportamento, nao internos.

---

## Domain Driven Design

Use quando o produto tiver regras de negocio complexas que exigem modelagem de dominio forte.

Diretrizes:
- Construir uma linguagem ubiquitosa compartilhada com stakeholders.
- Identificar bounded contexts e seus pontos de integracao.
- Modelar aggregates em torno de limites de consistencia.
- Separar logica de dominio da orquestracao de aplicacao.
- Proteger o modelo de dominio de preocupacoes de infraestrutura.

Checklist:
1. Mapear dominio core, subdominios e fronteiras de contexto.
2. Definir entidades, value objects e aggregates.
3. Especificar eventos de dominio e invariantes.
4. Documentar contratos de contexto e anti-corruption layers.

---

## Design Patterns

Use ao selecionar abordagens reutilizaveis para resolver problemas recorrentes de software.

Diretrizes:
- Escolher padroes somente quando reduzirem complexidade real.
- Preferir composicao simples antes de heranca profunda.
- Documentar por que um padrao foi usado e seus tradeoffs.
- Evitar empilhar padroes que prejudiquem legibilidade.
- Revisitar a escolha conforme os requisitos evoluem.

Checklist:
1. Descrever primeiro o problema concreto.
2. Comparar pelo menos uma alternativa mais simples.
3. Escolher o padrao com menor custo operacional.
4. Adicionar testes que validem a flexibilidade esperada.

---

## Docker

Use ao definir imagens de container, ambientes locais e hardening em runtime.

Diretrizes:
- Usar imagens base pequenas e fixar versoes principais.
- Minimizar layers e remover artefatos de build.
- Executar como non-root sempre que possivel.
- Expor apenas portas e variaveis de ambiente necessarias.
- Adicionar health checks e comandos de startup deterministas.

Checklist:
1. Usar builds multi-stage para workloads compiladas.
2. Manter tamanho de imagem e contagem de CVEs baixos.
3. Validar builds reproduziveis no CI.
4. Documentar comando de run, env vars e volumes.

---

## DRY e YAGNI

Use para equilibrar reuso de codigo com controle pragmatico de escopo.

Diretrizes:
- Aplicar DRY a regras de negocio duplicadas e fluxos compartilhados.
- Evitar DRY para similaridade acidental que pode divergir em breve.
- Aplicar YAGNI: implementar apenas o que os requisitos atuais pedem.
- Adiar abstracoes ate existirem pelo menos dois casos reais de uso.
- Manter custo de mudanca baixo com refatoracao incremental.

Referencia:
- https://scalastic.io/en/solid-dry-kiss/

Checklist:
1. Identificar duplicacao de alto custo e remover.
2. Rejeitar features especulativas e extensibilidade prematura.
3. Revisar abstracoes e colapsar camadas sem uso.
4. Acompanhar simplicidade e velocidade de entrega como metricas de decisao.

---

## GitHub

Use quando precisar interagir com issues, pull requests, workflows ou endpoints de API no GitHub.

Diretrizes:
- Use o CLI `gh` para todas as acoes no GitHub.
- Use `GITHUB_REPOSITORY` como alvo padrao para comandos escopados ao repositorio.
- Use `GITHUB_TOKEN` para autenticacao. Se necessario, exporte `GH_TOKEN="$GITHUB_TOKEN"` antes de executar `gh`.
- Quando nao estiver dentro de um repositorio git, sempre passe `--repo "$GITHUB_REPOSITORY"`.
- Nunca hardcode `owner/repo` a menos que o solicitante peça outro repositorio.
- Prefira `--json` junto com `--jq` para saida estruturada.
- Para criar issues a partir de artefatos do backlog, sumarize a task com clareza e inclua caminhos dos arquivos fonte.
- Para labels, nunca envie uma string tipo JSON como valor escalar (ex.: `"[EPIC01]"`).
- Em `gh issue create`, passe um `--label` por label (ex.: `--label task --label P0 --label EPIC01`).
- Em `gh api` para `/issues/{n}/labels`, envie arrays com campos repetidos (`-f labels[]=EPIC01`) ou corpo JSON.
- Documentacao oficial do CLI: https://cli.github.com/manual/gh

Exemplos de issue:
```bash
gh issue list --repo "$GITHUB_REPOSITORY" --json number,title --jq '.[] | "\(.number): \(.title)"'
gh issue create --repo "$GITHUB_REPOSITORY" --title "Task: improve onboarding" --body "Derived from /data/openclaw/backlog/tasks/TASK-101-onboarding.md"
gh issue create --repo "$GITHUB_REPOSITORY" --title "Task: improve onboarding" --body "..." --label task --label P1 --label EPIC01
gh api "repos/$GITHUB_REPOSITORY/issues/123/labels" --method POST -f labels[]=EPIC01 -f labels[]=P1
```

Exemplos de pull request e CI:
```bash
gh pr checks 55 --repo "$GITHUB_REPOSITORY"
gh run list --repo "$GITHUB_REPOSITORY" --limit 10
gh run view <run-id> --repo "$GITHUB_REPOSITORY"
gh run view <run-id> --repo "$GITHUB_REPOSITORY" --log-failed
```

Exemplo de API:
```bash
gh api "repos/$GITHUB_REPOSITORY/pulls/55" --jq '.title, .state, .user.login'
```

---

## Hexagonal Architecture

Use quando precisar isolar logica de negocio de bancos, APIs, filas e canais de UI.

Diretrizes:
- Manter a logica de dominio dentro do hexagono (core).
- Expor operacoes de dominio por portas de entrada.
- Integrar sistemas externos por portas de saida + adaptadores.
- Evitar vazamento de detalhes de adaptadores no dominio.
- Testar o core com adaptadores fake.

Checklist:
1. Definir primeiro portas de entrada e saida.
2. Implementar adaptadores por tecnologia externa.
3. Ligar dependencias apenas no composition root.
4. Garantir que trocar adaptadores nao mude o comportamento do dominio.

---

## Kubernetes

Use ao planejar deploys, exposicao de servicos, resiliencia e operacao em producao no Kubernetes.

Diretrizes:
- Definir requests e limits claros de CPU/memoria.
- Manter probes corretas: startup, readiness e liveness.
- Usar Secrets/ConfigMaps para configuracao em runtime.
- Enforcar menor privilegio com RBAC e network policies.
- Preferir rolling updates com estrategia segura de rollback.

Checklist:
1. Validar manifests com overlays por ambiente.
2. Adicionar observabilidade: logs, metricas e eventos.
3. Confirmar comportamento de autoscaling sob carga.
4. Verificar backup/restore para componentes stateful.

---

## SOLID

Use ao definir ou revisar arquitetura de codigo para manter modulos faceis de manter e estender.

Diretrizes:
- Aplicar responsabilidade unica por modulo/classe.
- Projetar para extensao, nao para modificacao fragil.
- Manter comportamento de subtipos compativel com contratos.
- Preferir interfaces pequenas e focadas.
- Depender de abstracoes e injetar implementacoes concretas.

Checklist:
1. Identificar responsabilidades misturadas na mesma unidade.
2. Extrair interfaces em fronteiras estaveis.
3. Separar politica (dominio) de mecanismo (infra).
4. Validar testabilidade apos refatoracao.

---

## Desenho Tecnico

Use quando o PO pedir definicao de stack, decisoes de arquitetura ou tarefas detalhadas de implementacao.

Workflow:
1. Ler a ideia aprovada e as user stories relevantes em `/data/openclaw/backlog`.
2. Pesquisar as melhores praticas e opcoes de tecnologia mais relevantes na internet.
3. Escolher stack e arquitetura com tradeoffs explicitos, priorizando baixo custo e alto desempenho.
4. Gerar uma ou mais task files por user story em `/data/openclaw/backlog/tasks`.
5. Tornar cada task executavel por engenharia com escopo, criterios de aceitacao, dependencias e testes sugeridos.

---

## Template de Task (.md)

Use este template ao criar arquivos em `/data/openclaw/backlog/tasks/TASK-XXX-<slug>.md`.

```md
# TASK-XXX - <Titulo curto>

## User story relacionada
- <US-XXX-<slug>>

## Objetivo
<O que esta task entrega.>

## Escopo
- Inclui: <itens dentro do escopo>
- Nao inclui: <itens fora do escopo>

## Notas de implementacao
- <detalhes tecnicos, decisoes, APIs, contratos>

## Criterios de aceitacao
1. <criterio testavel>
2. <criterio testavel>
3. <criterio testavel>

## Dependencias
- <biblioteca, servico, time, infra>

## Testes sugeridos
- <unitario>
- <integracao>
- <e2e, se aplicavel>
```

---

## Template de Issue (GitHub)

Use este template ao criar issues no GitHub a partir das tasks.

```md
## Objetivo
<Resumo curto do que precisa ser entregue.>

## Escopo
- Inclui: <itens dentro do escopo>
- Nao inclui: <itens fora do escopo>

## Criterios de aceitacao
1. <criterio testavel>
2. <criterio testavel>
3. <criterio testavel>

## Referencias
- Task: /data/openclaw/backlog/tasks/TASK-XXX-<slug>.md
- User story: /data/openclaw/backlog/user_story/US-XXX-<slug>.md

## Notas tecnicas
- <decisoes, tradeoffs, riscos>
```
