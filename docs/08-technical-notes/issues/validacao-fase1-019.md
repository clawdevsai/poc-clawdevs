# Validação Fase 1 — 019: Management-team com provedor nuvem e line-up

**Issue:** [019-validacao-management-nuvem-line-up.md](019-validacao-management-nuvem-line-up.md)

## Checklist de validação

- [ ] **llm-providers:** ConfigMap [k8s/llm-providers-configmap.yaml](../../k8s/llm-providers-configmap.yaml) aplicado; chaves `agent_ceo`, `agent_po` (e demais) existem.
- [ ] **Provedor local (padrão):** CEO e PO respondem no Telegram usando Ollama no cluster (`ollama_local`) após `make up`.
- [ ] **Provedor nuvem (opcional):** Se usar Ollama Cloud: `k8s/ollama/secret.yaml` com `OLLAMA_API_KEY`; alterar `agent_ceo` e/ou `agent_po` para `ollama_cloud` no ConfigMap; reiniciar deployment; concluir login (script no `make up`).
- [ ] **Outros provedores (OpenRouter, OpenAI, etc.):** Criar secret no namespace (ex.: `OPENROUTER_API_KEY`); alterar valor em llm-providers-configmap para o agente; config do OpenClaw com ID do modelo correspondente; reiniciar deployment.
- [ ] **Line-up documentado:** Tabela de modelo sugerido por agente em [41-fase1-agentes-soul-pods.md](../41-fase1-agentes-soul-pods.md) (§ Line-up); referência a [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) e [37-deploy-fase0-telegram-ceo-ollama.md](../37-deploy-fase0-telegram-ceo-ollama.md).

## Status

Documentação e line-up implementados. Teste manual com provedor nuvem fica a cargo do ambiente (criar secret e ajustar ConfigMap conforme seção "Management-team com provedor nuvem" no doc 37).
