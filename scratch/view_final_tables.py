import docx
import sys

sys.stdout.reconfigure(encoding='utf-8')

doc = docx.Document('Immune_Landscape_HNSC.docx')

for idx, table in enumerate(doc.tables):
    print(f"\n=========================================")
    print(f"--- Table {idx+1} ---")
    print(f"=========================================")
    for r_idx, row in enumerate(table.rows):
        cells = []
        for cell in row.cells:
            cells.append(cell.text.strip().replace('\n', ' '))
        # standard tables have no cell merging, so deduplicate adjacent duplicate cells
        dedup = []
        for c in cells:
            if not dedup or dedup[-1] != c:
                dedup.append(c)
        print(" | ".join(dedup))
