import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('generate_docx.py', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        if any(term in line for term in ['Supplementary Figure', 'S1', 'S2', 'S3']) and ('figure' in line.lower() or 'supp' in line.lower()):
            print(f"{i}: {line.strip()}")
