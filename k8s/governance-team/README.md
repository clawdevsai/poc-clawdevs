# Governance Team — Governance Proposer

**Governance Proposer:** propõe ajustes a rules, soul, skills e configs em repositório dedicado; cria PR para o Diretor aprovar. Roda em **sessão isolada** (CronJob ou job sob demanda), **CPU apenas** (não usa GPU Lock). Provedor LLM padrão: **ollama_local** (modelo leve em CPU, ex.: qwen2.5:7b).

Provedor configurável em `clawdevs-llm-providers` (chave `agent_governance_proposer`).

Ref: [docs/35-governance-proposer.md](../docs/35-governance-proposer.md).
