# Sandbox seccomp/eBPF (028) — Implementação

**Container do sandbox com perfil seccomp:** O Job do sandbox efêmero está configurado com `securityContext.seccompProfile` (tipo `Localhost`, perfil `seccomp-install-sandbox.json`). O perfil deve estar instalado no nó em `/var/lib/kubelet/seccomp/`. Ref: [k8s/sandbox/job-install-sandbox.yaml](../../k8s/sandbox/job-install-sandbox.yaml), [k8s/sandbox/README.md](../../k8s/sandbox/README.md).

**Bloqueio de `socket`:** O perfil [seccomp-install-sandbox.json](../../k8s/sandbox/seccomp-install-sandbox.json) bloqueia as syscalls de rede: `socket`, `connect`, `bind`, `listen`, `accept`, `accept4`, `sendto`, `recvfrom`, `send`, `recv`, `sendmsg`, `recvmsg` (ação `SCMP_ACT_ERRNO`). Durante a fase de instalação (npm/pip) no sandbox, o kernel nega essas syscalls — impede comunicações maliciosas e exfiltração.

**Bloqueio de `execve`:** Bloquear `execve` para processos não autorizados exige whitelist por binário (ex.: permitir apenas o binário do npm/pip e dependências conhecidas). Isso é configurável no nó (perfil por processo ou eBPF) ou com perfil seccomp mais complexo. Documentado em [k8s/sandbox/README.md](../../k8s/sandbox/README.md): "Bloqueio de execve para processos não autorizados (whitelist de binários) exige perfil por processo ou configuração no nó". A mitigação de rede (bloqueio de socket) já está implementada no perfil atual.

**Documentação:** [05-seguranca-e-etica.md](../05-seguranca-e-etica.md) §1.3 e [14-seguranca-runtime-agentes.md](../14-seguranca-runtime-agentes.md) descrevem as regras do sandbox e a consistência com este perfil.

Ref: [028-sandbox-seccomp-ebpf-kernel.md](028-sandbox-seccomp-ebpf-kernel.md).
