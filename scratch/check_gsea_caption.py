with open("generate_docx.py", "r", encoding="utf-8") as f:
    text = f.read()

import re
matches = re.findall(r"add_figure\(\s*doc,\s*\"HNSC_HPV_GSEA_dotplot.png\",\s*\"([^\"]*)\"\s*\)", text)
for m in matches:
    print(f"GSEA dotplot caption: {m}")
