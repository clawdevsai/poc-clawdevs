# Sandbox efêmero para instalação de dependências (Fase 2 — 028)

Sandbox com **restrições a nível de kernel (seccomp)** para `npm install` / `pip install`: bloqueio de syscalls de **rede** (socket, connect, bind, listen, etc.) para impedir exfiltração mesmo que um pacote malicioso execute código em runtime.

## Arquivos

- **seccomp-install-sandbox.json** — Perfil seccomp que bloqueia syscalls de rede. Bloqueio de **execve** para processos não autorizados exige whitelist por binário (configuração no nó ou perfil mais complexo); este perfil cobre a mitigação de rede. Ref: [docs/issues/028-sandbox-seccomp-ebpf-kernel.md](../../docs/issues/028-sandbox-seccomp-ebpf-kernel.md).
- **job-install-sandbox.yaml** — Job template que usa o perfil. O container roda sem privilégios e com `capabilities: drop: ["ALL"]`.

## Como usar

1. **Instalar o perfil no nó** (onde o Minikube/Kubernetes roda):
   ```bash
   sudo mkdir -p /var/lib/kubelet/seccomp/
   sudo cp k8s/sandbox/seccomp-install-sandbox.json /var/lib/kubelet/seccomp/
   ```
   No Minikube: `minikube ssh` e repetir os comandos acima no nó, ou montar o arquivo via addon.

2. **Aplicar o Job** (exemplo; em produção o orquestrador cria o Job sob demanda):
   ```bash
   kubectl apply -f k8s/sandbox/job-install-sandbox.yaml
   ```

3. O **comando do container** deve ser substituído pelo script real de instalação (ex.: `npm install` ou `pip install` em diretório montado por volume temporário). O resultado permanece no volume; o orquestrador aplica quarentena de disco (diff, SAST, entropia) antes de transferir para o repositório.

## Referências

- [05-seguranca-e-etica.md](../../docs/05-seguranca-e-etica.md) § 1.3 (Restrições a nível de kernel no sandbox)
- [14-seguranca-runtime-agentes.md](../../docs/14-seguranca-runtime-agentes.md)
- [028-sandbox-seccomp-ebpf-kernel.md](../../docs/issues/028-sandbox-seccomp-ebpf-kernel.md)
