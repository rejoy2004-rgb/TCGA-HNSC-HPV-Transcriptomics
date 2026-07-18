# Provenance and Annotation Details of `HNSC_HPV_status.csv`

The file `data_processed/HNSC_HPV_status.csv` contains the clinical Human Papillomavirus (HPV) status annotations for the TCGA-HNSC cohort analyzed in this study. 

## Source Dataset
The HPV status annotations were retrieved from the cBioPortal repository for the TCGA Head and Neck Squamous Cell Carcinoma publication cohort:
* **Study**: Head and Neck Squamous Cell Carcinoma (TCGA, Nature 2015)
* **cBioPortal Study ID**: `hnsc_tcga_pub`
* **cBioPortal Data Directory**: [cBioPortal/datahub/public/hnsc_tcga_pub](https://github.com/cBioPortal/datahub/tree/master/public/hnsc_tcga_pub)
* **Source File**: `data_clinical_patient.txt`

## HPV Status Assignment Method
In the TCGA HNSC marker paper (*"Comprehensive genomic characterization of head and neck squamous cell carcinomas"*, Nature 2015), HPV status was determined based on:
1. **Genomic Alignment**: Detection of viral DNA sequences and high expression of HPV E6/E7 viral oncogene transcripts in RNA-sequencing data.
2. **Clinical Staging**: Immunohistochemistry (p16 staining) where clinical results were available.

Patients identified as positive for HPV-16 or other high-risk HPV types were annotated as `HPV+` (36 cases), and those who tested negative were annotated as `HPV-` (243 cases) within the publication cohort.

## File Generation Steps
The file `data_processed/HNSC_HPV_status.csv` was generated from the raw publication metadata using the following transformations:
1. The patient identifier (`PATIENT_ID`, e.g., `TCGA-BA-4074`) was converted to a sample-level barcode (`Sample ID`) by appending the primary solid tumor suffix (`-01`), matching the TCGA sample naming convention.
2. The `HPV_STATUS` column value of `HPV+` was mapped to `positive`, and `HPV-` was mapped to `negative`.
3. Samples lacking a definitive HPV clinical annotation (i.e. those marked as `[Not Available]` or missing in the patient publication file) were excluded.
4. The final mapping contains the columns:
   - `Sample ID` (e.g. `TCGA-BA-4074-01`)
   - `HPV Status` (either `positive` or `negative`)

## Final Cohort Composition
The resulting matched cohort for down-stream RNA-seq differential expression and immune deconvolution analysis comprises:
* **Total Patients**: 279
* **HPV-Negative**: 243
* **HPV-Positive**: 36
