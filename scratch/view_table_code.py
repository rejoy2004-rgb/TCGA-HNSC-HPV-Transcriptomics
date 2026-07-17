import sys
import re

# Ensure stdout is in utf-8
sys.stdout.reconfigure(encoding='utf-8')

with open('generate_docx.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Locate Table 5 definition
match_t5 = re.search(r'# Insert Table 5', code)
if match_t5:
    start_idx = match_t5.start()
    # print 120 lines from there
    lines = code[start_idx:].split('\n')[:150]
    print("\n".join(lines))
else:
    print("Could not find Table 5 marker")
