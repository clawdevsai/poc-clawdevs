---
description: Padrões de escrita, manutenção de código, documentação e testes.
---
# ✍️ Qualidade e Manutenção (Code Standards)

- **KISS e SOLID:**
    - Escreva código denso e performático, mas evite abstrações desnecessárias.
    - Se uma função puder ser pura, ela DEVE ser pura.
    - Evite estados globais; utilize o Redis para persistência de estado entre agentes.
- **Escrita Humanizada:**
    - NUNCA utilize clichês de IA (ex: "Certamente!", "Como um modelo de linguagem...", "Espero que ajude").
    - Documentações e comentários devem ter voz direta, técnica e executiva.
- **Testing First:**
    - NUNCA reporte uma tarefa como "concluída" sem validação ponta a ponta no sandbox.
    - O Architect deve recusar terminantemente qualquer PR com cobertura inferior a 80%.
- **Documentação como Única Fonte da Verdade:**
    - O primeiro passo de qualquer tarefa é consultar a pasta `docs/`.
    - Se a documentação estiver desatualizada, a primeira tarefa é atualizar o documento antes de tocar no código.
- **Manutenibilidade:**
    - Código que "funciona mas é confuso" é considerado bloqueio técnico.
    - Priorize a legibilidade para outros agentes e para o Diretor humano.

## 🚫 Restrições de Papel (Manutenção)
- **Architect:** NUNCA altera código diretamente. Sua função é ser o juiz de qualidade.
- **CEO/PO:** NUNCA escrevem código técnico. Focam em Visão, Valor e Backlog.
- **DBA:** NUNCA permite schemas que degradem a performance de hardware (full table scans, falta de índices).
