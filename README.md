# Transcriptionally active HPV-positive HNSCC: meiotic gene programme, promoter hypomethylation and immune context

Code, processed data, results, figures and the manuscript for the study **“Transcriptionally active HPV-positive head and neck squamous cell carcinoma is associated with a coordinated meiotic gene programme and promoter hypomethylation.”**

## Summary of findings

- **Meiotic programme.** Of 4,744 genes differentially expressed between HPV+ (n = 36) and HPV− (n = 243) TCGA-HNSC primary tumours, six of the twelve most significant are meiotic. Meiotic gene categories, but not the classic MAGE/CTAG cancer–testis antigens, are enriched among HPV+-upregulated genes.
- **Methylation and viral activity.** Meiotic promoters are hypomethylated in HPV+ tumours, in step with expression. A six-gene core score (MEI1, SMC1B, STAG3, SYCP2, SYCE2, MAJIN) separates transcriptionally active HPV+ tumours from HPV− tumours (AUC 0.959), whereas HPV DNA-positive, transcriptionally silent tumours do not differ.
- **Immune microenvironment.** CIBERSORTx (LM22; Benjamini–Hochberg across all 22 populations) shows higher plasma-cell and CD8+ T-cell fractions and lower M0 macrophage, resting NK-cell and resting CD4+ memory T-cell fractions in HPV+ tumours.
- **Malignant-cell localisation.** In two single-cell cohorts, the meiotic signal is confined to malignant cells.
- **Keratinisation.** Keratinisation and epithelial-differentiation programmes are reduced in HPV+ tumours.
- **Survival (exploratory).** Univariable Cox models link higher expression of leading HPV-associated genes to longer overall survival. These models are unadjusted for HPV status or other covariates.

The TCGA analyses (differential expression, enrichment, immune deconvolution, survival) are fully reproducible from this repository. The panel, methylation, external-cohort and single-cell analyses (GSE65858, GSE38266, GSE181919, GSE182227) are reproducible with `scripts/meiotic_programme/` (section 5).

## Repository structure

```text
├── requirements.txt                       Python dependencies
├── manuscript/
│   ├── FINAL_INTEGRATED_MANUSCRIPT.docx   integrated manuscript
│   ├── submission_figures/                Figures 1–7 and the unnumbered graphical abstract (TIFF + PNG; PDF where a vector source exists; Figure 1 is the authors' study overview)
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
│   ├── meiotic_programme/                 panel, methylation, GSE65858, GSE38266, GSE181919, GSE182227 (section 5)
│   ├── sensitivity_analyses/                   review sensitivity analyses (CIs, nulls, promoter definition, B/plasma, HPV definition)
│   └── figures/                           figure assembly and export scripts
├── data_raw/                              cBioPortal clinical files and GDC manifest
├── data_processed/                        HPV status, CIBERSORTx input and Job14 results
│   └── meiotic_programme/                 95-gene panel (cta_geneset.csv) and frozen enrichment inputs
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

**Required input that is not in the repository:** the RNA-seq count object `data_raw/HNSC_data.rds` (GDC, TCGA-HNSC, STAR – Counts). It is too large to deposit and must be rebuilt with the code below before `prepare_hpv_metadata.R`, `prepare_cibersort_input.R`, `validate_cibersort_input.R` and `HPV_HNSC_Revision.R` can run. Everything downstream of those R scripts that is archived (`data_processed/`, `results/`) can be used without it:

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
python scripts/figures/make_enrichment_panels.py   # Figure 2a, 2c and Supplementary Fig. S2a panels (volcano and enrichment re-run)
python scripts/figures/make_tme_figure.py          # Figure 5
python scripts/figures/compose_figures.py          # composed/Figure1–6 = manuscript Figures 2–7 (except 5 = TME script); Supplementary Figs S2, S4
python scripts/figures/compose_figures_vector.py   # vector PDF versions of the composed figures
python scripts/figures/make_supp_dotplots.py       # Supplementary Fig. S3 (downregulated GO and KEGG)
python scripts/figures/make_cd8_validation.py      # Supplementary Fig. S5 (CD8A/CD8B vs CIBERSORTx)
python scripts/figures/make_forest_plot.py         # Supplementary Fig. S6
python scripts/figures/make_km_zfr2.py             # Supplementary Fig. S7 (Kaplan–Meier with numbers at risk)
python scripts/figures/make_graphical_abstract.py
python scripts/figures/export_submission_figures.py
node scripts/build_integrated_manuscript.js        # requires: npm install docx
python scripts/export_tables.py                   # Tables 1–6 and S1–S11 as CSV
python scripts/validate_manuscript_docx.py [rendered.pdf]   # structure and layout checks on the built .docx
python scripts/audit_references.py                # Crossref check of the reference list (needs network)
```

Notes on the figure scripts:

- `make_enrichment_panels.py` draws Figure 2a (volcano from `results/HNSC_DESeq2_All_Results.csv`), Figure 2c and Supplementary Fig. S2a from the deposited DESeq2, GO and GSEA outputs, so figures and text share one source. Run `compose_figures.py` afterwards (the panel folders of Figures 3, 4 and 6 are written by `scripts/meiotic_programme/run_meiotic_analysis.py --panels` and `gse182227_singlecell.py --panels`; do not re-run the full composer unless those folders are current).
- `make_km_zfr2.py` reads `results/review_sensitivity/ZFR2_KM_input.csv`: DESeq2-normalised ZFR2 counts and overall survival for the 279 tumours, built by `scripts/sensitivity_analyses/km_zfr2_counts.py` from GDC STAR counts. The groups are a median split; a median split on normalised counts equals one on VST values. The base-R Kaplan–Meier block in `HPV_HNSC_Revision.R` writes `figures/HNSC_BestGene_KM_R.png` and does not overwrite the manuscript figure.
- `make_cd8_validation.py` reads `results/review_sensitivity/CD8_validation_input.csv`; Spearman ρ is rank-based, so it is the same for normalised-count and variance-stabilised expression.
- Figure text sizes: `meiotic_programme/run_meiotic_analysis.py` rescales the text of the figures that are reduced to page width (`FONT_SCALE` in that file).

### 5. Meiotic programme: panel, methylation, external cohorts and single cell

```bash
pip install -r scripts/meiotic_programme/requirements.txt
python scripts/meiotic_programme/make_figure1_deg.py --panels                  # Figure 2 (volcano, lollipop, GO bars)
python scripts/meiotic_programme/run_meiotic_analysis.py --data DATA/meiotic --panels
python scripts/meiotic_programme/tcga_purity_regression.py                       # purity / proliferation models
python scripts/meiotic_programme/gse182227_singlecell.py --data DATA/meiotic --panels
```

`run_meiotic_analysis.py` runs, in order: origin of the hypothesis (GSEA ranking, panel-category enrichment, panel/DEG overlap) → TCGA-HNSC promoter hypomethylation and methylation–expression coupling → GSE65858 validation (viral activity, per-gene and per-category AUC, module coherence with permutation nulls, confounder controls) → GSE38266 methylation replication → GSE181919 malignant-cell localisation. Public data are downloaded into `DATA/meiotic` (outside the repository; GSE181919 is ~1.2 GB, use `--skip-singlecell` to omit it). Outputs go to `results/meiotic_programme/`; `--panels` rewrites the 600 dpi panels in `figures/source_panels_600dpi/`.

| Module (`scripts/meiotic_programme/meiotic/`) | Content |
|---|---|
| `config.py` | 95-gene panel (7 categories), core-6 module, constants, seed |
| `data_tcga.py`, `data_geo.py` | cBioPortal and GEO loaders |
| `enrichment_provenance.py` | GSEA / GO / panel-overlap re-test (Supp. Fig. S2) |
| `tcga_discovery.py` | TCGA promoter methylation (Fig. 3a, b) |
| `gse65858_validation.py` | viral activity, specificity, coherence, confounders (Fig. 4, Supp. Fig. S4) |
| `gse38266_replication.py` | independent methylation replication (Fig. 3c) |
| `gse181919_singlecell.py`, `sc_scoring.py` | single-cell analysis and Tirosh module scoring (Fig. 6) |
| `figures.py`, `fig_gse182227.py`, `panel_export.py` | figure builders and 600 dpi per-panel export |

`tcga_purity_regression.py` repeats the purity and proliferation models of Supplementary Table S5 and Section 3.9 with ABSOLUTE purity calls (`data_raw/TCGA_mastercalls.abs_tables_JSedit.fixed.txt`, the public PanCancer Atlas file from the GDC; the script gives the download address) and writes `results/meiotic_programme/purity/`. The GSE65858 coherence permutation nulls use 1,000 size-matched draws with seed 123 in both `gse65858_validation.py` and `scripts/sensitivity_analyses/gse65858_stats.py`, so both give P = 0.001 (95% null interval 0.027–0.273). In the single-cell stage MAJIN is resolved to its deposited symbol C11orf85, and all Mann–Whitney tests are two-sided (exact at tumour level).

`gse182227_singlecell.py` annotates GSE182227 from scratch (Leiden clustering, marker lineages, inferred-CNV malignant calls), scores malignant cells and fits the pooled two-cohort per-tumour models with proliferation adjustment (Fig. 6). The enrichment inputs in `data_processed/meiotic_programme/` are frozen copies of the outputs the manuscript numbers were computed from; regenerated GO/GSEA outputs in `results/` can differ slightly.

### 6. Review sensitivity analyses

These analyses download public data (GEO, cBioPortal, GDC) into a working folder `DATA` (outside the repository) and write their results to `results/review_sensitivity/`. Place `GSE65858_series_matrix.txt.gz`, `GPL10558.annot.gz`, `GSE38266_series_matrix.txt.gz` (GEO) and `HM450.hg38.manifest.gencode.v36.tsv.gz` (zhou-lab/InfiniumAnnotationV1) in `DATA/geo` first.

```bash
python scripts/sensitivity_analyses/gse65858_prep.py DATA/geo
python scripts/sensitivity_analyses/gse65858_stats.py DATA/geo results/review_sensitivity/GSE65858_core_module_CIs_and_nulls.json
python scripts/sensitivity_analyses/tcga_fetch.py DATA
python scripts/sensitivity_analyses/core_probes_and_gse38266.py DATA
python scripts/sensitivity_analyses/gdc_fetch.py DATA data_raw          # about 1.6 GB of GDC HM450 files
python scripts/sensitivity_analyses/tcga_methylation_sensitivity.py DATA .
python scripts/sensitivity_analyses/gse182227_auc_ci.py results/review_sensitivity/GSE182227_AUC_CI.json
python scripts/sensitivity_analyses/km_zfr2_counts.py . DATA/km   # GDC STAR counts -> ZFR2 survival and CD8 validation inputs (about 1 GB)
```

## Software

R 4.6.0 with Bioconductor 3.23: DESeq2 1.52.0, clusterProfiler 4.20.0, enrichplot 1.32.0, org.Hs.eg.db 3.23.1, TCGAbiolinks 2.40.0 and survival 3.8.6. Full versions are in `results/sessionInfo.txt` and `results/package_versions.csv`.

Python 3.11: install everything with `pip install -r requirements.txt` (PyMuPDF, pandas, numpy, scipy, matplotlib, Pillow, python-docx, statsmodels, scikit-learn, requests, lifelines, python-igraph, leidenalg, umap-learn, scanpy and anndata); `scripts/meiotic_programme/requirements.txt` lists the subset needed for the meiotic-programme and single-cell analyses. Node.js: `docx`.

## Data sources

- TCGA-HNSC RNA-seq: [Genomic Data Commons](https://portal.gdc.cancer.gov/projects/TCGA-HNSC)
- Clinical and HPV annotations: [cBioPortal](https://www.cbioportal.org/) (`hnsc_tcga_pub`, `hnsc_tcga`)
- GEO: GSE65858, GSE38266, GSE181919, GSE182227

## Reproducibility status

See `documentation/Reproducibility_Audit.md` for what has and has not been re-run. In short: the Python stages that use shipped or small public inputs were re-run and reproduce the archived outputs; the R stages and the 1.2 GB GSE181919 single-cell stage were not re-run in the audit environment.

## Licence

Code is released under the MIT licence (see `LICENSE`).
