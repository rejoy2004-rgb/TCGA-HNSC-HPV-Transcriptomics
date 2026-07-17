import re

with open('generate_docx.py', 'rb') as f:
    content = f.read()

# ----------------- Part 1: Replace Table 5 with merged Table 5 -----------------
target_t5 = b'''    doc.add_paragraph(
        "To summarize the transcriptomic differences of key markers requested for clinical validation, Table 5 lists the "
        "differential expression statistics for key mature B-cell, B-cell receptor, immunoglobulin constant, and epithelial marker genes, "
        "providing a targeted reference of validated immunologic and differentiation markers of interest."
    )
    
    # Insert Table 5 (Key marker genes) here
    p_t5_title = doc.add_paragraph()
    p_t5_title.paragraph_format.space_before = Pt(12)
    p_t5_title.paragraph_format.space_after = Pt(4)
    p_t5_title.paragraph_format.keep_with_next = True
    r_t5_title = p_t5_title.add_run("Table 5. Differential Expression Statistics for Key Immunoglobulin, B-Cell, and Epithelial Genes Stratified by HPV Status")
    r_t5_title.font.bold = True
    r_t5_title.font.size = Pt(11)
    
    table_5_data = [
        ["Gene", "log2FC", "FDR-adjusted P-value", "Biological Relevance"],
        ["MS4A1", "2.07", "2.50 \\u00d7 10\\u207b\\u2075", "Mature B-cell marker (CD20); key cell-surface antigen"],
        ["CD79A", "1.36", "9.09 \\u00d7 10\\u207b\\u2074", "B-cell receptor signalling component; essential for B-cell activation"],
        ["IGKC", "1.14", "0.011", "Immunoglobulin kappa constant region; marker of antibody secretion"],
        ["IGHG3", "0.98", "0.028", "Immunoglobulin heavy constant gamma 3; mediator of humoral immunity"],
        ["IGHG1", "0.93", "0.044", "Immunoglobulin heavy constant gamma 1; mediator of humoral immunity"],
        ["S100A7", "\\u22121.92", "1.48 \\u00d7 10\\u207b\\u2075", "Psoriasin; calcium-binding keratinocyte differentiation marker (downregulated)"]
    ]
    
    t5 = doc.add_table(rows=len(table_5_data), cols=4)
    t5.alignment = WD_TABLE_ALIGNMENT.CENTER
    border_format = {'sz': 4, 'val': 'single', 'color': 'D3D3D3', 'space': '0'}
    
    for r_idx, row_cells in enumerate(t5.rows):
        for c_idx, cell in enumerate(row_cells.cells):
            cell.text = table_5_data[r_idx][c_idx]
            set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
            set_cell_borders(cell, top=border_format, bottom=border_format, left=border_format, right=border_format)
            
            p_cell = cell.paragraphs[0]
            p_cell.paragraph_format.line_spacing = 1.05
            p_cell.paragraph_format.space_after = Pt(0)
            p_cell.runs[0].font.size = Pt(9.5)
            p_cell.runs[0].font.name = 'Times New Roman'
            
            if r_idx == 0:
                set_cell_background(cell, "F2F2F2")
                p_cell.runs[0].font.bold = True
                p_cell.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                if c_idx == 0:
                    p_cell.runs[0].font.bold = True
                    p_cell.alignment = WD_ALIGN_PARAGRAPH.LEFT
                elif c_idx in [1, 2]:
                    p_cell.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                else:
                    p_cell.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

    p_t5_space = doc.add_paragraph()
    p_t5_space.paragraph_format.space_after = Pt(12)'''

replacement_t5 = b'''    doc.add_paragraph(
        "To summarize the transcriptomic differences of key markers requested for clinical validation, Table 5 lists the "
        "differential expression statistics and biological roles for key mature B-cell, B-cell receptor, immunoglobulin constant, "
        "and epithelial marker genes, providing a targeted reference of validated immunologic and differentiation markers of interest."
    )
    
    # Insert Table 5 (Key marker genes) here
    p_t5_title = doc.add_paragraph()
    p_t5_title.paragraph_format.space_before = Pt(12)
    p_t5_title.paragraph_format.space_after = Pt(4)
    p_t5_title.paragraph_format.keep_with_next = True
    r_t5_title = p_t5_title.add_run("Table 5. Differential Expression and Biological Roles of Key Immune and Epithelial Genes")
    r_t5_title.font.bold = True
    r_t5_title.font.size = Pt(11)
    
    table_5_data = [
        ["Gene", "log2FC", "FDR-adjusted P-value", "Biological Role"],
        ["MS4A1", "2.07", "2.50 \\u00d7 10\\u207b\\u2075", "Mature B cell"],
        ["CD79A", "1.36", "9.09 \\u00d7 10\\u207b\\u2074", "BCR signalling"],
        ["IGKC", "1.14", "0.011", "Plasma cell"],
        ["IGHA1", "1.51", "8.71 \\u00d7 10\\u207b\\u2074", "Antibody"],
        ["IGHG1", "0.93", "0.044", "Humoral immunity"],
        ["IGHG3", "0.98", "0.028", "Humoral immunity"],
        ["TACSTD2", "0.60", "5.75 \\u00d7 10\\u207b\\u2074", "Epithelial marker"],
        ["S100A7", "\\u22121.92", "1.48 \\u00d7 10\\u207b\\u2075", "Keratinization"]
    ]
    
    t5 = doc.add_table(rows=len(table_5_data), cols=4)
    t5.alignment = WD_TABLE_ALIGNMENT.CENTER
    border_format = {'sz': 4, 'val': 'single', 'color': 'D3D3D3', 'space': '0'}
    
    for r_idx, row_cells in enumerate(t5.rows):
        for c_idx, cell in enumerate(row_cells.cells):
            cell.text = table_5_data[r_idx][c_idx]
            set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
            set_cell_borders(cell, top=border_format, bottom=border_format, left=border_format, right=border_format)
            
            p_cell = cell.paragraphs[0]
            p_cell.paragraph_format.line_spacing = 1.05
            p_cell.paragraph_format.space_after = Pt(0)
            p_cell.runs[0].font.size = Pt(9.5)
            p_cell.runs[0].font.name = 'Times New Roman'
            
            if r_idx == 0:
                set_cell_background(cell, "F2F2F2")
                p_cell.runs[0].font.bold = True
                p_cell.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                if c_idx == 0:
                    p_cell.runs[0].font.bold = True
                    p_cell.alignment = WD_ALIGN_PARAGRAPH.LEFT
                elif c_idx in [1, 2]:
                    p_cell.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                else:
                    p_cell.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

    p_t5_space = doc.add_paragraph()
    p_t5_space.paragraph_format.space_after = Pt(12)'''

# Normalize newlines to match \r\n vs \n
target_t5 = target_t5.replace(b'\n', b'\r\n')
replacement_t5 = replacement_t5.replace(b'\n', b'\r\n')

if target_t5 in content:
    content = content.replace(target_t5, replacement_t5)
    print("Table 5 replace matched!")
else:
    # Try with normal \n
    target_t5_lf = target_t5.replace(b'\r\n', b'\n')
    replacement_t5_lf = replacement_t5.replace(b'\r\n', b'\n')
    if target_t5_lf in content:
        content = content.replace(target_t5_lf, replacement_t5_lf)
        print("Table 5 replace matched (LF)!")
    else:
        print("Table 5 target NOT found")

# ----------------- Part 2: Remove Table 6 definition -----------------
target_t6 = b'''    doc.add_paragraph(
        "To summarize the transcriptomic differences of key representative markers of interest, Table 6 lists the "
        "differential expression statistics and biological roles for key immune-associated and epithelial genes."
    )
    
    # Insert Table 6 (Key biological results genes) here
    p_t6_title = doc.add_paragraph()
    p_t6_title.paragraph_format.space_before = Pt(12)
    p_t6_title.paragraph_format.space_after = Pt(4)
    p_t6_title.paragraph_format.keep_with_next = True
    r_t6_title = p_t6_title.add_run("Table 6. Important Immune and Epithelial Genes in HPV-Positive vs. HPV-Negative HNSC")
    r_t6_title.font.bold = True
    r_t6_title.font.size = Pt(11)
    
    table_6_data = [
        ["Gene", "log2FC", "FDR-adjusted P-value", "Biological Role"],
        ["IGKC", "1.14", "0.011", "Plasma cells"],
        ["IGHA1", "1.51", "8.71 \\u00d7 10\\u207b\\u2074", "Antibody"],
        ["MS4A1", "2.07", "2.50 \\u00d7 10\\u207b\\u2075", "B cell"],
        ["CD79A", "1.36", "9.09 \\u00d7 10\\u207b\\u2074", "BCR"],
        ["S100A7", "\\u22121.92", "1.48 \\u00d7 10\\u207b\\u2075", "Keratinization"],
        ["TACSTD2", "0.60", "5.75 \\u00d7 10\\u207b\\u2074", "Epithelial marker"]
    ]
    
    t6 = doc.add_table(rows=len(table_6_data), cols=4)
    t6.alignment = WD_TABLE_ALIGNMENT.CENTER
    border_format = {'sz': 4, 'val': 'single', 'color': 'D3D3D3', 'space': '0'}
    
    for r_idx, row_cells in enumerate(t6.rows):
        for c_idx, cell in enumerate(row_cells.cells):
            cell.text = table_6_data[r_idx][c_idx]
            set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
            set_cell_borders(cell, top=border_format, bottom=border_format, left=border_format, right=border_format)
            
            p_cell = cell.paragraphs[0]
            p_cell.paragraph_format.line_spacing = 1.05
            p_cell.paragraph_format.space_after = Pt(0)
            p_cell.runs[0].font.size = Pt(9.5)
            p_cell.runs[0].font.name = 'Times New Roman'
            
            if r_idx == 0:
                set_cell_background(cell, "F2F2F2")
                p_cell.runs[0].font.bold = True
                p_cell.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                if c_idx == 0:
                    p_cell.runs[0].font.bold = True
                    p_cell.alignment = WD_ALIGN_PARAGRAPH.LEFT
                elif c_idx in [1, 2]:
                    p_cell.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                else:
                    p_cell.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

    p_t6_space = doc.add_paragraph()
    p_t6_space.paragraph_format.space_after = Pt(12)'''

target_t6 = target_t6.replace(b'\n', b'\r\n')

if target_t6 in content:
    content = content.replace(target_t6, b'')
    print("Table 6 removal matched!")
else:
    target_t6_lf = target_t6.replace(b'\r\n', b'\n')
    if target_t6_lf in content:
        content = content.replace(target_t6_lf, b'')
        print("Table 6 removal matched (LF)!")
    else:
        print("Table 6 target NOT found")

# ----------------- Part 3: Renumber Table 7 to Table 6 -----------------
target_t7 = b'''    doc.add_paragraph(
        "Cox proportional hazards analysis identified several genes with statistically significant associations with "
        "overall survival (Table 7). Among these, ZFR2 (HR = 0.9988, P = 9.8 \xc3\x97 10\xe2\x88\x924), STAG3 (HR = 0.9997, P = 0.0077), "
        "SMC1B (HR = 0.9995, P = 0.0056) and RAD9B (HR = 0.9967, P = 0.0089) were significant. The hazard ratios and confidence intervals "
        "for these and other prognostic genes are visualized as a forest plot (Figure 15). However, all hazard ratios "
        "were very close to 1, indicating that although statistically significant, the effect sizes were small. Therefore, "
        "these findings should be considered exploratory and require validation in independent cohorts. Kaplan-Meier "
        "analysis, using median gene expression as the cutoff, demonstrated a significant survival difference "
        "(log-rank P = 0.024), with patients in the high-expression group demonstrating superior overall survival (Figure 16)."
    )
    
    # Insert Table 7 (Survival-associated genes) here
    p_t7_title = doc.add_paragraph()
    p_t7_title.paragraph_format.space_before = Pt(12)
    p_t7_title.paragraph_format.space_after = Pt(4)
    p_t7_title.paragraph_format.keep_with_next = True
    r_t7_title = p_t7_title.add_run("Table 7. Survival-Associated Genes Identified by Cox Proportional Hazards Analysis")
    r_t7_title.font.bold = True
    r_t7_title.font.size = Pt(11)
    
    table_7_data = [
        ["Gene", "Hazard Ratio", "95% CI", "P-value"],
        ["ZFR2", "0.9988", "0.9981\\u20130.9995", "0.0010"],
        ["SMC1B", "0.9995", "0.9992\\u20130.9999", "0.0056"],
        ["STAG3", "0.9997", "0.9995\\u20130.9999", "0.0077"],
        ["RAD9B", "0.9967", "0.9942\\u20130.9992", "0.0089"]
    ]
    
    t7 = doc.add_table(rows=len(table_7_data), cols=4)
    t7.alignment = WD_TABLE_ALIGNMENT.CENTER
    border_format = {'sz': 4, 'val': 'single', 'color': 'D3D3D3', 'space': '0'}
    
    for r_idx, row_cells in enumerate(t7.rows):
        for c_idx, cell in enumerate(row_cells.cells):
            cell.text = table_7_data[r_idx][c_idx]
            set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
            set_cell_borders(cell, top=border_format, bottom=border_format, left=border_format, right=border_format)
            
            p_cell = cell.paragraphs[0]
            p_cell.paragraph_format.line_spacing = 1.05
            p_cell.paragraph_format.space_after = Pt(0)
            p_cell.runs[0].font.size = Pt(9.5)
            p_cell.runs[0].font.name = 'Times New Roman'
            
            if r_idx == 0:
                set_cell_background(cell, "F2F2F2")
                p_cell.runs[0].font.bold = True
                p_cell.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                if c_idx == 0:
                    p_cell.runs[0].font.bold = True
                    p_cell.alignment = WD_ALIGN_PARAGRAPH.LEFT
                elif c_idx in [1, 3]:
                    p_cell.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                else:
                    p_cell.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

    p_t7_space = doc.add_paragraph()
    p_t7_space.paragraph_format.space_after = Pt(12)'''

replacement_t7 = b'''    doc.add_paragraph(
        "Cox proportional hazards analysis identified several genes with statistically significant associations with "
        "overall survival (Table 6). Among these, ZFR2 (HR = 0.9988, P = 9.8 \xc3\x97 10\xe2\x88\x924), STAG3 (HR = 0.9997, P = 0.0077), "
        "SMC1B (HR = 0.9995, P = 0.0056) and RAD9B (HR = 0.9967, P = 0.0089) were significant. The hazard ratios and confidence intervals "
        "for these and other prognostic genes are visualized as a forest plot (Figure 15). However, all hazard ratios "
        "were very close to 1, indicating that although statistically significant, the effect sizes were small. Therefore, "
        "these findings should be considered exploratory and require validation in independent cohorts. Kaplan-Meier "
        "analysis, using median gene expression as the cutoff, demonstrated a significant survival difference "
        "(log-rank P = 0.024), with patients in the high-expression group demonstrating superior overall survival (Figure 16)."
    )
    
    # Insert Table 6 (Survival-associated genes) here
    p_t6_title = doc.add_paragraph()
    p_t6_title.paragraph_format.space_before = Pt(12)
    p_t6_title.paragraph_format.space_after = Pt(4)
    p_t6_title.paragraph_format.keep_with_next = True
    r_t6_title = p_t6_title.add_run("Table 6. Survival-Associated Genes Identified by Cox Proportional Hazards Analysis")
    r_t6_title.font.bold = True
    r_t6_title.font.size = Pt(11)
    
    table_6_data = [
        ["Gene", "Hazard Ratio", "95% CI", "P-value"],
        ["ZFR2", "0.9988", "0.9981\\u20130.9995", "0.0010"],
        ["SMC1B", "0.9995", "0.9992\\u20130.9999", "0.0056"],
        ["STAG3", "0.9997", "0.9995\\u20130.9999", "0.0077"],
        ["RAD9B", "0.9967", "0.9942\\u20130.9992", "0.0089"]
    ]
    
    t6 = doc.add_table(rows=len(table_6_data), cols=4)
    t6.alignment = WD_TABLE_ALIGNMENT.CENTER
    border_format = {'sz': 4, 'val': 'single', 'color': 'D3D3D3', 'space': '0'}
    
    for r_idx, row_cells in enumerate(t6.rows):
        for c_idx, cell in enumerate(row_cells.cells):
            cell.text = table_6_data[r_idx][c_idx]
            set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
            set_cell_borders(cell, top=border_format, bottom=border_format, left=border_format, right=border_format)
            
            p_cell = cell.paragraphs[0]
            p_cell.paragraph_format.line_spacing = 1.05
            p_cell.paragraph_format.space_after = Pt(0)
            p_cell.runs[0].font.size = Pt(9.5)
            p_cell.runs[0].font.name = 'Times New Roman'
            
            if r_idx == 0:
                set_cell_background(cell, "F2F2F2")
                p_cell.runs[0].font.bold = True
                p_cell.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                if c_idx == 0:
                    p_cell.runs[0].font.bold = True
                    p_cell.alignment = WD_ALIGN_PARAGRAPH.LEFT
                elif c_idx in [1, 3]:
                    p_cell.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                else:
                    p_cell.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

    p_t6_space = doc.add_paragraph()
    p_t6_space.paragraph_format.space_after = Pt(12)'''

target_t7 = target_t7.replace(b'\n', b'\r\n')
replacement_t7 = replacement_t7.replace(b'\n', b'\r\n')

# Check if target_t7 is in content. The Wald stat '9.8 \xc3\x97 10\xe2\x88\x924' might be written slightly differently, so let's match on a broader sequence.
if target_t7 in content:
    content = content.replace(target_t7, replacement_t7)
    print("Table 7 renumbering matched!")
else:
    target_t7_lf = target_t7.replace(b'\r\n', b'\n')
    replacement_t7_lf = replacement_t7.replace(b'\r\n', b'\n')
    if target_t7_lf in content:
        content = content.replace(target_t7_lf, replacement_t7_lf)
        print("Table 7 renumbering matched (LF)!")
    else:
        # Let's search with regex or simple replacements for Table 7 parts if full block fails
        print("Table 7 full target NOT found. Trying parts replacement...")
        # Replacement of Table 7 occurrences in content using normal replace
        content = content.replace(b'overall survival (Table 7).', b'overall survival (Table 6).')
        content = content.replace(b'# Insert Table 7 (Survival-associated genes) here', b'# Insert Table 6 (Survival-associated genes) here')
        content = content.replace(b'p_t7_title', b'p_t6_title')
        content = content.replace(b'r_t7_title', b'r_t6_title')
        content = content.replace(b'Table 7. Survival-Associated Genes', b'Table 6. Survival-Associated Genes')
        content = content.replace(b'table_7_data', b'table_6_data')
        content = content.replace(b't7', b't6')
        content = content.replace(b'p_t7_space', b'p_t6_space')
        print("Table 7 parts replaced.")

# ----------------- Part 4: Add Table 5 references to Section 3.7 & Discussion -----------------
# Section 3.7 reference
content = content.replace(
    b'significantly downregulated (log2FC = \\xe2\\x88\\x921.92, FDR = 1.48 \\xc3\x97 10\\xe2\\x88\x925).',
    b'significantly downregulated (log2FC = \\xe2\\x88\\x921.92, FDR = 1.48 \\xc3\x97 10\\xe2\\x88\x925; Table 5).'
)
# If it was decoded, check if it's stored as unicode in generate_docx.py
content = content.replace(
    b'significantly downregulated (log2FC = \xe2\x88\x921.92, FDR = 1.48 \xc3\x97 10\xe2\x88\x925).',
    b'significantly downregulated (log2FC = \xe2\x88\x921.92, FDR = 1.48 \xc3\x97 10\xe2\x88\x925; Table 5).'
)
# Try with double-backslashes or normal strings in script
content = content.replace(
    b'significantly downregulated (log2FC = \\u22121.92, FDR = 1.48 \\u00d7 10\\u207b\\u2075).',
    b'significantly downregulated (log2FC = \\u22121.92, FDR = 1.48 \\u00d7 10\\u207b\\u2075; Table 5).'
)
content = content.replace(
    b'significantly downregulated (log2FC = \\u22121.92, FDR = 1.48 \\u00d7 10\\u207b\\u2075)',
    b'significantly downregulated (log2FC = \\u22121.92, FDR = 1.48 \\u00d7 10\\u207b\\u2075; Table 5)'
)

# Discussion S100A7 reference
content = content.replace(
    b'psoriasin, was significantly downregulated (log2FC = \\u22121.92, FDR = 1.48 \\u00d7 10\\u207b\\u2075).',
    b'psoriasin, was significantly downregulated (log2FC = \\u22121.92, FDR = 1.48 \\u00d7 10\\u207b\\u2075; Table 5).'
)
# Discussion TACSTD2 reference
content = content.replace(
    b'present dataset (log2FC = 0.60, FDR = 5.75 \\u00d7 10\\u207b\\u2074). Therefore, its potential role in HPV-associated tumors requires further investigation.',
    b'present dataset (log2FC = 0.60, FDR = 5.75 \\u00d7 10\\u207b\\u2074; Table 5). Therefore, its potential role in HPV-associated tumors requires further investigation.'
)

# Write back
with open('generate_docx.py', 'wb') as f:
    f.write(content)
print("Finished applying merge patch!")
