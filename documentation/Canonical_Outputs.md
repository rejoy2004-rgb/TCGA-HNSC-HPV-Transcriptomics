# Canonical Manuscript Outputs

This maps every figure and table in `manuscript/FINAL_INTEGRATED_MANUSCRIPT.docx` to its file and its source.

- **Figure exports:** main figures in `manuscript/submission_figures/`, supplementary figures in `supplementary/figures/` (LZW TIFF + PNG), produced by `scripts/figures/export_submission_figures.py`.
- **Table exports:** main tables in `manuscript/tables/`; supplementary tables in `supplementary/tables/`. These CSVs are exported from the built manuscript, so they match it exactly.
- **Rebuilding the manuscript:** `scripts/build_integrated_manuscript.js` (requires the `docx` npm package).

## Main figures

| Figure | Content | Source / script |
|---|---|---|
| Figure 1 | Differential expression (volcano, meiotic panel genes, GO terms) | 600 dpi panels in `figures/source_panels_600dpi/Figure 1/` → `scripts/figures/compose_figures.py` |
| Figure 2 | Promoter hypomethylation and replication (GSE38266) | `figures/source_panels_600dpi/Figure 3/` → `compose_figures.py` |
| Figure 3 | Viral-activity dependence and specificity (GSE65858) | `figures/source_panels_600dpi/Figure 4/` → `compose_figures.py` |
| Figure 4 | Immune microenvironment (CIBERSORTx) | `scripts/figures/make_tme_figure.py` from `data_processed/CIBERSORTx_Job14_Results.csv` |
| Figure 5 | Malignant-cell localisation (GSE181919) | `figures/source_panels_600dpi/Figure 6/` → `compose_figures.py` |
| Figure 6 | Single-cell replication (GSE182227) | `figures/source_panels_600dpi/Figure 7/` → `compose_figures.py` |
| Graphical abstract | Study summary | `scripts/figures/make_graphical_abstract.py` |

## Main tables

| Table | Content | Source |
|---|---|---|
| Table 1 | Clinical characteristics (n = 279) | `scripts/calculate_demographics.py` |
| Table 2 | Cohorts and roles | Methods |
| Table 3 | Category AUCs, GSE65858 | external-cohort and single-cell analyses |
| Table 4 | Module coherence, GSE65858 | external-cohort and single-cell analyses |
| Table 5 | Immune populations differing by HPV status | `results/HNSC_HPV_Immune_Comparison_All22_BH.csv` |
| Table 6 | Single-cell tumour-level contrasts | external-cohort and single-cell analyses |

## Supplementary figures

| Figure | Content | Source |
|---|---|---|
| S1 | PCA | `figures/HNSC_HPV_PCA.png` (`scripts/HPV_HNSC_Revision.R`) |
| S2 | Origin of the meiotic hypothesis (GSEA, category and panel enrichment) | `figures/source_panels_600dpi/Figure 2/` → `compose_figures.py` |
| S3 | Downregulated GO and KEGG pathways | `figures/HNSC_HPV_GO_Downregulated.png`, `figures/HNSC_HPV_KEGG_Downregulated.png` → `scripts/figures/make_supp_composites.py` |
| S4 | Module coherence | `figures/source_panels_600dpi/Figure 5/` → `compose_figures.py` |
| S5 | CD8+ T-cell deconvolution validation | `figures/Figure_CD8A_Validation.png`, `figures/Figure_CD8B_Validation.png` → `scripts/figures/make_supp_composites.py` |
| S6 | Exploratory Cox forest plot | `scripts/figures/make_forest_plot.py` from `results/HNSC_Standardized_Cox_Results.csv` |
| S7 | ZFR2 Kaplan–Meier | `figures/HNSC_BestGene_KM.png` (`scripts/HPV_HNSC_Revision.R`) |

## Supplementary tables

| Table | Content | Source |
|---|---|---|
| S1 | Six-gene core module | external-cohort and single-cell analyses |
| S2 | Top up- and downregulated genes | `results/HNSC_DESeq2_All_Results.csv` |
| S3 | Immune and epithelial marker genes, unadjusted and site-adjusted | `results/HNSC_DESeq2_All_Results.csv`, `results/HNSC_DESeq2_PrimarySite_Adjusted_All_Results.csv` |
| S4 | Panel-category enrichment | external-cohort and single-cell analyses |
| S5 | Confounder and sensitivity analyses | external-cohort analyses; review rows from `results/review_sensitivity/` (`scripts/review_analyses/`) |
| S6 | All 22 CIBERSORTx populations | `results/HNSC_HPV_Immune_Comparison_All22_BH.csv` |
| S7 | CD8/M2 ratio | `results/HNSC_CD8_M2_ratio_data.csv` |
| S8 | Deconvolution marker validation | `results/Deconvolution_Marker_Validation.csv` (`scripts/validate_deconvolution_markers.py`) |
| S9 | Malignant-cell specificity | external-cohort and single-cell analyses |
| S10 | Proliferation adjustment | external-cohort and single-cell analyses |
| S11 | Exploratory Cox models | `results/HNSC_Standardized_Cox_Results.csv` |

## Review sensitivity analyses

| Analysis | Output | Script |
|---|---|---|
| GSE65858: DeLong and bootstrap AUC CIs (active, silent, DNA-based, oropharynx-only); size-matched coherence nulls for the active (n = 35) and silent (n = 25) groups; four-gene score | `results/review_sensitivity/GSE65858_core_module_CIs_and_nulls.json` | `gse65858_prep.py`, `gse65858_stats.py` |
| TCGA-HNSC and GSE38266: single promoter definition (1,500 bp upstream to 500 bp downstream of an annotated TSS) for the core genes; six- vs four-gene methylation composites; B/plasma adjustment (CIBERSORTx fractions and marker score); HPV definitions p16-or-ISH, ISH-only and oropharynx-only | `results/review_sensitivity/TCGA_GSE38266_methylation_sensitivity.json` | `tcga_fetch.py`, `core_probes_and_gse38266.py`, `gdc_fetch.py`, `tcga_methylation_sensitivity.py` |
| GSE182227: DeLong and bootstrap CI for the per-tumour four-gene AUC | `results/review_sensitivity/GSE182227_AUC_CI.json` | `gse182227_auc_ci.py` |
