#!/usr/bin/env python3
"""Health check minimo para endpoint Ollama (local ou cloud)."""
from __future__ import annotations

import json
from urllib.error import URLError
from urllib.parse import urljoin
from urllib.request import urlopen


def _extract_model_names(payload: dict) -> set[str]:
    names: set[str] = set()
    for item in payload.get("models", []) or []:
        if not isinstance(item, dict):
            continue
        model = str(item.get("model") or "").strip()
        name = str(item.get("name") or "").strip()
        if model:
            names.add(model)
        if name:
            names.add(name)
    return names


def check_ollama_health(base_url: str, model: str, timeout_sec: float = 5.0) -> tuple[list[str], dict]:
    errors: list[str] = []
    details = {
        "reachable": False,
        "model_available": False,
        "models_count": 0,
    }
    if not base_url:
        errors.append("OLLAMA_BASE_URL vazio")
        return errors, details
    if not model:
        errors.append("OLLAMA_MODEL vazio")
        return errors, details
    endpoint = urljoin(base_url.rstrip("/") + "/", "api/tags")
    try:
        with urlopen(endpoint, timeout=timeout_sec) as response:
            raw = response.read().decode("utf-8")
        payload = json.loads(raw or "{}")
        model_names = _extract_model_names(payload)
        details["reachable"] = True
        details["models_count"] = len(model_names)
        details["model_available"] = model in model_names
        if not details["model_available"]:
            errors.append(f"modelo nao encontrado no Ollama: {model}")
    except URLError as error:
        errors.append(f"falha ao conectar no Ollama ({endpoint}): {error}")
    except Exception as error:
        errors.append(f"falha no health check do Ollama: {error}")
    return errors, details
