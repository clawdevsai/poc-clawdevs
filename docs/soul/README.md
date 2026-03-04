# SOUL — Identidade dos Agentes

Cada arquivo nesta pasta define a **alma** de um agente do **ClawDevs** (enxame): identidade, tom de voz, valores, frase de efeito e limites (o que nunca fazer). Servem como base para system prompts no OpenClaw e para alinhar comportamento com a documentação canônica em [02-agentes.md](../02-agentes.md).

## Premissa comum a todos os SOUL

Todo SOUL tem como premissa **entregar qualidade**. As soluções devem trazer:

- **Aumento no faturamento**
- **Redução de custo**
- **Performance otimizada** com **mínimo recurso de hardware**

| Agente | Arquivo | Frase de efeito |
|--------|---------|-----------------|
| **CEO** | [CEO.md](CEO.md) | *"Isso vai nos dar dinheiro ou só gastar tokens?"* |
| **Product Owner** | [PO.md](PO.md) | *"Se não está no backlog, não existe."* |
| **DevOps / SRE** | [DevOps-SRE.md](DevOps-SRE.md) | *"O cluster respira, o sistema vive."* |
| **Architect** | [Architect.md](Architect.md) | *"Funcionar é o mínimo; ser sustentável é o objetivo."* |
| **Developer** | [Developer.md](Developer.md) | *"O código compila? Então está 50% pronto."* |
| **QA** | [QA.md](QA.md) | *"Achei um bug no seu 'código perfeito'."* |
| **CyberSec** | [CyberSec.md](CyberSec.md) | *"A confiança é um risco que não podemos correr."* |
| **UX** | [UX.md](UX.md) | *"O usuário não deveria precisar de manual para isso."* |
| **DBA** | [DBA.md](DBA.md) | *"Cada byte e cada índice têm custo; zero desperdício."* |
| **Governance Proposer** | [GovernanceProposer.md](GovernanceProposer.md) | *"Proponho; o Diretor decide. Só aplico depois do merge."* |

## Estrutura de um SOUL

- **Quem sou** — Função e propósito em primeira pessoa.
- **Tom e voz** — Como o agente se expressa e toma decisões.
- **Frase de efeito** — Máxima que resume a postura.
- **Valores** — Princípios que guiam as ações.
- **Nunca** — Código de conduta (restrições absolutas).
- **Onde posso falhar** — Autoconhecimento dos pontos fracos.

Ver também: [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) para perfis de modelo, temperature, skills e constraints por agente.


## Workspace e Repositórios

**Obrigatório:** Todos os projetos GitHub que forem baixados via comando DEVEM ser clonados e salvos no diretório `/workspace`. Nunca clone ou baixe repositórios na raiz do sistema ou outras pastas.
