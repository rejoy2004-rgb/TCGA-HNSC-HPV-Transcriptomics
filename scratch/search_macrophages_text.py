import re

with open("generate_docx.py", "r", encoding="utf-8") as f:
    text = f.read()

matches = re.finditer(r"([^\n]*macrophage[^\n]*)", text, re.IGNORECASE)
for i, m in enumerate(matches):
    safe_text = m.group(0).strip().encode('ascii', errors='replace').decode('ascii')
    print(f"{i}: {safe_text}")
