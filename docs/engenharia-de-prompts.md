<!-- 
  Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.
 -->

# Engenharia de prompts

Referência curta de técnicas para instruir modelos de linguagem de forma previsível e reutilizável. Útil ao desenhar prompts operacionais (por exemplo junto de `container/base/openclaw-config/shared/SDD_OPERATIONAL_PROMPTS.md`).

## Técnicas

### Few-shot prompting

Fornecer exemplos reais de entrada e saída para padronizar o comportamento.

**Na prática:** inclua 2–5 pares `(entrada → saída)` representativos; cubra variações comuns (tom, formato, casos limite) para o modelo imitar o padrão sem ambiguidade.

### Iterative refinement

Desenvolver o prompt em camadas, refinando a cada ciclo de resposta.

**Na prática:** comece com objetivo e restrições mínimas; avalie a primeira resposta; acrescente clareza, contraexemplos ou checklist até o resultado estabilizar. Evite inflar tudo num único bloco sem feedback.

### Role prompting

Atribuir personas específicas para elevar a qualidade técnica da resposta.

**Na prática:** defina papel, público, nível de detalhe e critérios de qualidade (ex.: “atuando como arquiteto de software, para um time sênior”). Combine com domínio e formato de saída quando fizer sentido.

### Prompt as code

Tratar prompts como ativos do time: versionados e compartilhados.

**Na prática:** mantenha prompts em repositório (arquivos `.md` ou templates), com revisão em PR, nomes estáveis e changelog quando o comportamento mudar. Evite cópias soltas em chats sem rastreio.

### Reverse prompting

Partir da saída ou do resultado desejado para inferir, reconstruir ou refinar a instrução que a produziria.

**Na prática:** descreva o formato e o conteúdo ideal (ou cole um exemplo alvo) e peça ao modelo que proponha o prompt, as restrições ou o checklist que melhor geram esse resultado; use o output como rascunho para iterar (alinhado a *iterative refinement*).

## Resumo

| Técnica               | Foco principal                          |
|-----------------------|-----------------------------------------|
| Few-shot prompting    | Exemplos para padronizar comportamento  |
| Iterative refinement  | Melhorar o prompt por ciclos            |
| Role prompting        | Persona e rigor técnico                 |
| Prompt as code        | Versionamento e governança              |
| Reverse prompting     | Do resultado desejado à instrução       |

As técnicas se complementam: *prompt as code* preserva o que funcionou; *few-shot* e *role* definem o padrão; *reverse* e *iterative* fecham a lacuna entre intenção e entrega.
