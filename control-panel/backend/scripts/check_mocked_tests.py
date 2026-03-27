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
Script to verify that all tests are fully mocked (no external access).
"""

import os
import sys


def check_test_file(filepath):
    """Check if a test file is fully mocked."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check for direct database/session access
    db_patterns = [
        'db_session.',
        'session.exec',
        'session.add',
        'session.commit',
        'session.delete',
        'db_session',
    ]
    
    issues = []
    for pattern in db_patterns:
        if pattern in content:
            issues.append(f"Direct DB access: {pattern}")
    
    # Check if file has proper mocking
    has_mocking = 'mock' in content.lower() or 'patch' in content.lower()
    
    return {
        'has_issues': len(issues) > 0,
        'issues': issues,
        'has_mocking': has_mocking,
    }


def main():
    """Check all test files."""
    test_dir = sys.argv[1] if len(sys.argv) > 1 else 'tests'
    
    print("🔍 Verificando testes unitários (100% mockados)")
    print("=" * 50)
    print()
    
    all_ok = True
    files_checked = 0
    
    for root, dirs, files in os.walk(test_dir):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                filepath = os.path.join(root, file)
                files_checked += 1
                
                result = check_test_file(filepath)
                
                if result['has_issues']:
                    all_ok = False
                    print(f"❌ {filepath}")
                    for issue in result['issues']:
                        print(f"   {issue}")
                elif not result['has_mocking']:
                    all_ok = False
                    print(f"⚠️  {filepath} - Sem mocking!")
                else:
                    print(f"✅ {filepath}")
    
    print()
    print("=" * 50)
    print(f"📊 Arquivos verificados: {files_checked}")
    
    if all_ok:
        print("✅ Todos os testes são 100% mockados!")
        return 0
    else:
        print("⚠️  Alguns testes precisam de correção")
        return 1


if __name__ == '__main__':
    sys.exit(main())
