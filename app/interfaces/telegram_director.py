#!/usr/bin/env python3
"""Bridge Telegram -> cmd:strategy (diretor conversa com CEO via chat)."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from app.shared.redis_client import get_redis_with_retry

TELEGRAM_BOT_TOKEN = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
TELEGRAM_CHAT_ID = (os.getenv("TELEGRAM_CHAT_ID") or "").strip()
STREAM_CMD_STRATEGY = os.getenv("STREAM_CMD_STRATEGY", "cmd:strategy")
STREAM_DRAFT_ISSUE = os.getenv("STREAM_DRAFT_ISSUE", "draft.2.issue")
STREAM_CODE_READY = os.getenv("QA_STREAM", "code:ready")
STREAM_EVENT_DEVOPS = os.getenv("STREAM_EVENT_DEVOPS", "event:devops")
STATE_KEY_OFFSET = os.getenv("TELEGRAM_OFFSET_KEY", "telegram:director:last_update_id")
STATE_KEY_PENDING_PREFIX = os.getenv("TELEGRAM_PENDING_KEY_PREFIX", "telegram:director:pending_start")
OLLAMA_BASE_URL = (os.getenv("OLLAMA_BASE_URL") or os.getenv("OLLAMA_HOST") or "http://ollama:11434").rstrip("/")
OLLAMA_CLOUD_BASE_URL = (os.getenv("OLLAMA_CLOUD_BASE_URL") or "https://ollama.com").rstrip("/")
OLLAMA_MODEL = (
    os.getenv("OPENCLAW_MODEL_CEO_PRIMARY")
    or os.getenv("OPENCLAW_MODEL_CEO")
    or os.getenv("OLLAMA_MODEL")
    or "qwen3.5:397b-cloud"
).strip()
CEO_LOCAL_FALLBACK_MODEL = (os.getenv("OPENCLAW_MODEL_CEO_LOCAL_FALLBACK") or "qwen2.5:3b").strip()
OLLAMA_API_KEY = (os.getenv("OLLAMA_API_KEY") or "").strip()
KEY_PREFIX = (os.getenv("KEY_PREFIX_PROJECT") or "project:v1").strip()
GITHUB_REPO = (os.getenv("GITHUB_REPO") or os.getenv("GH_REPO") or "").strip()
GITHUB_TOKEN = (os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN") or "").strip()
ENABLE_WEB_SEARCH = (os.getenv("TELEGRAM_ENABLE_WEB_SEARCH") or "1").strip().lower() in {"1", "true", "yes", "on"}
MAX_MESSAGE_CHARS = 3800

STATE_BACKLOG = "Backlog"
STATE_REFINAMENTO = "Refinamento"
STATE_READY = "Ready"
STATE_IN_PROGRESS = "InProgress"
STATE_DEPLOYED = "Deployed"
STATE_DONE = "Done"

STATUS_KEYWORDS = (
    "/status",
    "status",
    "andamento",
    "progresso",
    "como está",
    "como esta",
    "o que falta",
    "quantas tarefas",
    "quantos prs",
)
START_KEYWORDS = (
    "/iniciar",
    "iniciar desenvolvimento",
    "começar desenvolvimento",
    "comecar desenvolvimento",
    "start development",
)
SEARCH_HINTS = (
    "/pesquisar",
    "pesquise",
    "buscar na internet",
    "busque na internet",
    "dados atuais",
    "últimas notícias",
    "ultimas noticias",
    "latest",
)
CONFIRM_KEYWORDS = (
    "sim",
    "pode iniciar",
    "pode iniciar desenvolvimento",
    "inicie",
    "iniciar agora",
    "autorizo",
    "confirmo",
    "ok iniciar",
)
DENY_KEYWORDS = (
    "não",
    "nao",
    "aguarde",
    "espera",
    "ainda não",
    "ainda nao",
    "cancelar",
)


def _telegram_request(method: str, payload: dict) -> dict:
    base = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/{method}"
    data = urllib.parse.urlencode(payload).encode("utf-8")
    request = urllib.request.Request(base, data=data, method="POST")
    with urllib.request.urlopen(request, timeout=70) as response:
        raw = response.read().decode("utf-8")
    body = json.loads(raw)
    if not body.get("ok"):
        raise RuntimeError(f"telegram_{method}_error: {body}")
    return body


def send_message(chat_id: str, text: str) -> None:
    try:
        safe_text = text if len(text) <= MAX_MESSAGE_CHARS else (text[: (MAX_MESSAGE_CHARS - 20)] + "\n\n[resposta truncada]")
        _telegram_request("sendMessage", {"chat_id": chat_id, "text": safe_text})
    except Exception as error:
        print(f"[telegram] erro ao responder chat {chat_id}: {error}")


def ensure_polling_mode() -> None:
    """Force getUpdates mode (disable webhook) to prevent transport conflicts."""
    try:
        _telegram_request("deleteWebhook", {"drop_pending_updates": False})
    except Exception as error:
        print(f"[telegram] aviso: nao foi possivel limpar webhook: {error}")


def generate_ceo_reply(instruction: str) -> str | None:
    def to_cloud_model_name(model_name: str) -> str:
        return model_name[:-6] if model_name.endswith("-cloud") else model_name

    def list_available_models() -> list[str]:
        try:
            with urllib.request.urlopen(f"{OLLAMA_BASE_URL}/api/tags", timeout=10) as response:
                payload = json.loads(response.read().decode("utf-8"))
            models = payload.get("models") or []
            names = [str(m.get("name") or "").strip() for m in models if isinstance(m, dict)]
            return [name for name in names if name]
        except Exception:
            return []

    available_models = list_available_models()
    model_candidates = [OLLAMA_MODEL]
    if CEO_LOCAL_FALLBACK_MODEL and CEO_LOCAL_FALLBACK_MODEL not in model_candidates:
        model_candidates.append(CEO_LOCAL_FALLBACK_MODEL)
    if available_models and all(candidate not in available_models for candidate in model_candidates):
        model_candidates.insert(0, available_models[0])

    last_error: Exception | None = None
    for model_name in model_candidates:
        chat_payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Você é o CEO técnico do ClawDevs AI. Responda em português, "
                        "de forma objetiva, com foco em estratégia de produto e execução."
                    ),
                },
                {"role": "user", "content": instruction},
            ],
            "stream": False,
        }
        endpoints: list[tuple[str, dict]] = [
            ("/api/chat", chat_payload),
            ("/v1/chat/completions", chat_payload),
        ]
        for endpoint, payload in endpoints:
            body = json.dumps(payload).encode("utf-8")
            request = urllib.request.Request(
                f"{OLLAMA_BASE_URL}{endpoint}",
                data=body,
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            try:
                with urllib.request.urlopen(request, timeout=90) as response:
                    raw = response.read().decode("utf-8")
                parsed = json.loads(raw)
                if endpoint == "/api/chat":
                    message = parsed.get("message") or {}
                    content = (message.get("content") or "").strip()
                else:
                    choices = parsed.get("choices") or []
                    message = (choices[0] or {}).get("message") if choices else {}
                    content = (message or {}).get("content", "").strip()
                if content:
                    if model_name != OLLAMA_MODEL:
                        print(f"[telegram] CEO fallback de modelo aplicado: {OLLAMA_MODEL} -> {model_name}")
                    return content
            except Exception as error:
                last_error = error
                continue

    print(f"[telegram] falha ao gerar resposta CEO via Ollama: {last_error}")

    if OLLAMA_API_KEY:
        cloud_seen: set[str] = set()
        for model_name in model_candidates:
            cloud_model = to_cloud_model_name(model_name)
            if cloud_model in cloud_seen:
                continue
            cloud_seen.add(cloud_model)
            chat_payload = {
                "model": cloud_model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Você é o CEO técnico do ClawDevs AI. Responda em português, "
                            "de forma objetiva, com foco em estratégia de produto e execução."
                        ),
                    },
                    {"role": "user", "content": instruction},
                ],
                "stream": False,
            }
            body = json.dumps(chat_payload).encode("utf-8")
            request = urllib.request.Request(
                f"{OLLAMA_CLOUD_BASE_URL}/api/chat",
                data=body,
                method="POST",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {OLLAMA_API_KEY}",
                },
            )
            try:
                with urllib.request.urlopen(request, timeout=90) as response:
                    raw = response.read().decode("utf-8")
                parsed = json.loads(raw)
                message = parsed.get("message") or {}
                content = (message.get("content") or "").strip()
                if content:
                    print("[telegram] CEO usando Ollama Cloud via API key.")
                    return content
            except Exception as error:
                last_error = error
                continue

        print(f"[telegram] falha ao gerar resposta CEO via Ollama Cloud: {last_error}")
    return None


def _to_int(value, default: int = 0) -> int:
    try:
        if value is None:
            return default
        if isinstance(value, bytes):
            value = value.decode("utf-8", errors="replace")
        return int(str(value).strip())
    except (ValueError, TypeError):
        return default


def _xlen(redis_client, stream_name: str) -> int:
    try:
        return _to_int(redis_client.xlen(stream_name), 0)
    except Exception:
        return 0


def fetch_github_pr_stats() -> tuple[int | None, int | None, str]:
    if not GITHUB_REPO:
        return None, None, "GITHUB_REPO não configurado"

    url = f"https://api.github.com/repos/{GITHUB_REPO}/pulls?state=all&per_page=100"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "clawdevs-telegram-director",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))
        if not isinstance(data, list):
            return None, None, "resposta inesperada da API do GitHub"
        total = len(data)
        opened = sum(1 for pr in data if str(pr.get("state", "")).lower() == "open")
        return opened, total, "ok"
    except Exception as error:
        return None, None, f"falha GitHub API: {error}"


def collect_progress(redis_client) -> dict:
    states = {
        STATE_BACKLOG: 0,
        STATE_REFINAMENTO: 0,
        STATE_READY: 0,
        STATE_IN_PROGRESS: 0,
        STATE_DEPLOYED: 0,
        STATE_DONE: 0,
    }
    total_issues = 0
    pattern = f"{KEY_PREFIX}:issue:*:state"
    try:
        for raw_key in redis_client.scan_iter(match=pattern):
            key = raw_key.decode("utf-8", errors="replace") if isinstance(raw_key, bytes) else str(raw_key)
            issue_id = key.replace(f"{KEY_PREFIX}:issue:", "").replace(":state", "")
            if not issue_id:
                continue
            total_issues += 1
            raw_state = redis_client.get(key)
            state = raw_state.decode("utf-8", errors="replace") if isinstance(raw_state, bytes) else str(raw_state or "")
            if state in states:
                states[state] += 1
    except Exception:
        pass

    prs_open, prs_total, prs_note = fetch_github_pr_stats()

    return {
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ"),
        "issues_total": total_issues,
        "states": states,
        "po_tasks_created_total": _xlen(redis_client, STREAM_DRAFT_ISSUE),
        "code_ready_total": _xlen(redis_client, STREAM_CODE_READY),
        "devops_events_total": _xlen(redis_client, STREAM_EVENT_DEVOPS),
        "commands_received_total": _xlen(redis_client, STREAM_CMD_STRATEGY),
        "prs_open": prs_open,
        "prs_total": prs_total,
        "prs_note": prs_note,
    }


def format_progress_message(progress: dict) -> str:
    states = progress["states"]
    prs_open = progress["prs_open"]
    prs_total = progress["prs_total"]
    prs_line = f"{prs_open} abertos / {prs_total} total" if prs_open is not None and prs_total is not None else f"indisponível ({progress['prs_note']})"

    return (
        "📊 Status do Projeto (CEO)\n\n"
        f"Atualizado em: {progress['timestamp_utc']}\n\n"
        "1) Execução de tarefas\n"
        f"- Issues totais: {progress['issues_total']}\n"
        f"- Backlog: {states[STATE_BACKLOG]}\n"
        f"- Refinamento: {states[STATE_REFINAMENTO]}\n"
        f"- Ready: {states[STATE_READY]}\n"
        f"- Em desenvolvimento: {states[STATE_IN_PROGRESS]}\n"
        f"- Deployed: {states[STATE_DEPLOYED]}\n"
        f"- Done: {states[STATE_DONE]}\n\n"
        "2) Pipeline de agentes\n"
        f"- Tarefas criadas pelo PO (draft.2.issue): {progress['po_tasks_created_total']}\n"
        f"- Entregas para QA (code:ready): {progress['code_ready_total']}\n"
        f"- Eventos para DevOps (event:devops): {progress['devops_events_total']}\n"
        f"- Demandas recebidas no CEO (cmd:strategy): {progress['commands_received_total']}\n\n"
        "3) Git / PRs\n"
        f"- PRs: {prs_line}\n"
    )


def _extract_search_results(payload: dict, limit: int = 5) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for topic in payload.get("RelatedTopics", []) or []:
        if isinstance(topic, dict) and topic.get("Text") and topic.get("FirstURL"):
            out.append((str(topic["Text"]), str(topic["FirstURL"])))
        for sub in topic.get("Topics", []) if isinstance(topic, dict) else []:
            if isinstance(sub, dict) and sub.get("Text") and sub.get("FirstURL"):
                out.append((str(sub["Text"]), str(sub["FirstURL"])))
        if len(out) >= limit:
            break
    return out[:limit]


def run_web_search(query: str) -> str:
    if not ENABLE_WEB_SEARCH:
        return "Pesquisa web desabilitada por configuração."
    url = "https://api.duckduckgo.com/?" + urllib.parse.urlencode(
        {"q": query, "format": "json", "no_redirect": "1", "no_html": "1", "skip_disambig": "1"}
    )
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": "clawdevs-telegram-director"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
        abstract = str(payload.get("AbstractText") or "").strip()
        abstract_url = str(payload.get("AbstractURL") or "").strip()
        rows = _extract_search_results(payload, limit=5)
        parts = []
        if abstract:
            if abstract_url:
                parts.append(f"- Resumo: {abstract} ({abstract_url})")
            else:
                parts.append(f"- Resumo: {abstract}")
        if rows:
            parts.append("- Fontes:")
            parts.extend(f"  - {text} ({url})" for text, url in rows)
        if not parts:
            return "Sem resultados relevantes de busca web para esta consulta."
        return "\n".join(parts)
    except Exception as error:
        return f"Falha na busca web: {error}"


def should_show_status(text: str) -> bool:
    lowered = text.lower().strip()
    return any(keyword in lowered for keyword in STATUS_KEYWORDS)


def is_start_command(text: str) -> bool:
    lowered = text.lower().strip()
    return any(keyword in lowered for keyword in START_KEYWORDS)


def should_search_web(text: str) -> bool:
    lowered = text.lower().strip()
    return any(keyword in lowered for keyword in SEARCH_HINTS)


def is_confirmation(text: str) -> bool:
    lowered = text.lower().strip()
    return any(keyword == lowered or keyword in lowered for keyword in CONFIRM_KEYWORDS)


def is_denial(text: str) -> bool:
    lowered = text.lower().strip()
    return any(keyword == lowered or keyword in lowered for keyword in DENY_KEYWORDS)


def pending_key(chat_id: str) -> str:
    return f"{STATE_KEY_PENDING_PREFIX}:{chat_id}"


def get_pending_start(redis_client, chat_id: str) -> dict | None:
    raw = redis_client.get(pending_key(chat_id))
    if not raw:
        return None
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8", errors="replace")
    try:
        data = json.loads(str(raw))
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def save_pending_start(redis_client, chat_id: str, data: dict) -> None:
    redis_client.set(pending_key(chat_id), json.dumps(data), ex=60 * 60 * 6)


def clear_pending_start(redis_client, chat_id: str) -> None:
    redis_client.delete(pending_key(chat_id))


def get_updates(offset: int) -> list[dict]:
    body = _telegram_request(
        "getUpdates",
        {
            "offset": offset,
            "timeout": 30,
            "allowed_updates": json.dumps(["message"]),
        },
    )
    return body.get("result", [])


def normalize_issue_id(update_id: int) -> str:
    return f"TG-{update_id}"


def handle_message(redis_client, update: dict) -> None:
    message = update.get("message") or {}
    chat = message.get("chat") or {}
    chat_id = str(chat.get("id") or "")
    text = (message.get("text") or "").strip()
    update_id = int(update.get("update_id", 0))

    if not chat_id or not text:
        return

    if TELEGRAM_CHAT_ID and chat_id != TELEGRAM_CHAT_ID:
        send_message(chat_id, "Chat não autorizado para este bot.")
        return

    if text in {"/start", "/help"}:
        send_message(
            chat_id,
            "Comandos disponíveis:\n"
            "- /status: status estruturado do projeto\n"
            "- iniciar desenvolvimento <demanda>: CEO analisa e pede confirmação\n"
            "- sim / pode iniciar: confirma e inicia pipeline assíncrono (retorna Ref TG-...)\n"
            "- /pesquisar <tema>: CEO responde com contexto web + estratégia\n\n"
            "Também aceito mensagens livres para o CEO.",
        )
        return

    if should_show_status(text):
        progress = collect_progress(redis_client)
        send_message(chat_id, format_progress_message(progress))
        return

    pending = get_pending_start(redis_client, chat_id)
    if is_denial(text) and pending:
        clear_pending_start(redis_client, chat_id)
        send_message(chat_id, "Perfeito. Não vou iniciar o desenvolvimento agora. Quando quiser, me peça novamente.")
        return

    if is_confirmation(text):
        if not pending:
            send_message(chat_id, "Não há nenhuma demanda pendente para iniciar. Me diga a demanda primeiro.")
            return
        issue_id = str(pending.get("issue_id") or normalize_issue_id(update_id))
        directive = str(pending.get("directive") or "").strip()
        if not directive:
            send_message(chat_id, "Não consegui recuperar a demanda pendente. Pode reenviar o pedido de início?")
            clear_pending_start(redis_client, chat_id)
            return

        payload = {
            "issue_id": issue_id,
            "directive": directive,
            "source": "telegram",
            "event_name": "cmd.strategy.start_development",
            "chat_id": chat_id,
            "update_id": str(update_id),
        }
        redis_client.xadd(STREAM_CMD_STRATEGY, payload, maxlen=5000, approximate=True)
        clear_pending_start(redis_client, chat_id)
        send_message(
            chat_id,
            "✅ Desenvolvimento iniciado de forma assíncrona.\n"
            f"Ref: {issue_id}\n\n"
            "Posso te atualizar com o status a qualquer momento usando /status.",
        )
        print(f"[telegram] publicado em {STREAM_CMD_STRATEGY}: {issue_id}")
        return

    wants_start = is_start_command(text)
    issue_id = normalize_issue_id(update_id) if wants_start else None

    research = ""
    if should_search_web(text):
        research = run_web_search(text)

    progress = collect_progress(redis_client)
    status_context = format_progress_message(progress)
    if wants_start:
        ceo_prompt = (
            "Você é o CEO do ClawDevs falando com o diretor no Telegram.\n"
            "Tom: natural, direto, sem formato engessado.\n"
            "Objetivo: confirmar entendimento da demanda e apresentar plano curto.\n"
            "Regra obrigatória: NÃO iniciar desenvolvimento ainda; encerre perguntando literalmente:\n"
            "\"Posso iniciar o desenvolvimento?\"\n\n"
            f"Demanda recebida:\n{text}\n\n"
            f"Status atual interno:\n{status_context}\n\n"
        )
    else:
        ceo_prompt = (
            "Você é o CEO do ClawDevs falando com o diretor no Telegram.\n"
            "Responda em português, de forma natural, objetiva e útil para decisão.\n"
            "Não use template fixo numerado.\n"
            "Quando fizer sentido, traga: o que já está pronto, o que falta e próximo passo recomendado.\n\n"
            f"Mensagem do diretor:\n{text}\n\n"
            f"Status atual interno:\n{status_context}\n\n"
        )
    if research:
        ceo_prompt += f"Contexto web (best-effort):\n{research}\n\n"

    ceo_reply = generate_ceo_reply(ceo_prompt)
    if ceo_reply:
        if wants_start:
            save_pending_start(
                redis_client,
                chat_id,
                {
                    "issue_id": issue_id,
                    "directive": f"[START_DEVELOPMENT]\n{text}",
                    "requested_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ"),
                    "source_update_id": str(update_id),
                },
            )
            send_message(
                chat_id,
                f"CEO:\n{ceo_reply}\n\n"
                "Se você confirmar, eu inicio em modo assíncrono e te envio o Ref (TG-...).",
            )
        else:
            send_message(chat_id, f"CEO:\n{ceo_reply}")
    else:
        if wants_start:
            save_pending_start(
                redis_client,
                chat_id,
                {
                    "issue_id": issue_id,
                    "directive": f"[START_DEVELOPMENT]\n{text}",
                    "requested_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ"),
                    "source_update_id": str(update_id),
                },
            )
            send_message(
                chat_id,
                "Entendi a demanda. Posso iniciar o desenvolvimento?\n"
                "Se você confirmar, eu inicio assíncrono e retorno o Ref (TG-...).",
            )
        else:
            fallback = (
                "CEO:\n"
                "Recebi sua mensagem e já analisei com os dados internos do projeto. "
                "Agora temos o fluxo de confirmação ativo: eu só inicio desenvolvimento após sua autorização explícita.\n\n"
                "Se quiser, posso te passar um posicionamento objetivo agora com:\n"
                "- o que está pronto\n"
                "- o que falta\n"
                "- próximo passo recomendado\n"
                "- status atual do pipeline\n\n"
                "Me diga: \"me dá um status do projeto\" ou descreva a demanda para eu preparar e perguntar "
                "\"Posso iniciar o desenvolvimento?\"."
            )
            if research:
                fallback += f"\n\nContexto web (best-effort):\n{research}"
            send_message(chat_id, fallback)


def main() -> int:
    if not TELEGRAM_BOT_TOKEN:
        print("[telegram] TELEGRAM_BOT_TOKEN não definido. Bridge desabilitada.")
        while True:
            time.sleep(60)

    redis_client = get_redis_with_retry()
    ensure_polling_mode()
    last_update_id = int(redis_client.get(STATE_KEY_OFFSET) or 0)
    next_offset = last_update_id + 1 if last_update_id > 0 else 0

    print(
        f"[telegram] bridge ativa | stream={STREAM_CMD_STRATEGY} "
        f"| chat_filter={'on' if TELEGRAM_CHAT_ID else 'off'}"
    )

    while True:
        try:
            updates = get_updates(next_offset)
            for update in updates:
                update_id = int(update.get("update_id", 0))
                if update_id:
                    next_offset = update_id + 1
                    redis_client.set(STATE_KEY_OFFSET, str(update_id))
                handle_message(redis_client, update)
        except urllib.error.HTTPError as error:
            if error.code == 409:
                print(
                    "[telegram] conflito 409 no getUpdates: outro polling ativo "
                    "com o mesmo bot token."
                )
            else:
                print(f"[telegram] erro HTTP: {error}")
            time.sleep(5)
        except urllib.error.URLError as error:
            print(f"[telegram] erro de rede: {error}")
            time.sleep(5)
        except Exception as error:
            print(f"[telegram] erro no loop: {error}")
            time.sleep(5)


if __name__ == "__main__":
    raise SystemExit(main())
