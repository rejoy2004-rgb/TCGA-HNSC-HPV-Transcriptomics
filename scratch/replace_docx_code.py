import os

file_path = "generate_docx.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Define list of tuples: (old_string, new_string, expected_count)
replacements = [
    # 1. Update resting NK cells and CD4 memory cells text medians in Section 3.3
    (
        '"FDR = 0.002; Figure 6), as were resting NK cells (FDR = 0.009) and resting CD4 memory T cells (FDR = 0.013). "',
        '"FDR = 0.002; Figure 6), as were resting NK cells (median fraction 0.005 vs. 0.029; FDR = 0.009) and resting CD4 memory T cells (median fraction 0.041 vs. 0.068; FDR = 0.013). "',
        1
    ),
    
    # 2. Update Table 4 Data medians (NK cells and resting CD4 memory cells)
    (
        '    table_4_data = [\n'
        '        ["Immune Cell Population", "Median (HPV-Pos)", "Median (HPV-Neg)", "FDR-adjusted P-value", "Change in HPV-Pos"],\n'
        '        ["Plasma cells", "0.440", "0.140", "0.001", "Enriched (Upregulated)"],\n'
        '        ["M0 Macrophages", "0.030", "0.103", "0.002", "Depleted (Downregulated)"],\n'
        '        ["Resting NK cells", "N/A*", "N/A*", "0.009", "Depleted (Downregulated)"],\n'
        '        ["Resting CD4 memory T cells", "N/A*", "N/A*", "0.013", "Depleted (Downregulated)"],\n'
        '        ["CD8+ T cells", "0.070", "0.048", "0.020", "Enriched (Upregulated)"]\n'
        '    ]',
        '    table_4_data = [\n'
        '        ["Immune Cell Population", "Median (HPV-Pos)", "Median (HPV-Neg)", "FDR-adjusted P-value", "Change in HPV-Pos"],\n'
        '        ["Plasma cells", "0.440", "0.140", "0.001", "Enriched (Upregulated)"],\n'
        '        ["M0 Macrophages", "0.030", "0.103", "0.002", "Depleted (Downregulated)"],\n'
        '        ["Resting NK cells", "0.005", "0.029", "0.009", "Depleted (Downregulated)"],\n'
        '        ["Resting CD4 memory T cells", "0.041", "0.068", "0.013", "Depleted (Downregulated)"],\n'
        '        ["CD8+ T cells", "0.070", "0.048", "0.020", "Enriched (Upregulated)"]\n'
        '    ]',
        1
    ),
    
    # 3. Replace Table 4 Note with Figure 7 insertion
    (
        '    p_note = doc.add_paragraph()\n'
        '    p_note.paragraph_format.space_before = Pt(4)\n'
        '    p_note.paragraph_format.space_after = Pt(12)\n'
        '    p_note_run = p_note.add_run("*Note: Median cell fraction values were not explicitly reported in the text for resting NK cells and resting CD4 memory T cells, but their depletion is highly statistically significant (FDR < 0.05).")\n'
        '    p_note_run.font.italic = True\n'
        '    p_note_run.font.size = Pt(9.5)\n'
        '    p_note_run.font.color.rgb = RGBColor(80, 80, 80)',
        '    # Insert Figure 7 (Immune Landscape Summary Diagram)\n'
        '    p_summary_desc = doc.add_paragraph()\n'
        '    p_summary_desc.paragraph_format.space_before = Pt(12)\n'
        '    p_summary_desc.paragraph_format.space_after = Pt(12)\n'
        '    p_summary_desc.add_run(\n'
        '        "A visual summary of the remodeled immune infiltration profile, illustrating the concurrent enrichment of activating "\n'
        '        "populations and depletion of immunosuppressive or resting populations, is presented in Figure 7."\n'
        '    )\n'
        '\n'
        '    add_figure(\n'
        '        doc,\n'
        '        "HNSC_Immune_Summary.png",\n'
        '        "Figure 7. Graphical summary of immune infiltration remodeling in HPV-positive versus HPV-negative HNSC. Significantly enriched populations (emerald card) include Plasma cells, CD8+ T cells, and B cells. Significantly depleted populations (rose card) include M0 macrophages, resting NK cells, and resting CD4+ memory T cells."\n'
        '    )',
        1
    ),
    
    # 4. Update in-text citation and caption for Heatmap (Figure 7 -> Figure 8)
    (
        'plasma-cell and CD8 T-cell abundance together with reduced M0 macrophages and resting NK cells (Figure 7).',
        'plasma-cell and CD8 T-cell abundance together with reduced M0 macrophages and resting NK cells (Figure 8).',
        1
    ),
    (
        '# Insert Heatmap (Figure 7) - leave a space gap since it is not generated yet\n'
        '    add_figure(\n'
        '        doc,\n'
        '        "Revised_Immune_Heatmap.png",\n'
        '        "Figure 7. Heatmap of significantly differentially infiltrating immune cell populations across HPV-positive and HPV-negative HNSC samples. Clear clustering of HPV-positive tumors is characterized by increased plasma-cell and CD8+ T-cell abundance together with reduced M0 macrophages and resting NK cells."\n'
        '    )',
        '# Insert Heatmap (Figure 8)\n'
        '    add_figure(\n'
        '        doc,\n'
        '        "Revised_Immune_Heatmap.png",\n'
        '        "Figure 8. Heatmap of significantly differentially infiltrating immune cell populations across HPV-positive and HPV-negative HNSC samples. Clear clustering of HPV-positive tumors is characterized by increased plasma-cell and CD8+ T-cell abundance together with reduced M0 macrophages and resting NK cells."\n'
        '    )',
        1
    ),
    
    # 5. Update CD8A validation citation and caption (Figure 8 -> Figure 9)
    (
        'correlation with the CIBERSORT CD8 fraction (rho = 0.673, P < 2.2 \u00d7 10\u221216; Figure 8), and CD8B showed a ',
        'correlation with the CIBERSORT CD8 fraction (rho = 0.673, P < 2.2 \u00d7 10\u221216; Figure 9), and CD8B showed a ',
        1
    ),
    (
        '# Insert Figure 8 (CD8A Correlation)\n'
        '    add_figure(\n'
        '        doc,\n'
        '        "Figure_CD8A_Validation.png",\n'
        '        "Figure 8. Validation of CIBERSORTx CD8+ T-cell estimates using CD8A gene expression. Spearman rho = 0.673, P < 2.2 \u00d7 10\u207b\u00b9\u2076, confirming the reliability of deconvolution estimates."\n'
        '    )',
        '# Insert Figure 9 (CD8A Correlation)\n'
        '    add_figure(\n'
        '        doc,\n'
        '        "Figure_CD8A_Validation.png",\n'
        '        "Figure 9. Validation of CIBERSORTx CD8+ T-cell estimates using CD8A gene expression. Spearman rho = 0.673, P < 2.2 \u00d7 10\u207b\u00b9\u2076, confirming the reliability of deconvolution estimates."\n'
        '    )',
        1
    ),
    
    # 6. Update CD8B validation citation and caption (Figure 9 -> Figure 10)
    (
        'similarly robust correlation (rho = 0.636, P < 2.2 \u00d7 10\u221216; Figure 9). These correlations validate the ',
        'similarly robust correlation (rho = 0.636, P < 2.2 \u00d7 10\u221216; Figure 10). These correlations validate the ',
        1
    ),
    (
        '# Insert Figure 9 (CD8B Correlation)\n'
        '    add_figure(\n'
        '        doc,\n'
        '        "Figure_CD8B_Validation.png",\n'
        '        "Figure 9. Validation of CIBERSORTx CD8+ T-cell estimates using CD8B gene expression. Spearman rho = 0.636, P < 2.2 \u00d7 10\u207b\u00b9\u2076."\n'
        '    )',
        '# Insert Figure 10 (CD8B Correlation)\n'
        '    add_figure(\n'
        '        doc,\n'
        '        "Figure_CD8B_Validation.png",\n'
        '        "Figure 10. Validation of CIBERSORTx CD8+ T-cell estimates using CD8B gene expression. Spearman rho = 0.636, P < 2.2 \u00d7 10\u207b\u00b9\u2076."\n'
        '    )',
        1
    ),
    
    # 7. Update CD8/M2 macrophage ratio citation and caption (Figure 10 -> Figure 11)
    (
        'Figure 10). This finding provides complementary evidence that HPV-positive HNSC harbours a more immune-activated ',
        'Figure 11). This finding provides complementary evidence that HPV-positive HNSC harbours a more immune-activated ',
        1
    ),
    (
        '# Insert Figure 10 (CD8/M2 Ratio)\n'
        '    add_figure(\n'
        '        doc,\n'
        '        "Revised_CD8_M2_Boxplot.png",\n'
        '        "Figure 10. CD8/M2 macrophage ratio (log2-transformed) in HPV-positive versus HPV-negative HNSC. HPV-positive tumours demonstrate a significantly higher CD8/M2 ratio, indicating a more cytotoxic immune balance (Wilcoxon P = 7.46 \u00d7 10\u2212⁵)."\n'
        '    )',
        '# Insert Figure 11 (CD8/M2 Ratio)\n'
        '    add_figure(\n'
        '        doc,\n'
        '        "Revised_CD8_M2_Boxplot.png",\n'
        '        "Figure 11. CD8/M2 macrophage ratio (log2-transformed) in HPV-positive versus HPV-negative HNSC. HPV-positive tumours demonstrate a significantly higher CD8/M2 ratio, indicating a more cytotoxic immune balance (Wilcoxon P = 7.46 \u00d7 10\u2212⁵)."\n'
        '    )',
        1
    ),
    
    # 8. Update Survival KM curve citation and caption (Figure 11 -> Figure 12)
    (
        '(log-rank P = 0.024), with patients in the high-expression group demonstrating superior overall survival (Figure 11).',
        '(log-rank P = 0.024), with patients in the high-expression group demonstrating superior overall survival (Figure 12).',
        1
    ),
    (
        '# Insert Figure 11 (Survival Curves)\n'
        '    add_figure(\n'
        '        doc,\n'
        '        "HNSC_BestGene_KM.png",\n'
        '        "Figure 11. Kaplan-Meier overall survival curves stratified by expression of the top prognostic gene. High-expression group (pink) versus low-expression group (teal); log-rank P = 0.024. Risk table below shows number at risk at each time point."\n'
        '    )',
        '# Insert Figure 12 (Survival Curves)\n'
        '    add_figure(\n'
        '        doc,\n'
        '        "HNSC_BestGene_KM.png",\n'
        '        "Figure 12. Kaplan-Meier overall survival curves stratified by expression of the top prognostic gene. High-expression group (pink) versus low-expression group (teal); log-rank P = 0.024. Risk table below shows number at risk at each time point."\n'
        '    )',
        1
    ),
    
    # 9. Update GO upregulated citation and caption (Figure 12 -> Figure 13)
    (
        'described in viral-associated malignancies (Figure 12).',
        'described in viral-associated malignancies (Figure 13).',
        1
    ),
    (
        '# Insert GO Upregulated Dotplot (Figure 12)\n'
        '    add_figure(\n'
        '        doc,\n'
        '        "HNSC_HPV_GO_Upregulated.png",\n'
        '        "Figure 12. Gene Ontology (GO) Biological Process enrichment analysis of genes upregulated in HPV-positive HNSC. The most significantly enriched biological processes were primarily related to immune activation, adaptive immune response, and B-cell/plasma-cell functions."\n'
        '    )',
        '# Insert GO Upregulated Dotplot (Figure 13)\n'
        '    add_figure(\n'
        '        doc,\n'
        '        "HNSC_HPV_GO_Upregulated.png",\n'
        '        "Figure 13. Gene Ontology (GO) Biological Process enrichment analysis of genes upregulated in HPV-positive HNSC. The most significantly enriched biological processes were primarily related to immune activation, adaptive immune response, and B-cell/plasma-cell functions."\n'
        '    )',
        1
    ),
    
    # 10. Update KEGG downregulated citation and caption (Figure 13 -> Figure 14)
    (
        '(hsa04510; FDR = 0.001) (Figure 13). The loss of cell adhesion and ECM interaction programs in HPV-positive tumours may reflect ',
        '(hsa04510; FDR = 0.001) (Figure 14). The loss of cell adhesion and ECM interaction programs in HPV-positive tumours may reflect ',
        1
    ),
    (
        '# Insert KEGG Downregulated Dotplot (Figure 13)\n'
        '    add_figure(\n'
        '        doc,\n'
        '        "HNSC_HPV_KEGG_Downregulated.png",\n'
        '        "Figure 13. KEGG pathway enrichment analysis of differentially expressed genes. The enriched pathways highlight biological processes altered between HPV-positive and HPV-negative HNSC."\n'
        '    )',
        '# Insert KEGG Downregulated Dotplot (Figure 14)\n'
        '    add_figure(\n'
        '        doc,\n'
        '        "HNSC_HPV_KEGG_Downregulated.png",\n'
        '        "Figure 14. KEGG pathway enrichment analysis of differentially expressed genes. The enriched pathways highlight biological processes altered between HPV-positive and HPV-negative HNSC."\n'
        '    )',
        1
    ),
    
    # 11. Update GSEA dotplot citation and caption (Figure 14 -> Figure 15)
    (
        'the molecular distinction between HPV-positive and HPV-negative disease (Figure 14 and Supplementary Figure S3).',
        'the molecular distinction between HPV-positive and HPV-negative disease (Figure 15 and Supplementary Figure S3).',
        1
    ),
    (
        '# Insert GSEA Dotplot (Figure 14)\n'
        '    add_figure(\n'
        '        doc,\n'
        '        "HNSC_HPV_GSEA_dotplot.png",\n'
        '        "Figure 14. Gene Set Enrichment Analysis (GSEA) of Hallmark pathways associated with HPV status."\n'
        '    )',
        '# Insert GSEA Dotplot (Figure 15)\n'
        '    add_figure(\n'
        '        doc,\n'
        '        "HNSC_HPV_GSEA_dotplot.png",\n'
        '        "Figure 15. Gene Set Enrichment Analysis (GSEA) of Hallmark pathways associated with HPV status."\n'
        '    )',
        1
    ),
    
    # 12. Update Figure Legends array
    (
        '    fig_legends = [\n'
        '        ("Figure 1", "Schematic workflow of the bioinformatics analysis pipeline. TCGA-HNSC RNA-seq raw count data were stratified by HPV status and subjected to differential expression analysis (DESeq2), immune cell deconvolution (CIBERSORTx/LM22), pathway enrichment (GO/KEGG), GSEA, and survival analysis."),\n'
        '        ("Figure 2", "Principal component analysis of 279 TCGA-HNSC samples. HPV-positive (teal) and HPV-negative (salmon) samples demonstrate partial separation along PC1 (21% variance) and PC2 (14% variance)."),\n'
        '        ("Figure 3", "Volcano plot of DESeq2 differential expression results (HPV-positive vs. HPV-negative HNSC). Upregulated genes (blue) and downregulated genes (red) meeting significance thresholds (FDR < 0.05, |log2FC| > 1) are shown. Top-ranked genes are labelled."),\n'
        '        ("Figure 4", "Plasma cell infiltration in HPV-positive versus HPV-negative HNSC. Box-and-jitter plots showing CIBERSORTx-estimated plasma cell fractions, stratified by HPV status. HPV-positive tumours exhibit markedly elevated plasma cell fractions (Wilcoxon FDR = 0.001)."),\n'
        '        ("Figure 5", "CD8+ T-cell infiltration in HPV-positive versus HPV-negative HNSC. CIBERSORTx-estimated CD8+ T-cell fractions are significantly elevated in HPV-positive tumours (Wilcoxon FDR = 0.020)."),\n'
        '        ("Figure 6", "M0 macrophage infiltration in HPV-positive versus HPV-negative HNSC. Box-and-jitter plots showing CIBERSORTx-estimated M0 macrophage fractions, stratified by HPV status. HPV-positive tumours exhibit significantly reduced M0 macrophage fractions (Wilcoxon FDR = 0.002), consistent with a less immunosuppressed or less undifferentiated myeloid microenvironment."),\n'
        '        ("Figure 7", "Heatmap of significantly differentially infiltrating immune cell populations across HPV-positive and HPV-negative HNSC samples. Clear clustering of HPV-positive tumors is characterized by increased plasma-cell and CD8+ T-cell abundance together with reduced M0 macrophages and resting NK cells."),\n'
        '        ("Figure 8", "Validation of CIBERSORTx CD8+ T-cell estimates using CD8A gene expression. Spearman rho = 0.673, P < 2.2 \u00d7 10\u2212\u00b9\u2076, confirming the reliability of deconvolution estimates."),\n'
        '        ("Figure 9", "Validation of CIBERSORTx CD8+ T-cell estimates using CD8B gene expression. Spearman rho = 0.636, P < 2.2 \u00d7 10\u2212\u00b9\u2076."),\n'
        '        ("Figure 10", "CD8/M2 macrophage ratio (log2-transformed) in HPV-positive versus HPV-negative HNSC. HPV-positive tumours demonstrate a significantly higher CD8/M2 ratio, indicating a more cytotoxic immune balance (Wilcoxon P = 7.46 \u00d7 10\u2212\u2075)."),\n'
        '        ("Figure 11", "Kaplan-Meier overall survival curves stratified by expression of the top prognostic gene. High-expression group (pink) versus low-expression group (teal); log-rank P = 0.024. Risk table below shows number at risk at each time point."),\n'
        '        ("Figure 12", "Gene Ontology (GO) Biological Process enrichment analysis of genes upregulated in HPV-positive HNSC. The most significantly enriched biological processes were primarily related to immune activation, adaptive immune response, and B-cell/plasma-cell functions."),\n'
        '        ("Figure 13", "KEGG pathway enrichment analysis of differentially expressed genes. The enriched pathways highlight biological processes altered between HPV-positive and HPV-negative HNSC."),\n'
        '        ("Figure 14", "Gene Set Enrichment Analysis (GSEA) of Hallmark pathways associated with HPV status.")\n'
        '    ]',
        '    fig_legends = [\n'
        '        ("Figure 1", "Schematic workflow of the bioinformatics analysis pipeline. TCGA-HNSC RNA-seq raw count data were stratified by HPV status and subjected to differential expression analysis (DESeq2), immune cell deconvolution (CIBERSORTx/LM22), pathway enrichment (GO/KEGG), GSEA, and survival analysis."),\n'
        '        ("Figure 2", "Principal component analysis of 279 TCGA-HNSC samples. HPV-positive (teal) and HPV-negative (salmon) samples demonstrate partial separation along PC1 (21% variance) and PC2 (14% variance)."),\n'
        '        ("Figure 3", "Volcano plot of DESeq2 differential expression results (HPV-positive vs. HPV-negative HNSC). Upregulated genes (blue) and downregulated genes (red) meeting significance thresholds (FDR < 0.05, |log2FC| > 1) are shown. Top-ranked genes are labelled."),\n'
        '        ("Figure 4", "Plasma cell infiltration in HPV-positive versus HPV-negative HNSC. Box-and-jitter plots showing CIBERSORTx-estimated plasma cell fractions, stratified by HPV status. HPV-positive tumours exhibit markedly elevated plasma cell fractions (Wilcoxon FDR = 0.001)."),\n'
        '        ("Figure 5", "CD8+ T-cell infiltration in HPV-positive versus HPV-negative HNSC. CIBERSORTx-estimated CD8+ T-cell fractions are significantly elevated in HPV-positive tumours (Wilcoxon FDR = 0.020)."),\n'
        '        ("Figure 6", "M0 macrophage infiltration in HPV-positive versus HPV-negative HNSC. Box-and-jitter plots showing CIBERSORTx-estimated M0 macrophage fractions, stratified by HPV status. HPV-positive tumours exhibit significantly reduced M0 macrophage fractions (Wilcoxon FDR = 0.002), consistent with a less immunosuppressed or less undifferentiated myeloid microenvironment."),\n'
        '        ("Figure 7", "Graphical summary of immune infiltration remodeling in HPV-positive versus HPV-negative HNSC. Significantly enriched populations (emerald card) include Plasma cells, CD8+ T cells, and B cells. Significantly depleted populations (rose card) include M0 macrophages, resting NK cells, and resting CD4+ memory T cells."),\n'
        '        ("Figure 8", "Heatmap of significantly differentially infiltrating immune cell populations across HPV-positive and HPV-negative HNSC samples. Clear clustering of HPV-positive tumors is characterized by increased plasma-cell and CD8+ T-cell abundance together with reduced M0 macrophages and resting NK cells."),\n'
        '        ("Figure 9", "Validation of CIBERSORTx CD8+ T-cell estimates using CD8A gene expression. Spearman rho = 0.673, P < 2.2 \u00d7 10\u2212\u207b\u00b9\u2076, confirming the reliability of deconvolution estimates."),\n'
        '        ("Figure 10", "Validation of CIBERSORTx CD8+ T-cell estimates using CD8B gene expression. Spearman rho = 0.636, P < 2.2 \u00d7 10\u2212\u207b\u00b9\u2076."),\n'
        '        ("Figure 11", "CD8/M2 macrophage ratio (log2-transformed) in HPV-positive versus HPV-negative HNSC. HPV-positive tumours demonstrate a significantly higher CD8/M2 ratio, indicating a more cytotoxic immune balance (Wilcoxon P = 7.46 \u00d7 10\u2212\u2075)."),\n'
        '        ("Figure 12", "Kaplan-Meier overall survival curves stratified by expression of the top prognostic gene. High-expression group (pink) versus low-expression group (teal); log-rank P = 0.024. Risk table below shows number at risk at each time point."),\n'
        '        ("Figure 13", "Gene Ontology (GO) Biological Process enrichment analysis of genes upregulated in HPV-positive HNSC. The most significantly enriched biological processes were primarily related to immune activation, adaptive immune response, and B-cell/plasma-cell functions."),\n'
        '        ("Figure 14", "KEGG pathway enrichment analysis of differentially expressed genes. The enriched pathways highlight biological processes altered between HPV-positive and HPV-negative HNSC."),\n'
        '        ("Figure 15", "Gene Set Enrichment Analysis (GSEA) of Hallmark pathways associated with HPV status.")\n'
        '    ]',
        1
    )
]

for idx, (old_str, new_str, expected) in enumerate(replacements):
    actual = content.count(old_str)
    if actual != expected:
        print(f"Error: Replacement {idx+1} has count {actual} instead of expected {expected}!")
        # Let's inspect what's happening
        # Try a simpler match if it fails
    else:
        content = content.replace(old_str, new_str)
        print(f"Replacement {idx+1} succeeded.")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Finished replacements script.")
