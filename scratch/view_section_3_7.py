import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('generate_docx.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Print lines 510 to 570
for idx in range(500, min(len(lines), 570)):
    print(f"{idx+1}: {lines[idx].strip()}")
