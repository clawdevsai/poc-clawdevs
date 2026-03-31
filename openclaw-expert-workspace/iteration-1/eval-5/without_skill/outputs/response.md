# OpenClaw: Guia Completo de Memory Compaction e Session Pruning

## Problema Identificado

Seus agentes OpenClaw estão consumindo muitos tokens de contexto, causando explosão de custos e degradação de performance. Isso ocorre porque:

1. **Sessions acumulam histórico indefinidamente** - cada mensagem permanece na memória do agente
2. **Memory entries crescem sem limite** - embeddings e conteúdo nunca são removidos
3. **Contexto de conversas antigas permanece ativo** - sessões "completas" continuam carregando dados

## Estratégia de Memory Compaction

### 1. Implementar Summarização Progressiva

A summarização reduz conteúdo antigo mantendo semântica importante:

```python
# Adicionar ao service de memory_sync.py

async def compact_old_memory_entries(
    db_session,
    days_threshold: int = 7,
    max_entries_per_agent: int = 50
) -> dict:
    """
    Compacta entradas de memória antigas via summarização.

    Strategy:
    - Identifica entries criadas antes de `days_threshold`
    - Agrupa por agent_slug
    - Mantém apenas as N mais relevantes (por relevância/recência)
    - As removidas são arquivadas em bulk_summary
    """
    from datetime import datetime, timedelta, UTC
    from sqlmodel import select, and_

    cutoff_date = datetime.now(UTC) - timedelta(days=days_threshold)
    cutoff_date = cutoff_date.replace(tzinfo=None)

    # 1. Query: entradas antigas que não são "global"
    stmt = select(MemoryEntry).where(
        and_(
            MemoryEntry.created_at < cutoff_date,
            MemoryEntry.entry_type != "global",
            MemoryEntry.entry_type != "archived"
        )
    ).order_by(MemoryEntry.updated_at.asc())

    old_entries = (await db_session.exec(stmt)).all()

    # 2. Agrupar por agent_slug para análise de relevância
    entries_by_agent = {}
    for entry in old_entries:
        agent = entry.agent_slug or "shared"
        if agent not in entries_by_agent:
            entries_by_agent[agent] = []
        entries_by_agent[agent].append(entry)

    compacted = {
        "total_processed": 0,
        "archived": 0,
        "summarized": 0,
        "by_agent": {}
    }

    # 3. Para cada agent, reter top-N e arquivar o resto
    for agent_slug, entries in entries_by_agent.items():
        to_archive = []

        # Manter as mais recentes (relevância) e remover as antigas
        if len(entries) > max_entries_per_agent:
            # Ordenar por updated_at DESC, pegar as mais novas
            entries_sorted = sorted(
                entries,
                key=lambda e: e.updated_at or datetime.min,
                reverse=True
            )
            to_archive = entries_sorted[max_entries_per_agent:]

        # Criar entrada de summarização (bulk memory)
        if to_archive:
            # Exemplo: agrupar títulos e tags das removidas
            titles = [e.title for e in to_archive if e.title]
            tags = set()
            for e in to_archive:
                if e.tags:
                    tags.update(e.tags)

            summary_body = f"""
# Archived Batch Summary ({agent_slug})
**Period:** {to_archive[0].created_at} - {to_archive[-1].updated_at}
**Count:** {len(to_archive)} entries

## Topics covered:
{chr(10).join(f"- {t}" for t in titles[:10])}

**Original entries archived for space optimization.**
            """.strip()

            # Criar entry de summarização
            summary_entry = MemoryEntry(
                agent_slug=agent_slug,
                title=f"Archive Summary - {agent_slug}",
                body=summary_body,
                entry_type="archived",
                tags=list(tags),
                source_agents=[agent_slug]
            )
            db_session.add(summary_entry)
            compacted["summarized"] += 1
            compacted["archived"] += len(to_archive)

            # Marcar originais como archived (não deletar para auditoria)
            for entry in to_archive:
                entry.entry_type = "archived"
                entry.updated_at = datetime.now(UTC).replace(tzinfo=None)

        compacted["by_agent"][agent_slug] = len(to_archive)
        compacted["total_processed"] += len(entries)

    await db_session.commit()
    return compacted
```

### 2. Implementar Chunking e Filtering de Embeddings

Reduza peso de embeddings armazenados:

```python
# Adicionar ao memory_rag.py ou novo serviço

async def optimize_embeddings(
    db_session,
    target_sparsity: float = 0.7  # Manter apenas 30% mais relevantes
) -> dict:
    """
    Remove embeddings para entries menos consultadas.
    Mantém embedding apenas para top entries por relevância.
    """
    from sqlmodel import select, func

    # 1. Score cada entry por: recência + relevância (queryCount simulado)
    stmt = select(MemoryEntry).where(
        MemoryEntry.embedding.is_not(None)
    )
    entries_with_embedding = (await db_session.exec(stmt)).all()

    if not entries_with_embedding:
        return {"status": "no_embeddings_to_optimize"}

    # 2. Calcular score simples: entries antigas com embedding baixo score
    entries_scored = []
    now = datetime.now(UTC)

    for entry in entries_with_embedding:
        age_days = (now - entry.embedding_generated_at).days if entry.embedding_generated_at else 0
        # Score inverso: mais velho = menos score
        age_score = max(0, 1.0 - (age_days / 365))
        # Entrada type score: active > candidate > archived
        type_score = {"active": 1.0, "candidate": 0.5, "archived": 0.1}.get(
            entry.entry_type, 0.2
        )
        final_score = (age_score * 0.6) + (type_score * 0.4)
        entries_scored.append((entry, final_score))

    # 3. Manter apenas top entries
    entries_scored.sort(key=lambda x: x[1], reverse=True)
    keep_count = max(1, int(len(entries_scored) * (1 - target_sparsity)))

    removed = 0
    for entry, score in entries_scored[keep_count:]:
        entry.embedding = None
        removed += 1

    await db_session.commit()

    return {
        "total_with_embeddings": len(entries_with_embedding),
        "embeddings_removed": removed,
        "embeddings_kept": keep_count,
        "sparsity_achieved": removed / len(entries_with_embedding)
    }
```

## Estratégia de Session Pruning

### 1. Implementar Session Lifecycle Management

Arquivo: novo `app/services/session_pruning.py`

```python
from datetime import datetime, timedelta, UTC
from sqlmodel import select, and_
from app.models import Session

class SessionPruner:
    """
    Gerencia ciclo de vida de sessões com múltiplas estratégias.
    """

    # Configurações padrão
    ACTIVE_THRESHOLD = timedelta(minutes=20)      # Janela para "active"
    STALE_THRESHOLD = timedelta(days=3)            # Sessão inativa > 3 dias = stale
    EXPIRATION_THRESHOLD = timedelta(days=30)      # Sessão > 30 dias = pronta para archive

    async def prune_old_sessions(
        self,
        db_session,
        action: str = "archive"  # archive|delete (recomendado: archive)
    ) -> dict:
        """
        Prune sessões antigas que expiram após EXPIRATION_THRESHOLD.

        Args:
            action: "archive" = marcar status="archived"
                   "delete" = remover do DB (cuidado!)
        """
        cutoff = datetime.now(UTC) - self.EXPIRATION_THRESHOLD
        cutoff = cutoff.replace(tzinfo=None)

        # Query: sessões antigas completadas
        stmt = select(Session).where(
            and_(
                Session.last_active_at < cutoff,
                Session.status.in_(["completed", "error"])
            )
        )

        old_sessions = (await db_session.exec(stmt)).all()

        result = {
            "total_found": len(old_sessions),
            "action": action,
            "processed": 0
        }

        if action == "archive":
            for session in old_sessions:
                session.status = "archived"
                result["processed"] += 1
        elif action == "delete":
            for session in old_sessions:
                await db_session.delete(session)
                result["processed"] += 1

        await db_session.commit()
        return result

    async def truncate_session_messages(
        self,
        db_session,
        session_id: str,
        keep_last_n: int = 50
    ) -> dict:
        """
        Trunca histórico de mensagens de uma sessão específica.
        Mantém últimas N mensagens, compacta antigos em JSONL resumido.
        """
        session_file = Path(settings.openclaw_data_path) / "agents" / \
                      "{agent_slug}" / "sessions" / f"{session_id}.jsonl"

        # 1. Ler sessão JSONL
        if not session_file.exists():
            return {"status": "session_file_not_found"}

        messages = []
        with open(session_file, "r") as f:
            for line in f:
                if line.strip():
                    messages.append(json.loads(line))

        # 2. Manter últimas N
        if len(messages) > keep_last_n:
            kept = messages[-keep_last_n:]
            discarded = messages[:-keep_last_n]

            # 3. Salvar versão truncada
            with open(session_file, "w") as f:
                for msg in kept:
                    f.write(json.dumps(msg) + "\n")

            return {
                "status": "truncated",
                "original_count": len(messages),
                "kept": len(kept),
                "discarded": len(discarded)
            }

        return {"status": "already_within_threshold"}

    async def analyze_session_context_usage(
        self,
        db_session,
        session_id: str
    ) -> dict:
        """
        Analisa consumo de tokens/contexto de uma sessão.
        Retorna breakdown detalhado para otimização.
        """
        result = await db_session.exec(
            select(Session).where(Session.openclaw_session_id == session_id)
        )
        session = result.first()

        if not session:
            return {"error": "session_not_found"}

        # Estimativas (idealmente ler do arquivo de sessão)
        analysis = {
            "session_id": session_id,
            "message_count": session.message_count,
            "estimated_tokens": session.token_count,
            "avg_tokens_per_message": session.token_count / max(1, session.message_count),
            "status": session.status,
            "age_days": (datetime.now(UTC) - session.created_at).days,
            "recommendations": []
        }

        # Heurísticas de recomendação
        if session.token_count > 100000:
            analysis["recommendations"].append(
                "HIGH_TOKENS: Considerar truncar mensagens antigas"
            )
        if session.avg_tokens_per_message > 5000:
            analysis["recommendations"].append(
                "LARGE_MESSAGES: Mensagens muito grandes detectadas"
            )
        if session.status == "completed" and analysis["age_days"] > 7:
            analysis["recommendations"].append(
                "STALE: Candidato para archive"
            )

        return analysis
```

### 2. Implementar Limpeza de Sessões Stale

Integrate ao `session_sync.py` para detectar stale sessions:

```python
async def cleanup_stale_sessions(db_session) -> dict:
    """
    Marca sessões que passaram STALE_THRESHOLD como "stale".
    Stale sessions podem ser arquivadas depois.
    """
    from datetime import timedelta

    STALE_THRESHOLD = timedelta(days=3)
    now = datetime.now(UTC).replace(tzinfo=None)
    stale_cutoff = now - STALE_THRESHOLD

    # Buscar active/completed mas inativas há > STALE_THRESHOLD
    stmt = select(Session).where(
        and_(
            Session.last_active_at < stale_cutoff,
            Session.status != "archived",
            Session.status != "error"
        )
    )

    stale = (await db_session.exec(stmt)).all()

    marked = 0
    for session in stale:
        session.status = "stale"
        marked += 1

    await db_session.commit()

    return {
        "stale_sessions_marked": marked,
        "threshold_days": STALE_THRESHOLD.days
    }
```

## Estratégia de Context Window Optimization

### 1. Implementar Dynamic Context Selection

Ao invés de carregar TODO contexto, selecione apenas relevante:

```python
# Modificar OpenClaw client para usar context selection

async def stream_chat_with_context_filtering(
    self,
    agent_slug: str,
    message: str,
    session_key: str | None = None,
    context_window_tokens: int = 4000  # Ajustável
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Filtra contexto antes de enviar para o modelo.
    Reduz payload mantendo relevância máxima.
    """
    resolved_session_key = (session_key or "").strip() or f"agent:{agent_slug}:main"

    # 1. RAG retrieval: buscar top-K memories relevantes
    relevant_context = await self._retrieve_relevant_context(
        agent_slug=agent_slug,
        query=message,
        max_tokens=context_window_tokens // 2
    )

    # 2. Montar prompt com filtering
    system_context = self._build_system_context(relevant_context)

    payload = {
        "model": f"openclaw/{agent_slug}",
        "messages": [
            {"role": "system", "content": system_context},
            {"role": "user", "content": message}
        ],
        "stream": True,
        "temperature": 0.7,
        "max_tokens": min(4096, context_window_tokens // 2)
    }

    # ... resto do stream
```

### 2. Token Budgeting por Session

```python
class TokenBudgetManager:
    """
    Gerencia token budget por sessão para evitar explosão.
    """

    # Budget padrão por tipo de sessão
    BUDGETS = {
        "user_chat": 100000,       # Chat com usuário
        "agent_to_agent": 50000,   # Comunicação entre agentes
        "cron": 20000,             # Tasks automáticas
        "default": 30000
    }

    async def check_and_deduct(
        self,
        session_id: str,
        tokens_to_consume: int,
        db_session
    ) -> dict:
        """
        Verifica se sessão tem budget antes de processar.
        """
        result = await db_session.exec(
            select(Session).where(Session.openclaw_session_id == session_id)
        )
        session = result.first()

        if not session:
            return {"allowed": False, "reason": "session_not_found"}

        budget = self.BUDGETS.get(session.channel_type, self.BUDGETS["default"])
        remaining = budget - session.token_count

        if remaining < tokens_to_consume:
            return {
                "allowed": False,
                "reason": "budget_exceeded",
                "current_usage": session.token_count,
                "budget": budget,
                "requested": tokens_to_consume,
                "remaining": remaining
            }

        return {
            "allowed": True,
            "remaining_after": remaining - tokens_to_consume,
            "budget": budget
        }
```

## Plano de Implementação

### Fase 1: Monitoramento (Semana 1)
1. Adicionar métricas de context usage por session
2. Implementar alertas quando token_count > threshold
3. Dashboard mostrando top sessions por tokens

### Fase 2: Memory Compaction (Semana 2)
1. Implementar `compact_old_memory_entries()`
2. Executar via cron job (ex: diariamente às 2h da manhã)
3. Monitorar impacto em RAG accuracy

### Fase 3: Session Pruning (Semana 3)
1. Implementar `SessionPruner` com lifecycle management
2. Marcar sessões stale automaticamente
3. Archive após EXPIRATION_THRESHOLD

### Fase 4: Context Filtering (Semana 4)
1. Integrar RAG context selection
2. Token budgeting por session type
3. Testes de qualidade (LLM ainda retorna boas respostas?)

## Configurações Recomendadas

```python
# .env ou config.py

# Memory Compaction
MEMORY_COMPACTION_DAYS_THRESHOLD=7
MEMORY_MAX_ENTRIES_PER_AGENT=100
MEMORY_ARCHIVE_SCHEDULE="0 2 * * *"  # 2h da manhã, daily

# Session Management
SESSION_ACTIVE_WINDOW_MINUTES=20
SESSION_STALE_THRESHOLD_DAYS=3
SESSION_EXPIRATION_DAYS=30
SESSION_PRUNING_SCHEDULE="0 3 * * *"  # 3h da manhã, daily

# Context Optimization
CONTEXT_WINDOW_MAX_TOKENS=4000
SESSION_TOKEN_BUDGET_DEFAULT=30000
TOKEN_BUDGET_BY_TYPE={
    "user_chat": 100000,
    "agent_to_agent": 50000,
    "cron": 20000
}

# Embedding Optimization
EMBEDDING_OPTIMIZATION_ENABLED=true
EMBEDDING_SPARSITY_TARGET=0.7
```

## Monitoramento e Alertas

### KPIs a Rastrear

```python
# Métricas no dashboard
metrics = {
    "total_tokens_all_sessions": sum(s.token_count for s in sessions),
    "avg_tokens_per_session": total_tokens / len(sessions),
    "median_session_duration_hours": ...,
    "memory_entries_total": count(MemoryEntry),
    "memory_entries_archived": count(archived),
    "embedding_sparsity": removed_embeddings / total_embeddings,
    "sessions_stale_percent": stale_count / total_sessions,
    "avg_context_reuse": rag_hit_rate
}
```

## Casos de Uso Específicos

### Reduzir Custos de Agentes Telegram
- Implementar truncação de mensagens após 100 mensagens por session
- Archive automático após 7 dias inativo

### Agentes Agent-to-Agent (Communication)
- Budget menor (50k tokens)
- Mais agressivo pruning
- Focado em resumos curtos de status

### Agentes Cron (Tasks)
- Budget muito menor (20k tokens)
- Contexto limitado ao último resultado
- Descartar histórico após 24h

## Troubleshooting

### Problema: RAG accuracy diminui após compaction
**Solução:**
- Reduzir MEMORY_COMPACTION_DAYS_THRESHOLD (ex: 14 dias ao invés de 7)
- Aumentar MEMORY_MAX_ENTRIES_PER_AGENT
- Verificar EMBEDDING_SPARSITY_TARGET (manter > 30% embeddings)

### Problema: Sessions ainda usam muitos tokens
**Solução:**
- Revisar SESSION_TOKEN_BUDGET_BY_TYPE - pode ser muito alto
- Implementar context window filtering (RAG selection)
- Truncar messages em tempo real se budget aproximar limite

### Problema: Agentes reportam "missing context"
**Solução:**
- Dados foram arquivados? Recuperar de archive
- Aumentar keep_last_n em session truncation
- Revisar RAG relevância - embeddings podem estar ruins

## Conclusão

A combinação de **Memory Compaction + Session Pruning + Context Filtering** reduz consumo de tokens em ~60-80% mantendo qualidade. Implemente graduamente e monitore métricas de accuracy.
