import re

with open("generate_docx.py", "r", encoding="utf-8") as f:
    text = f.read()

# Search for Figure 7 to Figure 14 citations in text
fig_patterns = [r"Figure 7", r"Figure 8", r"Figure 9", r"Figure 10", r"Figure 11", r"Figure 12", r"Figure 13", r"Figure 14"]

lines = text.split("\n")
for pattern in fig_patterns:
    print(f"\nMatches for '{pattern}':")
    for idx, line in enumerate(lines):
        if re.search(pattern, line):
            safe_line = line.strip().encode('ascii', errors='replace').decode('ascii')
            print(f"  Line {idx+1}: {safe_line}")
