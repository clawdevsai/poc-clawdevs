# [team-devs-ai] Ferramenta GitHub (gh CLI) para agentes

**Fase:** 7 — Ferramentas  
**Labels:** tooling, github

## Descrição

Integrar o uso do GitHub CLI (gh) pelos agentes: Issues, PRs, status de CI (gh pr checks, gh run list/view), gh api para consultas avançadas. PO, Developer, Architect, DevOps, QA e CyberSec. Nunca expor tokens; Zero Trust e validação em runtime.

## Critérios de aceite

- [x] Requisito documentado: gh instalado e autenticado (gh auth login); uso de --repo quando fora do repo. **Ref:** [20-ferramenta-github-gh.md](../20-ferramenta-github-gh.md) § Requisito.
- [x] Comandos principais documentados: gh issue, gh pr, gh pr checks, gh run list, gh run view, gh api (exemplos para PR, runs, logs falhos). **Ref:** Doc 20 § Pull Requests (checks, run list, run view, --log-failed), API, Saída JSON.
- [x] Matriz de uso por agente: PO (backlog, Issues, Projects), Developer (PRs, Issues), Architect (revisão, merge), DevOps (repos, CI/CD), QA (checks, falhas), CyberSec (auditoria). **Ref:** Doc 20 § Quem pode usar (tabela).
- [x] Segurança: nunca expor tokens em chat/logs/repo; validação antes de executar comandos que acessam recursos externos. **Ref:** Doc 20 § Segurança; [05-seguranca-e-etica.md](../05-seguranca-e-etica.md), [14-seguranca-runtime-agentes.md](../14-seguranca-runtime-agentes.md).

## Referências

- [20-ferramenta-github-gh.md](../20-ferramenta-github-gh.md)
