# Checklist to complete the R and remaining stages

Not yet verified: all R scripts, the GSE181919 / GSE182227 single-cell stages, the GDC downloads, the review-sensitivity scripts not run, and CIBERSORTx re-execution.

## Environment
- [ ] R 4.6.0 and Bioconductor 3.23 (as in `results/sessionInfo.txt`; R is not installed on the audit machine). Install DESeq2 1.52.0, clusterProfiler 4.20.0, enrichplot 1.32.0, org.Hs.eg.db 3.23.1, TCGAbiolinks 2.40.0, survival 3.8.6, and the packages the scripts load but the README does not list: EnhancedVolcano, pheatmap, ggplot2, RColorBrewer, AnnotationDbi, SummarizedExperiment.
- [ ] Python 3.11 with `pip install -r requirements.txt` (now includes PyMuPDF) and `scripts/meiotic_programme/requirements.txt`.
- [ ] Node.js with `npm install docx` (manuscript build). Microsoft Word or LibreOffice for the layout check.
- [ ] Disk space: GSE181919 about 1.2 GB; GDC HM450 files about 1.6 GB; GDC STAR counts about 1 GB; the TCGA count object several GB while building.

## Missing input: `data_raw/HNSC_data.rds`
- [ ] Rebuild from the GDC with the TCGAbiolinks code in README section 1 (project TCGA-HNSC, STAR - Counts). Needs network access to the GDC; open-access counts need no token.
- [ ] Confirm it contains the 566 RNA-seq samples (520 primary tumours; 279 with an HPV call) described in Methods 2.1.

## Order of commands (from the repository root)
1. `python scripts/download_data.py` (cBioPortal clinical files; checked: reproduces the archived files apart from line endings).
2. `Rscript scripts/prepare_hpv_metadata.R`, then `prepare_cibersort_input.R`, then `validate_cibersort_input.R`.
3. `Rscript scripts/HPV_HNSC_Revision.R` (DESeq2, GO/KEGG/GSEA, immune comparison, Cox). Needs steps 1-2, `data_processed/HNSC_HPV_status.csv` and `data_processed/CIBERSORTx_Job14_Results.csv`.
4. Python stages already reproduced: `calculate_demographics.py`, `validate_deconvolution_markers.py`, the figure scripts, `run_meiotic_analysis.py --skip-singlecell`.
5. Not yet run: `run_meiotic_analysis.py` without `--skip-singlecell`, `gse182227_singlecell.py`, `tcga_purity_regression.py`, and the `scripts/review_analyses/` commands in README section 6.
6. Compare each regenerated file in `results/` with the archived version and record any difference (small differences in GO/GSEA output are expected per the README).

## GSE182227 discrepancy (needs the authors)
- [ ] Re-run `python scripts/meiotic_programme/gse182227_singlecell.py --data DATA/meiotic --panels` (needs the GSE182227 download) and `python scripts/review_analyses/gse182227_auc_ci.py ...`, then compare with the manuscript values (see `Reproducibility_Audit.md`, "Finding: GSE182227 numbers ..."). Decide which analysis version is final before editing the Results, Table 6, Table S10, Figure 7 and the Limitations.

## Cannot be done locally
- [ ] CIBERSORTx: needs a CIBERSORTx account and the web server (settings in `documentation/CIBERSORTx_Provenance.md`). The archived Job 14 output stays the reference.
