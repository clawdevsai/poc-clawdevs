# Memory Compaction e Session Pruning no OpenClaw

## Problema Identificado

Quando um agente OpenClaw está consumindo muitos tokens e o contexto explode, existem **duas estratégias principais e complementares** para otimizar:

1. **Session Pruning** - Remove dados antigos de ferramentas do contexto *antes* do modelo ver
2. **Memory Compaction** - Sumariza conversas antigas e as armazena de forma persistente

Ambas funcionam em camadas diferentes e devem ser usadas **juntas** para máxima eficiência.

---

## Strategy 1: Session Pruning (Redução em Tempo Real)

### O que é?

Session pruning **remove resultados de ferramentas envelhecidos do contexto enviado ao modelo** sem modificar o histórico salvo em disco. Ele atua na memória, por requisição.

**Importante**: Pruning `NÃO` muda as transcrições armazenadas - apenas o que o modelo vê em cada chamada.

### Como Ativar

#### Método 1: Configuração Automática (Recomendado)

```json
{
  "agents": {
    "defaults": {
      "contextPruning": {
        "mode": "cache-ttl",
        "ttl": "5m"
      }
    }
  }
}
```

**Trigger automático**: Quando o tempo desde a última chamada para Anthropic exceder o TTL configurado.

#### Método 2: Configuração Granular

```json
{
  "agents": {
    "defaults": {
      "contextPruning": {
        "mode": "cache-ttl",
        "ttl": "5m",
        "keepLastAssistants": 3,
        "softTrimRatio": 0.3,
        "hardClearRatio": 0.5,
        "minPrunableToolChars": 50000,
        "softTrim": {
          "maxChars": 4000,
          "headChars": 1500,
          "tailChars": 1500
        },
        "tools": {
          "allow": ["exec", "read"],
          "deny": ["*image*"]
        }
      }
    }
  }
}
```

### Parâmetros Explicados

| Parâmetro | Padrão | Propósito |
|-----------|--------|----------|
| `mode` | `off` | `cache-ttl` ativa pruning baseado em TTL |
| `ttl` | `5m` | Tempo de vida do cache Anthropic antes de re-cachear |
| `keepLastAssistants` | `3` | Mantém últimas 3 respostas do assistente (nunca prune) |
| `softTrimRatio` | `0.3` | Threshold para soft-trim em vez de hard-clear |
| `minPrunableToolChars` | `50k` | Só prune se resultado de ferramenta > 50KB |
| `softTrim.maxChars` | `4000` | Tamanho máximo após trim (head + tail) |
| `softTrim.headChars` | `1500` | Caracteres mantidos no início |
| `softTrim.tailChars` | `1500` | Caracteres mantidos no fim |

### Estratégias de Trim

#### Soft-Trim (Padrão para Resultados Pequenos)
Mantém início + fim, insere ellipsis + metadata:

```
[Original tool result: 125,000 chars]

...{TRIMMED: kept head 1500 chars + tail 1500 chars, removed middle 122,000 chars}...

[End of original tool result]
```

**Quando usa**: Resultado < `hardClearRatio` (50%) do máximo permitido

#### Hard-Clear (Para Resultados Enormes)
Replace completo:

```
[Old tool result content cleared]
```

**Quando usa**: Resultado > `hardClearRatio` (50%) do máximo permitido

### Exemplo Prático: Agente com Muitos Reads

Problema: Seu agente executa 50+ `read` calls em arquivos grandes durante investigação.

**Configuração otimizada**:

```json
{
  "agents": {
    "defaults": {
      "contextPruning": {
        "mode": "cache-ttl",
        "ttl": "5m",
        "keepLastAssistants": 5,
        "softTrim": {
          "maxChars": 2000,
          "headChars": 800,
          "tailChars": 800
        },
        "tools": {
          "deny": ["read"]
        }
      }
    }
  }
}
```

**Efeito**: Resultados de `read` tool nunca são prunidos - são críticos. Outros resultados são trimados agressivamente (max 2KB cada).

### Desativar Pruning

```json
{
  "agents": {
    "defaults": {
      "contextPruning": {
        "mode": "off"
      }
    }
  }
}
```

---

## Strategy 2: Memory Compaction (Sumarização Persistente)

### O que é?

Memory compaction **sumariza conversas antigas em textos curtos** que são salvos permanentemente na sessão. Quando compactação ocorre, as mensagens antigas são substituídas por um resumo.

**Diferença de Pruning**: Compaction **modifica** o que está armazenado em disco; pruning apenas afeta a leitura.

### Como Ativar

#### Método 1: Automático (Recomendado)

Compactação automática ativa quando o contexto fica próximo ao limite:

```json
{
  "agents": {
    "defaults": {
      "compaction": {
        "enabled": true,
        "model": "claude-opus-4-5-20250805"
      }
    }
  }
}
```

#### Método 2: Manual (Durante Conversas)

Em qualquer chat com o agente:

```
/compact
```

Com instruções customizadas:

```
/compact Sumarize apenas decisões e recomendações chave
```

### Parâmetros de Compaction

```json
{
  "agents": {
    "defaults": {
      "compaction": {
        "enabled": true,
        "model": "claude-opus-4-5-20250805",
        "identifierPolicy": "strict"
      }
    }
  }
}
```

**Identifier Policy**:
- `"strict"` (padrão): Preserva nomes e IDs de usuários, funcões, etc.
- `"off"`: Anonimiza completamente
- `"custom"`: Regras customizadas

### O Que Happens During Compaction

1. **Trigger**: Contexto atinge ~80% da capacidade
2. **Turno Silent**: Um agente silencioso executa a sumarização
3. **Persistência**: Resumo é salvo no arquivo JSONL da sessão
4. **Output**: `NO_REPLY` (não responde ao usuário)
5. **Memory Flush**: Antes da compactação, o agente tenta salvar memórias duráveis em `MEMORY.md`

### Exemplo: Sessão de Investigação Longa

Você tem uma sessão de debug que rodou por 200+ mensagens.

**Configuração**:

```json
{
  "agents": {
    "defaults": {
      "compaction": {
        "enabled": true,
        "model": "claude-opus-4-5-20250805",
        "identifierPolicy": "strict"
      },
      "contextPruning": {
        "mode": "cache-ttl",
        "ttl": "3m"
      }
    }
  }
}
```

**O que acontece**:
- Primeiras 150 mensagens → sumarizadas (compactadas)
- Ultimas 50 mensagens → contexto ativo
- Tool results > 50KB → soft-trimmed (pruning)
- Modelo recebe: [Resumo (5KB)] + [Últimas 50 mensagens] + [Trimmed tools]

### Quando Compactar Manualmente

**Sinais**:
```
/context list
```

Se você vir:
- `Context usage: 85%+`
- Muitos `toolResult` messages antigas
- Sessão tem 100+ turnos

**Ação**:
```
/compact
```

Ou com objetivo específico:
```
/compact Preserve only the bug findings and reproduction steps
```

---

## Strategy 3: Combinação Ideal (Recomendado)

Use **ambas as estratégias juntas** para máxima eficiência:

```json
{
  "agents": {
    "defaults": {
      "contextPruning": {
        "mode": "cache-ttl",
        "ttl": "5m",
        "keepLastAssistants": 3,
        "softTrim": {
          "maxChars": 3000,
          "headChars": 1200,
          "tailChars": 1200
        }
      },
      "compaction": {
        "enabled": true,
        "model": "claude-opus-4-5-20250805",
        "identifierPolicy": "strict"
      }
    }
  }
}
```

### Como Trabalham Juntas

```
TURNO 1-50:     Contexto normal (tudo visível)
                ↓
TURNO 51:       Contexto 75% cheio
                ↓
TURNO 52:       Compaction automática
                - Mensagens 1-40 → sumarizadas
                - Mensagens 41-51 + resumo mantidos
                ↓
TURNO 53:       Novo usuário input
                - Pruning remove tool results > 50KB
                - Sumarização já ocorreu (ganho permanente)
                ↓
TURNO 54-100:   Contexto seguro (nunca explode)
```

---

## Monitoramento e Diagnóstico

### Verificar Status Atual

```bash
openclaw status
```

Mostra:
- Caminho de sessões
- Sessões recentes

### Contexto em Tempo Real

No chat:

```
/status
```

Output:
```
Context usage: 62%
Session: agent:coding:main
Files injected: SOUL.md, AGENTS.md, ...
Recent compactions: 2024-03-15 15:30:00
```

### Detalhe Completo

```
/context detail
```

Mostra breakdown por categoria:
- System prompt: 8,500 tokens
- Conversation history: 24,300 tokens
- Tool results: 15,200 tokens
- Bootstrap files: 3,100 tokens
- **Total: 51,100 / 80,000 (64%)**

### Sessões Persistentes

Listar todas com tamanhos:

```bash
openclaw sessions --json | jq '.[] | {key, messageCount, sizeBytes}'
```

Limpar antigas manualmente:

```bash
rm ~/.openclaw/agents/<agentId>/sessions/<SessionId>.jsonl
```

---

## Troubleshooting

### Problema: Tokens Ainda Explodindo Mesmo com Pruning

**Causa**: Pruning só afeta `toolResult` messages, não conversas.

**Solução**: Force compaction manual:

```
/compact Remove old conversation history, keep only recent findings
```

### Problema: Compaction Está Removendo Detalhes Importantes

**Causa**: Modelo sumariando agressivamente.

**Solução**: Use `identifierPolicy` e instruções:

```json
{
  "compaction": {
    "enabled": true,
    "model": "claude-opus-4-5-20250805",
    "identifierPolicy": "strict"
  }
}
```

E chame:
```
/compact Preserve all specific error messages and stack traces verbatim
```

### Problema: Sessão Muito Lenta Após Compaction

**Causa**: Modelo sumariador processando contexto grande.

**Solução**: Use modelo mais rápido:

```json
{
  "compaction": {
    "model": "claude-haiku-4-5-20251001"
  }
}
```

### Problema: Memória Permanente Não Está Salvando

**Causa**: `MEMORY.md` não existente ou read-only.

**Solução**: Criar manualmente:

```bash
touch ~/.openclaw/workspace/MEMORY.md
chmod 644 ~/.openclaw/workspace/MEMORY.md
```

Depois, no chat:
```
Remember: [important fact]
```

---

## Best Practices

1. **Pruning para Read-Heavy Agents**
   - Use `tools.deny: ["read"]` para não prunir reads críticos
   - `ttl: "3m"` para re-cachear rápido com prompt caching

2. **Compaction para Long-Running Sessions**
   - Enable automático
   - Chame `/compact` manualmente a cada 100+ mensagens

3. **Memory para Aprendizado Persistente**
   - Escreva em `MEMORY.md` fatos importantes
   - Use `memory_search` para recall semântico

4. **Monitoramento**
   - Check `/status` a cada 50 mensagens
   - Use `/context detail` se context > 70%

5. **Modelos**
   - Compaction: Use Opus (melhor qualidade)
   - Agent: Use seu modelo preferido (mais rápido)

---

## Resumo de Configuração Produção-Ready

```json
{
  "agents": {
    "defaults": {
      "contextPruning": {
        "mode": "cache-ttl",
        "ttl": "5m",
        "keepLastAssistants": 3,
        "minPrunableToolChars": 50000,
        "softTrim": {
          "maxChars": 3000,
          "headChars": 1200,
          "tailChars": 1200
        },
        "tools": {
          "allow": ["exec", "read"]
        }
      },
      "compaction": {
        "enabled": true,
        "model": "claude-opus-4-5-20250805",
        "identifierPolicy": "strict"
      },
      "memorySearch": {
        "provider": "gemini",
        "model": "gemini-embedding-2-preview",
        "query": {
          "hybrid": {
            "enabled": true,
            "mmr": { "enabled": true, "lambda": 0.7 }
          }
        }
      }
    }
  }
}
```

Salve em `~/.openclaw/openclaw.json` e recarregue o gateway:

```bash
openclaw gateway restart
```

---

## Comandos Rápidos

| Situação | Comando |
|----------|---------|
| Ver uso de contexto agora | `/status` |
| Ver breakdown detalhado | `/context detail` |
| Sumarizar sessão | `/compact` |
| Iniciar nova sessão | `/new` |
| Resetar contexto | `/reset` |
| Parar execução | `/stop` |
| Listar todas sessões | `openclaw sessions --json` |
| Deletar sessão antiga | `rm ~/.openclaw/agents/<id>/sessions/<key>.jsonl` |

---

## Conclusão

**O segredo para não explodir tokens**:

1. ✅ **Pruning automático** (`mode: cache-ttl`) → Remove tool results antigos
2. ✅ **Compaction automático** (`enabled: true`) → Sumariza conversas
3. ✅ **Memory durável** → Salva aprendizados em `MEMORY.md`
4. ✅ **Monitoramento** → `/status` regularmente
5. ✅ **Ação manual** → `/compact` quando context > 70%

Com essa combinação, você pode manter sessões rodando indefinidamente sem explosion de tokens.
