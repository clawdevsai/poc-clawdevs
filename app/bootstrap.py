#!/usr/bin/env python3
"""Bootstrap central para imports dos scripts executados diretamente."""
from __future__ import annotations

import os
import sys


def bootstrap_paths() -> str:
    app_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(app_dir)
    for path in (repo_root, app_dir):
        if path not in sys.path:
            sys.path.insert(0, path)
    return repo_root
