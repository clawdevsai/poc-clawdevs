# [team-devs-ai] Manual de primeiros socorros (GPU e cluster)

**Fase:** 3 — Operações  
**Labels:** ops, runbook

## Descrição

Documentar e, quando possível, automatizar o manual de primeiros socorros para quando a GPU travar ou o cluster entrar em estado zumbi. Fases: diagnóstico (nvidia-smi), reset cirúrgico (K8s: derrubar Ollama, limpar lock Redis, reiniciar device plugin), reset de driver (opção nuclear). **Recuperação padrão** é automática (checkpoint 80°C com branch efêmera de recuperação + Redis ACK + checkout limpo e Architect para conflitos quando aplicável); este manual é **exceção**.

## Critérios de aceite

- [ ] Fase 1: comandos de diagnóstico no host (nvidia-smi; se travar → Fase 3).
- [ ] Fase 2: passos para reset cirúrgico (kubectl delete pod -l app=ollama; redis-cli DEL gpu_active_lock; reiniciar nvidia-device-plugin).
- [ ] Fase 3: passos para reset de driver (minikube stop; fuser -kv /dev/nvidia*; recarregar driver se necessário).
- [ ] Documentar que a **recuperação padrão** é automática: checkpoint aos 80°C (commit em branch efêmera de recuperação via Redis), Redis Streams com ACK só após conclusão em disco, retomada com **checkout limpo** e, se houver conflito, **Architect (tarefa prioridade zero)** resolve na branch de recuperação antes de reentrega da tarefa — ver [06-operacoes.md](../06-operacoes.md). Manual (fases 1–3) é **último recurso** quando evict, balanceamento e recuperação automática não bastarem.
- [ ] Fundação (Phase 0): **TTL dinâmico** no GPU Lock e **node selectors** (DevOps/UX em CPU); preferência por evict automático e balanceamento avançado (issue 122). A recuperação e o desenho da fila consideram **validação pré-GPU em CPU** e **batching de PRs** (ver [03-arquitetura.md](../03-arquitetura.md) e [06-operacoes.md](../06-operacoes.md)). Ver [006-gpu-lock-script.md](006-gpu-lock-script.md), [03-arquitetura.md](../03-arquitetura.md).
- [ ] Referência à máquina de referência e ao script verify-machine.

## Referências

- [06-operacoes.md](../06-operacoes.md)
