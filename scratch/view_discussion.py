import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('generate_docx.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx in range(1123, min(len(lines), 1205)):
    print(f"{idx+1}: {lines[idx].strip()}")
