# Troubleshooting

Guia tecnico de diagnostico da stack Docker em execucao local.

## Conceito de diagnostico

A stack depende de 3 blocos:

1. **Base de dados e cache:** PostgreSQL + Redis
2. **Aplicacao:** OpenClaw + painel (backend, worker, frontend)
3. **Inferencia e busca:** Ollama + SearXNG (+ proxy)

A ordem de verificacao recomendada e: **containers -> health -> logs -> conectividade entre servicos**.

## Diagnostico inicial (passo unico)

```bash
make status
make logs
```

Logs por componente:

```bash
make openclaw-logs
make ollama-logs
make backend-logs
make frontend-logs
```

Inspecao direta no Docker:

```bash
docker ps -a --filter "name=^/clawdevs-"
docker inspect clawdevs-openclaw
docker inspect clawdevs-panel-backend
docker inspect clawdevs-ollama
```

## Problemas comuns

### 1) `make preflight` falha

**Causa comum:** variaveis obrigatorias ausentes no `.env`.

**Acao:**

1. Copiar `.env.example` para `.env` se necessario.
2. Preencher as chaves obrigatorias.
3. Rodar `make preflight` novamente.

### 2) Containers nao sobem ou reiniciam

**Acao:**

```bash
make down
make up-all-with-cache
make status
```

Se ainda falhar, confira logs com `make logs`.

Diagnostico adicional:

```bash
docker inspect clawdevs-postgres
docker inspect clawdevs-redis
docker inspect clawdevs-panel-backend
```

### 3) Painel nao abre em `localhost:3000`

**Acao:**

```bash
make panel-url
make frontend-logs
make backend-logs
```

Verifique tambem se a porta `3000` esta ocupada por outro processo local.

### 4) OpenClaw sem resposta em `localhost:18789`

**Acao:**

```bash
make openclaw-logs
make openclaw-shell
```

No shell do container, valide processo e configuracao de runtime.

### 5) Ollama sem modelo, lento ou indisponivel

**Acao:**

```bash
make ollama-logs
make ollama-list
```

Se estiver usando GPU, tente `make up-gpu` no proximo restart.

Validacao adicional:

```bash
docker inspect clawdevs-ollama
```

### 6) Migracoes do backend falhando

**Acao:**

```bash
make migrate
make backend-logs
```

Se necessario, confirme conectividade do backend com banco e redis via `docker inspect clawdevs-panel-backend`.

### 7) Falha de autenticacao no painel

**Causa comum:** credenciais de admin/token inconsistentes no `.env`.

**Acao:**

```bash
make preflight
make up-panel-backend
make up-token-init
make up-panel-frontend
```

Depois, validar com `make panel-url`.

## Recuperacao rapida

```bash
make down
make up-all-with-cache
```

## Reset destrutivo

```bash
make reset
```

## Limpeza completa da stack

```bash
make destroy
```

## Nota

Este projeto usa fluxo Docker via `Makefile` e scripts em `scripts/docker/`.
