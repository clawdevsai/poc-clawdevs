# [team-devs-ai] Sandbox efêmero: seccomp/eBPF (bloqueio execve e socket)

**Fase:** 2 — Segurança  
**Labels:** security, sandbox, kernel

## Descrição

Reforçar o **sandbox efêmero** (npm/pip, instalação de dependências) com **restrições a nível de kernel** no container, para neutralizar execução dinâmica de código ofuscado (eval, exec, base64 em runtime) que a análise estática (SonarQube, semgrep) e o hash SHA256 não conseguem detectar. A defesa é transferida em parte da camada de texto para o **sistema operacional**. Especificação em [05-seguranca-e-etica.md](../05-seguranca-e-etica.md) (seção 1.3 — Restrições a nível de kernel no sandbox) e [14-seguranca-runtime-agentes.md](../14-seguranca-runtime-agentes.md).

## Critérios de aceite

- [ ] **Container do sandbox efêmero** (usado para `npm install`, `pip install` e instalação de dependências) configurado com **perfil seccomp** ou regras **eBPF** no Kubernetes (ou runtime equivalente).
- [ ] **Bloqueio de `execve`:** durante a **fase crítica** (janela em que o script de instalação — ex.: npm ou pip — está rodando dentro do sandbox), bloquear a syscall **`execve`** para processos filhos não autorizados (whitelist explícita: ex.: apenas binário do npm/pip e dependências conhecidas). Se script ofuscado tentar chamar binário para rodar payload, o kernel encerra o processo.
- [ ] **Bloqueio de `socket`:** durante a mesma fase de instalação de dependências, bloquear a syscall **`socket`** — impede comunicações maliciosas IPC ou preparação de rede; kernel retorna permission denied.
- [ ] Documentação em [05-seguranca-e-etica.md](../05-seguranca-e-etica.md) e [14-seguranca-runtime-agentes.md](../14-seguranca-runtime-agentes.md) reflete as regras (já atualizada; validar consistência com implementação).

## Implementação (início Fase 2)

- **Perfil seccomp** que bloqueia syscalls de **rede** (socket, connect, bind, listen, accept, sendto, recvfrom, etc.): [k8s/sandbox/seccomp-install-sandbox.json](../../k8s/sandbox/seccomp-install-sandbox.json). Instalar no nó em `/var/lib/kubelet/seccomp/`.
- **Job template** do sandbox efêmero: [k8s/sandbox/job-install-sandbox.yaml](../../k8s/sandbox/job-install-sandbox.yaml). Uso: orquestrador cria Job sob demanda para `npm install`/`pip install`; resultado em volume temporário, quarentena de disco antes de transferir ao repo.
- **Bloqueio de execve** para processos não autorizados (whitelist de binários) exige perfil por processo ou configuração no nó; documentado em [k8s/sandbox/README.md](../../k8s/sandbox/README.md).

## Referências

- [05-seguranca-e-etica.md](../05-seguranca-e-etica.md) (seção 1.3 — Restrições a nível de kernel no sandbox)
- [14-seguranca-runtime-agentes.md](../14-seguranca-runtime-agentes.md) (sandbox efêmero, regra de execução de código de terceiros)
- [024-skills-terceiros-checklist-egress.md](024-skills-terceiros-checklist-egress.md) (skills de terceiros, zero binários)
