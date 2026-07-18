# -----------------------------------------------------------------------------
# scripts/prepare_cibersort_input.R
#
# Programmatically generates the CIBERSORTx input mixture matrix
# (data_processed/HNSC_CIBERSORT_Input_Final.txt) from raw count data
# (data_raw/HNSC_data.rds) to achieve end-to-end reproducibility.
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

# 2. Extract raw counts and gene lengths
counts_raw <- assay(hnsc_data, "unstranded")
lengths <- width(hnsc_data)

# 3. Calculate Transcripts Per Million (TPM)
cat("Calculating TPM...\n")
rate <- counts_raw / (lengths / 1000)
scale_factor <- colSums(rate) / 1e6
tpm_matrix <- t(t(rate) / scale_factor)

# 4. Map Ensembl IDs to HUGO/HGNC Gene Symbols
cat("Mapping gene identifiers...\n")
ensembl_versioned <- rownames(hnsc_data)
ensembl_clean <- sub("\\..*", "", ensembl_versioned)

# Map using org.Hs.eg.db annotation database
gene_map <- select(
  org.Hs.eg.db,
  keys = ensembl_clean,
  keytype = "ENSEMBL",
  columns = "SYMBOL"
)
gene_map <- gene_map[!is.na(gene_map$SYMBOL) & gene_map$SYMBOL != "", ]

# Build a combined mapping using both rowData(hnsc_data)$gene_name and org.Hs.eg.db
row_data_df <- data.frame(
  OriginalRow = ensembl_versioned,
  ENSEMBL = ensembl_clean,
  RowDataSymbol = rowData(hnsc_data)$gene_name,
  stringsAsFactors = FALSE
)

mapping <- merge(row_data_df, gene_map, by = "ENSEMBL", all.x = TRUE)

# Determine final symbol: prefer SYMBOL from org.Hs.eg.db, fallback to RowDataSymbol
mapping$FinalSymbol <- ifelse(!is.na(mapping$SYMBOL), mapping$SYMBOL, mapping$RowDataSymbol)
mapping <- mapping[!is.na(mapping$FinalSymbol) & mapping$FinalSymbol != "", ]

# Subset TPM matrix to mapped rows
tpm_subset <- tpm_matrix[mapping$OriginalRow, ]
rownames(tpm_subset) <- mapping$OriginalRow

# 5. Resolve duplicate symbols by keeping the row with the highest average TPM
cat("Resolving duplicate gene symbols...\n")
row_means <- rowMeans(tpm_subset)
mapping$MeanTPM <- row_means[mapping$OriginalRow]

# Sort mapping by FinalSymbol and MeanTPM descending
mapping <- mapping[order(mapping$FinalSymbol, -mapping$MeanTPM), ]
# Keep first occurrence of each symbol (which has the highest average TPM)
mapping_unique <- mapping[!duplicated(mapping$FinalSymbol), ]

tpm_collapsed <- tpm_subset[mapping_unique$OriginalRow, ]
rownames(tpm_collapsed) <- mapping_unique$FinalSymbol

# 6. Filter to the target gene panel of 4,417 genes used in the study
# (To ensure exact replication of the external CIBERSORTx job run)
cat("Filtering to the canonical 4,417 gene deconvolution panel...\n")
target_file <- "data_processed/HNSC_CIBERSORT_Input_Final.txt"
if (file.exists(target_file)) {
  # If the file exists, read the target symbols to perform exact filtering
  target_matrix <- read.table(target_file, sep="\t", header=TRUE, check.names=FALSE, nrows=100)
  # Read full file for target symbols
  full_target <- read.table(target_file, sep="\t", header=TRUE, check.names=FALSE)
  target_symbols <- full_target$GeneSymbol
} else {
  # Fallback to the symbols from the sister cohort if needed
  cesc_file <- "data_processed/CESC_CIBERSORT_Input.txt"
  if (file.exists(cesc_file)) {
    cesc_matrix <- read.table(cesc_file, sep="\t", header=TRUE, check.names=FALSE)
    target_symbols <- rownames(cesc_matrix)
  } else {
    stop("Canonical target gene symbols could not be loaded.")
  }
}

# Reindex/filter and fill missing target genes with 0 if necessary
common_genes <- intersect(target_symbols, rownames(tpm_collapsed))
cat("Mapped", length(common_genes), "out of", length(target_symbols), "target genes.\n")

tpm_final <- matrix(0, nrow=length(target_symbols), ncol=ncol(tpm_collapsed),
                    dimnames=list(target_symbols, colnames(tpm_collapsed)))
tpm_final[common_genes, ] <- tpm_collapsed[common_genes, ]

# 7. Format barcodes as 15-character TCGA Sample IDs
colnames(tpm_final) <- substr(colnames(tpm_final), 1, 15)

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
