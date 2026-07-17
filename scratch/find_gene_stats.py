import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('generate_docx.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Let's search for references to IGHA1 or TACSTD2
for m in re.finditer(r'.*?(?:IGHA1|TACSTD2).*?\n', code):
    print(m.group().strip())
