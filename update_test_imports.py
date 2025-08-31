#!/usr/bin/env python3
"""
Script to update test file imports for the new directory structure.
"""

import os
import re

def update_test_file(file_path):
    """Update imports in a test file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Add sys.path.append if not present
    if 'sys.path.append' not in content:
        # Find the first import statement
        lines = content.split('\n')
        new_lines = []
        path_added = False
        
        for i, line in enumerate(lines):
            if not path_added and (line.startswith('import ') or line.startswith('from ')):
                new_lines.append('import sys')
                new_lines.append('sys.path.append("..")  # Add parent directory to path')
                new_lines.append('')
                path_added = True
            new_lines.append(line)
        
        content = '\n'.join(new_lines)
    
    # Update pipeline_stages imports
    content = re.sub(
        r'from pipeline_stages import',
        'from pipeline.pipeline_stages import',
        content
    )
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Updated: {file_path}")

def main():
    """Update all test files."""
    test_files = [
        'tests/test_aruco.py',
        'tests/test_pipeline_isolation.py',
        'tests/test_pipeline.py',
        'tests/test_single_pipeline.py',
        'tests/ut_aruco.py',
        'tests/test_modular_pipeline.py'
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            update_test_file(file_path)
        else:
            print(f"File not found: {file_path}")

if __name__ == "__main__":
    main()
