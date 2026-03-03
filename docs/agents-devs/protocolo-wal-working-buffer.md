# Protocolo WAL e Working Buffer

Referência operacional para **persistência de contexto** (Fase 5, issue 051). Detalhes em [13-habilidades-proativas.md](../13-habilidades-proativas.md) e [28-memoria-longo-prazo-elite.md](../28-memoria-longo-prazo-elite.md).

---

## Regra de ouro

> **O histórico de chat é buffer, não armazenamento. O que importa deve ser escrito agora — não "depois".**

Comunicar aos agentes (SOUL/AGENTS): antes de responder, verificar gatilhos WAL; a partir de ~60% de contexto, manter Working Buffer atualizado; após compactação, recuperar lendo buffer + SESSION-STATE.

---

## 1. Gatilhos WAL (Write-Ahead Log)

Em **toda mensagem**, antes de responder, verificar se a mensagem do usuário contém:

| Gatilho | Exemplo | Ação |
|--------|---------|------|
| **Correções** | "é X, não Y", "na verdade...", "quis dizer..." | Escrever em SESSION-STATE.md → depois responder |
| **Nomes próprios** | Empresas, produtos, pessoas, projetos | Escrever em SESSION-STATE.md → depois responder |
| **Preferências** | Cores, estilos, abordagens, ferramentas | Escrever em SESSION-STATE.md → depois responder |
| **Decisões** | "vamos com X", "usar Y", "não fazer Z" | Escrever em SESSION-STATE.md → depois responder |
| **Rascunhos** | Alterações em texto/código que o usuário propõe | Escrever em SESSION-STATE.md → depois responder |
| **Valores concretos** | Números, datas, IDs, URLs, prazos | Escrever em SESSION-STATE.md → depois responder |

Se **nenhum** gatilho for detectado, pode responder diretamente. Se **algum** for detectado: **Parar → Escrever SESSION-STATE.md → Responder**.

---

## 2. Fluxo WAL

1. **Parar** — não começar a responder ainda.
2. **Escrever** — atualizar `SESSION-STATE.md` com o detalhe (correção, nome, preferência, decisão, valor).
3. **Depois** — responder ao humano.

O detalhe parece óbvio no contexto; quando o contexto for truncado, só o que estiver em arquivo permanece.

---

## 3. Working Buffer (zona entre 60% e compactação)

- **Arquivo:** `memory/working-buffer.md` no workspace.
- **Quando atualizar:** A cada troca (mensagem do humano + resumo da resposta do agente) **após** o uso de contexto atingir ~60% (quando houver indicador de sessão).
- **Formato sugerido:** timestamp, mensagem humana, resumo da resposta do agente (1–2 frases + detalhes chave).
- **Uso:** Conteúdo usado para **recuperação pós-compactação** (ler antes de continuar).

---

## 4. Recuperação pós-compactação

Acionar quando:

- A sessão começa com tag `<summary>` ou menção a "truncado", "limite de contexto".
- O humano pergunta "onde paramos?", "continue", "o que estávamos fazendo?".
- O agente deveria saber algo mas não tem no contexto atual.

**Passos:**

1. Ler `memory/working-buffer.md`.
2. Ler `SESSION-STATE.md`.
3. Extrair e consolidar em `SESSION-STATE.md` o que for relevante; só então continuar a conversa.

---

## 5. Integração com gancho de validação de contexto

**Antes** da sumarização na nuvem, o gancho local ([context_validation_hook.py](../../scripts/context_validation_hook.py)) pode varrer o buffer de trabalho em busca de **intenções do usuário ou regras informais que não ganharam tag**. Se achar algo crítico, propõe extração para o **Session State** (SESSION-STATE.md).

- Uso: `CONTEXT_VALIDATION_HOOK_ENABLED=1 python context_validation_hook.py --buffer-file path/to/buffer.md [--session-state path/to/SESSION-STATE.md]`
- Ref: [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md), [28-memoria-longo-prazo-elite.md](../28-memoria-longo-prazo-elite.md).

---

## Referências

- [13-habilidades-proativas.md](../13-habilidades-proativas.md) — Pilares persistente e proativo; WAL; Working Buffer.
- [28-memoria-longo-prazo-elite.md](../28-memoria-longo-prazo-elite.md) — Seis camadas; Hot RAM (SESSION-STATE); working-buffer.
- [SESSION-STATE.example.md](SESSION-STATE.example.md) — Template de estado da sessão e invariantes.
