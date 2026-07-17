import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('generate_docx.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Let's search for volcano plot generation or loading of gene statistics in generate_docx.py
matches = re.finditer(r'def .*?volcano|volcano|deseq2', code, re.IGNORECASE)
for m in matches:
    start = max(0, m.start() - 100)
    end = min(len(code), m.end() + 200)
    print(f"Match found at position {m.start()}:\n{code[start:end]}\n{'-'*50}")
