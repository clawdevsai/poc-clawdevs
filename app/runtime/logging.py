#!/usr/bin/env python3
"""Logs estruturados em JSON para runtime e governanca."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from typing import Any


def log_event(event: str, **fields: Any) -> None:
    payload = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        **fields,
    }
    print(json.dumps(payload, ensure_ascii=False, default=str), file=sys.stdout)


def log_error(event: str, **fields: Any) -> None:
    payload = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "level": "error",
        **fields,
    }
    print(json.dumps(payload, ensure_ascii=False, default=str), file=sys.stderr)
