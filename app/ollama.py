#!/usr/bin/env python3
"""
Skill Ollama Local: gestão e uso de modelos Ollama (list, pull, rm, show, chat, generate, embed).
Em cluster: o chamador deve adquirir o GPU Lock antes de usar Ollama (ver gpu_lock.py e docs/31-ollama-local.md).

Ref: docs/31-ollama-local.md, docs/issues/074-ollama-local-skill.md
Uso: python3 scripts/ollama.py list | pull <model> | rm <model> | show <model> | chat <model> "msg" [-s system] | generate <model> "prompt" | embed <model> "text"
"""
import argparse
import json
import os
import sys

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")


def _req(path: str, method: str = "GET", data: dict = None) -> dict:
    try:
        import urllib.request
        url = f"{OLLAMA_HOST.rstrip('/')}{path}"
        body = json.dumps(data).encode("utf-8") if data else None
        req = urllib.request.Request(url, data=body, method=method)
        if body:
            req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        print(f"Erro Ollama: {e}", file=sys.stderr)
        raise


def cmd_list() -> None:
    out = _req("/api/tags")
    models = out.get("models") or []
    for m in models:
        name = m.get("name", "")
        size = m.get("size", 0)
        print(f"{name}\t{size}")


def cmd_pull(model: str) -> None:
    _req("/api/pull", method="POST", data={"name": model})
    print(f"Pull iniciado/concluído: {model}")


def cmd_rm(model: str) -> None:
    _req("/api/delete", method="POST", data={"name": model})
    print(f"Removido: {model}")


def cmd_show(model: str) -> None:
    out = _req(f"/api/show?name={model}")
    print(json.dumps(out, indent=2, ensure_ascii=False))


def cmd_chat(model: str, message: str, system: str = None) -> None:
    messages = [{"role": "user", "content": message}]
    if system:
        messages.insert(0, {"role": "system", "content": system})
    out = _req("/api/chat", method="POST", data={"model": model, "messages": messages, "stream": False})
    msg = (out.get("message") or {})
    content = msg.get("content", "")
    print(content)


def cmd_generate(model: str, prompt: str) -> None:
    out = _req("/api/generate", method="POST", data={"model": model, "prompt": prompt, "stream": False})
    print(out.get("response", "").strip())


def cmd_embed(model: str, text: str) -> None:
    out = _req("/api/embeddings", method="POST", data={"model": model, "prompt": text})
    emb = out.get("embeddings", [[]])
    if emb:
        print(json.dumps(emb[0][:5]))  # amostra
    else:
        print("[]")


def main() -> int:
    ap = argparse.ArgumentParser(description="Ollama Local: list, pull, rm, show, chat, generate, embed")
    ap.add_argument("cmd", choices=["list", "pull", "rm", "show", "chat", "generate", "embed"], help="Comando")
    ap.add_argument("args", nargs="*", help="Ex.: <model> ou <model> \"mensagem\"")
    ap.add_argument("-s", "--system", dest="system", default=None, help="System prompt (chat)")
    args = ap.parse_args()
    cmd, rest = args.cmd, args.args
    try:
        if cmd == "list":
            cmd_list()
        elif cmd == "pull":
            if not rest:
                print("Uso: ollama.py pull <model>", file=sys.stderr)
            else:
                cmd_pull(rest[0])
        elif cmd == "rm":
            if not rest:
                print("Uso: ollama.py rm <model>", file=sys.stderr)
            else:
                cmd_rm(rest[0])
        elif cmd == "show":
            if not rest:
                print("Uso: ollama.py show <model>", file=sys.stderr)
            else:
                cmd_show(rest[0])
        elif cmd == "chat":
            if len(rest) < 2:
                print("Uso: ollama.py chat <model> \"mensagem\" [-s system]", file=sys.stderr)
            else:
                cmd_chat(rest[0], " ".join(rest[1:]), args.system)
        elif cmd == "generate":
            if len(rest) < 2:
                print("Uso: ollama.py generate <model> \"prompt\"", file=sys.stderr)
            else:
                cmd_generate(rest[0], " ".join(rest[1:]))
        elif cmd == "embed":
            if len(rest) < 2:
                print("Uso: ollama.py embed <model> \"texto\"", file=sys.stderr)
            else:
                cmd_embed(rest[0], " ".join(rest[1:]))
    except Exception as e:
        print(str(e), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
