# Setup completo do enxame (Pop!_OS)

Script Bash que configura o ambiente do enxame de agentes em um único fluxo: coleta de chaves (Google Gemini, Telegram), instalação de dependências, Minikube (65% dos recursos), Redis, Ollama, ambiente de transcrição de áudio e configuração do OpenClaw com canal Telegram e voz.

## Pré-requisitos

- **Sistema:** Pop!_OS 22.04/24.04 (ou outra distro Linux; o script avisa se não for Pop!_OS).
- **Execução:** Não rodar como root; executar como usuário normal com `sudo` disponível.

## O que o script faz

1. **Validação:** Verifica se não está rodando como root; opcionalmente verifica se é Pop!_OS.
2. **Chaves:** Solicita e valida **Google AI Key (Gemini)**, **Telegram Bot Token** e **Telegram Chat ID** (não aceita vazios).
3. **Sistema:** `apt update && apt upgrade`; instala curl, wget, git, python3, ffmpeg, docker, conntrack, etc.
4. **Docker:** Instala via get.docker.com se não existir; adiciona o usuário ao grupo `docker`.
5. **NVIDIA:** Se `nvidia-smi` existir, instala `nvidia-container-toolkit` e reinicia o Docker.
6. **Minikube:** Instala minikube e kubectl se não existirem.
7. **Helm:** Instala Helm se não existir.
8. **Minikube start:** Calcula 65% de CPU e RAM, inicia com driver Docker, habilita ingress e dashboard; aplica plugin NVIDIA se houver GPU.
9. **Redis:** Helm repo bitnami; instala Redis em modo standalone, sem auth, sem persistência.
10. **Ollama:** Aplica Deployment e Service no Kubernetes (porta 11434, volume para modelos em `~/.ollama`).
11. **Transcrição:** Cria `~/enxame/transcription/`, grava `m4a_to_md.py`, venv com `faster-whisper` e `tqdm`.
12. **OpenClaw:** Gera `~/enxame/openclaw/config.yaml` com Telegram (token, chat_id, voice_to_text), provedores Google e Ollama, agentes CEO e coder, storage Redis.
13. **Aliases:** Adiciona ao `~/.bashrc`: `k`, `h`, `m`, `enxame`, `transcrever`, `ceo`, `enxame-status`, `enxame-start`, etc.
14. **start.sh:** Cria `~/enxame/start.sh` para iniciar Minikube e verificar Redis/Ollama.
15. **Testes:** Roda `docker run hello-world`, `kubectl get nodes`, verifica pods Redis e ambiente de transcrição.
16. **Mensagem final:** Exibe diretórios, comandos úteis, próximos passos e status.

## Como executar

```bash
# Salvar o script (conteúdo de setup.sh) como setup.sh
chmod +x setup.sh
./setup.sh
# Informar as chaves quando solicitado
source ~/.bashrc   # após o término
```

## Comandos úteis após o setup

| Comando            | Descrição                          |
|--------------------|------------------------------------|
| `enxame-status`    | Status do Minikube, pods e services |
| `enxame-start`     | Executa `~/enxame/start.sh`        |
| `transcrever F.m4a`| Transcreve áudio com m4a_to_md.py  |
| `ceo`              | Logs do pod Ollama (tail -f)       |
| `minikube dashboard` | Abre o dashboard do Kubernetes   |

## Arquivos e diretórios criados

- `~/enxame/` — raiz do projeto
- `~/enxame/transcription/` — script e venv de transcrição
- `~/enxame/openclaw/` — config.yaml do OpenClaw
- `~/enxame/start.sh` — script de inicialização do enxame

## Script completo

O script executável está em **scripts/setup.sh** na raiz do repositório ClawDevs. Execute a partir da raiz: `./scripts/setup.sh`. Não é necessário copiar; o script detecta o repositório e usa o Makefile e k8s/ para subir o cluster.

Referência: [09-setup-e-scripts.md](../09-setup-e-scripts.md) na documentação do enxame.
