# [team-devs-ai] Pods CEO e PO (nuvem) com OpenClaw

**Fase:** 1 — Agentes  
**Labels:** agents, k8s, openclaw

## Descrição

Implantar os pods do Agente CEO e do Agente PO com OpenClaw, usando modelos em nuvem (Gemini/OpenAI). Configuração de canais (ex.: Telegram), provedores e memória conforme doc.

## Critérios de aceite

- [ ] Deployment (ou equivalente) para CEO e PO no cluster, com OpenClaw configurado.
- [ ] Configuração de API (Google Gemini e/ou outros) via secrets ou config; sem credenciais em imagem.
- [ ] Canal Telegram (ou outro) configurado para interface com o Diretor.
- [ ] CEO como único ponto de contato com o Diretor; PO sem acesso à internet pública (restrição de rede ou config).

## Referências

- [04-infraestrutura.md](../04-infraestrutura.md) (Configuração dos agentes)
- [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md)
- [09-setup-e-scripts.md](../09-setup-e-scripts.md)
