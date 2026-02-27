# Setup e scripts

Objetivo: configurar o ambiente com **um único script** (`setup.sh`) que instala dependências, coleta chaves dos provedores OpenClaw escolhidos e Telegram, sobe Minikube (limites 65% da **máquina de referência** — ver [00-objetivo-e-maquina-referencia.md](00-objetivo-e-maquina-referencia.md)), Redis, Ollama, ambiente de transcrição de áudio e configuração do OpenClaw com canal Telegram e voz. **Configuração de rede e portas** (incluindo loopback e permissões necessárias para a interface) é resolvida automaticamente pelo script ou pela imagem de ambiente — o usuário **não precisa editar arquivos manualmente** dentro do container (evitando desvios para editores no terminal). Ao final, os agentes estão no Minikube local e o Agente CEO aguarda o primeiro projeto via Telegram (incluindo áudio convertido em texto).

## Versão canônica do setup

A versão completa e recomendada do `setup.sh`:

- Valida que não está rodando como root.
- Verifica se o sistema é Pop!_OS (ou avisa e pergunta se deseja continuar).
- Coleta e valida **chave(s) do(s) provedor(es) OpenClaw** (ex.: Ollama local sem chave; OpenRouter/OpenAI etc. conforme [lista canônica](07-configuracao-e-prompts.md#provedores-apenas-integrados-openclaw)), **Telegram Bot Token** e **Telegram Chat ID** (não aceita vazios).
- Atualiza o sistema e instala dependências (curl, git, python3, ffmpeg, docker, nvidia-container-toolkit, conntrack, etc.).
- Instala Docker, Minikube, kubectl e Helm (se ainda não existirem).
- Inicia Minikube com **65%** dos recursos da máquina de referência (CPU e RAM calculados dinamicamente). Para verificar se sua máquina é equivalente, use os comandos em [00-objetivo-e-maquina-referencia.md](00-objetivo-e-maquina-referencia.md) ou execute [docs/scripts/verify-machine.sh](scripts/verify-machine.sh) (a partir da raiz: `./docs/scripts/verify-machine.sh`).

**Validação 009 (transcrição):** A integração m4a→md está implementada: [scripts/setup.sh](../scripts/setup.sh) configura o diretório de transcrição, copia [scripts/m4a_to_md.py](../scripts/m4a_to_md.py), cria o venv com faster-whisper e gera `config.yaml` com `voice_to_text.command` e `output_dir`; o alias `transcrever` e o teste ao final do setup validam o fluxo.
- Instala Redis via Helm e deploy do Ollama no Kubernetes.
- Configura o ambiente de transcrição: diretório `~/enxame/transcription/`, script `m4a_to_md.py`, venv com `faster-whisper` e `tqdm`.
- Gera `~/enxame/openclaw/config.yaml` com canais Telegram (token, chat_id, comando de voz para texto) e provedor(es) OpenClaw (api_key ou OAuth conforme [documentação OpenClaw](https://docs.openclaw.ai)).
- Cria aliases no `~/.bashrc` (ex.: `enxame-status`, `transcrever`, `ceo`) e script `~/enxame/start.sh`.
- Executa testes de validação (Docker, Minikube, Redis, transcrição) e exibe mensagem final com próximos passos.

O script completo está em **[scripts/setup.sh](../scripts/setup.sh)** na raiz do repositório. Para usar: a partir da raiz do repositório ClawDevs, execute `./scripts/setup.sh` (ou `chmod +x scripts/setup.sh` se necessário). Recarregue o shell após o fim (`source ~/.bashrc`).

## Script de transcrição (m4a para texto)

O script **m4a_to_md.py** converte áudio M4A em texto (transcrição) e salva em arquivo `.md`. Uso previsto: **offline e sem custo de API** para transcrição (faster-whisper ou openai-whisper), com suporte a PT-BR. O OpenClaw usa esse script como comando de voz-para-texto no canal Telegram.

- **Entrada:** arquivo `.m4a` (ex.: áudio enviado pelo Telegram).
- **Saída:** arquivo `.md` com o texto transcrito.
- **Backends:** `faster-whisper` (recomendado) ou `openai-whisper`; requer `ffmpeg` no sistema.

A versão canônica está em [scripts/m4a_to_md.py](../scripts/m4a_to_md.py) na raiz do repositório. O `setup.sh` instala as dependências no venv em `~/enxame/transcription/venv` e configura no OpenClaw o comando:

`~/enxame/transcription/venv/bin/python ~/enxame/transcription/m4a_to_md.py`

(com caminho absoluto ajustado para o usuário).

## Configuração OpenClaw e Telegram

Exemplo de trecho do `config.yaml` gerado pelo setup (variáveis substituídas pelas chaves informadas):

```yaml
channels:
  telegram:
    token: "<TELEGRAM_BOT_TOKEN>"
    allowed_chat_ids:
      - <TELEGRAM_CHAT_ID>
    voice_to_text:
      enabled: true
      command: "/home/<USER>/enxame/transcription/venv/bin/python /home/<USER>/enxame/transcription/m4a_to_md.py"
      output_dir: "/home/<USER>/enxame/audio/transcriptions"

# Provedores: apenas integrados OpenClaw (Ollama local/cloud, OpenRouter, OpenAI, etc.)
# Exemplo com Ollama local + OpenRouter (ou usar só Ollama). Ver docs.openclaw.ai e 07-configuracao-e-prompts.md.
providers:
  ollama:
    host: "http://ollama-service.ai-agents.svc.cluster.local:11434"
    default_model: "llama3:8b"
  # openrouter ou openai conforme doc OpenClaw (variáveis OPENROUTER_API_KEY, OPENAI_API_KEY em secrets)
```

Documentação do canal Telegram: [OpenClaw – Telegram](https://docs.openclaw.ai/channels/telegram).

## Instruções de uso

1. Salvar o conteúdo de [scripts/setup.sh](scripts/setup.sh) como `setup.sh` (ex.: na raiz do projeto ou em `~/enxame/`).
2. Dar permissão de execução: `chmod +x setup.sh`.
3. Executar: `./setup.sh`.
4. Informar quando solicitado: chaves do(s) provedor(es) OpenClaw e Telegram Bot Token e Telegram Chat ID.
5. Após o término, recarregar o shell: `source ~/.bashrc` (ou abrir novo terminal).

## Teste imediato

Após a execução, envie um áudio em M4A para o seu bot do Telegram. O sistema deve: (1) Receber o áudio; (2) Transcrever localmente (faster-whisper); (3) Enviar o texto para o Agente CEO (provedor configurado, ex. Ollama ou OpenRouter); (4) Responder com análise estratégica. A transcrição e o modelo local (Ollama) podem ser usados offline, sem custo de API; o CEO em nuvem consome a API do provedor em nuvem escolhido (configurar limite de gastos no painel do provedor).

## Riscos e avisos

- **GPU passthrough:** Se o `nvidia-container-toolkit` exigir reinício do Docker, o script pode pausar; atender às mensagens do terminal (ex.: senha `sudo`).
- **Primeiro áudio:** O primeiro envio de áudio pode demorar 30–60 segundos a mais enquanto o modelo Whisper é baixado para o NVMe; em seguida a transcrição fica mais rápida.
- **Aliases:** O setup adiciona aliases ao `~/.bashrc` (ex.: `enxame-status`, `transcrever`, `ceo`). Use `enxame-status` para ver estado do Minikube, pods e serviços; `transcrever arquivo.m4a` para transcrever manualmente; `ceo` para seguir os logs do agente.

## GPU Lock (referência)

O script de GPU Lock em Python (Redis `SETNX` com **TTL dinâmico**) usado pelos agentes locais para serializar o uso da Ollama/GPU está descrito em [03-arquitetura.md](03-arquitetura.md) e [04-infraestrutura.md](04-infraestrutura.md). O TTL é calculado pelo tamanho do payload do evento (ex.: >500 linhas → 120 s, senão 60 s). Implementação de referência em [scripts/gpu_lock.md](scripts/gpu_lock.md); salvar como `scripts/gpu_lock.py` e importar pelos agentes.
