# Ollama Local (skill)

Os agentes do enxame podem **gerenciar e usar modelos Ollama locais** para inferência, embeddings e tool-use com LLMs locais. Este documento descreve as habilidades incorporadas do skill **ollama-local**: gestão de modelos (listar/puxar/remover), chat/completions, embeddings, tool-use e integração com sub-agentes OpenClaw (sessions_spawn). Alinhado a [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md) (perfis por agente que usam Ollama) e a [19-descoberta-instalacao-skills.md](19-descoberta-instalacao-skills.md) (instalação após Zero Trust).

**Quem usa:** DevOps (gestão de modelos, saúde do host), Developer/Architect/QA/CyberSec/UX (modelos locais nos pods); CEO/PO quando precisam de sub-agentes locais para tarefas especializadas.

---

## Configuração

Definir o host do Ollama (padrão `http://localhost:11434`):

```bash
export OLLAMA_HOST="http://localhost:11434"
# Ou servidor remoto:
export OLLAMA_HOST="http://192.168.1.100:11434"
```

O cluster usa o mesmo endpoint e GPU Lock (ver [03-arquitetura.md](03-arquitetura.md) e [09-setup-e-scripts.md](09-setup-e-scripts.md)).

---

## Referência rápida (scripts do skill)

Quando o skill **ollama-local** estiver instalado, os agentes podem usar:

| Ação | Comando (exemplo) |
|------|-------------------|
| Listar modelos | `python3 scripts/ollama.py list` |
| Puxar modelo | `python3 scripts/ollama.py pull llama3.1:8b` |
| Remover modelo | `python3 scripts/ollama.py rm modelname` |
| Detalhes do modelo | `python3 scripts/ollama.py show qwen3:4b` |
| Chat | `python3 scripts/ollama.py chat qwen3:4b "Pergunta"` |
| Chat com system prompt | `python3 scripts/ollama.py chat llama3.1:8b "Revisar este código" -s "Você é revisor de código"` |
| Completions (não-chat) | `python3 scripts/ollama.py generate qwen3:4b "Texto"` |
| Embeddings | `python3 scripts/ollama.py embed bge-m3 "Texto para embed"` |

---

## Seleção de modelos

**Por tipo de tarefa:**

- **CEO Telegram (respostas curtas):** `stewyphoenix19/phi3-mini_v1:latest` (config atual), ou `phi3:mini`, `qwen2.5:3b`, `qwen3:4b` — modelo leve, contextWindow 4096, maxTokens 512–1024 no OpenClaw. Ver [37-deploy-fase0-telegram-ceo-ollama.md](37-deploy-fase0-telegram-ceo-ollama.md) (Otimização de latência).
- **Respostas rápidas:** `qwen3:4b`
- **Código:** `qwen2.5-coder:7b`
- **Uso geral:** `llama3.1:8b`
- **Raciocínio:** `deepseek-r1:8b` ou `phi4-reasoning:latest`
- **Criativo/design:** `gemma3:12b`
- **Embeddings:** `bge-m3:latest`

**Por recurso:** Em máquinas com ~8GB VRAM, modelos até ~13B; com 16GB VRAM, modelos maiores. Ollama faz offload para CPU/RAM quando necessário; modelos maiores podem ficar mais lentos.

---

## Tool-use (function calling)

Alguns modelos locais suportam function calling. Com o skill instalado, usar `ollama_tools.py`:

```bash
# Uma requisição com tools
python3 scripts/ollama_tools.py single qwen2.5-coder:7b "Qual o tempo em Amsterdam?"

# Loop completo (modelo chama tools, recebe resultados, responde)
python3 scripts/ollama_tools.py loop qwen3:4b "Buscar tutoriais Python e resumir"

# Listar tools de exemplo
python3 scripts/ollama_tools.py tools
```

**Modelos com boa suporte a tools:** qwen2.5-coder, qwen3, llama3.1, mistral.

---

## Sub-agentes OpenClaw (sessions_spawn)

É possível spawnar sub-agentes com modelos Ollama locais via `sessions_spawn`. Em cenários de **alta concorrência** (FreeRide em rate limit e GPU bloqueada), o orquestrador pode **pausar a fila** do Sessions-Spawn; o estado do sub-agente é **serializado e persistido no LanceDB** (warm store) até a GPU ser liberada; ao receber do Redis o evento de liberação do GPU Lock, o estado é recuperado e o agente continua do ponto exato. Ver [22-modelos-gratuitos-openrouter-freeride.md](22-modelos-gratuitos-openrouter-freeride.md) (roteamento hierárquico e estado de pausa).

**Formato do modelo:** `ollama/<nome-do-modelo>`

Exemplo:

```python
sessions_spawn(
    task="Revisar este código Python em busca de bugs",
    model="ollama/qwen2.5-coder:7b",
    label="code-review"
)
```

**Perfil de auth:** OpenClaw exige um perfil mesmo para Ollama (sem auth real). Em `auth-profiles.json`:

```json
"ollama:default": {
  "type": "api_key",
  "provider": "ollama",
  "key": "ollama"
}
```

### Padrão Think Tank (agentes em paralelo)

Vários agentes locais em tarefas colaborativas:

```python
agents = [
    {"label": "architect", "model": "ollama/gemma3:12b", "task": "Desenhar a arquitetura do sistema"},
    {"label": "coder", "model": "ollama/qwen2.5-coder:7b", "task": "Implementar a lógica principal"},
    {"label": "reviewer", "model": "ollama/llama3.1:8b", "task": "Revisar bugs e melhorias"},
]
for a in agents:
    sessions_spawn(task=a["task"], model=a["model"], label=a["label"])
```

---

## API direta (integrações custom)

Para integrações que não usem os scripts do skill:

```bash
# Chat
curl $OLLAMA_HOST/api/chat -d '{"model":"qwen3:4b","messages":[{"role":"user","content":"Olá"}],"stream":false}'

# Generate
curl $OLLAMA_HOST/api/generate -d '{"model":"qwen3:4b","prompt":"Por que o céu é azul?","stream":false}'

# Listar modelos
curl $OLLAMA_HOST/api/tags

# Puxar modelo
curl $OLLAMA_HOST/api/pull -d '{"name":"phi3:mini"}'
```

---

## Troubleshooting

| Problema | Ação |
|----------|------|
| Connection refused | Verificar se Ollama está rodando (`ollama serve`), OLLAMA_HOST correto, firewall (porta 11434) em servidor remoto. |
| Modelo não carrega | Verificar VRAM; tentar modelo menor ou offload em CPU. |
| Respostas lentas | Modelo pode estar em CPU; usar quantização menor (ex.: `:7b` em vez de `:30b`). |
| Sub-agente OpenClaw usa modelo padrão | Garantir perfil `ollama:default` em auth-profiles e formato `ollama/modelname:tag`. |

---

## Segurança e alinhamento

- **Zero Trust:** Instalação do skill ollama-local segue o fluxo de [19-descoberta-instalacao-skills.md](19-descoberta-instalacao-skills.md) e checklist em [05-seguranca-e-etica.md](05-seguranca-e-etica.md).
- **Recursos:** Uso de modelos locais deve respeitar o limite do host (ex.: 65% no cluster). **Integração com GPU Lock:** agentes locais (Developer, Architect, QA, CyberSec, UX) adquirem o lock ([scripts/gpu_lock.py](../scripts/gpu_lock.py)) antes de chamar o Ollama; ao terminar, liberam o lock. O slot de revisão pós-dev adquire o lock uma vez e executa as etapas em sequência. Ver [04-infraestrutura.md](04-infraestrutura.md) e [06-operacoes.md](06-operacoes.md).
- **Auto-atualização:** Atualização de skills (incluindo ollama-local) pelo DevOps conforme [21-auto-atualizacao-ambiente.md](21-auto-atualizacao-ambiente.md).
