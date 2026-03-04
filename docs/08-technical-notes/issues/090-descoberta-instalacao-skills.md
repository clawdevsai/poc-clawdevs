# [team-devs-ai] Descoberta e instalação de skills (Zero Trust)

**Fase:** 8 — Skills e ambiente  
**Labels:** skills, security

## Descrição

Buscar skills no ecossistema (Skills CLI, skills.sh); apresentar opções ao Diretor; instalar somente após checklist de segurança e aprovação (Zero Trust). Nenhuma skill de terceiros instalada sem verificação. **Verificação criptográfica na borda:** manifesto de hash **SHA-256** obrigatório (`skillstracelock.json`); roteador OpenClaw (ou pipeline de borda) rejeita automaticamente qualquer download cujo hash não bata 100%. **Zero binários:** todas as skills devem ser script em texto claro (Python, Bash, etc.); pacotes pré-compilados proibidos.

## Critérios de aceite

- [ ] **Manifesto SHA-256:** fluxo exige `skillstracelock.json`; roteador/CI rejeita download com hash não batente (silenciosamente, sem depender de LLM).
- [ ] **Zero binários:** regra documentada — skills apenas em texto claro; Architect e DevOps rejeitam binários/pré-compilados.
- [ ] Fluxo documentado: buscar skills (Skills CLI ou skills.sh) → listar opções ao Diretor → checklist de segurança (origem, revisão SKILL.md, comandos suspeitos, hash, zero binários) → aprovação explícita → instalação.
- [ ] Checklist alinhado a 05-seguranca (skills de terceiros) e 024 (checklist egress).
- [ ] Regra: em dúvida, pedir aprovação ao Diretor; nunca instalar sem passar pelo checklist.
- [ ] Integração com 02-agentes: "descoberta e instalação de skills quando relevante" aplicável a todos os agentes.

## Referências

- [19-descoberta-instalacao-skills.md](../../05-tools-and-skills/19-descoberta-instalacao-skills.md)

## Verificação (Fase 8)

- Fluxo buscar → apresentar → checklist → aprovação → instalar: documentado em [19-descoberta-instalacao-skills.md](../../05-tools-and-skills/19-descoberta-instalacao-skills.md) (§ Fluxo).
- Integração com FEATURE_REQUESTS: doc 19 referencia registro em `.learnings/FEATURE_REQUESTS.md` e criação de skills ([29-criacao-de-skills.md](../../05-tools-and-skills/29-criacao-de-skills.md)); [10-self-improvement-agentes.md](../../03-agents/10-self-improvement-agentes.md) define quando registrar.
- Referência em SOUL: todos os agentes em [soul/](../../03-agents/soul/) referenciam descoberta e instalação (19) e criação (29).
