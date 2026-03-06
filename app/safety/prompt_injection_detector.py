#!/usr/bin/env python3
"""
Detecção de padrões de injeção de prompt (026).
Conteúdo externo deve ser tratado como DADO; apenas Diretor e workspace (AGENTS.md, SOUL.md) são fonte de instruções.
Ref: docs/05-seguranca-e-etica.md, docs/14-seguranca-runtime-agentes.md, docs/issues/026-detecao-injecao-prompt.md
"""
from __future__ import annotations

import os
import re
import sys

# Padrões típicos de injeção (instruções diretas, override, ofuscação)
DEFAULT_PATTERNS = [
    (r"ignore\s+(all\s+)?(previous|above|prior)\s+instructions", "ignore_previous_instructions", "high"),
    (r"ignore\s+your\s+(instructions|programming|guidelines)", "ignore_instructions", "high"),
    (r"you\s+are\s+now\s+", "you_are_now", "high"),
    (r"disregard\s+(your\s+)?(instructions|programming|rules)", "disregard_instructions", "high"),
    (r"forget\s+(everything|all)\s+(you\s+)?(know|learned)", "forget_everything", "high"),
    (r"new\s+system\s+prompt\s*:", "new_system_prompt", "high"),
    (r"system\s+prompt\s*:\s*", "system_prompt_label", "medium"),
    (r"ADMIN\s+OVERRIDE\s*:", "admin_override", "high"),
    (r"developer\s+mode\s*", "developer_mode", "medium"),
    (r"jailbreak", "jailbreak", "high"),
    (r"bypass\s+(your\s+)?(safety|restrictions|guidelines)", "bypass_safety", "high"),
    (r"pretend\s+you\s+are\s+", "pretend_you_are", "medium"),
    (r"act\s+as\s+if\s+you\s+(are|have)\s+", "act_as", "medium"),
    (r"\[INST\]\s*", "inst_tag", "medium"),
    (r"<\|im_start\|>", "im_start", "low"),
    (r"output\s+(the\s+)?(following|below)\s+without\s+", "output_without", "medium"),
    (r"do\s+not\s+(follow|obey|listen\s+to)\s+", "do_not_follow", "high"),
    (r"override\s+(your\s+)?(content\s+)?policy", "override_policy", "high"),
    (r"reveal\s+(your\s+)?(system\s+)?prompt", "reveal_prompt", "medium"),
    (r"repeat\s+(the\s+)?(words\s+)?above", "repeat_above", "low"),
]
# Carregar padrões adicionais de env (um por linha: regex\tname\tseverity)
EXTRA_PATTERNS_ENV = os.environ.get("PROMPT_INJECTION_EXTRA_PATTERNS", "")


def _load_patterns() -> list[tuple[re.Pattern[str], str, str]]:
    compiled = []
    for raw, name, sev in DEFAULT_PATTERNS:
        try:
            compiled.append((re.compile(raw, re.IGNORECASE), name, sev))
        except re.error:
            continue
    for line in EXTRA_PATTERNS_ENV.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) >= 2:
            try:
                p = re.compile(parts[0].strip(), re.IGNORECASE)
                name = parts[1].strip() or "custom"
                sev = (parts[2].strip() if len(parts) > 2 else "medium").lower()
                compiled.append((p, name, sev))
            except re.error:
                continue
    return compiled


_PATTERNS = None


def get_patterns() -> list[tuple[re.Pattern[str], str, str]]:
    global _PATTERNS
    if _PATTERNS is None:
        _PATTERNS = _load_patterns()
    return _PATTERNS


def detect(text: str) -> tuple[bool, list[tuple[str, str]]]:
    """
    Analisa texto em busca de padrões de injeção de prompt.
    Retorna (suspeito, [(nome_padrão, severidade), ...]).
    """
    if not text or not text.strip():
        return False, []
    hits = []
    for pattern, name, severity in get_patterns():
        if pattern.search(text):
            hits.append((name, severity))
    return len(hits) > 0, hits


def main() -> int:
    """CLI: prompt_injection_detector.py [arquivo|--stdin]. Exit 0 = sem suspeita, 1 = suspeita, 2 = erro."""
    if len(sys.argv) > 1 and sys.argv[1] != "--stdin":
        path = sys.argv[1]
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
        except OSError as e:
            print(f"Erro ao ler {path}: {e}", file=sys.stderr)
            return 2
    else:
        text = sys.stdin.read()

    suspect, hits = detect(text)
    if suspect:
        for name, sev in hits:
            print(f"SUSPECT\t{name}\t{sev}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
