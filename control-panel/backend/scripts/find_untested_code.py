#!/usr/bin/env python3

# Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Script to identify source files without corresponding test files.
Categorizes files and prioritizes based on importance.
"""

import sys
from pathlib import Path


def find_untested_code(src_dir, pattern="test"):
    src_path = Path(src_dir)
    if not src_path.exists():
        print(f"❌ Source directory not found: {src_dir}")
        return

    # Collect all Python source files
    source_files = []
    for py_file in src_path.rglob("*.py"):
        # Skip __init__.py and test files
        if py_file.name == "__init__.py" or pattern in py_file.name:
            continue
        source_files.append(py_file)

    # Collect all test files
    test_files = set()
    for py_file in src_path.rglob("*.py"):
        if pattern in py_file.name:
            test_files.add(py_file.stem)

    # Identify untested files
    untested = []
    tested = []

    for src in source_files:
        # Get relative path from src_dir
        rel_path = src.relative_to(src_path)
        parts = str(rel_path).split("/")

        # Skip __init__.py in core/models/api directories if they're empty
        if src.name == "__init__.py":
            continue

        # Check if test exists
        test_name = f"test_{src.name}"
        has_test = test_name in test_files

        # Determine category
        if "api" in parts:
            category = "API"
        elif "models" in parts:
            category = "Model"
        elif "core" in parts:
            category = "Core"
        elif "scripts" in parts:
            category = "Script"
        else:
            category = "Other"

        if has_test:
            tested.append((src, category))
        else:
            untested.append((src, category))

    # Print results
    print("🔍 Análise de Cobertura de Testes")
    print(f"📊 Arquivos de origem: {len(source_files)}")
    print(f"✅ Com testes: {len(tested)}")
    print(f"❌ Sem testes: {len(untested)}")
    print(f"📈 Cobertura atual: {len(tested) / len(source_files) * 100:.1f}%")
    print()

    # Categorize untested files
    by_category = {}
    for f, cat in untested:
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(f)

    print("📂 Arquivos sem teste por categoria:")
    for cat, files in sorted(by_category.items()):
        print(f"  - {cat}: {len(files)} arquivo(s)")
    print()

    # Print detailed list
    print("📝 Detalhamento dos arquivos sem teste:")
    for cat, files in sorted(by_category.items()):
        print(f"\n  [{cat}]")
        for f in sorted(files):
            rel = f.relative_to(src_path)
            print(f"    • {rel}")

    # Priority recommendations
    print("\n🎯 Priorização sugerida:")
    print("  1. API (endpoints públicos - alto impacto)")
    print("  2. Models (lógica de dados - crítica)")
    print("  3. Core (lógica central - importante)")
    print("  4. Scripts (automatização - média)")

    return untested


if __name__ == "__main__":
    src_dir = sys.argv[1] if len(sys.argv) > 1 else "app"
    find_untested_code(src_dir)
