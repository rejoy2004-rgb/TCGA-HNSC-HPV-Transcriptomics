import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('generate_docx.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Print lines 600 to 750
for idx in range(580, min(len(lines), 750)):
    print(f"{idx+1}: {lines[idx].strip()}")
