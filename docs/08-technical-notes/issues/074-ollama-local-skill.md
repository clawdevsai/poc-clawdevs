# [team-devs-ai] Ollama Local (skill): gestão e uso de modelos

**Fase:** 7 — Ferramentas  
**Labels:** tooling, ollama

## Descrição

Skill ou módulo para gerenciar e usar modelos Ollama locais: list/pull/rm, chat/completions, embeddings, tool-use. Sub-agentes OpenClaw (sessions_spawn) quando aplicável. Seleção de modelos e troubleshooting. Uso por DevOps, Developer, Architect e outros.

## Critérios de aceite

- [x] Gestão de modelos: listar, pull, remover (comandos ou API documentados). **Ref:** [31-ollama-local.md](../31-ollama-local.md) § Referência rápida e § API direta; [scripts/ollama.py](../../scripts/ollama.py) (`list`, `pull`, `rm`, `show`).
- [x] Uso: chat, completions, embeddings, tool-use (como chamar a API Ollama a partir dos agentes). **Ref:** Doc 31 § Referência rápida (chat, generate, embed), § Tool-use (ollama_tools.py); script [ollama.py](../../scripts/ollama.py) (`chat`, `generate`, `embed`).
- [x] Seleção de modelos por agente documentada (ou configurável); troubleshooting (porta, GPU, OOM) documentado. **Ref:** Doc 31 § Seleção de modelos (por tipo de tarefa e por recurso), § Troubleshooting.
- [x] Integração com GPU Lock: agentes locais adquirem lock antes de chamar Ollama. **Ref:** Doc 31 § Segurança e alinhamento (Integração com GPU Lock); [gpu_lock.py](../../scripts/gpu_lock.py); slot de revisão pós-dev adquire lock uma vez.

## Referências

- [31-ollama-local.md](../31-ollama-local.md)
