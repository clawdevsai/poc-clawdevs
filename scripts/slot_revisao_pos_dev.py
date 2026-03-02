#!/usr/bin/env python3
"""
Slot único "Revisão pós-Dev" (Fase 0 — 125).
Consome o stream code:ready (consumer group revisao-pos-dev), adquire GPU Lock uma vez,
executa Architect → QA → CyberSec → DBA em sequência, libera o lock e envia XACK.
Fase 3 (032): Architect real via Ollama; ao rejeitar registra strike (record_architect_rejection).
Ref: docs/39-consumer-groups-pipeline-revisao.md, docs/06-operacoes.md, docs/soul/Architect.md
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

# Adicionar diretório do script para importar gpu_lock e orchestration_phase3
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from gpu_lock import GPULock, get_redis

# Contingência cluster acéfalo (124): respeitar pausa
try:
    from acefalo_redis import is_consumption_paused
except ImportError:
    def is_consumption_paused(r=None):
        return False

# Fase 3 — strikes por issue (032) e fallback Architect no 2º strike
try:
    from orchestration_phase3 import record_architect_rejection
except ImportError:
    def record_architect_rejection(r, issue_id: str) -> int:
        return 0
try:
    from architect_fallback import run_fallback as run_architect_fallback
except ImportError:
    def run_architect_fallback(r, issue_id: str, reason: str = "", branch: str = "", title: str = ""):
        return None

# truncamento-finops — microADR ao aprovar (Architect)
try:
    from microadr_generate import generate_and_store_microadr
except ImportError:
    def generate_and_store_microadr(issue_id, branch, title, decision, related_pr=None):
        return None, None

STREAM_CODE_READY = os.getenv("STREAM_CODE_READY", "code:ready")
GROUP_REVISAO = os.getenv("CONSUMER_GROUP_REVISAO", "revisao-pos-dev")
CONSUMER_NAME = os.getenv("POD_NAME", os.getenv("HOSTNAME", "slot-1"))
BLOCK_MS = int(os.getenv("SLOT_BLOCK_MS", "5000"))
# Para testes: SIMULATE_ARCHITECT_REJECT=1 ou payload simulate_reject=1
SIMULATE_REJECT = os.getenv("SIMULATE_ARCHITECT_REJECT", "").strip().lower() in ("1", "true", "yes")

# Architect via Ollama (Fase 3). Vazio = usa stub (aprova). No cluster: OLLAMA_BASE_URL=http://ollama-service.ai-agents.svc.cluster.local:11434
OLLAMA_BASE_URL = (os.getenv("OLLAMA_BASE_URL") or "").strip().rstrip("/")
ARCHITECT_MODEL = os.getenv("ARCHITECT_MODEL", "glm-5:cloud")
ARCHITECT_TIMEOUT_SEC = int(os.getenv("ARCHITECT_TIMEOUT_SEC", "120"))
KEY_PREFIX = os.getenv("KEY_PREFIX_PROJECT", "project:v1")
# Em erro de rede/timeout: "approve" = retornar True (não travar); "reject" = retornar False (conservador). Default: reject
ARCHITECT_ON_ERROR_APPROVE = os.getenv("ARCHITECT_ON_ERROR", "reject").strip().lower() in ("approve", "1", "true")


def _payload_to_dict(data) -> dict:
    """Converte mensagem Redis (dict ou lista de pares) em dict."""
    if isinstance(data, dict):
        return {k: (v.decode() if isinstance(v, bytes) else v) for k, v in data.items()}
    if isinstance(data, (list, tuple)):
        out = {}
        for i in range(0, len(data) - 1, 2):
            k = data[i]
            v = data[i + 1]
            if isinstance(k, bytes):
                k = k.decode()
            if isinstance(v, bytes):
                v = v.decode()
            out[k] = v
        return out
    return {}


def _get_issue_context(r, issue_id: str, max_chars: int = 4000) -> str:
    """Lê contexto da issue no Redis (project:v1:issue:{id}). Retorna string para o prompt."""
    if not issue_id:
        return ""
    key = f"{KEY_PREFIX}:issue:{issue_id}"
    try:
        raw = r.get(key)
        if raw is None:
            return ""
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", errors="replace")
        return (raw[:max_chars] + "…") if len(raw) > max_chars else raw
    except Exception:
        return ""


def _architect_review_via_ollama(r, issue_id: str, payload: dict) -> tuple[bool, str]:
    """
    Chama Ollama com prompt de code review (perfil Architect).
    Retorna (aprovado, motivo). Motivo é a linha de rejeição se rejeitado, senão "".
    """
    issue_ctx = _get_issue_context(r, issue_id)
    branch = payload.get("branch", "")
    title = payload.get("title", "")

    system_prompt = """Você é o Architect (Arquiteto de Software): governança técnica e code review.
Aprove apenas se: código em conformidade com SOLID, testes presentes (ex.: 80% cobertura), sem desvio de ADRs.
Rejeite se: sem testes, fora do padrão, ou inseguro. Seja pragmático: seguro e funcional pode aprovar.
Responda em exatamente uma linha começando por APPROVED ou REJECTED: (ou REJEITADO:). Exemplo: REJECTED: falta cobertura de testes."""

    user_content = f"Issue id: {issue_id}. Branch: {branch or '(não informada)'}. Título: {title or '(vazio)'}.\n\nContexto da issue (especificação/critérios):\n{issue_ctx or '(nenhum contexto no Redis)'}\n\nO código desta tarefa está pronto para revisão. Aprove ou rejeite em uma linha (APPROVED ou REJECTED: razão)."

    body = {
        "model": ARCHITECT_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "stream": False,
    }
    url = f"{OLLAMA_BASE_URL}/api/chat"
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=ARCHITECT_TIMEOUT_SEC) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as e:
        print(f"  [Architect] Erro Ollama: {e}", file=sys.stderr)
        return (ARCHITECT_ON_ERROR_APPROVE, str(e))

    raw_content = ""
    try:
        raw_content = (data.get("message") or {}).get("content") or ""
    except Exception:
        pass
    if isinstance(raw_content, bytes):
        raw_content = raw_content.decode("utf-8", errors="replace")
    content_upper = raw_content.strip().upper()
    first_line = (raw_content.strip().split("\n")[0] or "")[:200]
    rejected = "REJECTED" in content_upper or "REJEITADO" in content_upper
    if rejected:
        print(f"  [Architect] Ollama respondeu: rejeitado — {first_line[:120]}")
        return (False, first_line)
    print(f"  [Architect] Ollama respondeu: aprovado — {first_line[:80]}")
    return (True, "")


def run_etapa(nome: str) -> None:
    """Simula uma etapa (QA, CyberSec, DBA). Em produção: chamar Ollama."""
    print(f"  [{nome}] Etapa executada (stub).")
    time.sleep(0.5)


def run_architect_etapa(r, payload: dict) -> tuple[bool, str]:
    """
    Executa etapa Architect. Retorna (aprovado, motivo_rejeicao).
    Se SIMULATE_ARCHITECT_REJECT ou payload simulate_reject=1: rejeita (teste).
    Se OLLAMA_BASE_URL estiver definido: chama Ollama com prompt de review (Architect).
    Caso contrário: stub aprova (compatibilidade).
    """
    if SIMULATE_REJECT or str(payload.get("simulate_reject", "")).strip() in ("1", "true"):
        print("  [Architect] Simulação de rejeição (SIMULATE_REJECT ou simulate_reject=1).")
        return (False, "simulate_reject")

    if OLLAMA_BASE_URL:
        issue_id = (payload.get("issue_id") or payload.get("issue") or payload.get("task_id") or "").strip()
        return _architect_review_via_ollama(r, issue_id, payload)

    print("  [Architect] Etapa executada (stub, OLLAMA_BASE_URL não definido).")
    time.sleep(0.5)
    return (True, "")


def processar_mensagem(r, stream: str, msg_id: str, data: dict) -> None:
    """Processa uma mensagem: Architect (rejeição → strike); se aprovado, QA → CyberSec → DBA; ACK."""
    payload = _payload_to_dict(data or {})
    issue_id = (payload.get("issue_id") or payload.get("issue") or payload.get("task_id") or "").strip()
    print(f"[Slot] Processando mensagem {msg_id} do stream {stream} issue_id={issue_id!r}")

    with GPULock():
        approved, reject_reason = run_architect_etapa(r, payload)
        if not approved:
            if issue_id:
                n = record_architect_rejection(r, issue_id)
                print(f"[Slot] Architect rejeitou — issue {issue_id} com {n} strike(s).")
                if n == 2:
                    try:
                        run_architect_fallback(
                            r, issue_id,
                            rejection_reason=reject_reason,
                            branch=payload.get("branch", ""),
                            title=payload.get("title", ""),
                        )
                        print(f"[Slot] Fallback Architect (2º strike) acionado para issue {issue_id}.")
                    except Exception as e:
                        print(f"[Slot] Falha ao acionar fallback Architect: {e}", file=sys.stderr)
            else:
                print("[Slot] Architect rejeitou (sem issue_id no payload; strike não registrado).")
            r.xack(stream, GROUP_REVISAO, msg_id)
            print(f"[Slot] XACK {stream} {GROUP_REVISAO} {msg_id}")
            return
        # truncamento-finops — gerar e armazenar microADR ao aprovar
        if issue_id:
            try:
                _, key = generate_and_store_microadr(
                    issue_id,
                    payload.get("branch", ""),
                    payload.get("title", "Code review aprovado"),
                    "Aprovado no code review (Architect).",
                    payload.get("pr"),
                )
                if key:
                    print(f"[Slot] MicroADR registrado para issue {issue_id} em {key}.")
            except Exception as e:
                print(f"[Slot] Falha ao gerar microADR: {e}", file=sys.stderr)
        run_etapa("QA")
        run_etapa("CyberSec")
        run_etapa("DBA")
    r.xack(stream, GROUP_REVISAO, msg_id)
    print(f"[Slot] XACK {stream} {GROUP_REVISAO} {msg_id}")


def main() -> None:
    r = get_redis()
    print(f"[Slot] Consumindo stream={STREAM_CODE_READY} group={GROUP_REVISAO} consumer={CONSUMER_NAME}")

    while True:
        if is_consumption_paused(r=r):
            time.sleep(60)
            continue
        # XREADGROUP: ">" = novas mensagens nunca entregues a nenhum consumer do group (0 = pendentes deste consumer)
        reply = r.xreadgroup(
            GROUP_REVISAO,
            CONSUMER_NAME,
            {STREAM_CODE_READY: ">"},
            block=BLOCK_MS,
            count=1,
        )
        if not reply:
            continue
        for stream, messages in reply:
            stream = stream if isinstance(stream, str) else stream.decode()
            for msg_id, data in messages:
                msg_id = msg_id if isinstance(msg_id, str) else msg_id.decode()
                data = data or {}
                try:
                    processar_mensagem(r, stream, msg_id, data)
                except Exception as e:
                    print(f"[Slot] Erro ao processar {msg_id}: {e}", file=sys.stderr)
                    # Não faz XACK; mensagem fica pendente para retry


if __name__ == "__main__":
    main()
