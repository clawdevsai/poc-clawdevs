# [team-devs-ai] Docker multi-stage e imagens enxutas por agente

**Fase:** 0 — Fundação  
**Labels:** foundation, docker, infra

## Descrição

Cada agente deve rodar em container com imagem enxuta (multi-stage build) para não estourar disco. Meta: ~300 MB por imagem (sem contar modelo LLM em volume compartilhado).

## Critérios de aceite

- [ ] Dockerfile multi-stage: estágio builder (dependências Python com --no-cache-dir), estágio runtime (apenas /root/.local e código necessário).
- [ ] ENV PYTHONDONTWRITEBYTECODE=1 e PYTHONUNBUFFERED=1; apenas essencial (git, curl) para OpenCode/OpenClaw.
- [ ] Logs direcionados para stdout (não gravar em disco dentro do container).
- [ ] Documentação dos limites de disco e da estratégia (ex.: 120 GB para cluster na máquina de referência).

## Referências

- [04-infraestrutura.md](../04-infraestrutura.md) (Docker: imagem base enxuta)
