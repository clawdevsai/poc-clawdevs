# [team-devs-ai] Ferramenta GitHub (gh CLI) para agentes

**Fase:** 7 — Ferramentas  
**Labels:** tooling, github

## Descrição

Integrar o uso do GitHub CLI (gh) pelos agentes: Issues, PRs, status de CI (gh pr checks, gh run list/view), gh api para consultas avançadas. PO, Developer, Architect, DevOps, QA e CyberSec. Nunca expor tokens; Zero Trust e validação em runtime.

## Critérios de aceite

- [ ] Requisito documentado: gh instalado e autenticado (gh auth login); uso de --repo quando fora do repo.
- [ ] Comandos principais documentados: gh issue, gh pr, gh pr checks, gh run list, gh run view, gh api (exemplos para PR, runs, logs falhos).
- [ ] Matriz de uso por agente: PO (backlog, Issues, Projects), Developer (PRs, Issues), Architect (revisão, merge), DevOps (repos, CI/CD), QA (checks, falhas), CyberSec (auditoria).
- [ ] Segurança: nunca expor tokens em chat/logs/repo; validação antes de executar comandos que acessam recursos externos.

## Referências

- [20-ferramenta-github-gh.md](../20-ferramenta-github-gh.md)
