# Imagem do pod Developer (Fase 1 — 013). Scripts são montados via ConfigMap (developer-scripts).
# Para integrar OpenCode: adicionar instalação do OpenCode nesta imagem (ex.: COPY de build
# ou pip/apt conforme documentação do OpenCode) ou usar imagem alternativa que já inclua OpenCode.
# Ref: docs/issues/013-pods-tecnicos-developer-opencode.md, docs/33-opencode-controller.md
FROM python:3.12-slim

RUN pip install --no-cache-dir redis

# OpenCode: descomentar ou adicionar camada quando houver método de instalação (ex. pip/apt).
# RUN pip install opencode  # ou COPY opencode /opt/opencode

WORKDIR /workspace
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
