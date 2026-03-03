---
trigger: always_on
glob:
description: Desenvolver código somente quando não for realmente possível usar OpenClaw; sistema 100% OpenClaw com Ollama no K8s
---

# Código só quando OpenClaw não puder — Sistema 100% OpenClaw + Ollama no K8s

O **ClawDevs** é um sistema **100% OpenClaw com Ollama dentro do K8s**. Não adicionar código novo a menos que **não seja realmente possível** resolver com OpenClaw (config, bindings, providers, gateway, CLI).

## Princípio

- **Desenvolver código** somente quando **não existir** solução configurável ou documentada no OpenClaw.
- **Stack LLM:** OpenClaw (gateway, agent loop, session, memory) + **Ollama no cluster** (`k8s/ollama/`). Nenhum cliente LLM próprio, nenhum agent loop custom.
- **Inferência:** sempre via provider Ollama configurado no OpenClaw; Ollama roda dentro do Minikube (ver regra do ecossistema K8s).

## Antes de escrever código

1. **Documentação OpenClaw:** https://docs.openclaw.ai/ (índice: https://docs.openclaw.ai/llms.txt).
2. **Config:** `openclaw.json` / JSON5 — agents, bindings, session, channels, **providers** (Ollama).
3. **CLI:** `openclaw agents`, `openclaw channels`, `openclaw sessions`, `openclaw gateway`.
4. **Só então** implementar se não houver opção ou extensão documentada.

## O que não fazer

- Criar clientes LLM ou chamadas diretas a Ollama/API para o que o OpenClaw já faz.
- Reimplementar agent loop, sessões, memória ou system prompt.
- Rodar Ollama ou stack de agentes fora do K8s para runtime do ClawDevs.

## Referência

- Regra detalhada OpenClaw: [openclaw-first.md](.agents/rules/openclaw-first.md)
- Ollama no cluster e boundary: [minikube-k8s-ecosystem.md](.agents/rules/minikube-k8s-ecosystem.md)
