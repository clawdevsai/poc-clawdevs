# [team-devs-ai] Setup "um clique" (setup.sh)

**Fase:** 0 — Fundação  
**Labels:** foundation, automation, devops

## Descrição

Implementar o script `setup.sh` que configura o ambiente completo do team-devs-ai em uma máquina equivalente à de referência: dependências, Minikube (65% dos recursos), Redis, Ollama, transcrição de áudio, OpenClaw com Telegram e voz.

## Critérios de aceite

- [ ] Script não executa como root; verifica SO (Pop!_OS ou aviso + confirmação).
- [ ] Coleta e valida chaves dos provedores OpenClaw escolhidos (conforme [lista canônica](../07-configuracao-e-prompts.md#provedores-apenas-integrados-openclaw)) e Telegram Bot Token e Telegram Chat ID (não aceita vazios).
- [ ] Instala dependências: curl, git, python3, ffmpeg, docker, nvidia-container-toolkit, conntrack, etc.
- [ ] Instala Docker, Minikube, kubectl e Helm se não existirem.
- [ ] Inicia Minikube com ~65% CPU e RAM da máquina (calculados dinamicamente ou documentados para máquina de referência).
- [ ] Instala Redis (Helm) e faz deploy do Ollama no Kubernetes.
- [ ] Configura transcrição: diretório `~/enxame/transcription/`, script `m4a_to_md.py`, venv com faster-whisper (ou openai-whisper).
- [ ] Gera `~/enxame/openclaw/config.yaml` com canais Telegram (token, chat_id, voice_to_text) e provedor(es) OpenClaw (api_key ou OAuth conforme doc).
- [ ] Cria aliases (ex.: `enxame-status`, `transcrever`, `ceo`) e script `~/enxame/start.sh`.
- [ ] Executa testes de validação (Docker, Minikube, Redis, transcrição) e exibe próximos passos.
- [ ] Configuração de rede/portas resolvida automaticamente (sem edição manual no container).

## Referências

- [09-setup-e-scripts.md](../09-setup-e-scripts.md)
- [00-objetivo-e-maquina-referencia.md](../00-objetivo-e-maquina-referencia.md)
