# [team-devs-ai] Validação management-team com provedor nuvem e line-up de agentes

**Fase:** 1 — Agentes  
**Labels:** agents, k8s, llm, nuvem

## Descrição

Validar e documentar o uso do **management-team** (CEO, PO) com **provedores de LLM em nuvem** (Ollama Cloud, OpenRouter, OpenAI, etc.) via ConfigMap `clawdevs-llm-providers` e secrets. Documentar o **line-up** recomendado (modelo por agente) para Fase 1 e onde configurar (OpenClaw config, llm-providers).

## Critérios de aceite

- [x] Documentação em [37-deploy-fase0-telegram-ceo-ollama.md](../37-deploy-fase0-telegram-ceo-ollama.md): seção "Management-team com provedor nuvem (Fase 1 — 019)" (secret, llm-providers, reinício).
- [x] Tabela ou seção **line-up** (modelo sugerido por agente para Fase 1) em [41-fase1-agentes-soul-pods.md](../41-fase1-agentes-soul-pods.md) (§ Line-up); referência a `k8s/llm-providers-configmap.yaml`.
- [x] Status de validação: [validacao-fase1-019.md](validacao-fase1-019.md) com checklist (teste manual com nuvem a cargo do ambiente).

## Referências

- [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md)
- [37-deploy-fase0-telegram-ceo-ollama.md](../37-deploy-fase0-telegram-ceo-ollama.md)
- [k8s/llm-providers-configmap.yaml](../../k8s/llm-providers-configmap.yaml)
- [k8s/management-team/](../../k8s/management-team/)
