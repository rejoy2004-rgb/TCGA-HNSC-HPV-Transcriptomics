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
The file `data_processed/HNSC_HPV_status.csv` and the detailed manifest `results/HNSC_Sample_Inclusion_Manifest.csv` are programmatically generated from the raw metadata file `data_raw/data_clinical_patient.txt` using the R script [prepare_hpv_metadata.R](file:///c:/Users/rejoy/Documents/Intern_Project/scripts/prepare_hpv_metadata.R).

The script executes the following workflow:
1. **Sample Type Filtration**: Expression barcodes from `data_raw/HNSC_data.rds` are filtered to keep only primary solid tumor samples (sample type code `01`, e.g., `TCGA-BA-4074-01`). Normal control tissue samples (sample type code `11`) and non-primary tumor samples are excluded.
2. **Patient-to-Sample Alignment**: Patient IDs (the first 12 characters of the barcode) are matched against the cBioPortal clinical annotations.
3. **HPV Label Mapping**: The clinical `HPV_STATUS` value of `HPV+` is mapped to `positive`, and `HPV-` is mapped to `negative`.
4. **Sample Inclusion Manifest Generation**: A detailed 566-row manifest is written to [HNSC_Sample_Inclusion_Manifest.csv](file:///c:/Users/rejoy/Documents/Intern_Project/results/HNSC_Sample_Inclusion_Manifest.csv) documenting the patient, mapped status, inclusion decision (`TRUE`/`FALSE`), and the exact inclusion or exclusion reason for every sample in the raw dataset.
5. **Processed Export**: The final deconvolution-compatible mapping is written to [HNSC_HPV_status.csv](file:///c:/Users/rejoy/Documents/Intern_Project/data_processed/HNSC_HPV_status.csv).

## Final Cohort Composition
The resulting matched cohort for down-stream RNA-seq differential expression and immune deconvolution analysis comprises:
* **Total Patients**: 279
* **HPV-Negative**: 243
* **HPV-Positive**: 36
