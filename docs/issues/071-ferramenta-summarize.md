# [team-devs-ai] Ferramenta summarize (URLs, PDFs, imagens, áudio, YouTube)

**Fase:** 7 — Ferramentas  
**Labels:** tooling, pipeline

## Descrição

CLI ou skill para sumarizar URLs, PDFs, imagens, áudio e YouTube. Uso no pipeline de truncamento e por CEO/PO. Instalação, flags e configuração.

## Critérios de aceite

- [x] Ferramenta (CLI ou skill) disponível para sumarizar: URLs, PDFs, imagens, áudio, YouTube. **Ref:** [12-ferramenta-summarize.md](../12-ferramenta-summarize.md) § Instalação, Quick start.
- [x] Flags e opções documentadas (ex.: idioma, tamanho máximo de saída). **Ref:** Doc 12 § Flags úteis (`--length`, `--max-output-tokens`, `--json`, `--youtube`, etc.).
- [x] Integração com pipeline de truncamento (redução de contexto) documentada. **Ref:** Doc 12 § Uso no ecossistema, Pre-flight obrigatório; [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md).
- [x] **Exceção:** conteúdo tagado como **invariante de negócio** ou **microADR** **não** deve ser passado ao summarize; microADR nunca é resumido. **Ref:** Doc 12 § Regra de ouro — exceções à sumarização; [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) §2.3; [ferramentas-fase7-referencia.md](../agents-devs/ferramentas-fase7-referencia.md) §071.
- [x] Uso por CEO e PO para resumos executivos documentado. **Ref:** Doc 12 § CEO/PO.

## Referências

- [12-ferramenta-summarize.md](../12-ferramenta-summarize.md)
