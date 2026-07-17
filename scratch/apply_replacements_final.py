file_path = "generate_docx.py"

with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Replace Figure 8/9/10 citations in CD8 correlation text
text = text.replace("P < 2.2 \u00d7 10\u221216; Figure 8)", "P < 2.2 \u00d7 10\u221216; Figure 9)")
text = text.replace("P < 2.2 \u00d7 10\u221216; Figure 9)", "P < 2.2 \u00d7 10\u221216; Figure 10)")

# 2. Replace CD8A Validation caption
old_cd8a_cap = '"Figure 8. Validation of CIBERSORTx CD8+ T-cell estimates using CD8A gene expression. Spearman rho = 0.673, P < 2.2 \u00d7 10\u207b\u00b9\u2076, confirming the reliability of deconvolution estimates."'
new_cd8a_cap = '"Figure 9. Validation of CIBERSORTx CD8+ T-cell estimates using CD8A gene expression. Spearman rho = 0.673, P < 2.2 \u00d7 10\u207b\u00b9\u2076, confirming the reliability of deconvolution estimates."'
text = text.replace(old_cd8a_cap, new_cd8a_cap)

# 3. Replace CD8B Validation caption
old_cd8b_cap = '"Figure 9. Validation of CIBERSORTx CD8+ T-cell estimates using CD8B gene expression. Spearman rho = 0.636, P < 2.2 \u00d7 10\u207b\u00b9\u2076."'
new_cd8b_cap = '"Figure 10. Validation of CIBERSORTx CD8+ T-cell estimates using CD8B gene expression. Spearman rho = 0.636, P < 2.2 \u00d7 10\u207b\u00b9\u2076."'
text = text.replace(old_cd8b_cap, new_cd8b_cap)

# 4. Replace CD8/M2 Ratio caption
old_ratio_cap = '"Figure 10. CD8/M2 macrophage ratio (log2-transformed) in HPV-positive versus HPV-negative HNSC. HPV-positive tumours demonstrate a significantly higher CD8/M2 ratio, indicating a more cytotoxic immune balance (Wilcoxon P = 7.46 \u00d7 10\u2212\u2075)."'
new_ratio_cap = '"Figure 11. CD8/M2 macrophage ratio (log2-transformed) in HPV-positive versus HPV-negative HNSC. HPV-positive tumours demonstrate a significantly higher CD8/M2 ratio, indicating a more cytotoxic immune balance (Wilcoxon P = 7.46 \u00d7 10\u2212\u2075)."'
text = text.replace(old_ratio_cap, new_ratio_cap)

# 5. Replace Survival KM curve caption
old_survival_cap = '"Figure 11. Kaplan-Meier overall survival curves stratified by expression of the top prognostic gene. High-expression group (pink) versus low-expression group (teal); log-rank P = 0.024. Risk table below shows number at risk at each time point."'
new_survival_cap = '"Figure 12. Kaplan-Meier overall survival curves stratified by expression of the top prognostic gene. High-expression group (pink) versus low-expression group (teal); log-rank P = 0.024. Risk table below shows number at risk at each time point."'
text = text.replace(old_survival_cap, new_survival_cap)

# 6. Locate and replace the entire fig_legends array at the end of the file
# We find where it starts and ends
start_marker = "fig_legends = ["
end_marker = "    ]"

start_pos = text.find(start_marker)
if start_pos != -1:
    # Find the next end_marker after start_pos
    end_pos = text.find(end_marker, start_pos)
    if end_pos != -1:
        end_pos += len(end_marker)
        
        # Define the new fig_legends array block
        new_legends_block = """fig_legends = [
        ("Figure 1", "Schematic workflow of the bioinformatics analysis pipeline. TCGA-HNSC RNA-seq raw count data were stratified by HPV status and subjected to differential expression analysis (DESeq2), immune cell deconvolution (CIBERSORTx/LM22), pathway enrichment (GO/KEGG), GSEA, and survival analysis."),
        ("Figure 2", "Principal component analysis of 279 TCGA-HNSC samples. HPV-positive (teal) and HPV-negative (salmon) samples demonstrate partial separation along PC1 (21% variance) and PC2 (14% variance)."),
        ("Figure 3", "Volcano plot of DESeq2 differential expression results (HPV-positive vs. HPV-negative HNSC). Upregulated genes (blue) and downregulated genes (red) meeting significance thresholds (FDR < 0.05, |log2FC| > 1) are shown. Top-ranked genes are labelled."),
        ("Figure 4", "Plasma cell infiltration in HPV-positive versus HPV-negative HNSC. Box-and-jitter plots showing CIBERSORTx-estimated plasma cell fractions, stratified by HPV status. HPV-positive tumours exhibit markedly elevated plasma cell fractions (Wilcoxon FDR = 0.001)."),
        ("Figure 5", "CD8+ T-cell infiltration in HPV-positive versus HPV-negative HNSC. CIBERSORTx-estimated CD8+ T-cell fractions are significantly elevated in HPV-positive tumours (Wilcoxon FDR = 0.020)."),
        ("Figure 6", "M0 macrophage infiltration in HPV-positive versus HPV-negative HNSC. Box-and-jitter plots showing CIBERSORTx-estimated M0 macrophage fractions, stratified by HPV status. HPV-positive tumours exhibit significantly reduced M0 macrophage fractions (Wilcoxon FDR = 0.002), consistent with a less immunosuppressed or less undifferentiated myeloid microenvironment."),
        ("Figure 7", "Graphical summary of immune infiltration remodeling in HPV-positive versus HPV-negative HNSC. Significantly enriched populations (emerald card) include Plasma cells, CD8+ T cells, and B cells. Significantly depleted populations (rose card) include M0 macrophages, resting NK cells, and resting CD4+ memory T cells."),
        ("Figure 8", "Heatmap of significantly differentially infiltrating immune cell populations across HPV-positive and HPV-negative HNSC samples. Clear clustering of HPV-positive tumors is characterized by increased plasma-cell and CD8+ T-cell abundance together with reduced M0 macrophages and resting NK cells."),
        ("Figure 9", "Validation of CIBERSORTx CD8+ T-cell estimates using CD8A gene expression. Spearman rho = 0.673, P < 2.2 \u00d7 10\u2212\u207b\u00b9\u2076, confirming the reliability of deconvolution estimates."),
        ("Figure 10", "Validation of CIBERSORTx CD8+ T-cell estimates using CD8B gene expression. Spearman rho = 0.636, P < 2.2 \u00d7 10\u2212\u207b\u00b9\u2076."),
        ("Figure 11", "CD8/M2 macrophage ratio (log2-transformed) in HPV-positive versus HPV-negative HNSC. HPV-positive tumours demonstrate a significantly higher CD8/M2 ratio, indicating a more cytotoxic immune balance (Wilcoxon P = 7.46 \u00d7 10\u2212\u2075)."),
        ("Figure 12", "Kaplan-Meier overall survival curves stratified by expression of the top prognostic gene. High-expression group (pink) versus low-expression group (teal); log-rank P = 0.024. Risk table below shows number at risk at each time point."),
        ("Figure 13", "Gene Ontology (GO) Biological Process enrichment analysis of genes upregulated in HPV-positive HNSC. The most significantly enriched biological processes were primarily related to immune activation, adaptive immune response, and B-cell/plasma-cell functions."),
        ("Figure 14", "KEGG pathway enrichment analysis of differentially expressed genes. The enriched pathways highlight biological processes altered between HPV-positive and HPV-negative HNSC."),
        ("Figure 15", "Gene Set Enrichment Analysis (GSEA) of Hallmark pathways associated with HPV status.")
    ]"""
        text = text[:start_pos] + new_legends_block + text[end_pos:]
        print("Successfully replaced fig_legends block.")
    else:
        print("Error: Could not find end_marker for fig_legends")
else:
    print("Error: Could not find start_marker for fig_legends")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)

print("Final replacement script finished.")
