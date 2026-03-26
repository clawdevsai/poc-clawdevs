#!/usr/bin/env python3
"""
Simple test runner that validates test files without external dependencies.
This is used when pytest is not available.
"""

import sys
import os
import ast

def check_test_file(filepath):
    """Check if a test file has valid syntax and test classes."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Parse the AST
        tree = ast.parse(content)
        
        # Find all test classes
        test_classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.name.startswith('Test'):
                    test_classes.append(node.name)
        
        # Find all test functions
        test_functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith('test_'):
                    test_functions.append(node.name)
        
        return {
            'valid': True,
            'classes': test_classes,
            'functions': test_functions,
            'errors': []
        }
    except SyntaxError as e:
        return {
            'valid': False,
            'classes': [],
            'functions': [],
            'errors': [f'Syntax error: {e}']
        }
    except Exception as e:
        return {
            'valid': False,
            'classes': [],
            'functions': [],
            'errors': [f'Error: {e}']
        }


def main():
    """Run checks on test files."""
    test_dir = sys.argv[1] if len(sys.argv) > 1 else 'tests'
    
    print(f"🔍 Validating test files in {test_dir}...")
    print()
    
    test_files = []
    for root, dirs, files in os.walk(test_dir):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                filepath = os.path.join(root, file)
                test_files.append(filepath)
    
    print(f"📊 Found {len(test_files)} test files")
    print()
    
    valid_count = 0
    invalid_count = 0
    
    for filepath in test_files:
        result = check_test_file(filepath)
        
        if result['valid']:
            valid_count += 1
            status = "✅"
        else:
            invalid_count += 1
            status = "❌"
        
        print(f"{status} {filepath}")
        if result['classes']:
            print(f"   Classes: {', '.join(result['classes'])}")
        if result['functions']:
            print(f"   Functions: {', '.join(result['functions'][:5])}...")  # Show first 5
        if result['errors']:
            for error in result['errors']:
                print(f"   Error: {error}")
        print()
    
    print(f"✅ Valid: {valid_count}")
    print(f"❌ Invalid: {invalid_count}")
    
    return 0 if invalid_count == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
