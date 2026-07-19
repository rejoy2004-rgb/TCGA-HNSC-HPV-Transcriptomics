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
total_raw <- length(expression_barcodes)
total_tumor <- sum(merged_manifest$Is_Tumor)
total_included <- nrow(cibersort_hpv_mapping)
excluded_non_tumor <- total_raw - total_tumor
excluded_no_hpv <- total_tumor - total_included

cat("\nFinal Cohort Composition:\n")
cat("  Total Samples: ", total_included, "\n")
cat("  HPV-Negative:  ", hpv_neg, " (Expected: 243)\n")
cat("  HPV-Positive:  ", hpv_pos, " (Expected: 36)\n")

# 6. Save Cohort Filtering Summary CSV
summary_df <- data.frame(
  Step = c(
    "Initial RNA-seq samples",
    "Primary tumor samples (Sample Type Code 01)",
    "Samples with HPV annotation",
    "HPV-negative",
    "HPV-positive"
  ),
  Count = c(
    total_raw,
    total_tumor,
    total_included,
    hpv_neg,
    hpv_pos
  ),
  stringsAsFactors = FALSE
)

summary_output_path <- "results/Cohort_Filtering_Summary.csv"
write.csv(summary_df, file = summary_output_path, row.names = FALSE)
cat("Cohort filtering summary written to:", summary_output_path, "\n")

# 7. Generate Cohort Filtering Flowchart (Figure S1)
cat("Generating cohort filtering flow diagram...\n")
dir.create("figures", showWarnings = FALSE)
flowchart_path <- "figures/Figure_S1_Cohort_Filtering.png"

# Setup high-resolution PNG
png(flowchart_path, width = 1800, height = 2400, res = 300)
par(mar = c(0.5, 0.5, 0.5, 0.5))
plot(1, type = "n", xlab = "", ylab = "", xlim = c(0, 10), ylim = c(0, 12), axes = FALSE)

# Helper function to draw rectangles with text
draw_box <- function(x, y, w, h, text_lines, bg = "#F0F4F8", border = "#2B5C8F") {
  rect(x - w/2, y - h/2, x + w/2, y + h/2, col = bg, border = border, lwd = 2)
  n_lines <- length(text_lines)
  for (i in 1:n_lines) {
    text(x, y + (h/4) * (n_lines/2 - i + 0.5), text_lines[i], cex = 0.8, font = ifelse(i == 1, 2, 1))
  }
}

# Draw Boxes
draw_box(5, 11.0, 4.4, 1.1, c("TCGA-HNSC RNA-Seq Dataset", paste0("n = ", total_raw, " samples")))
draw_box(8.3, 9.6, 2.8, 1.0, c("Excluded (non-tumor):", paste0("n = ", excluded_non_tumor, " normal controls"), "(Sample Type != '01')"), bg = "#FDF0F0", border = "#D32F2F")
draw_box(5, 8.2, 4.4, 1.1, c("Primary HNSC Tumors", paste0("n = ", total_tumor, " samples")))
draw_box(8.3, 6.8, 2.8, 1.0, c("Excluded (no clinical data):", paste0("n = ", excluded_no_hpv, " samples lacking"), "clinical HPV status"), bg = "#FDF0F0", border = "#D32F2F")
draw_box(5, 5.4, 4.4, 1.1, c("Final Analysis Cohort", paste0("n = ", total_included, " tumor samples")))

draw_box(2.7, 2.8, 3.2, 1.0, c("HPV-Negative Cohort", paste0("n = ", hpv_neg, " samples")))
draw_box(7.3, 2.8, 3.2, 1.0, c("HPV-Positive Cohort", paste0("n = ", hpv_pos, " samples")))

# Draw Arrows
arrows(5, 10.4, 5, 8.8, lwd = 2, length = 0.1)
arrows(5, 9.6, 6.8, 9.6, lwd = 2, length = 0.1)
arrows(5, 7.6, 5, 6.0, lwd = 2, length = 0.1)
arrows(5, 6.8, 6.8, 6.8, lwd = 2, length = 0.1)

arrows(5, 4.8, 2.7, 3.4, lwd = 2, length = 0.1)
arrows(5, 4.8, 7.3, 3.4, lwd = 2, length = 0.1)

dev.off()
cat("Cohort filtering flowchart saved to:", flowchart_path, "\n")

if (hpv_neg == 243 && hpv_pos == 36) {
  cat("\nSUCCESS: Cohort counts match expected manuscript values perfectly!\n")
} else {
  cat("\nWARNING: Cohort counts do not match expected manuscript values.\n")
}
