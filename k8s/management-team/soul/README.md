# SOUL — Management Team (CEO, PO)

ConfigMap **soul-management-agents**: SOUL do **CEO** e do **PO** (escopo management).

- **Escopo:** `ceo.md`, `po.md`. Fonte: [docs/soul/CEO.md](../../../docs/soul/CEO.md), [docs/soul/PO.md](../../../docs/soul/PO.md).
- **Gateway:** O deployment openclaw usa initContainer `soul-merge` para juntar este ConfigMap com `soul-development-agents` em `/workspace/soul` **e copiar `ceo.md` para `/workspace/SOUL.md`**. Não existe mais `workspace-ceo-configmap.yaml`; o SOUL do CEO vem unicamente de `soul-management-agents`.

## Checklist SOUL — 9 agentes (Minikube)

| Agente | Nome | Gênero | Arquivo | Função esperada | ConfigMap |
|--------|------|--------|---------|-----------------|-----------|
| CEO | Ricardo | H | ceo.md | Estratégia e interface com o Diretor | soul-management-agents |
| PO | Marina | M | po.md | Backlog e priorização | soul-management-agents |
| DevOps/SRE | Bruno | H | devops.md | Infraestrutura, CI/CD, governança de repositórios | soul-development-agents |
| Architect | André | H | architect.md | Governança técnica e qualidade de código | soul-development-agents |
| Developer | Lucas | H | developer.md | Implementação e codificação (Ollama + OpenCode) | soul-development-agents |
| QA | Rafael | H | qa.md | Garantia de qualidade e testes | soul-development-agents |
| CyberSec (CISO/DPO) | Diego | H | cybersec.md | Segurança da informação e conformidade | soul-development-agents |
| UX | Felipe | H | ux.md | Experiência do usuário e interface | soul-development-agents |
| DBA | Marco | H | dba.md | Governança de dados e performance de banco | soul-development-agents |

Nomes de pessoa; somente a PO (Marina) é mulher; os demais são homens. **Regra de apresentação:** Quando perguntarem "quem é você", "who are you" ou "qual seu nome", o agente responde com nome e função (ex.: "Sou o Lucas, Developer — implementação e codificação (Ollama + OpenCode).").

O initContainer `soul-merge` copia ambos os ConfigMaps para `/workspace/soul/` no pod openclaw; o gateway usa `<agentId>.md` (ex.: `developer.md`) para cada agente.

Ref: [docs/soul/README.md](../../../docs/soul/README.md), [development-team/soul/README.md](../../development-team/soul/README.md).
