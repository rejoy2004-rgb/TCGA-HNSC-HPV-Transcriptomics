import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('generate_docx.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Locate Table 6 definition
match_t6 = re.search(r'# Insert Table 6', code)
if match_t6:
    start_idx = match_t6.start()
    lines = code[start_idx:].split('\n')[:80]
    print("\n".join(lines))
else:
    print("Could not find Table 6 marker")
