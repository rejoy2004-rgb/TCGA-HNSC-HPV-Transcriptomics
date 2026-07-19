# -----------------------------------------------------------------------------
# scripts/validate_cibersort_input.R
#
# Validates the programmatically regenerated CIBERSORTx input matrix
# against the canonical archived values in data_processed/HNSC_CIBERSORT_Input_Final.txt.
#
# Metrics reported:
# - Dimensionality matching.
# - Gene symbol overlap count.
# - Pearson correlation across samples.
# - Mean and Maximum absolute difference.
# -----------------------------------------------------------------------------

library(SummarizedExperiment)

cat("--- Validating CIBERSORTx Input Matrix ---\n")

# 1. Load the archived file (the git-tracked version)
archived_path <- "data_processed/HNSC_CIBERSORT_Input_Final.txt"
if (!file.exists(archived_path)) {
  stop("Archived file 'data_processed/HNSC_CIBERSORT_Input_Final.txt' not found.")
}
cat("Loading archived matrix...\n")
archived <- read.table(archived_path, sep="\t", header=TRUE, check.names=FALSE)
rownames(archived) <- archived$GeneSymbol
archived_numeric <- as.matrix(archived[, 2:ncol(archived)])

# 2. Run the programmatic generation logic in memory
cat("Regenerating matrix in memory from raw data...\n")
rds_path <- "data_raw/HNSC_data.rds"
if (!file.exists(rds_path)) {
  stop("Raw counts file 'data_raw/HNSC_data.rds' not found.")
}
hnsc_data <- readRDS(rds_path)

tpm_matrix <- assay(hnsc_data, "tpm_unstrand")
ensembl_versioned <- rownames(hnsc_data)
ensembl_clean <- sub("\\..*", "", ensembl_versioned)

# Mapping symbols
library(org.Hs.eg.db)
gene_map <- select(org.Hs.eg.db, keys = ensembl_clean, keytype = "ENSEMBL", columns = "SYMBOL")
gene_map <- gene_map[!is.na(gene_map$SYMBOL) & gene_map$SYMBOL != "", ]

row_data_df <- data.frame(
  OriginalRow = ensembl_versioned,
  ENSEMBL = ensembl_clean,
  RowDataSymbol = rowData(hnsc_data)$gene_name,
  stringsAsFactors = FALSE
)

mapping <- merge(row_data_df, gene_map, by = "ENSEMBL", all.x = TRUE)
mapping$FinalSymbol <- ifelse(!is.na(mapping$SYMBOL), mapping$SYMBOL, mapping$RowDataSymbol)
mapping <- mapping[!is.na(mapping$FinalSymbol) & mapping$FinalSymbol != "", ]

tpm_subset <- tpm_matrix[mapping$OriginalRow, ]
row_means <- rowMeans(tpm_subset)
mapping$MeanTPM <- row_means[mapping$OriginalRow]

mapping <- mapping[order(mapping$FinalSymbol, -mapping$MeanTPM), ]
mapping_unique <- mapping[!duplicated(mapping$FinalSymbol), ]

tpm_collapsed <- tpm_subset[mapping_unique$OriginalRow, ]
rownames(tpm_collapsed) <- mapping_unique$FinalSymbol

# Filter to panel
panel_path <- "data_processed/canonical_cibersort_gene_panel.txt"
if (!file.exists(panel_path)) {
  stop("Canonical panel file not found.")
}
target_symbols <- readLines(panel_path)

common_genes <- intersect(target_symbols, rownames(tpm_collapsed))
tpm_final <- matrix(0, nrow=length(target_symbols), ncol=ncol(tpm_collapsed),
                    dimnames=list(target_symbols, colnames(tpm_collapsed)))
tpm_final[common_genes, ] <- tpm_collapsed[common_genes, ]

# 3. Quantitative Comparison
cat("\nPerforming Quantitative Comparison...\n")

# Check dimensions
dims_match <- identical(dim(archived_numeric), dim(tpm_final))
cat("Dimensions Match:", dims_match, "\n")
cat("  Archived:", dim(archived_numeric)[1], "genes x", dim(archived_numeric)[2], "samples\n")
cat("  Generated:", dim(tpm_final)[1], "genes x", dim(tpm_final)[2], "samples\n")

# Match rows and columns
common_genes_eval <- intersect(rownames(archived_numeric), rownames(tpm_final))
cat("Matched Genes Count:", length(common_genes_eval), "/", nrow(archived_numeric), "\n")

o_sub <- archived_numeric[common_genes_eval, ]
g_sub <- tpm_final[common_genes_eval, colnames(archived_numeric)]

# Calculate Pearson correlation per sample
pearsons <- sapply(1:ncol(o_sub), function(i) {
  if (sd(o_sub[, i]) == 0 || sd(g_sub[, i]) == 0) return(NA)
  cor(o_sub[, i], g_sub[, i])
})

cat("Mean Pearson Correlation across samples:", mean(pearsons, na.rm=TRUE), "\n")
cat("Median Pearson Correlation across samples:", median(pearsons, na.rm=TRUE), "\n")
cat("Min Pearson Correlation across samples:", min(pearsons, na.rm=TRUE), "\n")

# Calculate differences
diffs <- abs(o_sub - g_sub)
cat("Mean Absolute Difference:", mean(diffs), "\n")
cat("Max Absolute Difference:", max(diffs), "\n")

# Print overall verdict
verdict_text <- ""
if (mean(pearsons, na.rm=TRUE) > 0.9999 && mean(diffs) < 0.2) {
  verdict_text <- "SUCCESS. The regenerated matrix is numerically equivalent to the archived matrix (Mean Pearson r > 0.9999, mean diff < 0.2)."
} else {
  verdict_text <- "WARNING. Numeric divergence detected between regenerated and archived matrices."
}
cat("\nVERDICT:", verdict_text, "\n")

# Write validation report to file
report_content <- paste0(
  "CIBERSORTx Input Regeneration Validation Report\n",
  "-----------------------------------------------\n",
  "Execution Timestamp: ", Sys.time(), "\n",
  "R Version: ", R.version.string, "\n\n",
  "Validation Results:\n",
  "  Dimensions Match: ", dims_match, "\n",
  "  Archived Dim: ", dim(archived_numeric)[1], " x ", dim(archived_numeric)[2], "\n",
  "  Generated Dim: ", dim(tpm_final)[1], " x ", dim(tpm_final)[2], "\n",
  "  Matched Genes: ", length(common_genes_eval), " / ", nrow(archived_numeric), "\n",
  "  Mean Pearson Correlation: ", mean(pearsons, na.rm=TRUE), "\n",
  "  Median Pearson Correlation: ", median(pearsons, na.rm=TRUE), "\n",
  "  Min Pearson Correlation: ", min(pearsons, na.rm=TRUE), "\n",
  "  Mean Absolute Difference: ", mean(diffs), "\n",
  "  Max Absolute Difference: ", max(diffs), "\n\n",
  "Verdict: ", verdict_text, "\n"
)
writeLines(report_content, "results/CIBERSORTx_Validation_Report.txt")
cat("\nValidation report logged to 'results/CIBERSORTx_Validation_Report.txt'\n")
