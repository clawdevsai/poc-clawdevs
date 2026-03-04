# [team-devs-ai] Máquina de referência e script de verificação

**Fase:** 0 — Fundação  
**Labels:** foundation, docs, tooling

## Descrição

Garantir que qualquer desenvolvedor com hardware equivalente à máquina de referência possa replicar o ambiente team-devs-ai. Documentar as especificações verificadas e fornecer um script (ou comandos) para verificar se a máquina do usuário atende aos requisitos.

## Critérios de aceite

- [ ] Documento ou seção descrevendo a **máquina de referência**: CPU (ex.: AMD Ryzen 7 5800X, 8 cores/16 threads), GPU (ex.: NVIDIA RTX 3060 Ti 8GB, driver/CUDA), RAM (ex.: 31 GB), disco (ex.: NVMe 1TB, partição raiz com espaço livre).
- [ ] Comandos de verificação documentados: `lscpu`, `nvidia-smi`, `free -h`, `lsblk`, `df -h /`.
- [ ] Script `verify-machine.sh` (ou equivalente) que executa os comandos e exibe um resumo (OK/aviso) para CPU, GPU, RAM e disco.
- [ ] README ou doc que referencia este script e indica onde encontrar a máquina de referência (ex.: `00-objetivo-e-maquina-referencia.md`).

## Referências

- [00-objetivo-e-maquina-referencia.md](../00-objetivo-e-maquina-referencia.md)
- [scripts/verify-machine.sh](../scripts/verify-machine.sh), [scripts/verify-machine.md](../scripts/verify-machine.md)
