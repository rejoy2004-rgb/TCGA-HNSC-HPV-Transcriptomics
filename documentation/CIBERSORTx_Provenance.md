# CIBERSORTx Deconvolution Provenance

This document details the experimental provenance, input matrix preparation, and parameters used for the immune cell deconvolution of the TCGA-HNSC cohort, archived in `data_processed/CIBERSORTx_Job14_Results.csv`.

## Input Mixture Matrix Provenance
- **File**: `data_processed/HNSC_CIBERSORT_Input_Final.txt`
- **Original Source**: The Cancer Genome Atlas (TCGA) HNSC RNA-sequencing raw counts.

> [!NOTE]
> **Reproducibility Note**: The original processing script converting the raw counts inside `data_raw/HNSC_data.rds` into TPM values and resolving duplicate gene symbols was not archived in this repository. However, the exact resulting CIBERSORTx input mixture file is fully preserved and version-controlled at [HNSC_CIBERSORT_Input_Final.txt](file:///c:/Users/rejoy/Documents/Intern_Project/data_processed/HNSC_CIBERSORT_Input_Final.txt). Future replication runs should upload this file directly to bypass manual replication of the TPM pipeline.

### Matrix Generation Pipeline
The input file was prepared from raw data through the following steps:
1. **Raw Counts Matrix Extraction**: Raw unstranded count matrix was extracted from `data_raw/HNSC_data.rds`.
2. **TPM Normalization**: Count values were normalized to **Transcripts Per Million (TPM)** to adjust for differences in gene length and sequencing depth across samples:
   $$\text{TPM}_i = \left( \frac{C_i}{L_i} \right) \times \left( \frac{1}{\sum_j \frac{C_j}{L_j}} \right) \times 10^6$$
   where $C_i$ is the raw read count for gene $i$, and $L_i$ is the gene length.
3. **ID Mapping**: Ensembl Gene IDs (stripped of decimal version numbers, e.g., `ENSG00000153563`) were converted to official **HUGO/HGNC Gene Symbols** using the `org.Hs.eg.db` annotation database.
4. **Duplicate Resolution**: If multiple Ensembl IDs mapped to the same HGNC symbol, the row with the highest average TPM expression across the cohort was retained to generate a unique symbol-indexed matrix.
5. **Formatting**: Barcodes were formatted as 15-character TCGA sample IDs (e.g., `TCGA-BA-3829-01`). The resulting file was exported as a tab-delimited matrix.

---

## CIBERSORTx Execution Parameters (Factual Run Settings)
The deconvolution was run externally using the official CIBERSORTx web application:
* **Web Portal URL**: [cibersortx.stanford.edu](https://cibersortx.stanford.edu/)
* **Approximate Access Date**: June 2025

| Parameter | Configuration / Value | Rationale |
| :--- | :--- | :--- |
| **Signature Matrix** | `LM22` | Standard signature defining 22 mature leukocyte subsets. |
| **Deconvolution Mode** | `Relative` | Quantifies relative cell proportions (fractions sum to 1.0). |
| **Permutations** | `100` | Portal default for Monte Carlo p-value estimation. |
| **Quantile Normalization** | `Disabled` (`FALSE`) | **Bioconductor/RNA-seq standard**: QN is disabled for RNA-seq data to prevent distortion of high-expression outlier profiles. |
| **Batch Correction** | `None` | No batch correction applied. |
| **Archive Job ID** | `Job14` | Local tracking reference. (Note: Job IDs are web-server specific and not globally queryable; the settings above form the true provenance). |

---

## Verification & Replication Instructions
To replicate the deconvolution:
1. Log into the CIBERSORTx web portal ([cibersortx.stanford.edu](https://cibersortx.stanford.edu/)).
2. Navigate to **"Run Deconvolution"**.
3. Upload `data_processed/HNSC_CIBERSORT_Input_Final.txt` as the **Mixture file**.
4. Select `LM22` as the **Signature matrix file**.
5. Set parameters:
   - **Quantile normalization**: *Disable*
   - **Permutations**: *100*
   - **Batch correction**: *None*
   - **Run mode**: *Relative*
6. Click **Run**. The resulting downloaded CSV file corresponds to `data_processed/CIBERSORTx_Job14_Results.csv`.

> [!WARNING]
> **External Run Variance Warning**: The archived `CIBERSORTx_Job14_Results.csv` file is the canonical dataset used in the manuscript. Re-running the deconvolution using the external CIBERSORTx web application may produce small numerical variations in the output (especially in statistical p-value columns) due to updates in the external server code, underlying signature matrices, or stochastic differences in the Monte Carlo permutation sampling.
