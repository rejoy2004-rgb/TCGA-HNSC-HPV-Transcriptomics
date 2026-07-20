# Manuscript Data Sources and Traceability Audit

This document provides a complete audit trail mapping every category of scientific statistic, count, figure, and supplementary table generated in the final manuscript (`Immune_Landscape_HNSC.docx`) directly back to its source result file in the repository.

---

## 1. Primary Analysis Data Sources

| Manuscript Data Category | Generated Manuscript Values | Repository Source File Path | Extraction Method / Key |
| :--- | :--- | :--- | :--- |
| **Cohort Sample Counts** | 279 Total (243 HPV-Negative, 36 HPV-Positive) | [data_processed/HNSC_HPV_status.csv](file:///c:/Users/rejoy/Documents/Intern_Project/data_processed/HNSC_HPV_status.csv) | `HPV Status` frequency counts |
| **Cohort Sample Attrition** | 566 Raw -> 520 Tumors -> 279 Annotated | [results/Cohort_Filtering_Summary.csv](file:///c:/Users/rejoy/Documents/Intern_Project/results/Cohort_Filtering_Summary.csv) | `Step` vs. `Count` lookup |
| **Differential Expression Counts** | 4,744 Unadjusted DEGs, 4,800 Adjusted DEGs | [results/HNSC_DESeq2_All_Results.csv](file:///c:/Users/rejoy/Documents/Intern_Project/results/HNSC_DESeq2_All_Results.csv) | `padj < 0.05` & `\|log2FoldChange\| > 1` |
| **Plasma Cell Fraction** | Median 0.488 (HPV+) vs 0.145 (HPV-), FDR = 1.85e-04 | [results/HNSC_HPV_Immune_Comparison.csv](file:///c:/Users/rejoy/Documents/Intern_Project/results/HNSC_HPV_Immune_Comparison.csv) | `CellType == "Plasma cells"` |
| **CD8+ T-Cell Fraction** | Median 0.071 (HPV+) vs 0.043 (HPV-), FDR = 3.92e-04 | [results/HNSC_HPV_Immune_Comparison.csv](file:///c:/Users/rejoy/Documents/Intern_Project/results/HNSC_HPV_Immune_Comparison.csv) | `CellType == "T cells CD8"` |
| **M0 Macrophage Fraction** | Median 0.033 (HPV+) vs 0.131 (HPV-), FDR = 1.27e-05 | [results/HNSC_HPV_Immune_Comparison.csv](file:///c:/Users/rejoy/Documents/Intern_Project/results/HNSC_HPV_Immune_Comparison.csv) | `CellType == "Macrophages M0"` |
| **CD8/M2 Log2 Ratio Test** | Wilcoxon P = 7.43e-05 | [results/HNSC_CD8_M2_ratio_data.csv](file:///c:/Users/rejoy/Documents/Intern_Project/results/HNSC_CD8_M2_ratio_data.csv) | Computed ratio log2 values |
| **CD8 Marker Validation** | CD8A & CD8B Spearman correlation P-values | [results/HNSC_HPV_Immune_Comparison.csv](file:///c:/Users/rejoy/Documents/Intern_Project/results/HNSC_HPV_Immune_Comparison.csv) | Correlation tests with line markers |
| **Prognostic Candidate Cox** | ZFR2, STAG3, SMC1B, RAD9B Hazard Ratios | [results/HNSC_Standardized_Cox_Results.csv](file:///c:/Users/rejoy/Documents/Intern_Project/results/HNSC_Standardized_Cox_Results.csv) | `Gene` vs. `HR` / `Lower95CI` / `Upper95CI` |
| **GSEA Hallmark Pathways** | 3,041 enriched pathways (FDR < 0.25) | [results/HNSC_HPV_GSEA.csv](file:///c:/Users/rejoy/Documents/Intern_Project/results/HNSC_HPV_GSEA.csv) | `p.adjust < 0.25` ranking |

---

## 2. Dynamic Data-Driven Architecture (`generate_docx.py`)

The manuscript generator script [scripts/generate_docx.py](file:///c:/Users/rejoy/Documents/Intern_Project/scripts/generate_docx.py) reads these CSV result files programmatically using `pandas` at the start of execution. 

If an analysis script (`prepare_hpv_metadata.R` or `HPV_HNSC_Revision.R`) is updated and re-run, the next execution of `generate_docx.py` automatically updates every printed text paragraph, summary table, and inline statistics value in `Immune_Landscape_HNSC.docx`.

```python
# Programmatic Data Loading snippet from generate_docx.py
import os
import pandas as pd

hpv_df = pd.read_csv("data_processed/HNSC_HPV_status.csv")
n_hpv_neg = (hpv_df['HPV Status'] == 'negative').sum()
n_hpv_pos = (hpv_df['HPV Status'] == 'positive').sum()
n_total_cohort = len(hpv_df)

immune_df = pd.read_csv("results/HNSC_HPV_Immune_Comparison.csv")
plasma_stats = immune_df[immune_df['CellType'] == 'Plasma cells'].iloc[0]
```

---

## 3. Figures & Supplementary Tables Integration

All embedded images and tables are loaded directly from the canonical output paths verified in [documentation/Canonical_Outputs.md](file:///c:/Users/rejoy/Documents/Intern_Project/documentation/Canonical_Outputs.md):

* **Figures 1-11 & Supplementary Figures S1-S3**: Loaded directly from `figures/`.
* **Supplementary Tables S1-S14**: Generated directly from CSV files in `results/` and `data_processed/`.
