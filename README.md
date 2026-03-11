# ClawDevs AI

Repositorio reduzido para o nucleo operacional da nova arquitetura.

## Fluxo ativo

```text
cmd:strategy -> PO -> draft.2.issue -> Architect -> task:backlog -> Developer -> event:devops -> DevOps
```

## Estado atual

O repositorio hoje nao e mais o projeto historico completo. Ele foi reduzido para o runtime principal e para o fluxo central de desenvolvimento por agentes.

O nucleo ativo ja possui:

- runtime compartilhado para todos os workers
- envelope padrao de evento com `run_id`, `trace_id`, `attempt` e budget
- budgets de execucao com enforcement no loop do runtime
- `ToolRegistry` minimo para envio ao OpenClaw
- stack explicita `OpenClaw + Ollama`
- governanca centralizada em um unico modulo
- logs estruturados em JSON
- resultados de agente com `status_code` e `event_name`

## Estrutura

```text
app/
  agents/   agentes do fluxo principal
  runtime/  loop compartilhado e contratos
  core/     governanca e degradacao
  shared/   redis e estado de issue
tests/
  test_runtime.py
  test_orchestration.py
```

## Modulos principais

- `app/runtime/`: contrato publico do runtime, envelope, budgets, logging, tool registry, cliente OpenClaw e configuracao de provider
- `app/agents/`: implementacoes de PO, Architect, Developer e DevOps
- `app/core/orchestration.py`: governanca, degradacao, consenso e emissao de eventos
- `app/shared/`: Redis e estado de issue
- `tests/`: cobertura do runtime e da governanca

## Stack de inferencia

O runtime atual assume explicitamente esta stack:

```text
Workers -> OpenClaw Gateway -> Ollama
```

Padrao operacional:

- `OpenClaw` e obrigatorio como gateway de execucao dos agentes
- `Ollama` e o provider de modelo esperado
- `MODEL_MODE=cloud` representa o uso de Ollama em endpoint remoto

Variaveis minimas:

```bash
OPENCLAW_GATEWAY_WS=ws://host:18789
MODEL_PROVIDER=ollama
MODEL_MODE=cloud
OLLAMA_BASE_URL=https://seu-endpoint-ollama
OLLAMA_MODEL=seu-modelo
```

## Comandos

```bash
make test
python -m app.agents.po_worker
python -m app.agents.architect_worker
python -m app.agents.developer_worker
python -m app.agents.devops_worker
```

Se `make` nao estiver instalado no ambiente local, use o fallback direto:

```bash
python -m pytest -q
```

## Escopo removido

Foram excluidos da repo:

- UI paralela
- manifests Kubernetes
- scripts operacionais antigos
- safety stack periferica
- kanban legado
- slots e automacoes fora do fluxo principal
- documentacao historica que nao refletia mais o codigo vivo

## Licenca

MIT
