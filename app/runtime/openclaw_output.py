#!/usr/bin/env python3
"""Inspecao e validacao leve da saida retornada pelo OpenClaw."""
from __future__ import annotations

import json
from typing import Any

from .openclaw_assets import get_role_openclaw_config


REQUIRED_OUTPUT_FIELDS: dict[str, tuple[str, ...]] = {
    "po": ("status", "summary", "issues", "next_action"),
    "architect": ("status", "summary", "decision", "next_action"),
    "developer": ("status", "summary", "files_changed", "verification", "next_action"),
    "qa": ("status", "summary", "verification", "decision", "next_action"),
    "devops": ("status", "summary", "deployment", "next_action"),
    "dba": ("status", "summary", "db_risks", "decision", "next_action"),
    "cybersec": ("status", "summary", "security_findings", "decision", "next_action"),
    "architect_review": ("status", "summary", "decision", "next_action"),
}


def normalize_openclaw_output(output: Any) -> dict[str, Any]:
    if isinstance(output, dict):
        result = output.get("result")
        if isinstance(result, dict):
            payloads = result.get("payloads")
            if isinstance(payloads, list):
                for payload in payloads:
                    if isinstance(payload, dict):
                        text = payload.get("text")
                        if isinstance(text, str):
                            stripped = text.strip()
                            if stripped.startswith("{") and stripped.endswith("}"):
                                try:
                                    return json.loads(stripped)
                                except json.JSONDecodeError:
                                    pass
        if isinstance(output.get("raw"), str):
            raw = output["raw"].strip()
            if raw.startswith("{") and raw.endswith("}"):
                try:
                    return json.loads(raw)
                except json.JSONDecodeError:
                    return output
        return output
    if isinstance(output, str):
        stripped = output.strip()
        if stripped.startswith("{") and stripped.endswith("}"):
            try:
                return json.loads(stripped)
            except json.JSONDecodeError:
                return {"raw": output}
        return {"raw": output}
    return {"raw": str(output)}


def inspect_openclaw_output(role_name: str, output: Any) -> dict[str, Any]:
    normalized = normalize_openclaw_output(output)
    role_config = get_role_openclaw_config(role_name)
    schema_name = role_config.output_schema if role_config else None
    required = REQUIRED_OUTPUT_FIELDS.get(schema_name or "", ())
    missing = tuple(field for field in required if field not in normalized)

    return {
        "schema": schema_name,
        "is_json_object": isinstance(normalized, dict) and "raw" not in normalized,
        "missing_fields": missing,
        "valid": len(missing) == 0 if required else True,
        "normalized": normalized,
    }
