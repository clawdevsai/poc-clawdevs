# Habilidades proativas e heartbeat — Implementação (053)

Referência operacional dos **três pilares** (Proativo, Persistente, Autoaprimoramento), **heartbeat** e **ADL/VFM quantitativos**. Detalhes em [13-habilidades-proativas.md](../13-habilidades-proativas.md) e [06-operacoes.md](../06-operacoes.md).

---

## 1. Proativo

| Requisito | Onde está |
|-----------|-----------|
| Diretrizes "o que ajudaria o Diretor?" e reverse prompting | [13-habilidades-proativas.md](../13-habilidades-proativas.md) §1 — Antecipar necessidades, reverse prompting, check-ins úteis |
| Guardrail: nada para fora sem aprovação | Doc 13 §1 — "Construir proativamente **dentro** do workspace; **nada** vai para fora (e-mail, publicar, push em produção) sem aprovação explícita" |

---

## 2. Persistente

Integrado com WAL e Working Buffer (issue 051) e memória Elite (052).

| Artefato | Referência |
|----------|------------|
| WAL e Working Buffer | [protocolo-wal-working-buffer.md](protocolo-wal-working-buffer.md), [051-protocolo-wal-working-buffer.md](../issues/051-protocolo-wal-working-buffer.md) |
| Memória Elite (seis camadas) | [memoria-elite-seis-camadas-implementacao.md](memoria-elite-seis-camadas-implementacao.md), [052-memoria-elite-seis-camadas.md](../issues/052-memoria-elite-seis-camadas.md) |

---

## 3. Resourcefulness com diversidade obrigatória

Se a **mesma ferramenta** falhar **2x consecutivas** pelo **mesmo motivo**, o orquestrador **bloqueia essa ferramenta** no escopo da tarefa; o agente é forçado a mudar vetor (CLI, API, outra skill).

- **Doc:** [13-habilidades-proativas.md](../13-habilidades-proativas.md) §3 (Resourcefulness), [06-operacoes.md](../06-operacoes.md) (regras de orquestração).
- **Implementação:** política no orquestrador (contador de falhas por ferramenta/motivo por tarefa); quando atingir 2, bloquear ferramenta no escopo e forçar alternativas.

---

## 4. Persistência ↔ FinOps

Contador de tentativas integrado ao **Gateway FinOps**: no pre-flight, custo estimado × número da tentativa (penalidade progressiva). Ao atingir gatilho (ex.: comprometer cota diária restante), orquestrador **interrompe** a tarefa, **devolve ao backlog do PO** e **libera travas de hardware** (GPU).

- **Doc:** [06-operacoes.md](../06-operacoes.md) — "Persistência acoplada ao FinOps"; [13-habilidades-proativas.md](../13-habilidades-proativas.md) §3 "Integração persistência ↔ FinOps"; [10-self-improvement-agentes.md](../10-self-improvement-agentes.md).
- **Implementação:** Gateway/orquestrador aplica multiplicador (tentativa N) no pre-flight de custo; quando projeção > limite, interromper e devolver ao PO.

---

## 5. Autoaprimoramento: verificação antes de reportar (VBR)

"Não reportar 'pronto' sem verificação ponta a ponta." Código existe ≠ funcionalidade funciona.

- **Doc:** [13-habilidades-proativas.md](../13-habilidades-proativas.md) §3 "Verificar antes de reportar (VBR)".
- Incluir em SOUL/AGENTS: antes de dizer "feito"/"completo", testar do ponto de vista do usuário.

---

## 6. Heartbeat (check-in periódico)

Check-in periódico (ex.: CyberSec verifica padrões de injeção); uso produtivo do tempo em cada poll.

- **Checklist completo:** [13-habilidades-proativas.md](../13-habilidades-proativas.md) §4 "Heartbeat (checklist periódico)" — Comportamento proativo, Segurança (varredura injeção, integridade comportamental), Self-healing, Memória (% contexto, MEMORY.md, higiene), Surpresa proativa, Auto-atualização do ambiente.
- **Crons:** Doc 13 §5 — `systemEvent` vs `isolated agentTurn`; para checagens em background usar `isolated agentTurn`.

---

## 7. ADL/VFM quantitativos

| Guardrail | Onde está | Implementação |
|-----------|-----------|----------------|
| **VFM (fitness function)** | [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md), [05-seguranca-e-etica.md](../05-seguranca-e-etica.md) | Artefato estruturado (ex.: vfmscore.json) com variáveis numéricas; limite no Gateway bloqueia na borda. **CEO:** fitness no raciocínio (VFM_CEO_score.json), descarta evento se threshold negativo antes de enviar — [soul/CEO.md](../soul/CEO.md), issue 129. |
| **ADL (auditoria de desvio)** | [13-habilidades-proativas.md](../13-habilidades-proativas.md) §3, [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) §2.3, [05-seguranca-e-etica.md](../05-seguranca-e-etica.md) | microADR com seção de auditoria; **regex** contra lista negra de justificativas fracas; rejeição em tempo de execução. Script: [microadr_generate.py](../../scripts/microadr_generate.py); slot_revisao_pos_dev gera ao aprovar. |

---

## 8. Checklist de migração de ferramentas

Ao descontinuar ou trocar uma ferramenta:

- [ ] Crons — atualizar prompts que citam a ferramenta antiga.
- [ ] Scripts em `scripts/`.
- [ ] Docs: TOOLS.md, HEARTBEAT.md, AGENTS.md.
- [ ] Skills que a referenciem.
- [ ] Templates e exemplos de config.
- [ ] Rotinas diárias e heartbeats.

Após migração: executar o comando antigo (deve falhar ou estar indisponível); executar o novo (deve funcionar); verificar no próximo cron que o novo fluxo está em uso.

**Fonte:** [13-habilidades-proativas.md](../13-habilidades-proativas.md) §3 "Checklist de migração de ferramentas".

---

## Referências rápidas

| Tema | Doc principal |
|------|----------------|
| Pilares e heartbeat | [13-habilidades-proativas.md](../13-habilidades-proativas.md) |
| FinOps, contador tentativas, degradação | [06-operacoes.md](../06-operacoes.md) |
| Self-improvement, .learnings | [10-self-improvement-agentes.md](../10-self-improvement-agentes.md) |
| Gateway, perfis, truncamento | [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) |
| Zero Trust, segurança | [05-seguranca-e-etica.md](../05-seguranca-e-etica.md) |

Ref: [issues/053-habilidades-proativas-heartbeat.md](../issues/053-habilidades-proativas-heartbeat.md).
