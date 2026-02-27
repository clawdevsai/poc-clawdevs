# Configuração e prompts

Manifesto de configuração por agente (modelo, temperatura, skills, restrições), configuração avançada do OpenClaw e provedores (apenas integrados OpenClaw: Ollama local/cloud, OpenRouter, Qwen, Moonshot AI, OpenAI, Hugging Face).

---

## Configuração global

Todos os agentes locais apontam para o mesmo endpoint do Ollama e usam o GPU Lock (ver [03-arquitetura.md](03-arquitetura.md) e [09-setup-e-scripts.md](09-setup-e-scripts.md)). O pipeline de **validação pré-GPU** (SLM em CPU para sintaxe, lint, aderência SOLID) e a opção de **batching de PRs** (revisão em lote pelo Architect com janela de contexto única) reduzem contenção no lock e custo de VRAM; ver [03-arquitetura.md](03-arquitetura.md) e [06-operacoes.md](06-operacoes.md). Para gestão de modelos, chat/completions, embeddings, tool-use e sub-agentes OpenClaw com Ollama, ver [31-ollama-local.md](31-ollama-local.md).

---

## Causa raiz do custo: inchaço de contexto

A estratégia de redução de custos não pode tratar apenas o sintoma (ex.: parar operação se custo de API passar de $5/dia). A **causa raiz** é o **inchaço exponencial do contexto** nas configurações de memória do OpenClaw: o workspace memory anexa logs contínuos, históricos gigantes de conversas e blocos inteiros de código do OpenCode. Essa massa de dados **não filtrada** é enviada para os LLMs em nuvem (provedores OpenClaw, ex. OpenRouter, OpenAI) e o consumo de tokens torna-se catastrófico; o custo explode. Cortar a operação aos $5/dia evita falência, mas **não resolve a ineficiência** — o projeto pode ser paralisado prematuramente por **desperdício de tokens**, não porque o sistema trabalhou muito. A redução de custo sustentável depende do pipeline de truncamento e sumarização abaixo; o threshold de $5/dia deve ser mantido como **freio de emergência**.

**CEO Telegram (Ollama local):** Para reduzir truncamento (ex.: `limit=4096 prompt=12498`), configurar `contextWindow` no Gateway para o modelo do CEO (ex.: 8192 quando o modelo suportar); manter o SOUL do CEO **compacto** em `openclaw-workspace-ceo`; limitar histórico de conversa (últimas N mensagens) quando o OpenClaw permitir. Se o truncamento persistir, considerar modelo com janela maior (ex.: `ministral-3:3b` com 32k). Ver [issues/041-truncamento-contexto-finops.md](issues/041-truncamento-contexto-finops.md) para o pipeline completo (pre-flight Summarize, truncamento na borda).

---

## Perfis por agente (manifesto)

### CEO (estratégia)

- **Model (padrão):** Ollama local (ex.: `llama3:8b` ou `qwen2.5-coder:7b`) — tarefas pequenas e rotina.
- **Model (nuvem, sob demanda):** provedor integrado OpenClaw (ex.: OpenRouter, OpenAI, Ollama cloud) — apenas para validações complexas, raciocínio estratégico, criatividade e investigação na internet (web_search). Ver critérios em "Roteamento CEO/PO: local vs nuvem" abaixo e lista canônica em "Provedores (apenas integrados OpenClaw)".
- **Temperature:** 0.7
- **Skills:** `web_search`, `telegram_notify`, `financial_report`
- **Memory:** `project_vision_vector_db`
- **Constraint:** Proibido escrever código ou manipular arquivos técnicos. O freio de $5/dia é **freio de emergência** (última linha de defesa); o **controle primário** de custo e contexto é **determinístico na infraestrutura**: token bucket para eventos de estratégia e degradação por eficiência (ver seção 2.1). Se o custo de API exceder $5/dia, interromper e alertar.

### Product Owner (organizador)

- **Model (padrão):** Ollama local (ex.: `llama3:8b` ou `qwen2.5-coder:7b`) — tarefas pequenas e rotina.
- **Model (nuvem, sob demanda):** provedor integrado OpenClaw (ex.: OpenRouter, OpenAI, Ollama cloud) — apenas para validação complexa, raciocínio profundo ou pesquisa na internet. Ver critérios em "Roteamento CEO/PO: local vs nuvem" abaixo.
- **Temperature:** 0.3
- **Skills:** `github_api_manager`, `kanban_sync`
- **Memory:** `backlog_history`
- **Constraint:** Proibido alterar requisitos de tarefas em "In-Progress", **exceto** quando receber evento **technical_blocker** formalizado pelo Architect. Não pode definir a stack técnica sozinho. Deve usar ciclo de rascunho (draft) para o Architect validar viabilidade antes da tarefa ir para desenvolvimento.

### Developer (motor – local)

- **Model:** `deepseek-coder:6.7b` (Ollama)
- **Temperature:** 0.2
- **Skills:** `file_writer`, `gpu_lock_manager`, `git_commit`
- **Resource limit:** 4 GB RAM | 4 threads CPU
- **Constraint:** Proibido `git merge`. Proibido instalar pacotes sem autorização do CyberSec. Saída deve ser apenas código.

### Architect (juiz – local)

- **Model:** `llama3:8b` (Ollama)
- **Temperature:** 0.0
- **Skills:** `code_analyzer`, `adr_generator`, `file_reader`
- **Resource limit:** 2 GB RAM | 2 threads CPU
- **Constraint:** Proibido alterar código. Deve recusar PRs sem 80% de cobertura de testes. No **2º strike** o orquestrador injeta **prompt de compromisso**: o Architect deve **gerar o trecho de código exato** que tornaria o PR aprovado. No **5º strike** o contexto é empacotado e **roteado para arbitragem na nuvem**; só em falha da escalação o PR é marcado bloqueado/draft e removido da fila. Ver [06-operacoes.md](06-operacoes.md).

### DevOps / SRE (vigia – local)

- **Model:** `phi3:mini` (Ollama)
- **Temperature:** 0.1
- **Skills:** `minikube_monitor`, `resource_scaler`, `gpu_temp_check`
- **Memory:** `infrastructure_state`
- **Constraint:** Prioridade máxima: manter o host abaixo de 65%. **Aos 80°C (gatilho pré-crítico):** disparar evento de prioridade máxima no Redis ordenando **git stash** no repositório de trabalho (checkpoint transacional) — não derrubar pods ainda. **Aos 82°C:** pausar todos os agentes locais imediatamente (Q-Suite). Garantir que o pipeline Redis trate payloads como **idempotentes** e que o consumidor só envie **ACK após conclusão do trabalho em disco** (ver [06-operacoes.md](06-operacoes.md) e [03-arquitetura.md](03-arquitetura.md)).

### QA (caçador – local)

- **Model:** `llama3:8b` (Ollama)
- **Temperature:** 0.0
- **Skills:** `sandbox_executor`, `pytest_automation`
- **Resource limit:** 3 GB RAM | 2 threads CPU
- **Constraint:** Nunca rodar código fora da sandbox isolada. Não pode sugerir correções, apenas reportar falhas.

### CyberSec (auditor – local)

- **Model:** `llama3:8b` (Ollama)
- **Temperature:** 0.0
- **Skills:** `vulnerability_scanner`, `prompt_injection_filter`
- **Memory:** `security_incident_log`
- **Constraint:** Bloqueio imediato de qualquer PR que contenha chaves expostas ou dependências não homologadas.

### UX (designer – local)

- **Model:** `llama3-vision` (análise de interface)
- **Temperature:** 0.6
- **Skills:** `ui_validator`, `accessibility_checker`
- **Resource limit:** 4 GB RAM (vision exige mais VRAM)
- **Constraint:** Proibido sugerir mudanças que aumentem o tempo de carregamento em mais de 10%.

### DBA (guardião – local)

- **Model:** `llama3:8b` (Ollama) ou modelo adequado a análise de SQL/schema
- **Temperature:** 0.0
- **Skills:** `query_analyzer`, `schema_validator`, `file_reader`
- **Resource limit:** 2 GB RAM | 2 threads CPU
- **Constraint:** Bloquear PR com migrations sem índices necessários em colunas de filtro/join documentadas, ou com queries em caminho crítico que provoquem full table scan. Nunca aprovar alteração de schema que quebre contrato de API ou integração sem alinhar com o Architect.

### Governance Proposer (governança – sessão isolada, CPU)

- **Model:** `qwen2.5:7b` (Ollama) — rodando em **CPU** (não usa GPU Lock).
- **Temperature:** 0.3
- **Skills:** `web_search`, `github_gh`, `telegram_notify`
- **Resource limit:** 2 GB RAM | 2 threads CPU
- **Constraint:** Proibido fazer merge de PR. Só criar PR no repo dedicado para o Diretor aprovar. Aplicar modificações no workspace **apenas** após o Diretor aprovar e fazer merge na main (pull da main e sincronização). Operar em sessão isolada (cron); não consumir filas Redis do dia a dia. Ver [35-governance-proposer.md](35-governance-proposer.md).

---

## Roteamento CEO/PO: local vs nuvem

CEO e PO usam **Ollama local por padrão**; o provedor em nuvem (OpenRouter, OpenAI, Ollama cloud, etc. — lista canônica em "Provedores (apenas integrados OpenClaw)") é usado **sob demanda** conforme o tipo de tarefa. O Gateway ou orquestrador (OpenClaw) pode rotear por metadado do evento (`task_type: small` vs `task_type: requires_cloud`) ou por classificação prévia (regras ou SLM em CPU). Ver [03-arquitetura.md](03-arquitetura.md) (estágio de borda).

**Usar Ollama local (tarefas pequenas):**

- Respostas curtas ou confirmações.
- Priorizar próxima issue com contexto já conhecido.
- Validar critérios de aceite já definidos.
- Resumir status do sprint ou do backlog.
- Notificação ou digest simples.

**Usar nuvem apenas quando:**

- Validação mais complexa (múltiplas variáveis, ambiguidade de escopo).
- Raciocínio profundo / decisão estratégica.
- Criatividade (ideias, oportunidades, sugestões de produto).
- Precisão em investigação na internet (web search, pesquisa de mercado/concorrência).

---

## Configuração avançada OpenClaw

### 1. Skills (habilidades/ferramentas)

Scripts (em geral Python) que o agente pode invocar. Definir por agente: quem tem acesso a terminal, e-mail, NVMe, web.

- **Risco:** Dar `Terminal_Access` a todos pode permitir que um erro do QA apague código do Developer.
- **Recomendação:** Developer tem `File_Write`; apenas DevOps tem `System_Shell`.
- **Automação de browser:** Para testes E2E, validação de frontend e análise de UX, os agentes QA, Developer e UX podem usar o CLI **agent-browser** (navegação, snapshot, interações). Documentação completa em [11-ferramentas-browser.md](11-ferramentas-browser.md).
- **Sumarização de conteúdo:** Para reduzir contexto antes do envio à nuvem e para CEO/PO consumirem resumos de URLs, PDFs ou YouTube, pode-se usar o CLI **summarize**. Detalhes em [12-ferramenta-summarize.md](12-ferramenta-summarize.md).
- **Conversão de documentos para Markdown:** Para extrair texto estruturado de PDFs, Word, PowerPoint, Excel, HTML, imagens (OCR), áudio (transcrição), ZIP, YouTube ou EPub antes de sumarizar ou enviar ao contexto, usar **uvx markitdown**. Detalhes em [27-ferramenta-markdown-converter.md](27-ferramenta-markdown-converter.md).
- **GitHub (gh CLI):** Para Issues, PRs, status de CI e consultas à API do GitHub, os agentes PO, Developer, Architect, DevOps, QA e CyberSec usam o **gh** CLI. Documentação em [20-ferramenta-github-gh.md](20-ferramenta-github-gh.md).
- **MCP GitHub (público):** Acesso a repositórios públicos para busca e download de código de referência. Quando código é baixado ou buscado (MCP GitHub, Exa, web), aplicar **Zero Trust crítico** — validar se malicioso antes de incorporar. Ver [34-mcp-github-publico.md](34-mcp-github-publico.md), [05-seguranca-e-etica.md](05-seguranca-e-etica.md) (1.4), [14-seguranca-runtime-agentes.md](14-seguranca-runtime-agentes.md) (1.6).
- **Auto-atualização do ambiente:** Para manter o runtime e as skills instaladas atualizadas sem intervenção manual, configurar um cron (ou job equivalente) em **sessão isolada**, com entrega do resumo ao Diretor. Horário, timezone e canal de entrega são configuráveis. Documentação em [21-auto-atualizacao-ambiente.md](21-auto-atualizacao-ambiente.md).
- **Modelos gratuitos OpenRouter (FreeRide):** Quando o Diretor optar por usar **modelos gratuitos** em nuvem (OpenRouter), a skill FreeRide configura ranking e fallbacks no OpenClaw; reduz custo de API com tier gratuito. Documentação em [22-modelos-gratuitos-openrouter-freeride.md](22-modelos-gratuitos-openrouter-freeride.md).
- **API Gateway (Maton):** Para integração com 100+ APIs externas (Google, Slack, Notion, HubSpot, Stripe, etc.) com OAuth gerenciado, definir a variável de ambiente `MATON_API_KEY` (secrets do cluster); nunca em código ou repositório. Documentação em [25-api-gateway-integracao-apis.md](25-api-gateway-integracao-apis.md).

### 2. Memória e contexto (RAG e long-term memory)

- **Short-term:** Quantidade de mensagens anteriores enviadas ao modelo (aumentar gasta RAM/VRAM).
- **Long-term:** Integração com ChromaDB, Pinecone ou **LanceDB** (Warm Store); o agente consulta a memória em vez de reler tudo. O modelo de **memória em seis camadas** (Hot RAM, Warm Store, Cold Store, arquivo curado, cloud opcional, autoextração opcional) e a higiene de memória estão em [28-memoria-longo-prazo-elite.md](28-memoria-longo-prazo-elite.md).
- **Forgetfulness:** Esquecer logs antigos após conclusão de uma Issue para economizar espaço no NVMe; higiene semanal conforme doc 28.

### 2.1. Controle de FinOps no Gateway (regras, não agentes)

O **controle principal** de custo de contexto é feito por **regras no Gateway do OpenClaw** (configurações JSON/YAML), **antes** da requisição chegar ao provedor (OpenRouter, OpenAI, etc.). Não depender de ação reativa de agente (ex.: DevOps "limpar" contexto) nem apenas do freio de emergência ($5/dia): a gestão de contexto deve ser **determinística na infraestrutura**.

- **Max tokens por request no Gateway:** Configurar nas configs do Gateway um **limite rígido de max tokens por request** mapeado ao **perfil do agente** que usa nuvem (ex.: CEO, PO). O Gateway aplica o limite **antes** de enviar o payload ao provedor; assim o FinOps é garantido na borda, sem depender de o agente decidir o que enviar.
- **Limite VFM (evolução):** Para propostas de evolução (nova função, refatoração), o Gateway pode exigir artefato `vfmscore.json` e **limite numérico de aceitação** (fórmula ex.: horas_salvas × frequência_mensal − custo_tokens); se a pontuação for **inferior** ao threshold configurado, a alteração é **bloqueada na borda** — decisão determinística, sem debate em texto. O **CEO** deve realizar **autoavaliação econômica obrigatória no prompt** (artefato estruturado + descarte interno se threshold negativo) **antes** de enviar eventos de estratégia; o Gateway continua aplicando limite e bloqueio na borda como **redundância**. Ver [13-habilidades-proativas.md](13-habilidades-proativas.md), [soul/CEO.md](soul/CEO.md) e [05-seguranca-e-etica.md](05-seguranca-e-etica.md).
- **Acelerador preditivo de tokens:** Se o sistema **prever** estouro do orçamento (ex.: por tamanho do diff do PR ou histórico de tokens da tarefa), **rotear a tarefa para modelo local em CPU** (ex.: Phi-3 Mini) em vez de disparar o freio de emergência e alerta Telegram; a esteira continua gerando valor com degradação controlada de velocidade. Ver [05-seguranca-e-etica.md](05-seguranca-e-etica.md) e [22-modelos-gratuitos-openrouter-freeride.md](22-modelos-gratuitos-openrouter-freeride.md).
- **Token bucket (eventos de estratégia — Fase 2, issue 126):** Contador no orquestrador (Redis) para eventos com **tag de estratégia** (ex.: stream `cmd:strategy`). Limite por janela configurável (ex.: **máximo 5 eventos por hora**). Se o CEO tentar emitir além do limite, o Gateway **intercepta**: enfileirar para a próxima janela ou devolver erro ao agente. Implementação de referência: [scripts/gateway_token_bucket.py](../scripts/gateway_token_bucket.py). Variáveis: `TOKEN_BUCKET_MAX_PER_HOUR`, `REDIS_HOST`, `REDIS_PORT`.
- **Degradação por eficiência (126):** Orquestrador mede a **razão** entre ideias/diretrizes do CEO e épicos ou tarefas **aprovadas pelo PO**. Se a taxa cair **abaixo de limiar configurável**, bloquear temporariamente requisições ao modelo em nuvem para o CEO e **forçar roteamento para modelo local em CPU** (ex.: Phi-3). Objetivo: refinar ideias na fila em vez de gerar volume novo. Script de referência: mesmo `gateway_token_bucket.py` (chaves Redis: `ceo_ideas_count`, `po_approved_count`; env `EFFICIENCY_RATIO_MIN`).
- **$5/dia** permanece **freio de emergência**; token bucket e degradação por eficiência são o **controle primário** sustentável.
- **Orçamento de degradação:** O orquestrador (ou Gateway) mantém métrica acumulativa de eventos de 5ª strike (abandono) e de aprovação por omissão **cosmética** (timer não corre para impasses de código lógico/backend); se o percentual de tarefas do sprint nessa rota de fuga ultrapassar o limite configurável (ex.: 10–15%), primeiro é executado o **loop de consenso automatizado (pré-freio de mão)** — QA + Architect propõem ajuste temporário e testam em uma tarefa crítica (detalhes em [06-operacoes.md](06-operacoes.md)). A esteira só é **pausada** (freio de mão) **após** a falha desse loop (ou quando o loop não for aplicável). A retomada **só** ocorre após o **workflow de recuperação** documentado em [06-operacoes.md](06-operacoes.md): relatório de degradação gerado automaticamente, checklist do Diretor (MEMORY.md, ajuste de config) e **comando explícito de desbloqueio** (ex.: script/CLI) que autoriza os agentes a voltar a consumir o Redis.
- **Controle de taxa (token bucket) para eventos de estratégia:** O Gateway ou orquestrador aplica um limite **determinístico** ao número de **eventos de estratégia** (eventos publicados pelo CEO no stream com tag que identifica comando/diretriz estratégica, ex.: canal `cmd:strategy` ou metadado equivalente) por janela de tempo (ex.: **máximo 5 eventos por hora**, valor configurável). Se o CEO tentar emitir além do limite, o Gateway **intercepta** o comando: enfileira para a próxima janela ou descarta e devolve erro ao agente para aguardar. Assim o controle de taxa não depende do modelo probabilístico (LLM); fica na infraestrutura dura e evita paralisia por exaustão financeira antes de a cota $5/dia ser atingida.
- **Degradação por eficiência:** O orquestrador mede a **razão** entre ideias/diretrizes geradas pelo CEO e épicos ou tarefas **aprovadas pelo PO**. Se essa taxa cair **abaixo de um limiar configurável** (ex.: muitas diretrizes emitidas e poucas tarefas efetivamente aprovadas), o sistema **bloqueia temporariamente** as requisições ao modelo em nuvem para o CEO e **força o roteamento para modelo local em CPU** (ex.: Phi-3). O CEO passa a refinar as ideias já na fila em vez de gerar volume novo; a esteira segue viva sem consumir cota de API. É um **rebaixamento de privilégio** na prática: modelo local com janela de contexto menor e mais restrito.
- **Corte seco não pode agir sozinho:** Aplicar um corte seco quando o payload atinge o limite de tokens, **sem** passo anterior de sumarização, pode cortar no meio de um array ou objeto JSON e corromper o payload — o agente recebe código quebrado e pode entrar em alucinação. Por isso o limite de tokens no Gateway deve ser aplicado **após** o pre-flight de sumarização (ou, quando o pre-flight não se aplica, com regras de truncamento que preservem estrutura). Ver pre-flight abaixo.

### 2.2. Pipeline de truncamento e sumarização de contexto

Operar **antes** de qualquer transmissão para as APIs em nuvem, na camada de configuração, para eliminar o inchaço de dados. A sobrevivência do hardware **não** deve depender de um LLM: disjuntores programáticos na infraestrutura garantem que payloads gigantes nunca cheguem ao modelo.

- **Gancho de validação de contexto (pré-sumarização, local):** Antes de enviar o payload para sumarização na nuvem, executar uma etapa em que um **modelo local** (ex.: Llama 3, já usado no Architect) faz **varredura no buffer de trabalho** buscando **intenções do usuário** ou **regras informais** que não tenham tag. Se o modelo local identificar algo crítico para valor de negócio, **propor extração** para o arquivo principal de estado (SESSION-STATE.md). Objetivo: preservar valor de negócio sem gastar tokens de API e mitigar **amnésia funcional** (regras e preferências dizimadas pelo resumo). Ver [28-memoria-longo-prazo-elite.md](28-memoria-longo-prazo-elite.md).
- **Segregação dos critérios de aceite (obrigatória):** Os critérios de aceite originais das tarefas **não** podem estar no mesmo buffer que é sumarizado. Se estiverem, o PO recebe só o resumo e **perde a referência imutável** para comparar — fica incapaz de rejeitar o truncamento quando um critério foi omitido. Duas formas de garantir o acesso do PO aos critérios intactos: **(A) Tag de proteção:** Os critérios de aceite de toda issue recebem **obrigatoriamente** uma **tag especial** no Markdown (ex.: bloco `<!-- CRITERIOS_ACEITE -->` ou tag equivalente documentada no pipeline). O **script de limpeza/compacted do DevOps** é configurado com **regex** para **ignorar completamente** qualquer bloco dentro dessa tag — o modelo resume a conversa paralela, mas os critérios **passam ilesos** e não entram no input do sumarizador. **(B) Payload duplo (alternativa mais segura):** O orquestrador armazena os critérios em **arquivo separado** (ex.: `SESSION-STATE.md`, ou `session.md` por issue/sessão) e envia à nuvem um **payload duplo**: (1) o **resumo** da discussão técnica (economizando API) e (2) os **critérios originais** intactos, sem passar pelo sumarizador. O PO recebe os dois e faz a validação reversa com precisão. Ver [28-memoria-longo-prazo-elite.md](28-memoria-longo-prazo-elite.md) (onde ficam os critérios) e [12-ferramenta-summarize.md](12-ferramenta-summarize.md) (exceções à sumarização).
- **Validação reversa (PO):** Após a sumarização, o **PO** compara o **resumo gerado** com os **critérios de aceite originais** das tarefas — que **sempre** devem estar disponíveis intactos (via tag protegida ou payload duplo, acima). Se o resumo **omitir um critério fundamental**, o PO **rejeita o truncamento**; o sistema é forçado a **reestruturar o bloco** (ex.: manter trechos não sumarizados ou refazer o resumo). Garantia de qualidade na própria memória do enxame. Ver [02-agentes.md](02-agentes.md) (PO).
- **Pre-flight Summarize (obrigatório):** O CLI **Summarize** (ou equivalente) deve ser configurado como **pre-flight obrigatório** no fluxo de eventos do OpenClaw. Para issues ou conversas com **mais de três interações**, o orquestrador intercepta o payload antes do envio à nuvem; um **modelo local** (Ollama) gera um resumo executivo denso; o histórico bruto é substituído por esse resumo no payload; **só então** o Gateway libera o tráfego para o provedor em nuvem. A carga pesada sai da nuvem paga e vai para o hardware local de forma síncrona; evita corte no meio de JSON e reduz custo. Detalhes do CLI em [12-ferramenta-summarize.md](12-ferramenta-summarize.md).
- **Truncamento na borda (obrigatório):** Script (ex.: Python) na **entrada** do fluxo (antes de enfileirar no Redis Stream): conta tokens do payload (ex.: limite 4000 tokens); se exceder, aplica **truncamento bruto** — mantém cabeçalho do erro e causa raiz no final, remove o miolo do log/stack trace. O agente DevOps (e qualquer outro) **só recebe** payload já limitado; a máquina nunca recebe carga que estoure a VRAM. O Ollama não é usado para "resumir" logs gigantes (isso exigiria carregar o payload inteiro e causaria OOM).
- **Janela deslizante rigorosa:** Configurar (ex.: via `soul.md` ou equivalente no OpenClaw) uma janela de contexto rígida. Sumarização em modelo local (Ollama) ocorre como **pre-flight** (acima) para conversas com mais de N interações (ex.: 3); em outros casos, só **sobre payload já truncado na borda**.
- **Memória em duas camadas (e seis camadas):** Manter **dados brutos** em armazenamento de **curto prazo** e transferir **conceitos e decisões consolidadas** para um **banco vetorial de longo prazo** (Warm Store). O modelo na nuvem faz **consultas pontuais via RAG** em vez de carregar o histórico completo a cada prompt. O desenho completo (Hot RAM, Warm Store, Cold Store, arquivo curado, cloud, autoextração) está em [28-memoria-longo-prazo-elite.md](28-memoria-longo-prazo-elite.md).
- **TTL no Redis para working buffer:** As mensagens antigas do buffer de conversas (working buffer) no Redis devem **expirar automaticamente** via **TTL** configurado nas chaves — assim o "lixo digital" evapora da memória **sem depender do agente DevOps** para limpar chaves. O mesmo padrão de TTL já usado para o GPU Lock (ver [scripts/gpu_lock.md](scripts/gpu_lock.md)) estende-se às chaves do working buffer; a previsibilidade é lei da infraestrutura. Ver [28-memoria-longo-prazo-elite.md](28-memoria-longo-prazo-elite.md) e [13-habilidades-proativas.md](13-habilidades-proativas.md).
- **Redis Streams — ACK só após conclusão em disco:** Os consumidores do stream devem tratar mensagens como **transações idempotentes**: **não** enviar ACK até o trabalho estar **100% concluído em disco**. Em pausa brusca (ex.: 82°C), a mensagem permanece pendente na fila e é reentregue na retomada. Ver [06-operacoes.md](06-operacoes.md) e [03-arquitetura.md](03-arquitetura.md).

### 2.3. Livro razão de decisões, microADR e invariantes de negócio

Para evitar **amnésia arquitetural** causada pelo truncamento e sumarização agressiva (modelos e ferramentas de resumo tendem a generalizar e apagar nuances críticas de segurança ou design):

- **Livro razão de decisões (imutável):** Decisões estruturais **não** passam pelo pipeline de sumarização conversacional. O crescimento estrutural do projeto não pode virar resumo.
- **MicroADR:** Sempre que um **pull request for aprovado**, o Agente Architect usa a ferramenta Markdown (ex.: markitdown ou saída formatada — ver [27-ferramenta-markdown-converter.md](27-ferramenta-markdown-converter.md)) para gerar um **microADR** (registro de decisão arquitetural) em **JSON estrito**. Regra de ouro: o **microADR nunca é resumido**. Ele é anexado **diretamente** à memória vetorial de longo prazo (Warm Store), fora do funil de sumarização. **Auditoria de desvio (ADL):** O microADR deve incluir seção obrigatória de **auditoria de desvio**; a execução é feita por **regex** contra **lista negra de termos de justificativa fraca** (ex.: "parece melhor", "minha intuição sugere", "código mais limpo" sem métrica de complexidade). Se a justificativa casar, a submissão é **rejeitada em tempo de execução** na máquina local. Ver [13-habilidades-proativas.md](13-habilidades-proativas.md) e [28-memoria-longo-prazo-elite.md](28-memoria-longo-prazo-elite.md).
- **Invariantes de negócio:** Manter uma **lista de invariantes** no arquivo principal de estado da sessão (ex.: SESSION-STATE.md ou arquivo dedicado). Quando o Diretor definir uma **regra absoluta** (ex.: "token de login expira em 5 minutos"), ela recebe uma **tag especial** (marcação forte no texto). O **script de limpeza do DevOps** (usado na higiene de memória e no pipeline de compactação) deve ser configurado com um **regex** que **ignore** qualquer linha contendo essa tag — a janela de memória pode ser comprimida ao limite, mas as regras críticas de negócio **sobrevivem** à compactação.

### 3. Parâmetros de inferência

- **Temperature (0.0–1.0):** Architect 0.1 (precisão); UX 0.8 (criatividade).
- **Top-P / Top-K:** Diversidade da geração.
- **Max Tokens:** Limitar tamanho da resposta para evitar estouro de memória.

### 4. Canais de comunicação

Telegram, WhatsApp, Discord, Slack, CLI. Webhooks para avisar serviço externo quando o CyberSec detectar problema.

**Correlação mensagem–resposta (Telegram):** O gateway deve garantir que cada resposta no Telegram seja enviada **apenas** como resposta à mensagem do usuário que a gerou (correlação 1:1). Não misturar respostas: a resposta gerada para a mensagem A não pode ser enviada como resposta à mensagem B. Verificar na documentação do OpenClaw (ex.: [docs.openclaw.ai](https://docs.openclaw.ai)) se existe opção de processamento sequencial por chat ou uso de `reply_to_message_id`; configurar se disponível. Ver [issues/130-telegram-correlacao-mensagem-resposta.md](issues/130-telegram-correlacao-mensagem-resposta.md).

### 5. Autonomia (HIL – Human in the loop)

- **Always Ask:** agente planeja e o OpenClaw espera "OK" no Telegram.
- **Full Auto:** agente executa tudo (arriscado).
- **Threshold:** agente só pede permissão se custo > $0.50 ou comandos de deleção.

### 6. Sandbox e ambiente de execução

OpenClaw pode subir container temporário para o QA testar código. Definir resource limits por agente (ex.: UX 1 GB RAM, Developer 4 GB). **Developer:** comandos de instalação (npm, pip) e execução de código de terceiros devem rodar **exclusivamente** em **sandbox gerado dinamicamente**, sem privilégios e **air-gapped** (sem internet); o orquestrador destrói o container após cada execução. Dependências via proxy com whitelist de hashes aprovados. Ver [05-seguranca-e-etica.md](05-seguranca-e-etica.md) e [14-seguranca-runtime-agentes.md](14-seguranca-runtime-agentes.md).

### Tabela recomendada (cenário 65% hardware)

| Categoria | Configuração | Motivo |
|-----------|--------------|--------|
| Model routing | Nuvem para CEO/PO; local para técnicos | Economiza VRAM e melhora estratégia |
| Memory strategy | Vector DB (RAG) no NVMe compartilhado | Developer não esquece o que o PO pediu |
| **Truncamento/sumarização antes da nuvem** | **Gateway:** max tokens/request por perfil (CEO, PO). **Pre-flight:** Summarize obrigatório para &gt;3 interações (modelo local). Truncamento **na borda** (script antes de enfileirar, limite tokens) + janela deslizante + duas camadas. **Redis:** TTL nas chaves do working buffer (expiração automática, sem DevOps). | Controle FinOps na infraestrutura (regras no Gateway e Redis); evita payload que estoure VRAM; disjuntor não-LLM; corte seco só após pre-flight para não corromper JSON. |
| **RAG para consultas pontuais** | Dados brutos em curto prazo; conceitos no vetorial; nuvem consulta via RAG | Evitar histórico completo a cada prompt; reduz tokens e custo |
| Skill access | Por papel (role) | Impede QA de apagar arquivos do sistema |
| Temperature | 0.0 para CyberSec e Architect | Segurança e consistência |
| Max concurrency | 1 (DevOps gerencia o lock) | Evita OOM na RTX 3060 Ti |

**Riscos de configuração:** (1) Context overload: memória infinita em todos os agentes pode esgotar 32 GB de RAM em minutos. (2) Skill loop: agente em loop chamando Skill (ex.: web_search); usar timeout ou Max_Calls por tarefa.

---

## Provedores (apenas integrados OpenClaw)

O ClawDevs usa **somente** as tecnologias de inferência integradas ao OpenClaw. Nenhum provedor fora da lista abaixo (ex.: Google Gemini) deve ser documentado como opção canônica de LLM no stack ou no setup.

**Lista canônica (valor no ConfigMap `clawdevs-llm-providers` por agente):**

| # | Provedor / tecnologia   | Valor no K8s           |
|---|-------------------------|------------------------|
| 1 | Ollama (local / GPU)    | `ollama_local`         |
| 2 | Ollama (cloud)         | `ollama_cloud`         |
| 3 | OpenRouter             | `openrouter`           |
| 4 | Qwen (OAuth)           | `qwen_oauth`          |
| 5 | Moonshot AI            | `moonshot_ai`         |
| 6 | OpenAI                 | `openai`               |
| 7 | Hugging Face (Inference) | `huggingface_inference` |

Configuração: em **Kubernetes**, o ConfigMap `clawdevs-llm-providers` (`k8s/llm-providers-configmap.yaml`) define por agente (`agent_ceo`, `agent_po`, `agent_devops`, etc.). Padrão: **ollama_local** (Ollama GPU no cluster). CEO e PO também têm servidor (gateway OpenClaw) e podem usar nuvem sob demanda. Configuração via OpenClaw (config/gateway). APIs de produto (ex.: Google Sheets via Maton) continuam como estão; esta lista refere-se apenas a provedores de **inferência LLM**.

### Divisão de modelos

- **Nuvem (sob demanda):** OpenRouter, OpenAI, Ollama cloud, Qwen, Moonshot AI ou Hugging Face — usado para CEO e PO quando a tarefa exige validação complexa, raciocínio profundo, criatividade ou investigação na internet (ver "Roteamento CEO/PO: local vs nuvem" acima).
- **Ollama (local – RTX 3060 Ti):** CEO e PO em tarefas pequenas; Developer, Architect, DevOps, QA, CyberSec, UX. Resposta rápida e sem custo de token no tráfego local; a performance depende do hardware e do gerenciamento de recursos (limite ~65%, ver [04-infraestrutura.md](04-infraestrutura.md)).

### Gateway no OpenClaw (exemplo YAML)

O **controle de FinOps** deve estar no Gateway: configurar **max_tokens_per_request** (ou equivalente) por perfil de agente (ex.: CEO, PO) nas configs JSON/YAML do Gateway, de forma que a requisição seja limitada **antes** de chegar ao provedor. O pipeline de truncamento e pre-flight Summarize (seção 2.1 e 2.2) reduz o volume na causa raiz; o limite no Gateway é a barreira determinística final.

**Provedor Ollama (local):**

```yaml
# providers/ollama.yaml
provider: ollama
host: http://ollama-service.ai-agents.svc.cluster.local:11434
default_model: deepseek-coder-v2:lite
security_model: llama3:8b
```

**Provedor nuvem (ex.: OpenRouter ou OpenAI):** Consultar a [documentação OpenClaw](https://docs.openclaw.ai) para o formato exato por provedor. Exemplo genérico para OpenRouter (variável `OPENROUTER_API_KEY`) ou OpenAI (`OPENAI_API_KEY`); configurar no Gateway e nos secrets do cluster, nunca em repositório.

### Limite de gastos (provedor em nuvem)

Créditos de nuvem (ex.: OpenRouter, OpenAI, Ollama cloud) têm **data de validade** e **limite de consumo**. Para evitar surpresas na fatura, configurar um **limite rígido de gastos** (freio de emergência) no painel do provedor escolhido (OpenRouter, OpenAI, etc.). O pipeline de truncamento e sumarização de contexto (neste documento) reduz o consumo na causa raiz; o limite de gastos é a proteção final.

### Otimização de custos e hardware

- **Truncamento e sumarização antes da nuvem:** Implementar o pipeline descrito em "Pipeline de truncamento e sumarização de contexto" (truncamento **na borda** por tokens, janela deslizante, memória em duas camadas + RAG). Resumir contexto a cada N mensagens; enviar histórico inteiro em toda chamada ao CEO (nuvem) aumenta a fatura de forma insustentável.
- **Uso de CPU/RAM no host:** Com DevOps + Developer + Architect ativos, 8 threads podem estar ocupadas; evitar sobrecarregar o host (ex.: muitas abas no navegador) para não entrar em swap.
- **Ollama (performance local):** A inferência local sofre gargalos de processamento; reservar ~65% da capacidade da máquina para o cluster e o resto para o sistema operacional evita travamentos. Ver [04-infraestrutura.md](04-infraestrutura.md).
- **Modelos gratuitos em nuvem (OpenRouter):** Se o Diretor quiser usar IA em nuvem sem custo de API, a skill **FreeRide** configura o OpenClaw para modelos gratuitos do OpenRouter com fallbacks automáticos (rate limit). Ver [22-modelos-gratuitos-openrouter-freeride.md](22-modelos-gratuitos-openrouter-freeride.md).
- **NVMe e logs:** Com 200 GB, logs do Kubernetes podem encher o disco em pouco tempo; configurar `logrotate` para manter apenas os últimos ~500 MB.
