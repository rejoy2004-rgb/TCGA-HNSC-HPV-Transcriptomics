with open("generate_docx.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx in range(1159, min(len(lines), 1215)):
    safe_line = lines[idx].rstrip().encode('ascii', errors='replace').decode('ascii')
    print(f"{idx+1}: {safe_line}")
