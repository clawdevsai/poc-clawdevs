# Balanceamento dinâmico GPU/CPU e evict gracioso

Evolução **adicional** ao GPU Lock e à [estrategia-uso-hardware-gpu-cpu.md](estrategia-uso-hardware-gpu-cpu.md): balanceamento dinâmico de cargas, **PriorityClasses** para evict gracioso e referência ao **roteamento hierárquico** (nuvem → GPU → CPU) e ao **estado no LanceDB** quando a fila for pausada por saturação. Esta documentação reduz a dependência do [06-operacoes.md](../07-operations/06-operacoes.md) (manual de primeiros socorros) ao permitir que o cluster reaja automaticamente a pico térmico ou carga excessiva. Ref: [122-balanceamento-dinamico-gpu-cpu.md](../08-technical-notes/issues/122-balanceamento-dinamico-gpu-cpu.md).

---

## O que já está na Phase 0 (006, 004)

- **TTL dinâmico** por payload/linhas no GPU Lock; **node selectors** para DevOps/UX em CPU (sem GPU).
- **Validação pré-GPU em CPU** (SLM: sintaxe, lint, SOLID) e **batching de PRs** — reduzem carga na GPU e contenção no lock.
- Ver [006-gpu-lock-script.md](../08-technical-notes/issues/006-gpu-lock-script.md), [estrategia-uso-hardware-gpu-cpu.md](estrategia-uso-hardware-gpu-cpu.md).

---

## Balanceamento dinâmico (tarefas leves em CPU)

- **Objetivo:** Tarefas menos intensivas (ex.: análise de logs, checklist determinístico, revisão "leve") rodam em **modelos leves em CPU** (ex.: Phi-3 Mini), sem disputar a GPU.
- **Implementação:** Rotear pelo orquestrador ou pelo gateway: se a tarefa for classificada como "leve" (heurística por tipo de evento ou por tamanho do payload), enviar para provedor CPU-only (Ollama Phi-3 em nó com node selector `workload-type: cpu-only`). Documentação ou POC no orquestrador (config ou script que escolhe CPU vs GPU por tipo de job).
- **Efeito:** Menos contenção no GPU Lock; manual de primeiros socorros (reset GPU, driver) é acionado com menos frequência porque a GPU é usada só para trabalho pesado.

---

## Node selectors e taints (avançado)

- **Baseline:** DevOps e UX já usam node selector para CPU (006/004). Quando o cluster tiver **nós distintos** (ex.: pool GPU vs pool CPU), usar **taints e tolerations** para garantir que pods de inferência pesada não agendem em nós CPU-only e vice-versa.
- **Exemplo:** Nó GPU com `taint: nvidia.com/gpu=present:NoSchedule` e pods de inferência com toleration; nós CPU com `workload-type: cpu-only` e pods DevOps/UX/slot-leve com nodeSelector correspondente.
- Reduz necessidade de intervenção manual (evita pod em nó errado e falha em runtime).

---

## PriorityClasses (evict gracioso)

- **Objetivo:** Em **pico térmico** ou **carga excessiva**, o Kubernetes pode **evict** pods de **baixa prioridade** primeiro (evict gracioso), sem o operador precisar rodar o manual de primeiros socorros (ex.: [030-manual-primeiros-socorros-gpu.md](../08-technical-notes/issues/030-manual-primeiros-socorros-gpu.md)) para "liberar" a GPU à força.
- **Implementação:** Definir PriorityClass (ex.: `inference-low`) para jobs/pods de inferência que podem ser interrompidos (ex.: tarefas não críticas); PriorityClass alta (ex.: `inference-critical`) para o slot de revisão ou Developer ativo. Quando o kubelet ou o scheduler precisar liberar recursos, evicta os de prioridade mais baixa primeiro.
- **Documentação:** Incluir no `k8s/` (ex.: `limits.yaml` ou `priorityclass.yaml`) as classes e em quais deployments/jobs aplicá-las; referenciar neste doc.
- **Efeito:** Recuperação automática sem "manual de primeiros socorros" para evict; o manual continua válido para falha de driver ou hardware.

---

## Roteamento hierárquico e estado no LanceDB

- **Roteamento unificado (nuvem → GPU → CPU):** Conforme [22-modelos-gratuitos-openrouter-freeride.md](../07-operations/22-modelos-gratuitos-openrouter-freeride.md) e issue 093, o OpenClaw pode configurar fallbacks: nuvem primeiro, depois GPU local, por último modelo leve em CPU. Evita deadlock quando nuvem e GPU estão saturados.
- **Estado de pausa no LanceDB:** Quando a fila for **pausada por saturação** (ex.: FreeRide ou orquestrador pausa o Sessions-Spawn), o estado da conversa é **serializado e persistido no LanceDB** (warm store). Ao liberar o GPU Lock (ou recuperar capacidade), o orquestrador **recupera o estado do LanceDB** e o agente continua do ponto exato. Ver doc 22 e [093-modelos-gratuitos-openrouter-freeride.md](../08-technical-notes/issues/093-modelos-gratuitos-openrouter-freeride.md).
- **Efeito:** Menos perda de contexto e menos necessidade de "repetir do zero" após pico; reduz intervenção manual descrita no manual de operações.

---

## Como isso reduz dependência do manual 06-operacoes

| Aspecto | Sem balanceamento / PriorityClasses | Com balanceamento e evict gracioso |
|---------|-------------------------------------|-------------------------------------|
| **Pico de carga** | Operador pode precisar parar pods manualmente ou reiniciar GPU (manual primeiros socorros). | Evict gracioso remove pods de baixa prioridade; tarefas críticas seguem. |
| **Saturação nuvem + GPU** | Risco de deadlock; intervenção manual. | Roteamento hierárquico + pausa com estado no LanceDB; recuperação automática ao liberar lock. |
| **Tarefas leves** | Competem pela GPU e aumentam contenção. | Roteadas para CPU; GPU fica para trabalho pesado; menos lock e menos térmica. |

O [06-operacoes.md](../07-operations/06-operacoes.md) continua sendo a referência para **prevenção**, **hard timeout**, **recuperação** e **manual de primeiros socorros** quando falha de driver ou hardware; este doc complementa com comportamento **automático** que reduz a frequência com que o manual é necessário.

---

## Referências

- [estrategia-uso-hardware-gpu-cpu.md](estrategia-uso-hardware-gpu-cpu.md) — Estratégia base, slot único, pré-GPU, CPU.
- [03-arquitetura.md](../01-core/03-arquitetura.md), [04-infraestrutura.md](04-infraestrutura.md) — GPU Lock, node selectors, limites.
- [06-operacoes.md](../07-operations/06-operacoes.md) — Manual de operações e primeiros socorros.
- [22-modelos-gratuitos-openrouter-freeride.md](../07-operations/22-modelos-gratuitos-openrouter-freeride.md), [093-modelos-gratuitos-openrouter-freeride.md](../08-technical-notes/issues/093-modelos-gratuitos-openrouter-freeride.md) — Roteamento hierárquico e LanceDB.
- [006-gpu-lock-script.md](../08-technical-notes/issues/006-gpu-lock-script.md), [030-manual-primeiros-socorros-gpu.md](../08-technical-notes/issues/030-manual-primeiros-socorros-gpu.md) — GPU Lock e manual GPU.
