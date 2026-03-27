#!/usr/bin/env python3
"""
Script to analyze code coverage based on test files.
"""

import os
from pathlib import Path
import ast

def get_functions_from_file(filepath):
    """Get all function names from a Python file."""
    functions = []
    try:
        with open(filepath, 'r') as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
    except:
        pass
    return functions

def get_classes_from_file(filepath):
    """Get all class names from a Python file."""
    classes = []
    try:
        with open(filepath, 'r') as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
    except:
        pass
    return classes

def analyze_coverage():
    """Analyze coverage by comparing source files to test files."""
    
    project_root = Path("/home/node/.openclaw/projects/backend")
    app_dir = project_root / "app"
    tests_dir = project_root / "tests"
    
    # Find all source files
    source_files = []
    for root, dirs, files in os.walk(app_dir):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                filepath = Path(root) / file
                source_files.append(filepath)
    
    # Find all test files
    test_files = []
    for root, dirs, files in os.walk(tests_dir):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                filepath = Path(root) / file
                test_files.append(filepath)
    
    # Group source files by directory
    modules = {
        'models': [],
        'api': [],
        'core': [],
        'services': [],
        'tasks': []
    }
    
    for filepath in source_files:
        rel_path = str(filepath.relative_to(app_dir))
        
        if rel_path.startswith('models/'):
            modules['models'].append(filepath)
        elif rel_path.startswith('api/'):
            modules['api'].append(filepath)
        elif rel_path.startswith('core/'):
            modules['core'].append(filepath)
        elif rel_path.startswith('services/'):
            modules['services'].append(filepath)
        elif rel_path.startswith('tasks/'):
            modules['tasks'].append(filepath)
    
    print("🔍 Análise de Cobertura de Testes")
    print("=" * 50)
    print()
    
    for module_name, files in modules.items():
        print(f"📂 {module_name.upper()}")
        
        if not files:
            print("  Nenhum arquivo encontrado")
            print()
            continue
        
        for filepath in files:
            filename = filepath.name
            rel_path = str(filepath.relative_to(app_dir))
            
            # Find corresponding test file
            test_file = None
            test_name = f"test_{filename}"
            
            for tf in test_files:
                if filename in str(tf) or test_name in str(tf):
                    test_file = tf
                    break
            
            if test_file:
                test_classes = get_classes_from_file(test_file)
                print(f"  ✅ {rel_path}")
                print(f"     Testes: {len(test_classes)} classes")
            else:
                print(f"  ❌ {rel_path}")
                print("     Sem testes!")
        
        print()
    
    print("=" * 50)
    print("📊 Resumo da Cobertura")
    print()
    
    for module_name, files in modules.items():
        test_count = sum(
            1 for f in test_files if module_name in str(f)
        )
        total = len(files)
        coverage = (test_count / total * 100) if total > 0 else 0
        status = "✅" if coverage >= 100 else "⚠️" if coverage > 0 else "❌"
        print(f"  {status} {module_name}: {test_count}/{total} ({coverage:.0f}%)")

if __name__ == '__main__':
    analyze_coverage()
