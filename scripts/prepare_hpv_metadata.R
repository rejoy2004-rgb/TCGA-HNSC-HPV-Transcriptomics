# -----------------------------------------------------------------------------
# scripts/prepare_hpv_metadata.R
#
# Programmatically processes the raw cBioPortal clinical annotations to generate
# data_processed/HNSC_HPV_status.csv and a detailed cohort inclusion manifest.
#
# Inclusion Criteria:
# - Sample must be a primary solid tumor (TCGA sample code '01').
# - Patient must have a valid clinical HPV annotation ('HPV+' or 'HPV-').
# -----------------------------------------------------------------------------

library(SummarizedExperiment)

cat("--- Preparing HPV Status Metadata and Cohort Manifest ---\n")

# 1. Load raw clinical metadata
clinical_path <- "data_raw/data_clinical_patient.txt"
if (!file.exists(clinical_path)) {
  stop("Raw clinical patient file 'data_raw/data_clinical_patient.txt' not found.")
}
cat("Loading raw clinical patient metadata...\n")
clinical_data <- read.table(
  clinical_path,
  sep = "\t",
  header = TRUE,
  comment.char = "#",
  stringsAsFactors = FALSE
)
cat("Loaded raw metadata for", nrow(clinical_data), "patients.\n")

# 2. Load raw SummarizedExperiment counts to align samples
rds_path <- "data_raw/HNSC_data.rds"
if (!file.exists(rds_path)) {
  stop("Raw expression counts file 'data_raw/HNSC_data.rds' not found.")
}
hnsc_data <- readRDS(rds_path)
expression_barcodes <- colnames(hnsc_data)
cat("Found", length(expression_barcodes), "expression samples in raw RDS.\n")

# 3. Process Patient IDs and Map to Expression Samples
# TCGA Patient ID format: TCGA-XX-XXXX (12 characters)
# Expression barcode format: TCGA-XX-XXXX-XXA-XXX-XXXX-XX (e.g. TCGA-BA-4074-01A-...)
# We extract patient ID from expression barcodes using substr(barcode, 1, 12)
sample_manifest <- data.frame(
  Sample_ID = expression_barcodes,
  Patient_ID = substr(expression_barcodes, 1, 12),
  stringsAsFactors = FALSE
)

# Merge expression samples with clinical data
merged_manifest <- merge(sample_manifest, clinical_data, by.x = "Patient_ID", by.y = "PATIENT_ID", all.x = TRUE)

# Determine sample type (tumor vs normal control)
# In TCGA, sample types 01-09 are tumor, 10-19 are normal. Primary solid tumor is '01'.
merged_manifest$Sample_Type_Code <- substr(merged_manifest$Sample_ID, 14, 15)
merged_manifest$Is_Tumor <- merged_manifest$Sample_Type_Code == "01"

# Determine inclusion
merged_manifest$HPV_Status_Raw <- merged_manifest$HPV_STATUS
merged_manifest$Included <- merged_manifest$Is_Tumor &
                            !is.na(merged_manifest$HPV_Status_Raw) & 
                            merged_manifest$HPV_Status_Raw != "" & 
                            merged_manifest$HPV_Status_Raw != "[Not Available]"

# Define inclusion/exclusion reasons
merged_manifest$Reason <- ifelse(
  merged_manifest$Included,
  "Included: Primary solid tumor sample with complete HPV metadata",
  ifelse(
    !merged_manifest$Is_Tumor,
    paste0("Excluded: Normal control or non-primary tumor sample (Sample Type Code: ", merged_manifest$Sample_Type_Code, ")"),
    "Excluded: Missing or unavailable clinical HPV annotation"
  )
)

# Format HPV Status: map HPV+ to positive, HPV- to negative
merged_manifest$HPV_status <- ifelse(
  merged_manifest$Included,
  ifelse(merged_manifest$HPV_Status_Raw == "HPV+", "positive", "negative"),
  "Unknown"
)

# 4. Save the detailed sample inclusion manifest
manifest_output_path <- "results/HNSC_Sample_Inclusion_Manifest.csv"
dir.create("results", showWarnings = FALSE)
write.csv(
  merged_manifest[, c("Sample_ID", "Patient_ID", "HPV_status", "Included", "Reason")],
  file = manifest_output_path,
  row.names = FALSE
)
cat("Detailed sample inclusion manifest written to:", manifest_output_path, "\n")

# 5. Filter and export the final 279-patient deconvolution mapping to data_processed
# For cBioPortal-matching, we format barcodes as Sample ID (15-character prefix, e.g. TCGA-BA-4074-01)
included_samples <- merged_manifest[merged_manifest$Included, ]
cibersort_hpv_mapping <- data.frame(
  `Sample ID` = substr(included_samples$Sample_ID, 1, 15),
  `HPV Status` = included_samples$HPV_status,
  check.names = FALSE
)

# Deduplicate mapping to ensure 1 row per sample ID
cibersort_hpv_mapping <- cibersort_hpv_mapping[!duplicated(cibersort_hpv_mapping$`Sample ID`), ]

# Write final processed mapping
hpv_output_path <- "data_processed/HNSC_HPV_status.csv"
write.csv(
  cibersort_hpv_mapping,
  file = hpv_output_path,
  row.names = FALSE
)
cat("Processed HPV status mapping written to:", hpv_output_path, "\n")

# Summarize cohort composition
hpv_neg <- sum(cibersort_hpv_mapping$`HPV Status` == "negative")
hpv_pos <- sum(cibersort_hpv_mapping$`HPV Status` == "positive")
cat("\nFinal Cohort Composition:\n")
cat("  Total Samples: ", nrow(cibersort_hpv_mapping), "\n")
cat("  HPV-Negative:  ", hpv_neg, " (Expected: 243)\n")
cat("  HPV-Positive:  ", hpv_pos, " (Expected: 36)\n")

if (hpv_neg == 243 && hpv_pos == 36) {
  cat("\nSUCCESS: Cohort counts match expected manuscript values perfectly!\n")
} else {
  cat("\nWARNING: Cohort counts do not match expected manuscript values.\n")
}
