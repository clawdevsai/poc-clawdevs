# Criação de skills

Os agentes do enxame têm a habilidade de **criar e evoluir skills** que estendem capacidades de agentes com conhecimento especializado, fluxos de trabalho e integrações. Este documento consolida princípios, anatomia e processo de criação de skills, para uso quando não existir skill no ecossistema e a necessidade for recorrente (ver [19-descoberta-instalacao-skills.md](19-descoberta-instalacao-skills.md)) ou quando o Diretor solicitar uma skill nova.

**Segurança:** Skills criadas internamente seguem a mesma postura Zero Trust ao serem compartilhadas ou instaladas em outros ambientes. Não incluir comandos suspeitos, exfiltração ou dependências não verificadas. Ver [05-seguranca-e-etica.md](05-seguranca-e-etica.md) e [14-seguranca-runtime-agentes.md](14-seguranca-runtime-agentes.md).

---

## Quando usar esta habilidade

Usar quando:

- Não foi encontrada skill no ecossistema para a tarefa e a necessidade é recorrente ([19-descoberta-instalacao-skills.md](19-descoberta-instalacao-skills.md)); registrar em `.learnings/FEATURE_REQUESTS.md` conforme [10-self-improvement-agentes.md](10-self-improvement-agentes.md) e propor criação de skill.
- O Diretor ou o time pede explicitamente para criar ou atualizar uma skill para um domínio (ex.: fluxo interno, template, integração com API).
- Uma capacidade documentada em `.learnings/` ou em FEATURE_REQUESTS se repete e justifica um pacote reutilizável.

Não usar para substituir documentação já consolidada nesta pasta (ex.: expertise em documentação, escrita humanizada, frontend design, memória de longo prazo); usar para **novas** capacidades que se beneficiem de um pacote modular (scripts, referências, templates).

---

## O que uma skill oferece

1. **Fluxos especializados** — Procedimentos multi-etapa para um domínio.
2. **Integração com ferramentas** — Instruções para formatos de arquivo ou APIs.
3. **Expertise de domínio** — Conhecimento específico, schemas, regras de negócio.
4. **Recursos empacotados** — Scripts, referências e assets para tarefas complexas ou repetitivas.

---

## Princípios

### Concisão

O contexto é compartilhado com o resto da sessão. Incluir só o que o agente não sabe. Preferir exemplos curtos a explicações longas.

### Grau de liberdade

- **Alta liberdade (texto):** Várias abordagens válidas; decisões dependem do contexto.
- **Média (pseudocódigo/scripts parametrizados):** Padrão preferido com alguma variação.
- **Baixa (scripts específicos):** Operações frágeis; consistência crítica.

### Anatomia de uma skill

Toda skill tem um arquivo obrigatório **SKILL.md** e recursos opcionais:

```
skill-name/
├── SKILL.md (obrigatório)
│   ├── Frontmatter YAML: name, description (obrigatórios)
│   └── Corpo em Markdown: instruções de uso
└── Recursos opcionais
    ├── scripts/     — Código executável (Python/Bash etc.)
    ├── references/  — Documentação carregada no contexto quando necessário
    └── assets/      — Arquivos usados no resultado (templates, ícones, fontes)
```

- **SKILL.md:** Frontmatter com `name` e `description` (são usados para decidir quando a skill é acionada). No corpo: instruções e referências a scripts/references/assets.
- **scripts/:** Quando a mesma operação é reescrita muitas vezes ou exige determinismo; podem ser executados sem carregar no contexto.
- **references/:** Documentação, schemas, políticas; manter SKILL.md enxuto e referenciar aqui; evitar duplicar informação entre SKILL.md e references.
- **assets/:** Templates, imagens, boilerplate; não precisam ser carregados no contexto.

Não incluir em uma skill: README.md, INSTALLATION_GUIDE.md, CHANGELOG.md ou outros arquivos auxiliares; apenas o necessário para o agente executar a tarefa.

### Disclosure progressivo

1. **Metadados (name + description)** — Sempre em contexto.
2. **Corpo do SKILL.md** — Quando a skill dispara.
3. **Recursos (scripts/references/assets)** — Conforme o agente precisar.

Manter o corpo do SKILL.md essencial e sob ~500 linhas; conteúdo longo em arquivos em `references/` com referência clara no SKILL.md.

---

## Processo de criação (6 passos)

1. **Entender a skill com exemplos** — O que a skill deve fazer? Quais pedidos do usuário acionam ela? Definir casos de uso concretos.
2. **Planejar conteúdos reutilizáveis** — Para cada caso: que scripts, referências e assets ajudam? Listar scripts/, references/, assets/.
3. **Inicializar a skill** — Criar a pasta e estrutura. Usar `npx skills init <nome-skill>` quando disponível no ecossistema, ou criar manualmente: diretório, SKILL.md com frontmatter (name, description) e seções TODO, pastas scripts/, references/, assets/.
4. **Editar a skill** — Implementar primeiro os recursos (scripts, references, assets); testar scripts. Depois escrever o SKILL.md: descrição completa no frontmatter (incluir “quando usar”); corpo em imperativo/infinitivo; referências a workflows e padrões de saída quando aplicável.
5. **Empacotar (quando aplicável)** — Se o ecossistema tiver ferramenta de empacotamento (ex.: gerar .skill), validar (frontmatter, estrutura, descrição) e gerar o pacote. Caso contrário, a skill pode ser usada como pasta.
6. **Iterar** — Usar em tarefas reais; registrar falhas ou melhorias em .learnings/ e ajustar SKILL.md e recursos.

---

## Padrões úteis

### Fluxos (references/workflows)

- **Sequencial:** Listar passos claros no SKILL.md (ex.: analisar → mapear → validar → executar → verificar).
- **Condicional:** Definir pontos de decisão (ex.: “criar novo” vs “editar existente”) e encaminhar para subfluxos.

### Padrões de saída (references/output-patterns)

- **Template:** Para formato fixo (relatórios, APIs), definir estrutura exata no SKILL.md.
- **Exemplos:** Incluir pares entrada/saída quando a qualidade depende de estilo (ex.: mensagens de commit, resumos).

---

## Integração com .learnings/FEATURE_REQUESTS.md

Quando uma capacidade solicitada pelo usuário não existir no ecossistema e a necessidade for **recorrente**, registrar em `.learnings/FEATURE_REQUESTS.md` conforme [10-self-improvement-agentes.md](10-self-improvement-agentes.md). Itens recorrentes em FEATURE_REQUESTS são candidatos a virar skill: seguir o processo de 6 passos deste documento e alinhar com o Diretor antes de criar. A descoberta de skills ([19-descoberta-instalacao-skills.md](19-descoberta-instalacao-skills.md)) deve ser tentada primeiro; só propor criação quando não houver skill disponível.

---

## Quem pode usar

| Agente   | Criar/editar skill | Propor ao Diretor | Publicar/instalar |
|----------|--------------------|-------------------|--------------------|
| **CEO**  | Sim (visão de produto) | Sim | Não |
| **PO**   | Sim (fluxos, backlog) | Sim | Não |
| **Architect** | Sim (padrões, ADRs) | Sim | Não — aprovação técnica |
| **Developer** | Sim (scripts, integrações) | Sim | Não — depende de aprovação |
| **DevOps** | Sim (infra, CI) | Sim | Sim, apenas após aprovação e checklist |
| **QA**   | Sim (testes, E2E) | Sim | Não |
| **CyberSec** | Sim (segurança, conformidade) | Sim | Não — validar conteúdo |
| **UX**   | Sim (design, acessibilidade) | Sim | Não |

Publicar ou instalar skill em ambiente compartilhado segue o mesmo fluxo de [19-descoberta-instalacao-skills.md](19-descoberta-instalacao-skills.md) (Zero Trust, aprovação do Diretor).

---

## Relação com a documentação

- [19-descoberta-instalacao-skills.md](19-descoberta-instalacao-skills.md) — Quando não houver skill no ecossistema, propor criação e usar este doc.
- [10-self-improvement-agentes.md](10-self-improvement-agentes.md) — Registrar em FEATURE_REQUESTS quando a capacidade for solicitada; criação de skill é uma resolução possível.
- [05-seguranca-e-etica.md](05-seguranca-e-etica.md) — Zero Trust e checklist para skills de terceiros; skills internas também devem ser revisadas antes de distribuição.
- [14-seguranca-runtime-agentes.md](14-seguranca-runtime-agentes.md) — Validar comandos e paths em scripts incluídos na skill.
