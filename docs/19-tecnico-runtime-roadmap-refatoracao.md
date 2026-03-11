# Roadmap de Refatoracao do Runtime de Agentes

## Estado atual do repositorio

O roadmap abaixo descreve o alvo e a sequencia de refatoracao, mas varias etapas ja foram executadas no codigo vivo.

O estado atual consolidado e:

- `app/runtime/` existe e e a superficie publica do runtime
- os workers principais usam o mesmo loop compartilhado
- o envelope de evento ja padroniza `type`, `issue_id`, `run_id`, `trace_id`, `attempt` e `budget_started_at`
- `RunContext`, `ExecutionPolicy`, `AgentResult` e `ToolRegistry` ja existem
- o cliente OpenClaw foi movido para o runtime
- a governanca foi consolidada em `app/core/orchestration.py`
- o runtime ja aplica budget de tentativa e tempo antes do dispatch
- o requeue preserva o envelope e incrementa `attempt`
- logs estruturados em JSON ja existem no runtime e na governanca
- `AgentResult` ja expõe `status_code` e `event_name`

O que ainda falta neste roadmap nao e mais "fundacao". E principalmente acabamento de produto, clareza de workflow e evolucao de observabilidade.

## Objetivo

Reduzir a complexidade acidental do ClawDevs AI sem perder a ideia central do produto: um time de desenvolvimento autonomo baseado em agentes.

O problema principal hoje nao e falta de features. O problema principal e que o runtime esta distribuido entre varios scripts com responsabilidades repetidas:

- consumo de Redis Streams
- montagem de contexto para o agente
- chamada ao OpenClaw Gateway
- atualizacao de estado da issue
- retries, locks e budgets
- publicacao de eventos

Isso funciona para provar o fluxo, mas dificulta evolucao, teste, observabilidade e controle de falhas.

## Diagnostico do estado atual

Os arquivos abaixo concentram o nucleo operacional atual:

- `app/core/orchestration.py`
- `app/agents/po_worker.py`
- `app/agents/architect_worker.py`
- `app/agents/developer_worker.py`
- `app/agents/devops_worker.py`
- `app/runtime/openclaw_client.py`
- `app/shared/issue_state.py`
- `app/shared/redis_client.py`

### O que ja esta bom

- Redis Streams como barramento principal
- modelagem explicita de estados de issue
- mecanismos de governanca como strikes, degradacao e consenso
- runtime compartilhado com contrato publico unico
- envelope de evento padronizado
- budgets com enforcement no loop
- logs estruturados com `run_id` e `trace_id`
- separacao clara entre `agents`, `runtime`, `core` e `shared`

### O que esta travando a escalabilidade

- o fluxo ainda esta modelado mais por papel do que por workflow explicito
- a governanca ainda nao expõe um modelo de dominio proprio para seus eventos
- `shared/issue_state.py` ainda mistura contrato de dominio com acesso operacional
- o `ToolRegistry` existe, mas ainda esta minimo demais
- ainda nao existe camada `workflows/` separando transicao de negocio de execucao

## Principio de refatoracao

Refatorar sem reescrever o produto.

O alvo nao deve ser substituir tudo por uma arquitetura "bonita". O alvo deve ser extrair um runtime minimo comum e migrar os agentes para esse runtime por fatias, mantendo compatibilidade com Redis, OpenClaw e o fluxo atual.

## Estrutura alvo

```text
app/
  runtime/
    agent_runtime.py
    stream_worker.py
    run_context.py
    policies.py
    event_bus.py
    state_store.py
    tool_registry.py
    message_builder.py
  agents/
    base.py
    po_agent.py
    architect_agent.py
    developer_agent.py
    devops_agent.py
  workflows/
    strategy_to_issue.py
    draft_to_backlog.py
    backlog_to_code.py
    merge_to_deploy.py
    degradation_governance.py
  domain/
    issues.py
    events.py
    agent_roles.py
    execution_limits.py
```

## Responsabilidade de cada camada

### `runtime/`

Runtime generico. Nao conhece PO, Developer ou DevOps. Conhece apenas:

- como consumir eventos
- como montar um `RunContext`
- como aplicar politicas
- como delegar para um agente
- como registrar resultado

Isso ja existe em grande parte no codigo atual.

### `agents/`

Define o comportamento por papel. Cada agente implementa um contrato unico.

Exemplo de contrato:

```python
class RoleAgent:
    role_name: str

    def accepts(self, event: dict) -> bool: ...
    def build_instruction(self, ctx: RunContext) -> str: ...
    def on_success(self, ctx: RunContext, result: AgentResult) -> None: ...
    def on_failure(self, ctx: RunContext, error: Exception) -> None: ...
```

### `workflows/`

Fluxos de negocio compostos por etapas. O papel de workflow e definir o encadeamento entre estados e streams, nao executar a inferencia.

Essa ainda e a principal lacuna arquitetural.

### `integrations/`

Adaptadores para Redis, OpenClaw, GitHub, Slack e Telegram. Sem regra de negocio.

### `domain/`

Tipos, estados, nomes de eventos, limites e contratos estaveis.

Hoje isso ainda esta parcialmente distribuido entre `runtime`, `core` e `shared`.

## Mapeamento do codigo atual para a estrutura alvo

### Migrar quase sem alterar comportamento

- `app/shared/redis_client.py` -> `app/domain` ou `app/runtime/state_store.py`
- `app/shared/issue_state.py` -> `app/domain/issues.py`
- `app/core/orchestration.py` -> `app/workflows/degradation_governance.py`

### Reescrever como wrappers finos

- `app/agents/po_worker.py`
- `app/agents/architect_worker.py`
- `app/agents/developer_worker.py`
- `app/agents/devops_worker.py`

Esses arquivos devem virar apenas pontos de entrada, algo como:

```python
from runtime.stream_worker import run_stream_worker
from agents.po_agent import POAgent

if __name__ == "__main__":
    run_stream_worker(POAgent())
```

Esse objetivo ja foi cumprido.

## Contratos tecnicos que faltam hoje

### 1. Contrato de evento

Criar um envelope padrao para todos os streams:

```json
{
  "event_type": "task.created",
  "issue_id": "123",
  "run_id": "run-abc",
  "source": "po",
  "trace_id": "trace-xyz",
  "payload": {}
}
```

Esse contrato ja existe em versao minima, embora o payload ainda permaneça achatado por compatibilidade com Redis Streams.

### 2. Contrato de execucao

Todo processamento precisa gerar:

- `run_id`
- `attempt`
- `budget_started_at`
- `status`
- `status_code`
- `event_name`

Parte disso ja esta implementada; ainda falta modelagem mais forte de decisao e custos de run.

### 3. Politicas unificadas

Centralizar em um lugar unico:

- max tentativas por issue
- custo maximo por run
- custo diario por papel
- timeout por agente
- step limit por fluxo
- regras de degradacao

Hoje isso ja esta majoritariamente concentrado entre `runtime` e `core/orchestration.py`, mas ainda sem uma camada de dominio formal.

## Fases de execucao

## Fase 1. Consolidar fundacoes

Status: concluida

Objetivo: criar a infraestrutura minima sem mudar o produto.

Entregas:

- criar `app/runtime/`
- extrair cliente gateway e cliente Redis para adaptadores claros
- definir `RunContext`, `AgentResult` e `ExecutionPolicy`
- criar `event envelope` padrao
- criar `stream_worker.py` com o loop generico de consumo

Criterio de aceite:

- pelo menos um worker rodando no runtime novo
- sem mudar streams existentes
- sem quebrar os testes atuais

## Fase 2. Migrar os quatro fluxos principais

Status: concluida

Objetivo: tirar duplicacao dos workers centrais.

Ordem sugerida:

1. `po_worker.py`
2. `architect_worker.py`
3. `developer_worker.py`
4. `devops_worker.py`

Em cada migracao:

- manter nomes de stream e grupos
- manter formato atual de mensagem para o OpenClaw
- mover regras comuns para o runtime
- deixar o arquivo antigo como wrapper fino

Criterio de aceite:

- os quatro workers compartilham o mesmo loop base
- diferencas entre agentes ficam apenas em configuracao e hooks

## Fase 3. Separar runtime de workflow

Status: pendente

Objetivo: parar de tratar cada papel como pipeline.

Entregas:

- criar `workflows/strategy_to_issue.py`
- criar `workflows/draft_to_backlog.py`
- criar `workflows/backlog_to_code.py`
- criar `workflows/merge_to_deploy.py`
- mover transicoes de estado para um lugar unico

Criterio de aceite:

- e possivel entender o fluxo principal sem abrir quatro scripts de agente
- o runtime nao precisa conhecer o negocio de cada etapa

## Fase 4. Formalizar Tool Registry

Status: parcialmente concluida

Objetivo: parar de acoplar capacidade de agente ao texto do prompt ou a chamadas soltas.

Entregas:

- criar `tool_registry.py`
- registrar tools por papel
- definir permissao por role
- adicionar metadados de timeout, idempotencia e efeito colateral

Contrato minimo:

```python
ToolDefinition(
    name="publish_code_ready",
    allowed_roles={"developer"},
    timeout_sec=10,
    side_effect="redis_stream_write",
)
```

Criterio de aceite:

- toda acao externa relevante passa por uma definicao de tool
- fica claro o que cada agente pode ou nao pode fazer

Estado atual:

- o registry existe
- o envio para OpenClaw ja passa por ele
- ainda faltam tools adicionais e metadados operacionais mais ricos

## Fase 5. Unificar governanca

Status: parcialmente concluida

Objetivo: transformar strikes, consenso e degradacao em politica de execucao, nao em excecao espalhada.

Entregas:

- mover logica de `orchestration.py` para `workflows/degradation_governance.py`
- modelar budgets e thresholds como configuracao estruturada
- registrar decisao de governanca como evento de dominio

Criterio de aceite:

- existe um unico lugar para entender quando a esteira pausa, degrada ou retorna para PO

Estado atual:

- a governanca ja foi consolidada em `app/core/orchestration.py`
- ainda falta separar melhor eventos de dominio de implementacao operacional

## Fase 6. Simplificar operacao local

Objetivo: reduzir custo de desenvolvimento e reproducao.

Entregas:

- criar perfil local com `docker compose`
- deixar Kubernetes como alvo de ambiente avancado
- documentar modo minimo: Redis + Gateway + 2 ou 4 agentes principais

Criterio de aceite:

- um contribuidor consegue subir o core sem Minikube

## Fase 7. Observabilidade de runtime

Status: parcialmente concluida

Objetivo: tornar comportamento emergente auditavel.

Entregas:

- log estruturado com `trace_id`, `issue_id`, `run_id`, `agent_role`
- eventos de lifecycle: `received`, `started`, `forwarded`, `completed`, `failed`, `degraded`
- metricas minimas por papel e por fluxo

Criterio de aceite:

- Mission Control deixa de ser apenas UI e passa a refletir o runtime de forma consistente

Estado atual:

- logs estruturados ja existem
- `run_id`, `trace_id`, `status_code` e `event_name` ja estao no fluxo
- ainda faltam metricas e uma camada consumidora desses logs

## Prioridade real para os proximos 30 dias

Se houver pouco tempo, a sequencia correta e:

1. explicitar `workflows/` para o fluxo principal
2. separar `domain/issues.py` de `shared/issue_state.py`
3. enriquecer o `ToolRegistry` com metadados e novas tools
4. adicionar metricas derivadas dos logs estruturados
5. consolidar eventos de governanca como dominio estavel
6. documentar exemplos reais de operacao local do runtime

Nao recomendo abrir agora:

- novos papeis de agente
- novos canais de entrada
- novas features de UI
- mais automacao em Kubernetes

## Antipatrones a evitar na refatoracao

- reescrever tudo de uma vez
- misturar redesign de produto com migracao de runtime
- trocar Redis Streams antes de estabilizar contratos
- criar abstracao demais antes de migrar o primeiro worker
- mover governanca para prompt quando ela deve viver em codigo

## Estrutura minima de classes

```python
class RunContext:
    event: dict
    issue_id: str | None
    run_id: str
    attempt: int
    policy: "ExecutionPolicy"


class AgentResult:
    status: str
    summary: str
    next_event: dict | None
    cost_estimate: float | None


class ExecutionPolicy:
    timeout_sec: int
    max_attempts: int
    max_cost: float


class RoleAgent:
    role_name: str
    stream_name: str
    consumer_group: str

    def build_instruction(self, ctx: RunContext) -> str: ...
    def on_success(self, ctx: RunContext, result: AgentResult) -> None: ...
    def on_failure(self, ctx: RunContext, error: Exception) -> None: ...
```

## Como medir se a refatoracao deu certo

- menos codigo duplicado nos workers
- mais cobertura de teste sobre runtime do que sobre scripts isolados
- tempo menor para adicionar um novo papel
- menos chaves Redis "soltas" e mais contratos padronizados
- logs suficientes para reconstruir o caminho de uma issue
- capacidade de rodar localmente sem cluster completo

## Decisao recomendada

O proximo marco tecnico do projeto nao deve ser "mais um agente".

Esse marco ja deixou de ser a primeira versao do `Agent Runtime`, porque ela ja existe.

O proximo marco tecnico agora deve ser: `separacao explicita entre runtime, workflow e dominio`.

Sem isso, o projeto deixa de crescer por scripts, mas ainda corre o risco de crescer por acoplamento semantico entre papeis, eventos e regras de negocio.
