# [team-devs-ai] Ollama Local (skill): gestão e uso de modelos

**Fase:** 7 — Ferramentas  
**Labels:** tooling, ollama

## Descrição

Skill ou módulo para gerenciar e usar modelos Ollama locais: list/pull/rm, chat/completions, embeddings, tool-use. Sub-agentes OpenClaw (sessions_spawn) quando aplicável. Seleção de modelos e troubleshooting. Uso por DevOps, Developer, Architect e outros.

## Critérios de aceite

- [ ] Gestão de modelos: listar, pull, remover (comandos ou API documentados).
- [ ] Uso: chat, completions, embeddings, tool-use (como chamar a API Ollama a partir dos agentes).
- [ ] Seleção de modelos por agente documentada (ou configurável); troubleshooting (porta, GPU, OOM) documentado.
- [ ] Integração com GPU Lock: agentes locais adquirem lock antes de chamar Ollama.

## Referências

- [31-ollama-local.md](../31-ollama-local.md)
