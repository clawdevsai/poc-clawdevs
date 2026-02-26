---
description: Protocolos de persistência, WAL e gestão de contexto (Elite Memory).
---
# 🧠 Memória e Persistência (Elite Memory)

- **Protocolo WAL (Write-Ahead Log):**
    - Decisões, preferências do usuário, nomes de projetos e correções devem ser registrados em `SESSION-STATE.md` ANTES de qualquer resposta final ser enviada.
    - O histórico de chat é volátil; o workspace (arquivos `.md`) é a memória real.
- **Higiene de Contexto:**
    - Respeite o truncamento na borda.
    - **Invariantes de Negócio** (regras absolutas) e **MicroADRs** devem ser marcados com tags de proteção (`<!-- PROTECTED -->`) para evitar sumarização ou perda em processos de compactação.
- **MicroADRs Obrigatórios:**
    - Ao aprovar um PR, o Architect deve gerar um registro JSON estrito detalhando a decisão.
    - Inclua auditoria de desvio (ADL) para rejeitar justificativas vagas como "parece melhor" via análise de regex.
- **TTL de Memória Quente:** As chaves de conversas ativas no Redis devem ter expiração automática (TTL) para evitar o acúmulo de "lixo digital" e estouro de RAM.
- **RAG de Longo Prazo:** Utilize a `Warm Store` (LanceDB) para recuperar conceitos consolidados de sessões passadas em vez de reler logs brutos.
