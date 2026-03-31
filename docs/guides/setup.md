# Setup Local

**Publico:** engenharia backend, frontend e devops  
**SO:** Windows com Docker Desktop

## Requisitos

- Docker Desktop ativo
- `docker` no PATH
- `make` no PATH
- `git` no PATH
- arquivo `.env` na raiz do projeto

## Passo a passo

### 1) Preparar configuracao

```bash
cp .env.example .env
```

Preencha os segredos obrigatorios no `.env`.

### 2) Validar ambiente

```bash
make preflight
```

### 3) Subir stack completa

```bash
make up-all-with-cache
```

Alternativas:

- `make up-all` (sem cache de build)
- `make up-gpu` (forca `--gpus all` no container Ollama)

### 4) Verificar status

```bash
make status
make panel-url
```

URLs padrao:

- Frontend: `http://localhost:3000`
- Backend/API docs: `http://localhost:8000/docs`
- Gateway OpenClaw: `http://localhost:18789`
- Ollama API: `http://localhost:11434`

## Operacao diaria

```bash
make logs
make openclaw-logs
make ollama-logs
make backend-logs
make frontend-logs
make openclaw-shell
```

## Banco de dados e migracoes

```bash
make migrate
```

## Encerrar ou limpar

```bash
make down
make reset     # destrutivo: remove volumes da stack
make destroy   # destrutivo: remove stack e imagens locais da stack
```

## Observacoes importantes

- O fluxo oficial desta base usa Docker e scripts em `scripts/docker/`.
- Comandos do tipo `docker-compose get/describe/port-forward` nao fazem parte do fluxo atual.
