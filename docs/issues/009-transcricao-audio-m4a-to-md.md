# [team-devs-ai] Transcrição de áudio (m4a → texto .md)

**Fase:** 0 — Fundação  
**Labels:** foundation, tooling, openclaw

## Descrição

Script para converter áudio M4A em texto (transcrição) e salvar em .md. Uso: canal de voz do Telegram → texto para o Agente CEO. Offline, sem custo de API (faster-whisper ou openai-whisper), com suporte a PT-BR.

## Critérios de aceite

- [ ] Script `m4a_to_md.py` (ou equivalente): entrada .m4a, saída .md com texto transcrito.
- [ ] Backend configurável: faster-whisper (recomendado) ou openai-whisper; ffmpeg como dependência.
- [ ] Integração no setup: venv em `~/enxame/transcription/`, comando configurado no OpenClaw para voice_to_text (caminho absoluto ao script).
- [ ] Documentação de uso (incluindo primeiro áudio e download do modelo Whisper).

## Referências

- [09-setup-e-scripts.md](../09-setup-e-scripts.md) (Script de transcrição)
