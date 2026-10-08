# Transcriptionally active HPV-positive HNSCC: meiotic gene programme, promoter hypomethylation and immune context

Code, processed data, results, figures and the manuscript for the study **“Transcriptionally active HPV-positive head and neck squamous cell carcinoma is associated with a coordinated meiotic gene programme and promoter hypomethylation.”**

## Summary of findings

- **Meiotic programme.** Of 4,744 genes differentially expressed between HPV+ (n = 36) and HPV− (n = 243) TCGA-HNSC primary tumours, six of the twelve most significant are meiotic. Meiotic gene categories, but not the classic MAGE/CTAG cancer–testis antigens, are enriched among HPV+-upregulated genes.
- **Methylation and viral activity.** Meiotic promoters are hypomethylated in HPV+ tumours, in step with expression. A six-gene core score (MEI1, SMC1B, STAG3, SYCP2, SYCE2, MAJIN) separates transcriptionally active HPV+ tumours from HPV− tumours (AUC 0.959), whereas HPV DNA-positive, transcriptionally silent tumours do not differ.
- **Immune microenvironment.** CIBERSORTx (LM22; Benjamini–Hochberg across all 22 populations) shows higher plasma-cell and CD8+ T-cell fractions and lower M0 macrophage, resting NK-cell and resting CD4+ memory T-cell fractions in HPV+ tumours.
- **Malignant-cell localisation.** In two single-cell cohorts, the meiotic signal is confined to malignant cells.
- **Keratinisation.** Keratinisation and epithelial-differentiation programmes are reduced in HPV+ tumours.
- **Survival (exploratory).** Univariable Cox models link higher expression of leading HPV-associated genes to longer overall survival. These models are unadjusted for HPV status or other covariates.

The TCGA analyses (differential expression, enrichment, immune deconvolution, survival) are fully reproducible from this repository. The panel, methylation, external-cohort and single-cell analyses (GSE65858, GSE38266, GSE181919, GSE182227) are included as their results and 600 dpi figure panels.

## Repository structure

```text
├── manuscript/
│   ├── FINAL_INTEGRATED_MANUSCRIPT.docx   integrated manuscript
│   ├── submission_figures/                Figures 1–6 and graphical abstract (TIFF + PNG)
│   └── tables/                            Tables 1–6 (CSV)
├── supplementary/
│   ├── figures/                           Supplementary Figures S1–S7 (TIFF + PNG)
│   └── tables/                            Supplementary Tables S1–S11 (CSV)
├── scripts/
│   ├── prepare_hpv_metadata.R             cohort definition and HPV status (279 tumours)
│   ├── prepare_cibersort_input.R          TPM mixture matrix for CIBERSORTx
│   ├── validate_cibersort_input.R         checks on the mixture matrix
│   ├── HPV_HNSC_Revision.R                DESeq2, GO/KEGG/GSEA, immune comparison, survival
│   ├── calculate_demographics.py          Table 1
│   ├── download_data.py                   cBioPortal clinical files
│   ├── validate_deconvolution_markers.py  deconvolution marker validation
│   ├── build_integrated_manuscript.js     builds the manuscript .docx
│   ├── export_tables.py                   exports manuscript tables to CSV
│   ├── review_analyses/                   review sensitivity analyses (CIs, nulls, promoter definition, B/plasma, HPV definition)
│   └── figures/                           figure assembly and export scripts
├── data_raw/                              cBioPortal clinical files and GDC manifest
├── data_processed/                        HPV status, CIBERSORTx input and Job14 results
├── results/                               analysis outputs (review_sensitivity/ for the review analyses)
├── figures/
│   ├── source_panels_600dpi/              600 dpi panels for Figures 1–3, 5, 6 and Supplementary Figs S2, S4
│   ├── integrated/                        assembled and generated figures
│   └── *.png                              plots from HPV_HNSC_Revision.R used in the supplement
└── documentation/
    ├── Canonical_Outputs.md               map of every figure and table to its source
    ├── CIBERSORTx_Provenance.md
    └── HPV_status_provenance.md
```

## Reproducing the analyses

### 1. Data

Clinical annotations (cBioPortal, `hnsc_tcga_pub` and `hnsc_tcga`):

```bash
python scripts/download_data.py
```

RNA-seq counts (GDC, TCGA-HNSC, STAR – Counts), saved as `data_raw/HNSC_data.rds` (not included because of size):

```r
library(TCGAbiolinks)
query <- GDCquery(project = "TCGA-HNSC", data.category = "Transcriptome Profiling",
                  data.type = "Gene Expression Quantification", workflow.type = "STAR - Counts")
GDCdownload(query)
saveRDS(GDCprepare(query), "data_raw/HNSC_data.rds")
```

### 2. Cohort and immune deconvolution

```r
source("scripts/prepare_hpv_metadata.R")      # 279 primary tumours: 36 HPV+, 243 HPV−
source("scripts/prepare_cibersort_input.R")   # data_processed/HNSC_CIBERSORT_Input_Final.txt
source("scripts/validate_cibersort_input.R")
```

The mixture matrix was run on the CIBERSORTx web server (LM22, relative mode, 100 permutations, quantile normalisation disabled, no batch correction). The archived output is `data_processed/CIBERSORTx_Job14_Results.csv`; see `documentation/CIBERSORTx_Provenance.md`.

### 3. Main analysis

```r
source("scripts/HPV_HNSC_Revision.R")
```

This runs:
- DESeq2 (HPV status, with a primary-site sensitivity model)
- GO/KEGG over-representation and GO-BP GSEA
- immune-fraction comparisons across all 22 LM22 populations
- the CD8/M2 ratio and marker validation
- exploratory univariable Cox models

```bash
python scripts/validate_deconvolution_markers.py
python scripts/calculate_demographics.py
```

### 4. Figures and manuscript

Run from the repository root:

```bash
python scripts/figures/make_tme_figure.py          # Figure 4
python scripts/figures/compose_figures.py          # Figures 1–3, 5, 6; Supplementary Figs S2, S4
python scripts/figures/make_supp_composites.py     # Supplementary Figs S3, S5
python scripts/figures/make_forest_plot.py         # Supplementary Fig. S6
python scripts/figures/make_graphical_abstract.py
python scripts/figures/export_submission_figures.py
node scripts/build_integrated_manuscript.js        # requires: npm install docx
python scripts/export_tables.py                   # Tables 1–6 and S1–S11 as CSV
```

### 5. Review sensitivity analyses

These analyses download public data (GEO, cBioPortal, GDC) into a working folder `DATA` (outside the repository) and write their results to `results/review_sensitivity/`. Place `GSE65858_series_matrix.txt.gz`, `GPL10558.annot.gz`, `GSE38266_series_matrix.txt.gz` (GEO) and `HM450.hg38.manifest.gencode.v36.tsv.gz` (zhou-lab/InfiniumAnnotationV1) in `DATA/geo` first.

```bash
python scripts/review_analyses/gse65858_prep.py DATA/geo
python scripts/review_analyses/gse65858_stats.py DATA/geo results/review_sensitivity/GSE65858_core_module_CIs_and_nulls.json
python scripts/review_analyses/tcga_fetch.py DATA
python scripts/review_analyses/core_probes_and_gse38266.py DATA
python scripts/review_analyses/gdc_fetch.py DATA data_raw          # about 1.6 GB of GDC HM450 files
python scripts/review_analyses/tcga_methylation_sensitivity.py DATA .
python scripts/review_analyses/gse182227_auc_ci.py results/review_sensitivity/GSE182227_AUC_CI.json
```

## Software

R 4.6.0 with Bioconductor 3.23: DESeq2 1.52.0, clusterProfiler 4.20.0, enrichplot 1.32.0, org.Hs.eg.db 3.23.1, TCGAbiolinks 2.40.0 and survival 3.8.6. Full versions are in `results/sessionInfo.txt` and `results/package_versions.csv`.

Python 3.11: pandas, numpy, scipy, matplotlib, Pillow and python-docx. Node.js: `docx`.

## Data sources

- TCGA-HNSC RNA-seq: [Genomic Data Commons](https://portal.gdc.cancer.gov/projects/TCGA-HNSC)
- Clinical and HPV annotations: [cBioPortal](https://www.cbioportal.org/) (`hnsc_tcga_pub`, `hnsc_tcga`)
- GEO: GSE65858, GSE38266, GSE181919, GSE182227
