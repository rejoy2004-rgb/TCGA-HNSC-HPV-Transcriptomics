with open("generate_docx.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx in range(772, 788):
    line = lines[idx]
    escaped_line = "".join(f"\\u{ord(c):04x}" if ord(c) > 127 else c for c in line)
    print(f"Line {idx+1}: {escaped_line.strip()}")
