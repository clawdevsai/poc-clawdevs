# docs/agents-devs — Índice e navegação

Documentos operacionais para agentes: templates, protocolos, checklists e referências de implementação. A **árvore de decisão** completa (qual doc usar para cada tipo de pergunta) está em [18-expertise-documentacao.md](../18-expertise-documentacao.md).

---

## Fluxo: identificar → buscar → ler → citar

1. **Identificar a necessidade** — Usar a árvore de decisão em [18-expertise-documentacao.md](../18-expertise-documentacao.md) (§1).
2. **Buscar** — Se não tiver certeza do doc: grep ou busca por palavra-chave em `docs/` e `docs/agents-devs/`.
3. **Ler o doc** indicado (ou o mais relevante).
4. **Responder** com base no conteúdo e **citar o documento** (ex.: *"Conforme [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md), o pipeline..."*).

**Regra:** Não afirmar "não tenho essa informação" sem ter buscado na documentação do projeto. Integrar em SOUL/TOOLS/AGENTS: *"Antes de afirmar que não tem a informação, buscar em docs/ e docs/agents-devs e citar a fonte."*

---

## Índice por tema (agents-devs)

| Tema | Documento | Uso |
|------|-----------|-----|
| **Estado da sessão** | [SESSION-STATE.example.md](SESSION-STATE.example.md) | Template SESSION-STATE; invariantes de negócio (tag). |
| **Critérios de aceite** | [CRITERIOS_ACEITE-example.md](CRITERIOS_ACEITE-example.md) | Exemplo de critérios com tag de proteção. |
| **Memória (seis camadas)** | [memoria-elite-seis-camadas-implementacao.md](memoria-elite-seis-camadas-implementacao.md) | Mapeamento camadas → scripts e docs. |
| **WAL e Working Buffer** | [protocolo-wal-working-buffer.md](protocolo-wal-working-buffer.md) | Gatilhos WAL, fluxo, recuperação pós-compactação. |
| **Interação entre agentes** | [interacao-agentes-mensageria.md](interacao-agentes-mensageria.md) | Um OpenClaw; mensageria = gatilho; conversa compartilhada no canal/thread; um agente por vez; nunca DM entre agentes. |
| **Habilidades proativas e heartbeat** | [habilidades-proativas-heartbeat-implementacao.md](habilidades-proativas-heartbeat-implementacao.md) | Proativo, persistente, FinOps, ADL/VFM, checklist heartbeat. |
| **Escrita humanizada** | [escrita-humanizada-checklist.md](escrita-humanizada-checklist.md) | Checklist padrões de IA; revisar texto antes de enviar. |
| **MEMORY (decisões por omissão)** | [MEMORY.md](MEMORY.md) | Registro de aprovações por omissão cosmética. |
| **QA auditor** | [QA-AUDITOR-INSTRUCOES.md](QA-AUDITOR-INSTRUCOES.md) | Instruções para QA (dívida técnica, áreas para auditoria). |
| **Áreas para auditoria QA** | [areas-for-qa-audit.md](areas-for-qa-audit.md) | Lista de áreas para testes exploratórios. |
| **MicroADR** | [microADR-template.json](microADR-template.json) | Template de microADR (Architect). |
| **Ferramentas (Fase 7)** | [ferramentas-fase7-referencia.md](ferramentas-fase7-referencia.md) | Mapeamento browser, summarize, gh, markitdown (070–073). |

---

## Árvore de decisão (resumo)

Para **qual doc da pasta docs/ usar** conforme a pergunta, ver [18-expertise-documentacao.md](../18-expertise-documentacao.md) §1 (ex.: config → 07, 09; troubleshooting → 06, 05; conceitos → 01–04; ferramentas → 11, 12, 20, 24, 27; segurança → 05, 14, 15, 16; escrita → 17; frontend → 23).
