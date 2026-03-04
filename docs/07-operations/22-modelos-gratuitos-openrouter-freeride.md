# Modelos gratuitos OpenRouter (FreeRide)

Os agentes do enxame podem **configurar e usar modelos de IA gratuitos** do OpenRouter no OpenClaw por meio da skill **FreeRide**: ranking automático de modelos por qualidade, fallbacks para rate limit e atualização de `openclaw.json`. Este documento define quando usar, pré-requisitos, comandos e quem pode executá-los, alinhado à **postura Zero Trust** e à gestão de custos em [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md).

**Segurança:** FreeRide altera apenas as chaves de modelo em `~/.openclaw/openclaw.json` (`agents.defaults.model`, `agents.defaults.models`). Credenciais (OPENROUTER_API_KEY) não devem ser expostas em chat ou logs; ver [05-seguranca-e-etica.md](05-seguranca-e-etica.md) e [14-seguranca-runtime-agentes.md](14-seguranca-runtime-agentes.md).

---

## O que esta habilidade faz

- **Configura o OpenClaw** para usar modelos **gratuitos** do OpenRouter.
- **Rankeia** os modelos gratuitos disponíveis (contexto, capacidades, recência, confiança no provedor) e define o melhor como primário.
- **Configura fallbacks** para que, ao atingir rate limit, o OpenClaw troque automaticamente para o próximo modelo.
- **Preserva** o resto da configuração (gateway, canais, plugins, env, customInstructions, agentes nomeados).

O FreeRide opcionalmente oferece um **watcher** (daemon) para rotação automática quando houver rate limit.

**Roteamento hierárquico unificado (evitar deadlock):** Se o FreeRide atingir o limite de taxa **exatamente quando** a GPU local estiver bloqueada pelo GPU Lock (ex.: Developer validando compilação), pode ocorrer deadlock ou perda de estado. A config do OpenClaw deve padronizar um **protocolo de roteamento hierárquico**: unificar disponibilidade da nuvem, fila da GPU local e **CPU como última via**. Em `agents.defaults.model.fallbacks` incluir não só modelos alternativos do OpenRouter, mas o **último fallback estrutural** para um modelo local leve em **CPU apenas** (ex.: Phi-3 Mini). **Atenção:** fallback em CPU é último recurso — risco de memória e degradação de inferência com nove agentes + Kubernetes + Redis + LLM na CPU; quando não for viável forçar CPU, usar o hook de recuperação abaixo.

**Roteamento preditivo para orçamento:** Quando o sistema **prever** risco de estouro do orçamento diário (ex.: heurística baseada no tamanho do diff do PR ou no histórico de tokens da tarefa), **rotear a tarefa para modelo local em CPU** antes de acionar o freio de emergência ($5/dia) ou o Telegram. Complementa o fallback hierárquico e mantém a esteira funcionando sem travar a sprint. Ver [05-seguranca-e-etica.md](05-seguranca-e-etica.md) e [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md).

**Hook de recuperação (script FreeRide / watcher):** Quando **nuvem e GPU local estiverem saturadas**, o script ou daemon FreeRide (ex.: `script-free-ride-auto`, `freeride-watcher`) deve instruir o OpenClaw a **pausar a fila do Sessions-Spawn** — evita deadlock fatal e loop infinito. O orquestrador age como "maestro" da estafa física do sistema.

**Estado de pausa no LanceDB:** Ao pausar um sub-agente por saturação, o OpenClaw **serializa a árvore de raciocínio** (estado da conversa) e persiste no **LanceDB** (warm store, já usado pela memória Elite — ver [28-memoria-longo-prazo-elite.md](28-memoria-longo-prazo-elite.md)). O sub-agente fica em "coma controlado". Quando o Redis sinaliza a **deleção do GPU Lock** (outro agente liberou a GPU), o orquestrador **recupera o estado do LanceDB** e o agente continua do ponto exato da pausa. Assim o enxame não trava e o contexto não se perde.

---

## Quando usar

Usar quando o Diretor ou o time:

- Mencionar **IA gratuita**, **OpenRouter**, **redução de custos** com modelos em nuvem.
- Quiser **troca de modelo** (model switching) ou **fallbacks** para não interromper em rate limit.
- Pedir "usar modelos grátis" ou "deixar de pagar por API" no OpenClaw.

Não substitui o pipeline de truncamento e controle de custo (ver [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md)); **complementa** ao permitir uso de tier gratuito do OpenRouter quando for a escolha do Diretor.

---

## Pré-requisitos

1. **OPENROUTER_API_KEY** definida. Chave gratuita em https://openrouter.ai/keys. Verificar com `echo $OPENROUTER_API_KEY`; se vazia, o usuário deve definir:
   ```bash
   export OPENROUTER_API_KEY="sk-or-v1-..."
   # Ou persistir no OpenClaw:
   openclaw config set env.OPENROUTER_API_KEY "sk-or-v1-..."
   ```
2. **CLI `freeride`** instalada. Verificar com `which freeride`. Se não existir, a instalação é via ecossistema OpenClaw/ClawHub (ver [19-descoberta-instalacao-skills.md](19-descoberta-instalacao-skills.md)): instalar somente após checklist de segurança e aprovação do Diretor.

---

## Fluxo principal

Quando o Diretor quiser IA gratuita configurada:

```bash
# 1. Configurar melhor modelo gratuito + fallbacks
freeride auto

# 2. Reiniciar o gateway para o OpenClaw aplicar as mudanças
openclaw gateway restart
```

Validar com o usuário enviando `/status` para conferir o modelo ativo.

**Após qualquer comando que altere a config, executar `openclaw gateway restart`.**

---

## Referência de comandos

| Comando | Quando usar |
|---------|-------------|
| `freeride auto` | Diretor quer IA gratuita configurada (caso mais comum) |
| `freeride auto -f` | Quer fallbacks mas manter o modelo primário atual |
| `freeride auto -c 10` | Quer mais fallbacks (padrão é 5) |
| `freeride list` | Ver modelos gratuitos disponíveis |
| `freeride list -n 30` | Listar todos os modelos gratuitos |
| `freeride switch <model>` | Usar um modelo específico (ex.: `freeride switch qwen3-coder`) |
| `freeride switch <model> -f` | Adicionar modelo só como fallback |
| `freeride status` | Ver configuração atual do FreeRide |
| `freeride fallbacks` | Atualizar apenas os fallbacks |
| `freeride refresh` | Forçar atualização do cache de modelos |

### Watcher (opcional)

Para rotação automática em rate limit:

```bash
freeride-watcher --daemon    # Monitoramento contínuo
freeride-watcher --rotate    # Forçar rotação agora
freeride-watcher --status    # Histórico de rotações
```

---

## O que é escrito na config

O FreeRide altera apenas em `~/.openclaw/openclaw.json`:

- `agents.defaults.model.primary` — ex.: `openrouter/qwen/qwen3-coder:free`
- `agents.defaults.model.fallbacks` — ex.: `["openrouter/free", "nvidia/nemotron:free", ...]`; incluir **último fallback estrutural** para modelo local em CPU (ex.: `ollama/phi3:mini` com node selector CPU) para evitar deadlock quando nuvem e GPU estiverem saturadas.
- `agents.defaults.models` — allowlist para o comando `/model` mostrar os modelos gratuitos

O primeiro fallback é sempre `openrouter/free` (roteador inteligente do OpenRouter). O restante da config (gateway, canais, plugins, env, customInstructions, agentes nomeados) é preservado. Para **recuperação de estado** quando a fila for pausada por saturação, o estado é persistido no LanceDB e recuperado ao liberar o GPU Lock (ver seção "Roteamento hierárquico" e "Estado de pausa no LanceDB" acima).

---

## Quem pode usar

| Agente | Sugerir uso | Executar freeride / restart gateway |
|--------|-------------|-------------------------------------|
| **CEO** | Sim (estratégia de custo) | Não — escalar ao Diretor/DevOps. |
| **PO** | Sim | Não. |
| **DevOps/SRE** | Sim | Sim, após aprovação do Diretor para mudança de modelo em produção. |
| **Outros** | Podem mencionar a opção | Não — apenas DevOps (ou Diretor) altera config do OpenClaw. |

A execução de `freeride` e `openclaw gateway restart` deve ser feita por quem tem permissão operacional sobre o ambiente OpenClaw (ex.: DevOps), em alinhamento com o Diretor.

---

## FreeRide e descoberta de skills no fluxo do PO

- **FreeRide:** O PO pode **sugerir** ao Diretor reduzir custo com modelos gratuitos (ex.: "configurar IA gratuita para tarefas de prototipagem"); a decisão e a execução são do **Diretor** e do **DevOps** (após aprovação). O PO não executa `freeride` nem altera config; mantém o backlog alinhado a orçamento e prioridade. Quando o Diretor aprovar, o DevOps configura FreeRide conforme este doc e reinicia o gateway.
- **Descoberta de skills:** Quando uma tarefa priorizada pelo PO exigir uma capacidade que pode ser coberta por uma **skill** (ex.: busca web, integração com API), o agente que pegar a tarefa usa [19-descoberta-instalacao-skills.md](19-descoberta-instalacao-skills.md): busca skills, apresenta opções ao Diretor e só instala após checklist e aprovação. O PO está ciente de que tarefas que dependem de skill nova podem ficar em "aguardando aprovação" até o Diretor aprovar a instalação; o backlog não perde a tarefa.
- **Criação de skills:** Se não houver skill no ecossistema e a necessidade for recorrente, registrar em `.learnings/FEATURE_REQUESTS.md` e seguir [29-criacao-de-skills.md](29-criacao-de-skills.md); o PO pode priorizar a criação como tarefa quando o Diretor concordar.

---

## Relação com a documentação

- [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md) — Causa raiz do custo (inchaço de contexto), pipeline de truncamento, perfis por agente; FreeRide é uma opção para uso de tier gratuito OpenRouter quando o Diretor optar por reduzir custo com modelos gratuitos.
- [19-descoberta-instalacao-skills.md](19-descoberta-instalacao-skills.md) — FreeRide é uma skill do ecossistema OpenClaw/ClawHub; descoberta e instalação seguem o fluxo de proposta ao Diretor e checklist de segurança (Zero Trust).
- [21-auto-atualizacao-ambiente.md](21-auto-atualizacao-ambiente.md) — Atualização de skills já instaladas (incluindo FreeRide) pode ser feita pela rotina de auto-atualização; instalação inicial de FreeRide segue o fluxo de descoberta e aprovação.
- [05-seguranca-e-etica.md](05-seguranca-e-etica.md) — Credenciais e regras de instalação de skills de terceiros.
- [14-seguranca-runtime-agentes.md](14-seguranca-runtime-agentes.md) — Validação pré-execução de comandos (incluindo `freeride` e `openclaw`).
