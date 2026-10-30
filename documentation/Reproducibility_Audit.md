# Reproducibility audit

Audit date 2026-10-27, Windows 11, Python 3.11. Everything below was run in a scratch **copy** of the repository, and outputs were compared with the archived ones. This is not an end-to-end reproduction.

## Checked statically

- Every script, data file and output path named in `README.md`, `documentation/Canonical_Outputs.md` and the two provenance documents exists in the repository, except the files that are by design not shipped (below). All Python files compile (`py_compile`).
- Python dependencies: `pymupdf` was imported (`compose_figures_vector.py`, `validate_manuscript_docx.py`) but missing from `requirements.txt`; it has been added. R packages used by the R scripts (DESeq2, clusterProfiler, enrichplot, org.Hs.eg.db, survival, TCGAbiolinks, EnhancedVolcano, pheatmap, ggplot2, RColorBrewer, AnnotationDbi, SummarizedExperiment) are covered by the README Software section and `results/sessionInfo.txt`, except that EnhancedVolcano and pheatmap are not named in the README.
- The documented order (data download, then `prepare_hpv_metadata.R`, `prepare_cibersort_input.R`, `validate_cibersort_input.R`, `HPV_HNSC_Revision.R`, the Python validation and demographics scripts, the figure scripts, then the manuscript build) matches the file dependencies: the R scripts read `data_raw/HNSC_data.rds`; `HPV_HNSC_Revision.R` also reads `data_processed/HNSC_HPV_status.csv` and the CIBERSORTx output.

## Inputs that are not in the repository

| Input | Status | How to obtain |
|---|---|---|
| `data_raw/HNSC_data.rds` (TCGA-HNSC STAR counts) | Not included (size). Required by all four R scripts above. | TCGAbiolinks code in README section 1 (GDC, public) |
| GEO series matrices, `GPL10558.annot.gz`, HM450 hg38 manifest | Not included; downloaded by the scripts or placed in `DATA/` | GEO, zhou-lab |
| GSE181919 (about 1.2 GB), GDC HM450 files (about 1.6 GB), GDC STAR counts for `km_zfr2_counts.py` (about 1 GB) | Not included | public downloads, commands in README |
| CIBERSORTx run | Cannot be re-run locally; needs the CIBERSORTx web server and a free account. The archived output `data_processed/CIBERSORTx_Job14_Results.csv` and its input matrix are included, and the provenance document lists the settings. | cibersortx.stanford.edu |

`documentation/CIBERSORTx_Provenance.md` previously described the matrix pipeline as "fully automated" without saying that the .rds file is absent; this is now stated there and in the README.

## Re-run results

| Stage | Command | Result |
|---|---|---|
| Table 1 and cohort counts | `calculate_demographics.py` (re-downloads cBioPortal files) | Reproduced: 36 HPV+ / 243 HPV−, age P = 0.0534, sex P = 0.033, stage P = 0.845; the downloaded clinical files are identical to the archived ones apart from line endings |
| Deconvolution marker validation | `validate_deconvolution_markers.py` | Runs; CD8A/CD8B values are the rank correlations 0.735 / 0.689 (hard-coded from the R script in the script itself, now labelled as such) |
| Figures | `make_cd8_validation.py`, `make_forest_plot.py`, `make_km_zfr2.py`, `make_supp_dotplots.py`, `make_tme_figure.py`, `make_graphical_abstract.py`, `make_enrichment_panels.py` | All ran; every regenerated PNG is byte-identical to the archived one |
| TCGA, GSE65858 and GSE38266 analyses | `run_meiotic_analysis.py --skip-singlecell` (downloaded the GEO data) | Ran to completion; all 115 values in `headline_values.json` and every regenerated CSV match the archived ones |
| Spearman check of S5/S8 | recomputed from `CD8_validation_input.csv` | 0.7347 and 0.6892 |

## Finding: GSE182227 numbers in the manuscript do not match the stored outputs

`results/meiotic_programme/gse182227/` (files dated 2026-10-25; this folder is not on GitHub) was recomputed from `per_tumour_*.csv` and `regression_adjusted.csv`. GSE181919 agrees with the manuscript (four-gene beta 0.112 to 0.105). GSE182227 and the pooled model do not:

| Quantity | Manuscript, Doc 1 and Table S10 | Stored outputs (25 Oct) |
|---|---|---|
| GSE182227 four-gene HPV difference (per tumour) | 0.176 | 0.141 |
| GSE182227 four-gene AUC (11 HPV+ vs 5 HPV−) | 0.945 (DeLong 0.84-1.00; `GSE182227_AUC_CI.json`, 8 Oct) | 0.836, P = 0.038 |
| GSE182227 beta after proliferation adjustment | 0.115 (P = 0.01) | 0.077 (P = 0.11) |
| Pooled four-gene beta, unadjusted to adjusted | 0.141 to 0.109 (22% attenuation) | 0.125 to 0.089 (28.5%, with dataset term); 0.105 to 0.073 (30%, without) |

The manuscript values match the earlier 8 October analysis; the 25 October outputs appear to come from a later re-run. Which set is correct has **not** been established and the manuscript numbers were not changed. Until the authors reconcile them, the Abstract does not quote the 22% figure (the qualitative statement, that the pooled association stays significant after proliferation adjustment, holds in both sets). The single-cell GSE182227 stage was not re-run here.

## Not run (blockers)

- **All R scripts**: R is not installed on the audit machine, and `HNSC_data.rds` is absent. DESeq2, enrichment, immune comparisons and Cox models were therefore not re-derived; their archived CSVs were only read.
- **GSE181919 / GSE182227 single-cell stages**, GDC downloads (`gdc_fetch.py`, `km_zfr2_counts.py`), `tcga_purity_regression.py`, and the other `sensitivity_analyses/` scripts: not run (size, time).
- **CIBERSORTx**: external web service.

End-to-end reproducibility has **not** been verified.
