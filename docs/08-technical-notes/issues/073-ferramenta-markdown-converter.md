# [team-devs-ai] Ferramenta Markdown Converter (markitdown)

**Fase:** 7 — Ferramentas  
**Labels:** tooling, docs

## Descrição

Converter PDF, Word, PowerPoint, Excel, HTML, imagens, áudio, ZIP, YouTube e EPub para Markdown via `uvx markitdown` para processamento por LLM ou RAG. Uso por CEO, PO, Developer e pipeline de pré-processamento; integração com expertise em documentação.

## Critérios de aceite

- [x] Instalação e uso de `uvx markitdown` (ou equivalente) documentados. **Ref:** [27-ferramenta-markdown-converter.md](../27-ferramenta-markdown-converter.md) § Instalação, Uso básico.
- [x] Formatos suportados listados: PDF, Word, PowerPoint, Excel, HTML, imagens, áudio, ZIP, YouTube, EPub. **Ref:** Doc 27 § Formatos suportados.
- [x] Uso por CEO, PO, Developer e pipeline de pré-processamento documentado. **Ref:** Doc 27 § Uso no ecossistema de agentes.
- [x] **Uso pelo Architect para microADR:** ao aprovar PR, Architect gera microADR (JSON estrito) via markitdown ou saída formatada; anexado ao Warm Store, fora do pipeline de sumarização. **Ref:** Doc 27 § Architect — microADR; [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) §2.3; [microadr_generate.py](../../scripts/microadr_generate.py).
- [x] Integração com 18-expertise-documentacao (obter doc em formato processável). **Ref:** Doc 27 § Expertise em documentação; [18-expertise-documentacao.md](../18-expertise-documentacao.md).

## Referências

- [27-ferramenta-markdown-converter.md](../27-ferramenta-markdown-converter.md)
