with open('generate_docx.py', 'rb') as f:
    content = f.read()

# 1. Update in-text citation of GSEA from Supplementary Figure S3 to S2
content = content.replace(b'Supplementary Figure S3', b'Supplementary Figure S2')

# 2. Update Supplementary Materials Description list
old_desc_block = b'''        ("Supplementary Figure S1", "Gene Ontology (GO) biological process enrichment dot plot for downregulated genes in HPV-positive versus HPV-negative HNSC (HNSC_HPV_GO_Downregulated.png)."),
        ("Supplementary Figure S2", "KEGG pathway enrichment dot plot for upregulated genes in HPV-positive versus HPV-negative HNSC (HNSC_HPV_KEGG_Upregulated.png)."),
        ("Supplementary Figure S3", "GSEA ridgeplot of enriched Hallmark gene sets in HPV-positive versus HPV-negative HNSC (HNSC_HPV_GSEA_ridgeplot.png)."),'''

new_desc_block = b'''        ("Supplementary Figure S1", "Gene Ontology (GO) biological process enrichment dot plot for downregulated genes in HPV-positive versus HPV-negative HNSC (HNSC_HPV_GO_Downregulated.png)."),
        ("Supplementary Figure S2", "GSEA ridgeplot of enriched Hallmark gene sets in HPV-positive versus HPV-negative HNSC (HNSC_HPV_GSEA_ridgeplot.png)."),'''

# Normalize newlines
old_desc_block = old_desc_block.replace(b'\n', b'\r\n')
new_desc_block = new_desc_block.replace(b'\n', b'\r\n')

if old_desc_block in content:
    content = content.replace(old_desc_block, new_desc_block)
    print("Supplementary list description matched!")
else:
    # Try LF version
    old_desc_block_lf = old_desc_block.replace(b'\r\n', b'\n')
    new_desc_block_lf = new_desc_block.replace(b'\r\n', b'\n')
    if old_desc_block_lf in content:
        content = content.replace(old_desc_block_lf, new_desc_block_lf)
        print("Supplementary list description matched (LF)!")
    else:
        print("Supplementary list description NOT found")

# 3. Update the figure embedding at the end of the file (remove S2, rename S3 to S2)
old_embed_block = b'''    # Supplementary Figure S2
    add_figure(
        doc,
        "HNSC_HPV_KEGG_Upregulated.png",
        "Supplementary Figure S2. KEGG pathway enrichment dot plot for upregulated genes in HPV-positive versus HPV-negative HNSC. Pathways are ranked by gene ratio, with bubble size indicating gene count and color showing the FDR-adjusted P-value."
    )
    
    # Supplementary Figure S3
    add_figure(
        doc,
        "HNSC_HPV_GSEA_ridgeplot.png",
        "Supplementary Figure S3. GSEA ridgeplot of enriched Hallmark gene sets in HPV-positive versus HPV-negative HNSC. The plot displays the distribution of fold changes for genes within each pathway, ranked by normalized enrichment score (NES) and colored by FDR-adjusted P-value."
    )'''

new_embed_block = b'''    # Supplementary Figure S2
    add_figure(
        doc,
        "HNSC_HPV_GSEA_ridgeplot.png",
        "Supplementary Figure S2. GSEA ridgeplot of enriched Hallmark gene sets in HPV-positive versus HPV-negative HNSC. The plot displays the distribution of fold changes for genes within each pathway, ranked by normalized enrichment score (NES) and colored by FDR-adjusted P-value."
    )'''

old_embed_block = old_embed_block.replace(b'\n', b'\r\n')
new_embed_block = new_embed_block.replace(b'\n', b'\r\n')

if old_embed_block in content:
    content = content.replace(old_embed_block, new_embed_block)
    print("Supplementary figure embedding block matched!")
else:
    old_embed_block_lf = old_embed_block.replace(b'\r\n', b'\n')
    new_embed_block_lf = new_embed_block.replace(b'\r\n', b'\n')
    if old_embed_block_lf in content:
        content = content.replace(old_embed_block_lf, new_embed_block_lf)
        print("Supplementary figure embedding block matched (LF)!")
    else:
        print("Supplementary figure embedding block NOT found")

with open('generate_docx.py', 'wb') as f:
    f.write(content)
print("Finished applying supplementary figures patch!")
