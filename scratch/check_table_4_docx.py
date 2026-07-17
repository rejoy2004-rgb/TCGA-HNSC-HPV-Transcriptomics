import docx

doc_path = "Immune_Landscape_HNSC.docx"
doc = docx.Document(doc_path)

# Let's search for Table 4 (the one with Plasma cells or CIBERSORTx comparisons)
table_found = False
for i, table in enumerate(doc.tables):
    # check first cell text to see if it's Table 4
    if "Immune Cell Population" in table.rows[0].cells[0].text:
        table_found = True
        print(f"Table {i+1} rows content:")
        for r_idx, row in enumerate(table.rows):
            row_text = [cell.text.strip() for cell in row.cells]
            print(f"  Row {r_idx+1}: {row_text}")
        break

if not table_found:
    print("Table 4 not found in the document!")
