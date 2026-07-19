# -----------------------------------------------------------------------------
# scripts/prepare_cibersort_input.R
#
# Programmatically generates the CIBERSORTx input mixture matrix
# (data_processed/HNSC_CIBERSORT_Input_Final.txt) from raw counts data
# (data_raw/HNSC_data.rds) to achieve end-to-end reproducibility.
#
# Methodology:
# - Uses the official GDC pre-computed TPM values assay ("tpm_unstrand")
#   which models effective transcript lengths (exon union model) instead of
#   genomic coordinates.
# - Gene symbol mapping precedence:
#   1. org.Hs.eg.db Ensembl-to-Symbol query.
#   2. Fallback to rowData(hnsc_data)$gene_name.
# - Duplicates resolved by retaining the row with the maximum average TPM.
# - Filtered using version-controlled data_processed/canonical_cibersort_gene_panel.txt.
# -----------------------------------------------------------------------------

library(SummarizedExperiment)
library(org.Hs.eg.db)

cat("--- Preparing CIBERSORTx Input Matrix ---\n")

# 1. Load raw data
rds_path <- "data_raw/HNSC_data.rds"
if (!file.exists(rds_path)) {
  stop("Raw counts file 'data_raw/HNSC_data.rds' not found.")
}
hnsc_data <- readRDS(rds_path)
cat("Raw dataset dimensions:", dim(hnsc_data), "\n")

# 2. Extract pre-computed GDC TPM values assay (preserves effective transcript length model)
cat("Extracting GDC TPM values...\n")
tpm_matrix <- assay(hnsc_data, "tpm_unstrand")

# 3. Map Ensembl IDs to HUGO/HGNC Gene Symbols
cat("Mapping gene identifiers...\n")
ensembl_versioned <- rownames(hnsc_data)
ensembl_clean <- sub("\\..*", "", ensembl_versioned)

# Primary mapping: org.Hs.eg.db database
gene_map <- select(
  org.Hs.eg.db,
  keys = ensembl_clean,
  keytype = "ENSEMBL",
  columns = "SYMBOL"
)
gene_map <- gene_map[!is.na(gene_map$SYMBOL) & gene_map$SYMBOL != "", ]

# Fallback mapping: rowData(hnsc_data)$gene_name
row_data_df <- data.frame(
  OriginalRow = ensembl_versioned,
  ENSEMBL = ensembl_clean,
  RowDataSymbol = rowData(hnsc_data)$gene_name,
  stringsAsFactors = FALSE
)

mapping <- merge(row_data_df, gene_map, by = "ENSEMBL", all.x = TRUE)

# Apply mapping precedence: prefer org.Hs.eg.db Symbol, fallback to RowDataSymbol
mapping$FinalSymbol <- ifelse(!is.na(mapping$SYMBOL), mapping$SYMBOL, mapping$RowDataSymbol)
mapping <- mapping[!is.na(mapping$FinalSymbol) & mapping$FinalSymbol != "", ]

# Subset TPM matrix to mapped rows
tpm_subset <- tpm_matrix[mapping$OriginalRow, ]
rownames(tpm_subset) <- mapping$OriginalRow

# 4. Resolve duplicate symbols by keeping the row with the highest average TPM
cat("Resolving duplicate gene symbols...\n")
row_means <- rowMeans(tpm_subset)
mapping$MeanTPM <- row_means[mapping$OriginalRow]

# Sort mapping by FinalSymbol and MeanTPM descending
mapping <- mapping[order(mapping$FinalSymbol, -mapping$MeanTPM), ]
# Keep first occurrence of each symbol (highest average TPM)
mapping_unique <- mapping[!duplicated(mapping$FinalSymbol), ]

tpm_collapsed <- tpm_subset[mapping_unique$OriginalRow, ]
rownames(tpm_collapsed) <- mapping_unique$FinalSymbol

# 5. Filter to the canonical 4,417 gene deconvolution panel
cat("Filtering to the canonical 4,417 gene panel...\n")
panel_path <- "data_processed/canonical_cibersort_gene_panel.txt"
if (!file.exists(panel_path)) {
  stop("Canonical gene panel file 'data_processed/canonical_cibersort_gene_panel.txt' not found.")
}
target_symbols <- readLines(panel_path)

# Reindex and align
common_genes <- intersect(target_symbols, rownames(tpm_collapsed))
cat("Mapped", length(common_genes), "out of", length(target_symbols), "target genes.\n")

tpm_final <- matrix(0, nrow=length(target_symbols), ncol=ncol(tpm_collapsed),
                    dimnames=list(target_symbols, colnames(tpm_collapsed)))
tpm_final[common_genes, ] <- tpm_collapsed[common_genes, ]

# 6. Format barcodes as full TCGA Sample IDs (retaining original 28-character codes)
# No truncation to keep the matrix identical to original
colnames(tpm_final) <- colnames(tpm_collapsed)

# Format as data frame with GeneSymbol as first column
cibersort_input <- data.frame(GeneSymbol = rownames(tpm_final), tpm_final, check.names = FALSE)

# Save tab-separated mixture matrix
output_path <- "data_processed/HNSC_CIBERSORT_Input_Final.txt"
write.table(
  cibersort_input,
  file = output_path,
  sep = "\t",
  row.names = FALSE,
  quote = FALSE
)

cat("Success! CIBERSORTx input mixture matrix written to:", output_path, "\n")
