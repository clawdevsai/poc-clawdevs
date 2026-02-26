# [team-devs-ai] Ferramenta summarize (URLs, PDFs, imagens, áudio, YouTube)

**Fase:** 7 — Ferramentas  
**Labels:** tooling, pipeline

## Descrição

CLI ou skill para sumarizar URLs, PDFs, imagens, áudio e YouTube. Uso no pipeline de truncamento e por CEO/PO. Instalação, flags e configuração.

## Critérios de aceite

- [ ] Ferramenta (CLI ou skill) disponível para sumarizar: URLs, PDFs, imagens, áudio, YouTube.
- [ ] Flags e opções documentadas (ex.: idioma, tamanho máximo de saída).
- [ ] Integração com pipeline de truncamento (redução de contexto) documentada.
- [ ] **Exceção:** conteúdo tagado como **invariante de negócio** ou **microADR** **não** deve ser passado ao summarize; microADR nunca é resumido. Ver [12-ferramenta-summarize.md](../12-ferramenta-summarize.md) e [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) (seção 2.3).
- [ ] Uso por CEO e PO para resumos executivos documentado.

## Referências

- [12-ferramenta-summarize.md](../12-ferramenta-summarize.md)
