# CIBERSORTx Deconvolution Provenance

This document provides the exact parameters, inputs, and workflow configurations used to estimate immune cell fractions for the TCGA-HNSC cohort, archived in `data_processed/CIBERSORTx_Job14_Results.csv`.

## Input Mixture Matrix
- **File**: `data_processed/HNSC_CIBERSORT_Input_Final.txt`
- **Source**: TCGA-HNSC RNA-sequencing raw count datasets.
- **Normalization**: Transcripts Per Million (TPM) normalized values mapping to HUGO Gene Symbols.
- **Format**: Tab-delimited expression matrix with Gene Symbols in the first column and 15-character TCGA barcodes (e.g. `TCGA-BA-3829-01`) as headers.

## Deconvolution Execution Settings
The deconvolution was performed using the official CIBERSORTx web application.

| Parameter | Value / Setting | Rationale |
| :--- | :--- | :--- |
| **CIBERSORTx Portal** | [cibersortx.stanford.edu](https://cibersortx.stanford.edu/) | Standard academic deconvolution server |
| **Signature Matrix** | `LM22` | Standard signature matrix defining 22 mature human hematopoietic cell subsets |
| **Deconvolution Mode** | `Relative` | Quantifies cell proportions relative to the total immune cell pool (fractions sum to 1.0) |
| **Permutations** | `100` | Standard Monte Carlo permutation count for p-value estimation |
| **Quantile Normalization** | `Disabled` (`FALSE`) | **CRITICAL**: Quantile normalization was disabled, as recommended by CIBERSORTx developers for RNA-seq datasets (to avoid distorting relative count distributions) |
| **Batch Correction** | `None` | No batch correction applied |
| **Job ID** | `Job14` | Execution reference tracking ID on CIBERSORTx server |

## Replication Workflow
To replicate the deconvolution output:
1. Log into the CIBERSORTx web portal at [cibersortx.stanford.edu](https://cibersortx.stanford.edu/).
2. Navigate to the **"Run Deconvolution"** section.
3. Upload `data_processed/HNSC_CIBERSORT_Input_Final.txt` as the **Mixture file**.
4. Select `LM22` as the **Signature matrix file**.
5. Adjust the execution options to match:
   - **Quantile normalization**: *Disable*
   - **Permutations**: *100*
   - **Batch correction**: *None*
   - **Run mode**: *Relative*
6. Execute the job. The output file can be downloaded and matches `data_processed/CIBERSORTx_Job14_Results.csv` (minor variances in p-values may exist due to the random permutations).
