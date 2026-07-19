# Canonical Manuscript Outputs Mapping

This document provides a 1-to-1 mapping between the figures and supplementary tables in the submitted manuscript and the corresponding files in the repository. All exploratory, working, and intermediate duplicates have been archived under `figures/archive/` and `results/archive/` respectively.

## Figures Mapping

| Manuscript Figure | Description | Repository File Path |
| :--- | :--- | :--- |
| **Figure 1** | Study conceptual design and analysis workflow flowchart | [Figure_1_Workflow.png](file:///c:/Users/rejoy/Documents/Intern_Project/figures/Figure_1_Workflow.png) |
| **Figure 2** | Principal Component Analysis (PCA) of raw HNSC counts (Stratification) | [HNSC_HPV_PCA.png](file:///c:/Users/rejoy/Documents/Intern_Project/figures/HNSC_HPV_PCA.png) |
| **Figure 3** | DESeq2 Volcano plot of differentially expressed genes in HNSC | [Figure8_Volcano_DESeq2.png](file:///c:/Users/rejoy/Documents/Intern_Project/figures/Figure8_Volcano_DESeq2.png) |
| **Figure 4** | CIBERSORTx infiltration boxplot for Plasma cells | [Plasma_Cells_Boxplot.png](file:///c:/Users/rejoy/Documents/Intern_Project/figures/Plasma_Cells_Boxplot.png) |
| **Figure 5** | CIBERSORTx infiltration boxplot for CD8+ T cells | [HNSC_HPV_CD8_Boxplot.png](file:///c:/Users/rejoy/Documents/Intern_Project/figures/HNSC_HPV_CD8_Boxplot.png) |
| **Figure 6** | CIBERSORTx infiltration boxplot for M0 Macrophages | [M0_Macrophage_Boxplot.png](file:///c:/Users/rejoy/Documents/Intern_Project/figures/M0_Macrophage_Boxplot.png) |
| **Figure 7** | Overview landscape barplot of immune cell fraction deconvolution | [HNSC_Immune_Summary.png](file:///c:/Users/rejoy/Documents/Intern_Project/figures/HNSC_Immune_Summary.png) |
| **Figure 8** | Clustered immune cell fraction heatmap (HPV-positive vs. HPV-negative) | [Revised_Immune_Heatmap.png](file:///c:/Users/rejoy/Documents/Intern_Project/figures/Revised_Immune_Heatmap.png) |
| **Figure 9 (Left)** | Validation correlation of CD8+ T-cell fraction against `CD8A` expression | [Figure_CD8A_Validation.png](file:///c:/Users/rejoy/Documents/Intern_Project/figures/Figure_CD8A_Validation.png) |
| **Figure 9 (Right)** | Validation correlation of CD8+ T-cell fraction against `CD8B` expression | [Figure_CD8B_Validation.png](file:///c:/Users/rejoy/Documents/Intern_Project/figures/Figure_CD8B_Validation.png) |
| **Figure 10** | Ratio comparison of CD8+ T cells to M2 Macrophages | [Revised_CD8_M2_Boxplot.png](file:///c:/Users/rejoy/Documents/Intern_Project/figures/Revised_CD8_M2_Boxplot.png) |
| **Figure 11 (Left)** | Cox proportional-hazards forest plot of prognostic candidate risk genes | [HNSC_Forest_Plot_Final.png](file:///c:/Users/rejoy/Documents/Intern_Project/figures/HNSC_Forest_Plot_Final.png) |
| **Figure 11 (Right)** | Kaplan-Meier overall survival curve stratified by `ZFR2` | [HNSC_BestGene_KM.png](file:///c:/Users/rejoy/Documents/Intern_Project/figures/HNSC_BestGene_KM.png) |
| **Supplementary Figure S1** | GO biological process enrichment dotplot for downregulated genes | [HNSC_HPV_GO_Downregulated.png](file:///c:/Users/rejoy/Documents/Intern_Project/figures/HNSC_HPV_GO_Downregulated.png) |
| **Supplementary Figure S2** | GSEA ridgeplot of enriched Hallmark gene sets in HPV status | [HNSC_HPV_GSEA_ridgeplot.png](file:///c:/Users/rejoy/Documents/Intern_Project/figures/HNSC_HPV_GSEA_ridgeplot.png) |
| **Supplementary Figure S3** | Cohort selection attrition/filtering flow diagram | [Figure_S1_Cohort_Filtering.png](file:///c:/Users/rejoy/Documents/Intern_Project/figures/Figure_S1_Cohort_Filtering.png) |

## Supplementary Tables Mapping

| Manuscript Table | Description | Repository File Path |
| :--- | :--- | :--- |
| **Supplementary Table S1** | Complete DESeq2 differential expression results for all analyzed genes | [HNSC_DESeq2_All_Results.csv](file:///c:/Users/rejoy/Documents/Intern_Project/results/HNSC_DESeq2_All_Results.csv) |
| **Supplementary Table S2** | Significant differentially expressed genes (FDR < 0.05, \|log2FC\| > 1) | [HNSC_DESeq2_Significant_Genes.csv](file:///c:/Users/rejoy/Documents/Intern_Project/results/HNSC_DESeq2_Significant_Genes.csv) |
| **Supplementary Table S3** | Top 20 upregulated genes in HPV-positive HNSC, ranked by Wald statistic | [Top20_Upregulated_Genes.csv](file:///c:/Users/rejoy/Documents/Intern_Project/results/Top20_Upregulated_Genes.csv) |
| **Supplementary Table S4** | Top 20 downregulated genes in HPV-positive HNSC, ranked by Wald statistic | [Top20_Downregulated_Genes.csv](file:///c:/Users/rejoy/Documents/Intern_Project/results/Top20_Downregulated_Genes.csv) |
| **Supplementary Table S5** | Differential expression results for immunoglobulin-related genes | [Immunoglobulin_Genes_DESeq2.csv](file:///c:/Users/rejoy/Documents/Intern_Project/results/Immunoglobulin_Genes_DESeq2.csv) |
| **Supplementary Table S6** | Differential expression results for keratinization-associated genes | [Keratinization_Genes_DESeq2.csv](file:///c:/Users/rejoy/Documents/Intern_Project/results/Keratinization_Genes_DESeq2.csv) |
| **Supplementary Table S7** | CIBERSORTx immune cell fraction estimates across 22 immune cell populations | [CIBERSORTx_Job14_Results.csv](file:///c:/Users/rejoy/Documents/Intern_Project/data_processed/CIBERSORTx_Job14_Results.csv) |
| **Supplementary Table S8** | Wilcoxon rank-sum test comparison stats for CIBERSORTx cell fractions | [HNSC_HPV_Immune_Comparison.csv](file:///c:/Users/rejoy/Documents/Intern_Project/results/HNSC_HPV_Immune_Comparison.csv) |
| **Supplementary Table S9** | Univariate Cox proportional-hazards survival analysis results | [HNSC_Survival_Results.csv](file:///c:/Users/rejoy/Documents/Intern_Project/results/HNSC_Survival_Results.csv) |
| **Supplementary Table S10** | GSEA functional pathway results using MSigDB Hallmark gene sets | [HNSC_HPV_GSEA.csv](file:///c:/Users/rejoy/Documents/Intern_Project/results/HNSC_HPV_GSEA.csv) |
| **Supplementary Table S11** | KEGG pathway enrichment results for downregulated genes | [HNSC_HPV_KEGG_Downregulated.csv](file:///c:/Users/rejoy/Documents/Intern_Project/results/HNSC_HPV_KEGG_Downregulated.csv) |
| **Supplementary Table S12** | GO biological process enrichment results for upregulated genes | [HNSC_HPV_GO_Upregulated.csv](file:///c:/Users/rejoy/Documents/Intern_Project/results/HNSC_HPV_GO_Upregulated.csv) |
| **Supplementary Table S13** | GO biological process enrichment results for downregulated genes | [HNSC_HPV_GO_Downregulated.csv](file:///c:/Users/rejoy/Documents/Intern_Project/results/HNSC_HPV_GO_Downregulated.csv) |
| **Supplementary Table S14** | Cohort selection filtering attrition count summary table | [Cohort_Filtering_Summary.csv](file:///c:/Users/rejoy/Documents/Intern_Project/results/Cohort_Filtering_Summary.csv) |
