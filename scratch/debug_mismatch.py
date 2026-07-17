import re

with open("generate_docx.py", "r", encoding="utf-8") as f:
    text = f.read()

# Let's search for some simple keywords around the failing replacements
keywords = [
    "CD8A_Validation",
    "CD8B_Validation",
    "Revised_CD8_M2_Boxplot",
    "HNSC_BestGene_KM",
    "fig_legends = ["
]

for kw in keywords:
    print(f"\nSearching for '{kw}':")
    matches = [m.start() for m in re.finditer(re.escape(kw), text)]
    for m in matches:
        start_idx = max(0, m - 50)
        end_idx = min(len(text), m + 200)
        snippet = text[start_idx:end_idx]
        escaped_snippet = "".join(f"\\u{ord(c):04x}" if ord(c) > 127 else c for c in snippet)
        print(f"  Pos {m}: {repr(escaped_snippet)}")
