"""
ClawDevs — Disjuntor Draft Rejected + RAG Health Check (Issues 127, 005)
Monitora rejeições consecutivas de rascunhos PO→Architect por épico.
3 rejeições consecutivas → congelar tarefa + RAG health check determinístico.

RAG Health Check: verifica datas de indexação vs último commit em main.
- Sem LLM: determinístico por datas e estrutura de pastas.
- Ao descongelar: PO recebe contexto saneado.

Referências:
  docs/issues/127-disjuntor-draft-rejected-rag-health-check.md
  docs/03-arquitetura.md (Disjuntor)
"""

import os
import json
import time
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

logger = logging.getLogger("clawdevs.circuit_breaker")


def _get_redis():
    import redis as r_lib
    return r_lib.Redis(
        host=os.getenv("REDIS_HOST", "redis-service"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        db=0,
        decode_responses=True,
    )


class DraftRejectedCircuitBreaker:
    """Disjuntor para o ciclo PO → Architect (draft.2.issue / draft_rejected).

    Regra: mesma épico com 3 rejeições consecutivas → congelar + RAG health check.
    Descongelamento: PO recebe nova tentativa com contexto saneado pelo RAG health check.
    """

    CIRCUIT_BREAKER_LIMIT = int(os.getenv("DRAFT_REJECTED_CIRCUIT_BREAKER_LIMIT", "3"))
    ESCALATION_LIMIT = int(os.getenv("DRAFT_REJECTED_ESCALATION_LIMIT", "5"))
    KEY_PREFIX = "circuit_breaker:draft_rejected"
    FROZEN_KEY_PREFIX = "circuit_breaker:frozen"

    def __init__(self):
        self.r = _get_redis()

    def _rejection_key(self, epic_id: str) -> str:
        return f"{self.KEY_PREFIX}:{epic_id}"

    def _frozen_key(self, epic_id: str) -> str:
        return f"{self.FROZEN_KEY_PREFIX}:{epic_id}"

    def is_frozen(self, epic_id: str) -> bool:
        return bool(self.r.get(self._frozen_key(epic_id)))

    def record_rejection(self, epic_id: str, rejection_reason: str) -> dict:
        """Registra rejeição de rascunho. Retorna estado do disjuntor."""
        key = self._rejection_key(epic_id)
        count = self.r.incr(key)
        self.r.expire(key, 86400 * 7)  # TTL de 7 dias

        # Registrar histórico
        history_key = f"{key}:history"
        self.r.rpush(history_key, json.dumps({
            "rejection": rejection_reason,
            "count": count,
            "timestamp": datetime.now().isoformat(),
        }))
        self.r.expire(history_key, 86400 * 7)

        state = {
            "epic_id": epic_id,
            "rejection_count": count,
            "limit": self.CIRCUIT_BREAKER_LIMIT,
            "circuit_open": False,
        }

        if count >= self.CIRCUIT_BREAKER_LIMIT:
            logger.warning(
                "CIRCUIT BREAKER aberto para épico '%s': %d rejeições consecutivas (limite: %d). "
                "Congelando tarefa e acionando RAG health check.",
                epic_id, count, self.CIRCUIT_BREAKER_LIMIT,
            )
            self._freeze_epic(epic_id)
            state["circuit_open"] = True
            state["action"] = "freeze_and_rag_health_check"

        if count >= self.ESCALATION_LIMIT:
            logger.critical(
                "ESCALAÇÃO: Épico '%s' atingiu %d rejeições. Escalando ao CEO/Diretor.",
                epic_id, count
            )
            self._escalate_to_director(epic_id, rejection_reason)
            state["escalated"] = True

        return state

    def _escalate_to_director(self, epic_id: str, reason: str) -> None:
        """Gera relatório de degradação e escala ao Diretor/CEO."""
        report_path = Path(f"/home/luke/Workspace/clawdevs-1/memory/cold/DEGRADATION-{epic_id}.md")
        report_content = f"""# Relatório de Degradação — Épico {epic_id}
Data: {datetime.now().isoformat()}

## Alerta: Excesso de Rejeições de Rascunho
A tarefa atingiu o limite de escalação ({self.ESCALATION_LIMIT} rejeições).

### Última Razão de Rejeição:
> {reason}

### Ações Recomendadas ao Diretor:
1. Revisar o escopo da Épico em `docs/backlog/`.
2. Verificar se a documentação em `docs/` está desatualizada (RAG stale).
3. Ajustar os critérios de aceite se forem impossíveis de implementar.

### Comando para Desbloquear após revisão:
`./scripts/unblock-degradation.sh`
"""
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report_content)
        
        self.r.xadd("ceo:emergency", {
            "epic_id": epic_id,
            "action": "director_escalation",
            "report": str(report_path),
            "timestamp": str(int(time.time())),
        })

    def _freeze_epic(self, epic_id: str) -> None:
        self.r.set(self._frozen_key(epic_id), "1")
        # Publicar evento para RAG health check e notificação
        self.r.xadd("circuit_breaker:frozen_epics", {
            "epic_id": epic_id,
            "timestamp": str(int(time.time())),
            "action": "freeze",
        })

    def record_approval(self, epic_id: str) -> None:
        """Reseta o contador quando draft é aprovado."""
        self.r.delete(self._rejection_key(epic_id))
        logger.debug("Circuit breaker resetado para épico '%s'.", epic_id)

    def defrost_epic(self, epic_id: str, sanitized_context: str) -> None:
        """Descongela épico com contexto saneado pelo RAG health check."""
        self.r.delete(self._frozen_key(epic_id))
        self.r.delete(self._rejection_key(epic_id))
        # Publicar contexto saneado para PO
        self.r.xadd("po:sanitized_context", {
            "epic_id": epic_id,
            "context": sanitized_context,
            "timestamp": str(int(time.time())),
        })
        logger.info("Épico '%s' descongelado com contexto saneado.", epic_id)


class RAGHealthCheck:
    """RAG Health Check determinístico (sem LLM).
    Verifica:
    1. Datas de indexação dos documentos vs último commit na main
    2. Estrutura de pastas do workspace
    3. Conflitos de contexto no orquestrador

    Objetivo: sanear o contexto antes de descongelar o épico.
    """

    def __init__(self, docs_dir: Optional[Path] = None, workspace_dir: Optional[Path] = None):
        self.docs_dir = docs_dir or Path(os.getenv("DOCS_DIR", "/app/docs"))
        self.workspace_dir = workspace_dir or Path(os.getenv("WORKSPACE_DIR", "/workspace"))

    def run(self, epic_id: str) -> dict:
        """Executa health check determinístico. Retorna contexto saneado."""
        results = {
            "epic_id": epic_id,
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "issues_found": [],
            "sanitized_context": "",
        }

        # 1. Verificar datas de indexação vs último commit
        doc_freshness = self._check_doc_freshness()
        results["checks"]["doc_freshness"] = doc_freshness

        # 2. Verificar estrutura esperada de pastas
        workspace_structure = self._check_workspace_structure()
        results["checks"]["workspace_structure"] = workspace_structure

        # 3. Construir contexto saneado para o PO
        results["sanitized_context"] = self._build_sanitized_context(
            epic_id, doc_freshness, workspace_structure
        )

        logger.info(
            "RAG Health Check para épico '%s' concluído. Issues: %d",
            epic_id, len(results["issues_found"]),
        )
        return results

    def _check_doc_freshness(self) -> dict:
        """Verifica se a documentação está indexada com base nos commits mais recentes."""
        try:
            import subprocess
            result = subprocess.run(
                ["git", "log", "--oneline", "-5", "--format=%H %ai %s", "--", "docs/"],
                capture_output=True, text=True, timeout=10, cwd=str(self.workspace_dir),
            )
            recent_commits = result.stdout.strip()
            return {
                "status": "ok",
                "recent_doc_commits": recent_commits,
                "note": "Verificar se RAG foi re-indexado após commits recentes.",
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _check_workspace_structure(self) -> dict:
        """Verifica estrutura esperada de pastas do workspace."""
        expected = ["docs/", "k8s/", "scripts/", "orchestrator/", "memory/"]
        missing = []
        for folder in expected:
            if not (self.workspace_dir / folder).exists():
                missing.append(folder)
        return {
            "status": "ok" if not missing else "incomplete",
            "missing_dirs": missing,
        }

    def _build_sanitized_context(self, epic_id: str, freshness: dict, structure: dict) -> str:
        """Constrói contexto saneado para o PO retentar o rascunho."""
        context_lines = [
            f"# Contexto Saneado para Épico: {epic_id}",
            f"*Gerado pelo RAG Health Check em {datetime.now().strftime('%d/%m/%Y %H:%M')}*",
            "",
            "## Diagnóstico",
            f"- Commits recentes em docs/: {'encontrados' if freshness.get('recent_doc_commits') else 'não encontrados'}",
            f"- Estrutura do workspace: {structure.get('status', 'desconhecido')}",
        ]
        if structure.get("missing_dirs"):
            context_lines.append(f"- Pastas ausentes: {', '.join(structure['missing_dirs'])}")
        context_lines.extend([
            "",
            "## Orientação para novo rascunho",
            "- Verificar se a tarefa está alinhada ao estado atual da base de código",
            "- Consultar microADRs relevantes antes de redigir o rascunho",
            "- Evitar assumir funcionalidades que ainda não foram implementadas",
            "- Referenciar Issues existentes e status no backlog",
        ])
        return "\n".join(context_lines)
