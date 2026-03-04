# Exemplo de fluxo: Operação 2FA

Exemplo de coreografia do **ClawDevs**: implementação de um sistema de login com autenticação de dois fatores (2FA) via e-mail. Os agentes trabalham entre nuvem (Google Gemini) e o host local (Pop!_OS), respeitando o limite de 65% de hardware.

---

## Cenário

O Diretor pede: *"Quero implementar um sistema de login com autenticação de dois fatores (2FA) via e-mail."*

---

## Fase 1: Planejamento (nuvem – Google Gemini)

1. **Agente CEO (Gemini 1.5 Pro):** Recebe a ordem, pesquisa melhores práticas de 2FA, decide por tokens temporários (TOTP). Publica no Redis a diretriz: *"Implementar 2FA focado em segurança máxima e baixo custo de envio."*

2. **Agente PO (Gemini 1.5 Flash):** Lê a diretriz, cria 3 Issues no GitHub: `#1 Schema do banco`, `#2 Lógica de envio de e-mail`, `#3 Interface de verificação`. Avisa o time técnico via Redis: *"Prioridade 1 liberada."*

---

## Fase 2: Preparação (local – Ryzen 5800X)

3. **Agente DevOps (Ollama – Phi-3):** Acorda, verifica hardware (CPU ~15%, GPU livre, RAM ~12 GB). Cria a branch `feature/2fa-auth` e dispara o GPU Lock, reservando a VRAM para o próximo agente.

---

## Fase 3: Execução (local – RTX 3060 Ti)

4. **Agente Developer (Ollama – DeepSeek-Coder):** Obtém o lock da GPU. O OpenCode recebe o contexto das Issues #1 e #2. Implementa o código em Python, modelos de banco e lógica do token. Faz commit e libera a GPU: *"Código pronto para revisão."*

---

## Fase 4: Revisão (local – RTX 3060 Ti)

5. **Agente Architect (Ollama – Qwen2.5-Coder):** Obtém o lock da GPU. Revisa o código e recusa o PR: *"A função de geração de token está muito complexa; simplifique usando o padrão SOLID."* Devolve ao Developer.

6. **Agente Developer (Ollama):** Corrige e reenvia em pouco tempo (modelo ainda "quente" na VRAM). O Architect aprova: *"Código limpo e aderente."*

7. **Agente CyberSec (Ollama – Llama 3):** Revisa e identifica: *"Atenção: o token não expira. Adicione TTL (Time-to-Live) de 5 minutos."* Gera sub-task de segurança; o Developer corrige.

8. **Agente DBA (Ollama – Llama 3):** Revisa o schema do banco e as queries (Issue #1 e lógica de token). Verifica índices nas colunas de filtro (ex.: token, expiração). Solicita: *"Adicione índice na coluna de expiração do token para evitar full scan nas buscas por TTL."* O Developer ajusta a migration; o DBA aprova.

---

## Fase 5: Validação (local – sandbox)

9. **Agente QA (Ollama – Llama 3):** O DevOps sobe um container isolado no Minikube. O QA executa 15 testes automatizados. Todos passam (build verde).

10. **Agente UX (Ollama – Llama 3 Vision):** Analisa o componente de frontend: *"O campo de código 2FA precisa de foco automático ao abrir a tela."* Sugere ajuste final em CSS/JS.

---

## Fase 6: Fechamento (nuvem – Google Gemini)

11. **Agente CEO (Gemini 1.5 Pro):** Recebe o relatório final via Redis. Notifica o Diretor no Telegram: *"Diretor, o sistema 2FA está pronto na branch main. Custo da operação: $0.01 de API e 45 minutos de trabalho do ClawDevs. Posso fazer o deploy para staging?"*

---

## Pontos de risco (onde quase falhou)

- **Fase 4:** Se o Architect e o Developer entrassem em loop de discussão, o Agente DevOps poderia cortar o processo por excesso de tempo de uso da GPU, forçando escalonamento ao Diretor.
- O **CyberSec** barrou a ausência de TTL no token, evitando uma vulnerabilidade em produção.
- O **DBA** barra o merge se migrations ou queries violarem normas de banco ou comprometerem performance (ex.: falta de índice em coluna de filtro); no exemplo, a solicitação de índice na coluna de expiração evita full scan em produção.

Este fluxo ilustra o uso de Redis para estado e eventos, GPU Lock para serializar o uso da VRAM, e o papel de cada agente conforme [02-agentes.md](02-agentes.md) e [03-arquitetura.md](03-arquitetura.md).
