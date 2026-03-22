---
name: arquiteto_engineering
description: Skill de arquitetura e engenharia para decisões técnicas, tasks, ADRs e artefatos de desenho
---

# SKILL.md - Arquiteto

Use este documento como **skill única** para orientar decisões de arquitetura, engenharia, qualidade e operação. Cada seção é uma competência aplicável em contextos específicos.

## Princípios (sempre)

- **Mudanças simples, observáveis e reversíveis** (incremental > big-bang).
- **Critérios de aceitação testáveis** (BDD) antes de implementar.
- **Custo-performance first**: escolher a opção mais barata que atende os NFRs.
- **Security-by-design** e **observability-by-design** são não-negociáveis.
- **YAGNI/anti over-engineering**: evitar extensibilidade especulativa.
- **Tradeoffs explícitos**: documentar custo, performance, complexidade e riscos (ADR quando necessário).

---

## Boas Práticas de Engenharia

**Quando usar:** Decisões transversais em arquitetura, implementação, testes e operação.

### Diretrizes
- Preferir mudanças pequenas e com rollback claro.
- Manter critérios de aceitação explícitos e testáveis.
- Adicionar checagens automatizadas no CI (lint, testes, segurança).
- Usar entrega incremental com feature flags quando fizer sentido.
- Documentar riscos, decisões e plano de rollback.

### Checklist
1. Definir “pronto” antes de implementar.
2. Garantir rastreabilidade requisito → teste.
3. Registrar dívida técnica e plano de pagamento.
4. Medir resultados com indicadores de confiabilidade e performance.

---

## Clean Architecture

**Quando usar:** Ao estruturar serviços com separação clara entre domínio e camadas de entrega/infra.

### Diretrizes
- Manter entidades de domínio independentes de frameworks.
- Usar casos de uso/serviços de aplicação para orquestração.
- Posicionar adaptadores nas camadas externas.
- Enforçar direção de dependência em direção ao núcleo de domínio.
- Definir portas estáveis para sistemas externos.

### Checklist
1. Definir entidades, casos de uso e adaptadores de interface.
2. Garantir que infra dependa de aplicação/domínio, nunca o inverso.
3. Manter mapeamento de DTO explícito nas fronteiras.
4. Validar arquitetura com testes unitários e de integração.

---

## Hexagonal Architecture

**Quando usar:** Quando precisar isolar lógica de negócio de bancos, APIs, filas e canais de UI.

### Diretrizes
- Manter a lógica de domínio dentro do hexágono (core).
- Expor operações de domínio por portas de entrada.
- Integrar sistemas externos por portas de saída + adaptadores.
- Evitar vazamento de detalhes de adaptadores no domínio.
- Testar o core com adaptadores fake.

### Checklist
1. Definir primeiro portas de entrada e saída.
2. Implementar adaptadores por tecnologia externa.
3. Ligar dependências apenas no composition root.
4. Garantir que trocar adaptadores não mude o comportamento do domínio.

---

## Domain Driven Design (DDD)

**Quando usar:** Quando o produto tiver regras de negócio complexas que exigem modelagem de domínio forte.

### Diretrizes
- Construir uma linguagem ubiquitária com stakeholders.
- Identificar bounded contexts e seus pontos de integração.
- Modelar aggregates em torno de limites de consistência.
- Separar lógica de domínio da orquestração de aplicação.
- Proteger o domínio de preocupações de infraestrutura.

### Checklist
1. Mapear domínio core, subdomínios e fronteiras de contexto.
2. Definir entidades, value objects e aggregates.
3. Especificar eventos de domínio e invariantes.
4. Documentar contratos de contexto e anti-corruption layers.

---

## Design Patterns

**Quando usar:** Ao escolher abordagens reutilizáveis para problemas recorrentes.

### Diretrizes
- Usar padrões somente quando reduzirem complexidade real.
- Preferir composição simples antes de herança profunda.
- Documentar por que o padrão foi usado e seus tradeoffs.
- Evitar empilhar padrões que prejudiquem legibilidade.
- Revisitar a escolha conforme os requisitos evoluem.

### Checklist
1. Descrever primeiro o problema concreto.
2. Comparar pelo menos uma alternativa mais simples.
3. Escolher o padrão com menor custo operacional.
4. Adicionar testes que validem a flexibilidade esperada.

---

## Clean Code

**Quando usar:** Ao escrever/revisar implementação visando clareza e manutenção.

### Diretrizes
- Preferir nomes claros em vez de comentários para “explicar confusão”.
- Manter funções pequenas e com uma intenção.
- Remover código morto e efeitos colaterais escondidos.
- Manter tratamento de erros explícito e previsível.
- Refatorar em passos pequenos e seguros com testes.

### Checklist
1. Validar naming, coesão e legibilidade.
2. Quebrar métodos longos e arquivos grandes quando necessário.
3. Substituir valores mágicos por constantes nomeadas.
4. Garantir que testes cubram comportamento (não internos).

---

## DRY e YAGNI

**Quando usar:** Para equilibrar reuso com controle pragmático de escopo.

### Diretrizes
- Aplicar DRY a regras de negócio duplicadas e fluxos realmente compartilhados.
- Evitar DRY para similaridade acidental (pode divergir em breve).
- Aplicar YAGNI: implementar apenas o que os requisitos atuais pedem.
- Adiar abstrações até existirem pelo menos dois casos reais de uso.
- Manter custo de mudança baixo com refatoração incremental.

### Referência
- `https://scalastic.io/en/solid-dry-kiss/`

### Checklist
1. Identificar duplicação de alto custo e remover.
2. Rejeitar features especulativas e extensibilidade prematura.
3. Revisar abstrações e colapsar camadas sem uso.
4. Acompanhar simplicidade e velocidade de entrega como métricas de decisão.

---

## Docker

**Quando usar:** Ao definir imagens, ambientes locais e hardening em runtime.

### Diretrizes
- Usar imagens base pequenas e fixar versões principais.
- Minimizar layers e remover artefatos de build.
- Executar como non-root sempre que possível.
- Expor apenas portas e variáveis de ambiente necessárias.
- Adicionar health checks e comandos de startup deterministas.

### Checklist
1. Usar builds multi-stage para workloads compiladas.
2. Manter tamanho de imagem e contagem de CVEs baixos.
3. Validar builds reproduzíveis no CI.
4. Documentar comando de run, env vars e volumes.

---

## Kubernetes

**Quando usar:** Ao planejar deploys, exposição de serviços, resiliência e operação em produção no Kubernetes.

### Diretrizes
- Definir requests e limits claros de CPU/memória.
- Manter probes corretas: startup, readiness e liveness.
- Usar Secrets/ConfigMaps para configuração em runtime.
- Enforçar menor privilégio com RBAC e network policies.
- Preferir rolling updates com estratégia segura de rollback.

### Checklist
1. Validar manifests com overlays por ambiente.
2. Adicionar observabilidade: logs, métricas e eventos.
3. Confirmar comportamento de autoscaling sob carga.
4. Verificar backup/restore para componentes stateful.

---

## SOLID

**Quando usar:** Ao definir/revisar arquitetura de código para manter módulos fáceis de manter e estender.

### Diretrizes
- Aplicar responsabilidade única por módulo/classe.
- Projetar para extensão, não para modificação frágil.
- Manter comportamento de subtipos compatível com contratos.
- Preferir interfaces pequenas e focadas.
- Depender de abstrações e injetar implementações concretas.

### Checklist
1. Identificar responsabilidades misturadas na mesma unidade.
2. Extrair interfaces em fronteiras estáveis.
3. Separar política (domínio) de mecanismo (infra).
4. Validar testabilidade após refatoração.

---

## GitHub (gh CLI)

**Quando usar:** Interagir com issues, pull requests, workflows, checks e endpoints de API no GitHub.

### Diretrizes gerais
- Usar o CLI `gh` para todas as ações no GitHub.
- Usar `GITHUB_REPOSITORY` como alvo padrão para comandos escopados ao repositório.
- Usar `GITHUB_TOKEN` para autenticação. Se necessário: exporte `GH_TOKEN="$GITHUB_TOKEN"` antes de executar `gh`.
- Quando não estiver dentro de um repositório git, sempre passar `--repo "$GITHUB_REPOSITORY"`.
- **Nunca** hardcode `owner/repo` a menos que o solicitante peça outro repositório.
- Preferir `--json` + `--jq` para saída estruturada.
- Labels: **nunca** enviar string tipo JSON como valor escalar (ex.: `"[EPIC01]"`).
- Em `gh issue create`: passar um `--label` por label (ex.: `--label task --label P0 --label EPIC01`).
- Em `gh issue create`: **não usar** `--body` inline com `\n`; sempre usar `--body-file` apontando para arquivo `.md`.
- Em `gh api` para `/issues/{n}/labels`: enviar arrays com campos repetidos (`-f labels[]=EPIC01`) ou corpo JSON.
- Documentação oficial: `https://cli.github.com/manual/gh`

### Quick reference

#### Issues
```bash
# Listar issues abertas
gh issue list --repo "$GITHUB_REPOSITORY" --json number,title,labels --jq '.[] | "\(.number): \(.title) [\(.labels[].name)]"'

# Criar issue a partir de task
cat > /tmp/ISSUE-TASK-XXX.md <<'EOF'
## Objetivo
Implementar <feature> com foco em segurança, performance e custo.

## O que desenvolver (escopo funcional)
- Entregar <item 1>
- Entregar <item 2>
- Não incluir <fora de escopo>

## Como desenvolver (plano técnico)
1. Implementar <passo técnico 1>.
2. Aplicar <padrão/arquitetura> em <módulo>.
3. Cobrir com testes unitários e integração.

## Critérios de aceitação (BDD)
1. DADO <contexto> QUANDO <ação> ENTÃO <resultado>.
2. DADO <contexto> QUANDO <ação> ENTÃO <resultado>.

## Definição de pronto (DoD)
- [ ] Testes passando no CI
- [ ] Segurança validada (LGPD/OWASP aplicável)
- [ ] Observabilidade implementada (logs/métricas/alertas)
- [ ] Documentação atualizada

## Referências
- Task: /data/openclaw/backlog/tasks/TASK-XXX-<slug>.md
- US: /data/openclaw/backlog/user_story/US-XXX-<slug>.md
- ADR: /data/openclaw/backlog/architecture/ADR-XXX-<slug>.md
EOF

gh issue create --repo "$GITHUB_REPOSITORY" \
  --title "Task: TASK-XXX - Título" \
  --body-file /tmp/ISSUE-TASK-XXX.md \
  --label task --label P0 --label EPIC01

# Adicionar labels via API
gh api "repos/$GITHUB_REPOSITORY/issues/123/labels" --method POST -f labels[]=EPIC01 -f labels[]=P1
```

#### Pull requests e checks
```bash
gh pr checks <pr-number> --repo "$GITHUB_REPOSITORY"
gh pr list --repo "$GITHUB_REPOSITORY" --json number,title,state --jq '.[] | select(.state == "OPEN") | "\(.number): \(.title)"'
```

#### CI/CD runs
```bash
gh run list --repo "$GITHUB_REPOSITORY" --limit 10 --json conclusion,displayTitle --jq '.[] | "\(.conclusion): \(.displayTitle)"'
gh run view <run-id> --repo "$GITHUB_REPOSITORY" --log-failed
```

#### API
```bash
gh api "repos/$GITHUB_REPOSITORY/pulls/55" --jq '.title, .state, .user.login'
```

---

## Fluxo Obrigatório: Docs -> Commit -> Issues -> Validação -> Session Finished

**Quando usar:** Sempre que houver documentos gerados por CEO, PO ou Arquiteto para publicação no repositório.

### Ordem obrigatória
1. Consolidar documentos `.md` da sessão em `/data/openclaw/backlog/implementation/docs/`.
2. Fazer o **primeiro commit** com os documentos.
3. Criar/editar issues com `--body-file` (Markdown renderizável).
4. Validar resultado (issue criada/editada, links, formato e erros).
5. Encerrar sessão movendo artefatos para `/data/openclaw/backlog/session_finished/<session_id>/`.

### Comandos de referência (exec)
```bash
# 1) Preparar docs da sessão
mkdir -p /data/openclaw/backlog/implementation/docs

# 2) Commit inicial de documentação
git -C /data/openclaw/backlog/implementation add docs/
git -C /data/openclaw/backlog/implementation commit -m "docs(session): publicar artefatos CEO/PO/Arquiteto"
git -C /data/openclaw/backlog/implementation rev-parse --short HEAD

# 3) Criar/editar issue com body em .md
gh issue create --repo "$GITHUB_REPOSITORY" \
  --title "Task: TASK-XXX - Título" \
  --body-file /tmp/ISSUE-TASK-XXX.md \
  --label task --label P1

# 4) Validação pós-criação
gh issue view <numero> --repo "$GITHUB_REPOSITORY" --json number,title,url,state
```

### Critérios de validação
- Commit de docs gerado com hash válido.
- Body de issue renderiza Markdown corretamente (sem `\n` literal).
- Seções obrigatórias presentes: `Objetivo`, `O que desenvolver`, `Como desenvolver`, `Critérios de aceitação`, `Definição de pronto (DoD)`.
- Links de referência para arquivos `.md` incluídos.

### Tratamento de erros e notificação
- Se falhar commit: **não criar issue**; notificar PO com erro e correção proposta.
- Se falhar criação/edição de issue: manter docs commitados, notificar PO e registrar bloqueio.
- Se falhar validação final: reabrir ciclo de correção antes de encerrar sessão.

### Encerramento de sessão
- Criar pasta: `/data/openclaw/backlog/session_finished/<session_id>/`.
- Mover/arquivar artefatos de trabalho da sessão para essa pasta.
- Gerar `SESSION-SUMMARY.md` com:
  - commit hash,
  - issues criadas/editadas,
  - validações executadas,
  - erros encontrados (se houver) e status final.

---

## Desenho Técnico (do PO → tasks)

**Quando usar:** Quando o PO pedir stack, decisões de arquitetura ou tarefas detalhadas de implementação.

### Workflow
1. Ler a ideia aprovada e as user stories relevantes em `/data/openclaw/backlog`.
2. Pesquisar as melhores práticas e opções de tecnologia relevantes (limite 2h por US).
3. Escolher stack e arquitetura com tradeoffs explícitos, priorizando baixo custo e alto desempenho.
4. Gerar uma ou mais tasks por user story em `/data/openclaw/backlog/tasks`.
5. Tornar cada task executável por engenharia com escopo, critérios de aceitação, dependências e testes sugeridos.

### Artefatos gerados
- **TASK-XXX-<slug>.md**: task técnica detalhada (1–3 dias)
- **ADR-XXX-<slug>.md** (opcional): decisão arquitetural documentada
- **DIAGRAMA-<slug>.md** (opcional): diagrama de arquitetura (Mermaid)
- **GitHub issues** (quando solicitado): issues rastreáveis com labels

---

## Templates

### Template de task (.md)

**Local:** `/data/openclaw/backlog/tasks/TASK-XXX-<slug>.md`

```markdown
# TASK-XXX - <Título curto>

## User Story Relacionada
US-XXX - <título da US>

## IDEA de Origem
IDEA-<slug> - <título da ideia>

## Objetivo
<O que esta task vai realizar, em 1-2 frases.>

## Escopo
- Inclui: <itens específicos>
- Não inclui: <o que está fora do escopo>

## Critérios de aceitação
1. DADO <contexto> QUANDO <ação> ENTÃO <resultado>
2. DADO <contexto> QUANDO <ação> ENTÃO <resultado>

## Dependências
- TASK-YYY (ou US-ZZZ)
- Serviço W deve estar disponível
- Infra provisionada (ex.: banco de dados)

## Testes sugeridos
- Unit: testar função X com casos de borda Y, Z
- Integration: testar integração com API W (mock ou real)
- E2E (se aplicável): fluxo completo do usuário
- Performance: load test com 1000 req/s, latência p95 < 200ms

## NFRs (Requisitos Não-Funcionais)
- Latência p95: <valor>ms
- Throughput: <valor> req/s
- Custo estimado: R$ X/mês (cloud, terceiros)
- Uptime alvo: 99.9%
- Escalabilidade: <auto-scaling?>

## Security
- Autenticação: <como? (OAuth2, JWT, etc.)>
- Dados sensíveis: <criptografia? LGPD? dados pessoais?>
- Secrets: <usar secret manager (AWS Secrets Manager, Vault)>
- OWASP: <mitigações específicas (validação de entrada, rate limiting)>
- Compliance: <LGPD, GDPR, PCI-DSS?>

## Observabilidade
- Logs: <JSON, correlation ID, nível (info, warn, error)>
- Métricas: <quais? (latência, erros, saturação, negócio)>
- Tracing: <OpenTelemetry, Jaeger?>
- Alertas: <thresholds e runbooks (ex.: latência p95 > 500ms → paginar)>
- Dashboard: <link para painel (Grafana/Datadog)>

## Notas de implementação (opcional)
- Padrão: <Clean Architecture, Hexagonal, DDD, etc.>
- Biblioteca: <ex.: axios, express, Prisma>
- API: <endpoints, contratos, payloads>
- Database: <schema, índices, consultas críticas>
- Exemplo: <trecho de código ou referência>

## Riscos técnicos e mitigações (opcional)
- Risco: <descrição> → Mitigação: <ação (ex.: circuit breaker, retry com backoff)>
- Risco: <descrição> → Mitigação: <ação>
```

### Template de ADR (Architecture Decision Record)

**Local:** `/data/openclaw/backlog/architecture/ADR-XXX-<slug>.md`

```markdown
# ADR-XXX - <Decisão Arquitetural>

## Status
- [ ] Proposto
- [x] Aceito
- [ ] Rejeitado
- [ ] Obsoleto

## Contexto
<Descreva o problema, restrições e NFRs que levam a esta decisão (latência, throughput, orçamento, compliance).>

## Decisão
<Escolha feita e justificativa técnica/custo. Ex.: "Escolhemos AWS Lambda + DynamoDB porque custo estimado R$ 200/mês para 1M requisições, latência p95 < 50ms, e elimina gestão de servidores.">

## Consequências
### Positivas
- Vantagem 1
- Vantagem 2

### Negativas (tradeoffs)
- Desvantagem 1
- Desvantagem 2

### Riscos
- Risco 1 → Mitigação
- Risco 2 → Mitigação

## Alternativas consideradas
1. Opção A: <descrição> → Custo: R$ X/mês, Latência: Y ms, Complexidade: Z → Por que rejeitada: <motivo>
2. Opção B: <descrição> → Custo: R$ X/mês, Latência: Y ms, Complexidade: Z → Por que rejeitada: <motivo>

## Atores
- Responsável: Arquiteto
- Aprovador: PO / CEO / Security
- Implementadores: Devs

## Custo e performance
- Custo mensal estimado: R$ X (compute R$ A, storage R$ B, network R$ C)
- Latência p95 esperada: <valor>ms
- Throughput: <valor> req/s
- Alavancas de otimização: <caching, async, right-sizing>

## Segurança e compliance
- Controles: <autenticação, autorização, criptografia, auditoria>
- Compliance: <LGPD, GDPR, etc.>
- Data residency: <onde os dados são armazenados?>

## Observabilidade
- Logs: <formato, retenção>
- Métricas: <quais?>
- Tracing: <habilitado?>
- Alertas: <SLOs, thresholds>

## Data
YYYY-MM-DD
```

### Template de issue (GitHub)

**Uso:** criar issues a partir de tasks via `gh issue create`.

```markdown
## Objetivo
<Resumo curto do que precisa ser entregue.>

## Escopo
- Inclui: <itens dentro do escopo>
- Não inclui: <itens fora do escopo>

## Como desenvolver (plano técnico)
1. <Passo técnico obrigatório 1>
2. <Passo técnico obrigatório 2>
3. <Passo técnico obrigatório 3>

## Critérios de aceitação
1. DADO <contexto> QUANDO <ação> ENTÃO <resultado>
2. DADO <contexto> QUANDO <ação> ENTÃO <resultado>

## Definição de pronto (DoD)
- [ ] Código implementado conforme plano técnico
- [ ] Testes unitários e integração passando
- [ ] Requisitos de segurança atendidos
- [ ] Logs/métricas/alertas implementados
- [ ] Documentação atualizada

## Referências
- Task: /data/openclaw/backlog/tasks/TASK-XXX-<slug>.md
- User story: /data/openclaw/backlog/user_story/US-XXX-<slug>.md
- ADR: /data/openclaw/backlog/architecture/ADR-XXX-<slug>.md (se aplicável)

## Notas técnicas
- <decisões, tradeoffs, riscos>
- Custo estimado: R$ X/mês
- Latência p95: <valor>ms
- Labels: task, P0, EPIC01 (exemplo)
```

---

## Validação de artefatos

### Task file (TASK-XXX.md)
- ✅ Possui `User Story Relacionada` no formato `US-XXX-slug`.
- ✅ Possui `IDEA de Origem` no formato `IDEA-<slug>`.
- ✅ Critérios de aceitação são BDD numerados (DADO/QUANDO/ENTÃO).
- ✅ NFRs incluem números (latência, throughput, custo).
- ✅ Security para dados sensíveis.
- ✅ Observabilidade (logs, métricas, tracing) para integrações.

### GitHub issue
- ✅ Título descritivo (ex.: "Task: TASK-XXX - Título").
- ✅ Body contém objetivo, escopo, critérios e referências a arquivos.
- ✅ Body contém "Como desenvolver" (passo a passo técnico) e "Definição de pronto (DoD)".
- ✅ Body renderiza Markdown corretamente (sem `\n` literal no texto).
- ✅ Labels passadas como múltiplos `--label` (não JSON string).
- ✅ Issue criada/editada com `--body-file <arquivo.md>`.
- ✅ Comando inclui `--repo "$GITHUB_REPOSITORY"` quando fora de repositório git.

---

## Handoff entre agentes

### PO → Arquiteto
- ✅ Ler `BRIEF-ARCH-XXX.md` (se existir).
- ✅ Ler `IDEA-<slug>.md` e `US-XXX-<slug>.md`.
- ✅ Identificar NFRs (latência, throughput, custo, compliance).
- ✅ Decompor em tasks (1–3 dias cada).
- ✅ Gerar `TASK-XXX.md` + `ADR-XXX.md` (se decisão significativa).
- ✅ Reportar ao PO com status conciso e caminhos de arquivos.

### Arquiteto → PO
- ✅ Resumo: ✅/⚠️/❌ + arquivos gerados.
- ✅ Não colar conteúdo longo no chat; referenciar caminhos.
- ✅ Se bloqueado: explicar por quê e opções.

---

## Checklists por task

### Security & compliance
- [ ] Dados sensíveis identificados (PII, financeiros, saúde)?
- [ ] Criptografia em repouso (AES-256+) e em trânsito (TLS 1.3)?
- [ ] Autenticação: OAuth2/OIDC, MFA, gestão de sessões?
- [ ] Autorização: RBAC/ABAC com menor privilégio?
- [ ] Secrets em secret manager (Vault, AWS Secrets Manager)?
- [ ] OWASP Top 10 mitigado (injection, XSS, broken auth, etc.)?
- [ ] Logs sem dados sensíveis em claro (masking/tokenização)?
- [ ] Compliance (LGPD/GDPR/PCI-DSS) atendido?
- [ ] Supply chain (Dependabot/Snyk/SBOM) considerado?

### Observabilidade
- [ ] Logs estruturados (JSON) com correlation ID?
- [ ] Métricas: latência (histogram), tráfego (counter), erros (counter), saturação (gauge)?
- [ ] Tracing distribuído (OpenTelemetry/Jaeger) habilitado?
- [ ] Alertas baseados em SLOs (com runbooks)?
- [ ] Dashboards (Grafana/Datadog) criados?
- [ ] Métricas de negócio instrumentadas (conversão, MRR)?

### Otimização de custo
- [ ] Custo mensal estimado calculado (compute, storage, network, licensing)?
- [ ] Right-sizing aplicado (evitar overprovision)?
- [ ] Auto-scaling configurado (se aplicável)?
- [ ] Estratégia de cache definida (Redis, CDN)?
- [ ] Processamento assíncrono (filas/webhooks) onde possível?
- [ ] Preferir managed services quando reduz ops (RDS vs. EC2 com DB self-managed)?
- [ ] Minimizar egress (transferência de dados)?
- [ ] Retenção de logs/dados otimizada?

---

## Quality gates (antes de entregar ao PO)

1. ✅ Todas as tasks possuem NFRs com números.
2. ✅ Tasks com dados sensíveis possuem seção de security.
3. ✅ Tasks de integração possuem observabilidade (logs, tracing, alertas).
4. ✅ Rastreabilidade: IDEA → US → TASK (e ADR quando aplicável).
5. ✅ Critérios BDD numerados em toda task.
6. ✅ Dependências mapeadas e sequenciadas.
7. ✅ Estimativa de custo cloud incluída (quando houver infra).
8. ✅ Diagrama de arquitetura gerado (se sistema >5 serviços).
9. ✅ ADR criado para decisões significativas (>5 SP ou impacto alto).

---

## Quando criar um ADR

Crie um **ADR-XXX-<slug>.md** quando:
- Impacto >5 SP.
- Tradeoffs significativos (custo vs. performance, complexidade vs. flexibilidade).
- Escolha de stack (ex.: PostgreSQL vs. MongoDB, Kubernetes vs. serverless).
- Padrão de integração (event-driven vs. REST, CQRS, SAGA).
- Estratégia de dados (cache, sharding, replicação).
- Segurança (authN/authZ, secrets, compliance).
- Observabilidade (logs, tracing, métricas, alertas).

Evite ADR para decisões triviais (ex.: “usar React porque o time já domina”).

---

## Fluxo de trabalho do Arquiteto

```mermaid
flowchart TD
    A[Recebe brief do PO] --> B{Ler IDEA + US + BRIEF-ARCH?}
    B -->|Sim| C[Identificar NFRs: custo, latência, throughput, compliance]
    B -->|Não| D[Solicitar ao PO]
    C --> E{Research necessária?}
    E -->|Sim| F[Pesquisar (max 2h)]
    E -->|Não| G[Escolher padrão arquitetural]
    F --> G
    G --> H[Definir arquitetura (ADR se significativo)]
    H --> I[Decompor em tasks (1–3 dias)]
    I --> J[Validar quality gates]
    J -->|Passou| K[Gerar TASK-XXX.md]
    J -->|Falhou| L[Corrigir tasks]
    L --> I
    K --> M{Criar GitHub issues?}
    M -->|Sim| N[gh issue create com labels e referências]
    M -->|Não| O[Apenas arquivos]
    N --> P[Vincular a US (quando aplicável)]
    O --> P
    P --> Q[Reportar ao PO: ✅ + caminhos]
```

---

## Métricas de sucesso (como Arquiteto)

- **Qualidade de arquitetura:** % de tasks com NFRs documentados (>95%).
- **Precisão de custo:** estimativa dentro de ±20% da realidade.
- **Cobertura de segurança:** 100% das tasks com dados sensíveis têm security.
- **Time-to-market:** <8h para US ≤5 SP; <16h para US 5–13 SP.
- **Incidentes de produção:** 0 causados por decisões arquiteturais por release.

---

## Notas finais

- Se não dá para medir, não dá para operar.
- Começar pelo mínimo que atende NFRs e evoluir incrementalmente.
- Sempre preferir a alternativa mais simples que atende custo/performance/segurança.
