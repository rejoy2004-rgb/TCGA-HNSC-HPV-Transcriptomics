# Canonical Manuscript Outputs

This maps every figure and table in `manuscript/FINAL_INTEGRATED_MANUSCRIPT.docx` to its file and its source.

- **Figure exports:** main figures in `manuscript/submission_figures/` (Figure1–Figure7; the internal names `composed/Figure1–6.png` are the older numbering, shifted by one), supplementary figures in `supplementary/figures/` (LZW TIFF + PNG), produced by `scripts/figures/export_submission_figures.py`.
- **Vector PDFs:** every figure also has a vector `.pdf` next to its TIFF and PNG, except Supplementary Fig. S1 (R plot, raster only) and Figure 6, whose PDF holds the 600 dpi raster because the deposited GSE182227 panels have no vector source. Composed figures are built by `scripts/figures/compose_figures_vector.py` (same layout as the raster composites, placing the vector panel PDFs); the other figures are saved as PDF by their own scripts.
- **Table exports:** main tables in `manuscript/tables/`; supplementary tables in `supplementary/tables/`. These CSVs are exported from the built manuscript, so they match it exactly.
- **Rebuilding the manuscript:** `scripts/build_integrated_manuscript.js` (requires the `docx` npm package).

## Main figures

| Figure | Content | Source / script |
|---|---|---|
| Figure 1 | Study overview (the authors' BioRender-style figure, recovered from their Google Doc "HPV Manuscript"; 2046 px wide, so about 300 dpi at print width) | `figures/integrated/Figure1_overview_original.png`; a 600 dpi export from the authors is still needed |
| Graphical abstract (unnumbered, after the Abstract) | Redrawn summary | `scripts/figures/make_graphical_abstract.py` |
| Figure 2 | Differential expression (volcano, meiotic panel genes, GO terms) | 600 dpi panels in `figures/source_panels_600dpi/Figure 1/` (panels a and c redrawn by `scripts/figures/make_enrichment_panels.py` from `results/HNSC_DESeq2_All_Results.csv` and `results/HNSC_HPV_GO_Upregulated.csv`) → `scripts/figures/compose_figures.py` |
| Figure 3 | Promoter hypomethylation and replication (GSE38266) | `figures/source_panels_600dpi/Figure 3/` (written by `scripts/meiotic_programme/run_meiotic_analysis.py --panels`) → `compose_figures.py` |
| Figure 4 | Viral-activity dependence and specificity (GSE65858) | `figures/source_panels_600dpi/Figure 4/` (written by `run_meiotic_analysis.py --panels`) → `compose_figures.py` |
| Figure 5 | Immune microenvironment (CIBERSORTx) | `scripts/figures/make_tme_figure.py` from `data_processed/CIBERSORTx_Job14_Results.csv` |
| Figure 6 | Malignant-cell localisation (GSE181919) | `figures/source_panels_600dpi/Figure 6/` → `compose_figures.py` |
| Figure 7 | Single-cell replication (GSE182227) | `figures/source_panels_600dpi/Figure 7/` → `compose_figures.py` |

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
| S2 | Origin of the meiotic hypothesis (GSEA, category and panel enrichment) | `figures/source_panels_600dpi/Figure 2/` (panel a from `scripts/figures/make_enrichment_panels.py` using `results/HNSC_HPV_GSEA.csv`; panels b, c from `run_meiotic_analysis.py --panels`) → `compose_figures.py` |
| S3 | Downregulated GO and KEGG pathways | `scripts/figures/make_supp_dotplots.py` from `results/HNSC_HPV_GO_Downregulated.csv` and `results/HNSC_HPV_KEGG_Downregulated.csv` |
| S4 | Module coherence | `figures/source_panels_600dpi/Figure 5/` → `compose_figures.py` |
| S5 | CD8+ T-cell deconvolution validation | `scripts/figures/make_cd8_validation.py` from `results/review_sensitivity/CD8_validation_input.csv` (built by `scripts/review_analyses/km_zfr2_counts.py`) |
| S6 | Exploratory Cox forest plot | `scripts/figures/make_forest_plot.py` from `results/HNSC_Standardized_Cox_Results.csv` |
| S7 | ZFR2 Kaplan–Meier with numbers at risk | `scripts/figures/make_km_zfr2.py` from `results/review_sensitivity/ZFR2_KM_input.csv` (built by `scripts/review_analyses/km_zfr2_counts.py`); `figures/HNSC_BestGene_KM_R.png` is the base-R version from `HPV_HNSC_Revision.R` |

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
| TCGA-HNSC tumour purity: ABSOLUTE calls (PanCancer Atlas) against HPV status and the core meiotic score; purity and proliferation as covariates (Supplementary Table S5, Section 3.9) | `results/meiotic_programme/purity/` | `scripts/meiotic_programme/tcga_purity_regression.py` (input `data_raw/TCGA_mastercalls.abs_tables_JSedit.fixed.txt`) |
| ZFR2 median-split survival input and CD8A/CD8B validation input from GDC STAR counts (DESeq2-normalised) | `results/review_sensitivity/ZFR2_KM_input.csv`, `results/review_sensitivity/CD8_validation_input.csv` | `scripts/review_analyses/km_zfr2_counts.py` |
| GSE181919 per-cell and per-tumour statistics (six-gene core score, MAJIN resolved as C11orf85, two-sided exact tests), TCGA methylation, GSE65858 and GSE38266 headline values | `results/meiotic_programme/` (`headline_values.json`, `sc_*.csv`, `table*.csv`) | `scripts/meiotic_programme/run_meiotic_analysis.py` |
