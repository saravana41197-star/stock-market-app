#!/usr/bin/env python3
"""Fix all .py files by removing literal backslash-quote sequences."""
import os
import glob

for py_file in glob.glob(r'D:\Groww\*.py'):
    if 'fix_files.py' in py_file:
        continue
    print(f"Fixing {py_file}...")
    with open(py_file, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    # Replace all literal \" with "
    fixed = content.replace('\\"', '"')
    fixed = fixed.replace("\\'", "'")
    with open(py_file, 'w', encoding='utf-8') as f:
        f.write(fixed)
    print(f"  ✓ {py_file}")

print("All files fixed!")
