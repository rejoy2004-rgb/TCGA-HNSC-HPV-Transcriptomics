with open('generate_docx.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Replace GSEA text citation (Supplementary Figure S3 -> S2)
text = text.replace("Supplementary Figure S3", "Supplementary Figure S2")

# 2. Replace description list elements
target_desc_s2 = '("Supplementary Figure S2", "KEGG pathway enrichment dot plot for upregulated genes in HPV-positive versus HPV-negative HNSC (HNSC_HPV_KEGG_Upregulated.png)."),'
if target_desc_s2 in text:
    text = text.replace(target_desc_s2, '')
    print("Replaced S2 description")
else:
    # try without trailing comma or different spacing
    lines = text.split('\n')
    new_lines = []
    for line in lines:
        if 'HNSC_HPV_KEGG_Upregulated.png' in line and 'Supplementary Figure S2' in line:
            print("Removed line:", line)
            continue
        new_lines.append(line)
    text = '\n'.join(new_lines)

# 3. Replace GSEA description key from S3 to S2
text = text.replace('("Supplementary Figure S3", "GSEA ridgeplot', '("Supplementary Figure S2", "GSEA ridgeplot')

# 4. Remove Supplementary Figure S2 embedding code
# Let's locate the block by search and replace
embedding_target = """    # Supplementary Figure S2
    add_figure(
        doc,
        "HNSC_HPV_KEGG_Upregulated.png",
        "Supplementary Figure S2. KEGG pathway enrichment dot plot for upregulated genes in HPV-positive versus HPV-negative HNSC. Pathways are ranked by gene ratio, with bubble size indicating gene count and color showing the FDR-adjusted P-value."
    )"""

# Clean trailing spaces and newlines
normalized_text = text.replace('\r\n', '\n')
if embedding_target in normalized_text:
    normalized_text = normalized_text.replace(embedding_target, '')
    print("Removed S2 embedding block")
else:
    # Let's find it line by line
    lines = normalized_text.split('\n')
    new_lines = []
    skip = 0
    for i, line in enumerate(lines):
        if 'HNSC_HPV_KEGG_Upregulated.png' in line:
            # We want to skip this block!
            # The block starts a few lines earlier with "# Supplementary Figure S2"
            # and ends a few lines later with ")"
            # Let's verify how many lines to remove.
            # We can remove the lines around it.
            # Let's just find where add_figure starts and ends.
            print("Found target image line at", i)
            # Remove previous 2 lines (comment, add_figure) and subsequent 4 lines
            # let's rewrite the list of lines to remove
            del new_lines[-2:]  # remove comment and add_figure(
            skip = 4  # skip next 4 lines: doc, image path, caption, and closing parenthesis
            continue
        if skip > 0:
            skip -= 1
            print("Skipped line:", line)
            continue
        new_lines.append(line)
    normalized_text = '\n'.join(new_lines)

with open('generate_docx.py', 'w', encoding='utf-8') as f:
    f.write(normalized_text)
print("Finished patching generate_docx.py")
