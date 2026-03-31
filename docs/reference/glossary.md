# Glossario

Termos mais usados nesta base.

- **Agent:** papel de IA com responsabilidades especificas (ex.: `dev_backend`).
- **OpenClaw:** runtime/orquestrador dos agentes.
- **Gateway:** endpoint do OpenClaw exposto localmente na porta `18789`.
- **Control Panel:** interface web e API administrativa (`3000` e `8000`).
- **Ollama:** runtime local de modelos LLM (`11434`).
- **Preflight:** validacao inicial de ambiente e segredos (`make preflight`).
- **Stack:** conjunto de containers da aplicacao controlados pelo `Makefile`.
- **Workspace do agente:** area de arquivos e memoria usada por cada agente.
- **SDD:** fluxo estruturado de especificacao e execucao (CONSTITUTION -> BRIEF -> SPEC -> PLAN -> TASK -> IMPLEMENTATION).
- **Migrate:** execucao das migracoes Alembic do backend (`make migrate`).
- **Logs agregados:** stream de logs dos containers em execucao (`make logs`).
- **Reset:** limpeza destrutiva dos volumes da stack (`make reset`).

Veja tambem:

- [INDEX](../INDEX.md)
- [Setup](../guides/setup.md)
- [Arquitetura](../architecture/overview.md)
