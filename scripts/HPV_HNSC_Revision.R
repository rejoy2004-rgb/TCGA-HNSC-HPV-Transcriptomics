# HNSC Transcriptomics and Immune Microenvironment Revision Analysis Script
# Comparison: HPV-Positive vs. HPV-Negative HNSC Cohort (n = 279)

set.seed(123)

# Load libraries
library(DESeq2)
library(SummarizedExperiment)
library(clusterProfiler)
library(org.Hs.eg.db)
library(AnnotationDbi)
library(EnhancedVolcano)
library(pheatmap)
library(ggplot2)
library(survival)
library(RColorBrewer)

# Create folders if they do not exist
dir.create("results", showWarnings = FALSE)
dir.create("figures", showWarnings = FALSE)

# -------------------------------------------------------------
# Part 1: Data Loading & Sample Alignment
# -------------------------------------------------------------
cat("--- Loading HNSC Data ---\n")
data_path <- "data_raw/HNSC_data.rds"
if (!file.exists(data_path)) {
  data_path <- "HNSC_data.rds"
}
if (!file.exists(data_path)) {
  stop("HNSC_data.rds not found. Please place it in data_raw/ or the current working directory.")
}

hnsc_data <- readRDS(data_path)
cat("SummarizedExperiment loaded. Dimensions:", paste(dim(hnsc_data), collapse = " x "), "\n")

# Load HPV Status Reference
hpv_status_path <- "data_processed/HNSC_HPV_status.csv"
if (!file.exists(hpv_status_path)) {
  hpv_status_path <- "HNSC_HPV_status.csv"
}
if (!file.exists(hpv_status_path)) {
  stop("HNSC_HPV_status.csv clinical mapping not found.")
}

hpv_meta <- read.csv(hpv_status_path)
# Clean columns since there may be empty comma columns
hpv_meta <- hpv_meta[, c(1, ncol(hpv_meta))]
colnames(hpv_meta) <- c("Sample.ID", "HPV.Status")
hpv_meta <- hpv_meta[!is.na(hpv_meta$HPV.Status) & hpv_meta$HPV.Status != "", ]
hpv_meta$Sample.ID <- trimws(hpv_meta$Sample.ID)
hpv_meta$HPV.Status <- trimws(hpv_meta$HPV.Status)

# Extract assay colData
meta <- as.data.frame(colData(hnsc_data))
meta$Sample.ID <- substr(rownames(meta), 1, 15)

# Merge colData with HPV status
meta_merged <- merge(meta, hpv_meta, by = "Sample.ID")
cat("Cohort aligned. Matches found:", nrow(meta_merged), "\n")
print(table(meta_merged$HPV.Status))

# Match colnames of expression matrix
common_barcodes <- intersect(colnames(hnsc_data), meta_merged$barcode)
meta_cohort <- meta_merged[meta_merged$barcode %in% common_barcodes, ]
rownames(meta_cohort) <- meta_cohort$barcode
hnsc_data <- hnsc_data[, meta_cohort$barcode]

# -------------------------------------------------------------
# Part 2: Differential Expression (DESeq2)
# -------------------------------------------------------------
cat("\n--- Running DESeq2 Differential Expression ---\n")
counts <- assay(hnsc_data, "unstranded")

# Filter low counts (counts >= 10 in at least 10 samples)
keep <- rowSums(counts >= 10) >= 10
counts_filtered <- counts[keep, ]
cat("Genes after low-count filtering:", nrow(counts_filtered), "\n")

# Factor and relevel groups
meta_cohort$HPV.Status <- factor(meta_cohort$HPV.Status, levels = c("negative", "positive"))

# 2.1 Unadjusted Model (HPV Status only)
dds <- DESeqDataSetFromMatrix(
  countData = counts_filtered,
  colData = meta_cohort,
  design = ~ HPV.Status
)
dds <- DESeq(dds)
res <- results(dds)
summary(res)

# Save unadjusted DEG results
write.csv(as.data.frame(res), "results/HNSC_DESeq2_All_Results.csv")
sig_res <- subset(as.data.frame(res), padj < 0.05 & abs(log2FoldChange) > 1)
write.csv(sig_res, "results/HNSC_DESeq2_Significant_Genes.csv")
cat("Saved unadjusted results. Significant DEGs (FDR < 0.05, |log2FC| > 1):", nrow(sig_res), "\n")

# 2.2 Adjusted Sensitivity Model (Adjusting for primary tumor site)
cat("\nRunning Adjusted DESeq2 Model...\n")
meta_cohort$primary_site_raw <- meta_cohort$primary_site
if (is.null(meta_cohort$primary_site_raw)) {
  meta_cohort$primary_site_raw <- meta_cohort$site_of_resection_or_biopsy
}

# Clean anatomical primary site categories
meta_cohort$site_clean <- sapply(meta_cohort$primary_site_raw, function(val) {
  if (is.null(val) || is.na(val) || val == "[Not Available]") return("Other/Unknown")
  val_lower <- tolower(trimws(val))
  if (grepl("larynx", val_lower)) return("Larynx")
  if (grepl("tongue|oral cavity|lip|floor of mouth|buccal|gum|palate", val_lower)) return("Oral Cavity")
  if (grepl("oropharynx|tonsil|base of tongue", val_lower)) return("Oropharynx")
  if (grepl("hypopharynx", val_lower)) return("Hypopharynx")
  return("Other/Unknown")
})

# Ensure categories are robust
site_table <- table(meta_cohort$site_clean)
meta_cohort$site_clean_robust <- ifelse(
  meta_cohort$site_clean %in% names(site_table[site_table > 1]),
  meta_cohort$site_clean,
  "Other/Unknown"
)
meta_cohort$site_clean_robust <- factor(meta_cohort$site_clean_robust)

dds_adj <- DESeqDataSetFromMatrix(
  countData = counts_filtered,
  colData = meta_cohort,
  design = ~ site_clean_robust + HPV.Status
)
dds_adj <- DESeq(dds_adj)
res_adj <- results(dds_adj, name = "HPV.Status_positive_vs_negative")

# Save adjusted DEG results
write.csv(as.data.frame(res_adj), "results/HNSC_DESeq2_PrimarySite_Adjusted_All_Results.csv")
sig_res_adj <- subset(as.data.frame(res_adj), padj < 0.05 & abs(log2FoldChange) > 1)
write.csv(sig_res_adj, "results/HNSC_DESeq2_PrimarySite_Adjusted_Significant_Genes.csv")
cat("Saved adjusted results. Adjusted Significant DEGs count:", nrow(sig_res_adj), "\n")

# 2.3 PCA and Volcano Plots
vsd <- vst(dds, blind = TRUE)

pca_data <- plotPCA(vsd, intgroup = "HPV.Status", returnData = TRUE)
percentVar <- round(100 * attr(pca_data, "percentVar"))
p_pca <- ggplot(pca_data, aes(PC1, PC2, color = HPV.Status)) +
  geom_point(size = 3) +
  scale_color_manual(values = c("negative" = "#F87171", "positive" = "#2DD4BF")) +
  xlab(paste0("PC1: ", percentVar[1], "% variance")) +
  ylab(paste0("PC2: ", percentVar[2], "% variance")) +
  theme_bw() +
  ggtitle("PCA of HNSC Cohort (Stratified by HPV Status)")
ggsave("figures/HNSC_HPV_PCA.png", p_pca, width = 7, height = 6, dpi = 300)

png("figures/Figure8_Volcano_DESeq2.png", width = 2100, height = 1800, res = 300)
print(
  EnhancedVolcano(
    res,
    lab = rownames(res),
    x = "log2FoldChange",
    y = "padj",
    pCutoff = 0.05,
    FCcutoff = 1,
    title = "HNSC Differential Expression (HPV+ vs. HPV-)",
    subtitle = "FDR-adjusted p-values and log2FC thresholds shown",
    legendPosition = "right"
  )
)
dev.off()
cat("PCA and Volcano plots generated.\n")

# -------------------------------------------------------------
# Part 3: Immune Cell Deconvolution (CIBERSORTx)
# -------------------------------------------------------------
cat("\n--- Running Immune Deconvolution Analysis ---\n")
cibersort_path <- "data_processed/CIBERSORTx_Job14_Results.csv"
if (!file.exists(cibersort_path)) {
  cibersort_path <- "CIBERSORTx_Job14_Results.csv"
}
if (!file.exists(cibersort_path)) {
  stop("CIBERSORTx_Job14_Results.csv not found.")
}

cibersort <- read.csv(cibersort_path)
cibersort$Sample.ID <- substr(cibersort$Mixture, 1, 15)

# Merge CIBERSORTx results with clinical variables
immune_data <- merge(cibersort, meta_cohort, by = "Sample.ID")
cat("CIBERSORTx samples matched to cohort:", nrow(immune_data), "\n")

# Define immune cells of interest (significant fractions in study)
cells <- c("Plasma cells", "T cells CD8", "Macrophages M0", "NK cells resting", "T cells CD4 memory resting")

# Perform Wilcoxon rank-sum tests and extract statistics
wilcox_results <- list()
for (cell in cells) {
  test_formula <- as.formula(paste("`", cell, "` ~ HPV.Status", sep = ""))
  w_test <- wilcox.test(test_formula, data = immune_data)
  
  neg_vals <- immune_data[immune_data$HPV.Status == "negative", cell]
  pos_vals <- immune_data[immune_data$HPV.Status == "positive", cell]
  
  wilcox_results[[cell]] <- data.frame(
    CellType = cell,
    Median_HPV_Negative = median(neg_vals, na.rm = TRUE),
    Median_HPV_Positive = median(pos_vals, na.rm = TRUE),
    Pvalue = w_test$p.value
  )
}
wilcox_df <- do.call(rbind, wilcox_results)
wilcox_df$FDR <- p.adjust(wilcox_df$Pvalue, method = "BH")
write.csv(wilcox_df, "results/HNSC_HPV_Immune_Comparison.csv", row.names = FALSE)
print(wilcox_df)

# Write out significant immune cells specifically
sig_immune <- subset(wilcox_df, FDR < 0.05)
write.csv(sig_immune, "results/HNSC_HPV_Significant_Immune_Cells.csv", row.names = FALSE)

# Generate Box-and-Jitter plots for publication
# 3.1 Plasma Cells
p_plasma <- ggplot(immune_data, aes(x = HPV.Status, y = `Plasma cells`, fill = HPV.Status)) +
  geom_boxplot(outlier.shape = NA) +
  geom_jitter(width = 0.2, alpha = 0.4, size = 1.5) +
  scale_fill_manual(values = c("negative" = "#F87171", "positive" = "#2DD4BF")) +
  labs(x = "HPV Status", y = "Plasma Cell Fraction", title = "Plasma Cell Infiltration in HNSC") +
  theme_bw()
ggsave("figures/Plasma_Cells_Boxplot.png", p_plasma, width = 6, height = 5, dpi = 300)

# 3.2 CD8+ T Cells
p_cd8 <- ggplot(immune_data, aes(x = HPV.Status, y = `T cells CD8`, fill = HPV.Status)) +
  geom_boxplot(outlier.shape = NA) +
  geom_jitter(width = 0.2, alpha = 0.4, size = 1.5) +
  scale_fill_manual(values = c("negative" = "#F87171", "positive" = "#2DD4BF")) +
  labs(x = "HPV Status", y = "CD8+ T-Cell Fraction", title = "CD8+ T-Cell Infiltration in HNSC") +
  theme_bw()
ggsave("figures/HNSC_HPV_CD8_Boxplot.png", p_cd8, width = 6, height = 5, dpi = 300)

# 3.3 M0 Macrophages
p_m0 <- ggplot(immune_data, aes(x = HPV.Status, y = `Macrophages M0`, fill = HPV.Status)) +
  geom_boxplot(outlier.shape = NA) +
  geom_jitter(width = 0.2, alpha = 0.4, size = 1.5) +
  scale_fill_manual(values = c("negative" = "#F87171", "positive" = "#2DD4BF")) +
  labs(x = "HPV Status", y = "M0 Macrophage Fraction", title = "M0 Macrophage Infiltration in HNSC") +
  theme_bw()
ggsave("figures/M2_Macrophage_Boxplot.png", p_m0, width = 6, height = 5, dpi = 300)

# 3.4 CD8 / M2 Macrophages log2-transformed ratio
immune_data$log2_CD8_M2_Ratio <- log2(
  (immune_data$`T cells CD8` + 1e-6) /
  (immune_data$`Macrophages M2` + 1e-6)
)
ratio_test <- wilcox.test(log2_CD8_M2_Ratio ~ HPV.Status, data = immune_data)
# Export ratio stats
write.csv(immune_data[, c("Sample.ID", "barcode", "T cells CD8", "Macrophages M2", "log2_CD8_M2_Ratio", "HPV.Status")], "results/HNSC_CD8_M2_ratio_data.csv", row.names = FALSE)

p_ratio <- ggplot(immune_data, aes(x = HPV.Status, y = log2_CD8_M2_Ratio, fill = HPV.Status)) +
  geom_boxplot(outlier.shape = NA) +
  geom_jitter(width = 0.2, alpha = 0.4, size = 1.5) +
  scale_fill_manual(values = c("negative" = "#F87171", "positive" = "#2DD4BF")) +
  labs(x = "HPV Status", y = "log2(CD8 / M2 Macrophage Ratio)", title = "CD8+ T-Cell to M2 Macrophage Ratio") +
  theme_bw()
ggsave("figures/Revised_CD8_M2_Boxplot.png", p_ratio, width = 6, height = 5, dpi = 300)

# -------------------------------------------------------------
# Part 4: CD8 Deconvolution Validation & Heatmap
# -------------------------------------------------------------
cat("\n--- Validating CD8+ T-Cell fractions against canonical markers ---\n")
vsd_genes <- rownames(vsd)
cd8a_id <- vsd_genes[grepl("ENSG00000153563", vsd_genes)] # CD8A Ensembl
cd8b_id <- vsd_genes[grepl("ENSG00000172116", vsd_genes)] # CD8B Ensembl

if (length(cd8a_id) > 0) {
  immune_data$CD8A_exp <- assay(vsd)[cd8a_id, immune_data$barcode]
  cor_a <- cor.test(immune_data$`T cells CD8`, immune_data$CD8A_exp, method = "spearman")
  
  p_cor_a <- ggplot(immune_data, aes(x = `T cells CD8`, y = CD8A_exp)) +
    geom_point(alpha = 0.6) +
    geom_smooth(method = "lm", color = "blue", fill = "lightblue") +
    labs(x = "CIBERSORTx CD8 Fraction", y = "CD8A Expression (VST counts)",
         title = paste("CD8+ T-cell validation against CD8A (rho =", round(cor_a$estimate, 3), ")")) +
    theme_bw()
  ggsave("figures/Figure_CD8A_Validation.png", p_cor_a, width = 6, height = 5, dpi = 300)
}

if (length(cd8b_id) > 0) {
  immune_data$CD8B_exp <- assay(vsd)[cd8b_id, immune_data$barcode]
  cor_b <- cor.test(immune_data$`T cells CD8`, immune_data$CD8B_exp, method = "spearman")
  
  p_cor_b <- ggplot(immune_data, aes(x = `T cells CD8`, y = CD8B_exp)) +
    geom_point(alpha = 0.6) +
    geom_smooth(method = "lm", color = "blue", fill = "lightblue") +
    labs(x = "CIBERSORTx CD8 Fraction", y = "CD8B Expression (VST counts)",
         title = paste("CD8+ T-cell validation against CD8B (rho =", round(cor_b$estimate, 3), ")")) +
    theme_bw()
  ggsave("figures/Figure_CD8B_Validation.png", p_cor_b, width = 6, height = 5, dpi = 300)
}

# Heatmap of immune cell infiltration
cat("Generating clustered heatmap of immune cell fractions...\n")
heatmap_matrix <- t(as.matrix(immune_data[, cells]))
colnames(heatmap_matrix) <- immune_data$barcode
heatmap_matrix <- t(scale(t(heatmap_matrix))) # Row-wise normalization (Z-score)

annotation_col <- data.frame(
  HPV = factor(immune_data$HPV.Status, levels = c("negative", "positive")),
  row.names = immune_data$barcode
)
ann_colors <- list(
  HPV = c("negative" = "#377EB8", "positive" = "#E41A1C")
)

png("figures/Figure8_Immune_Heatmap.png", width = 2100, height = 1200, res = 300)
pheatmap(
  heatmap_matrix,
  annotation_col = annotation_col,
  annotation_colors = ann_colors,
  show_colnames = FALSE,
  cluster_rows = TRUE,
  cluster_cols = TRUE,
  fontsize = 9,
  fontsize_row = 11,
  main = "Immune Cell Infiltration Heatmap (HPV-positive vs. HPV-negative HNSC)"
)
dev.off()

# -------------------------------------------------------------
# Part 5: Functional Enrichment (GO/KEGG/GSEA)
# -------------------------------------------------------------
cat("\n--- Running Functional Pathway Enrichment ---\n")
sig_res$gene_id <- sub("\\..*", "", rownames(sig_res))
gene_map_hnsc <- AnnotationDbi::select(
  org.Hs.eg.db,
  keys = sig_res$gene_id,
  columns = c("SYMBOL", "ENTREZID"),
  keytype = "ENSEMBL"
)
gene_map_hnsc <- na.omit(gene_map_hnsc)

sig_res_annotated <- merge(sig_res, gene_map_hnsc, by.x = "gene_id", by.y = "ENSEMBL")
write.csv(sig_res_annotated, "results/HNSC_HPV_DEGs_annotated.csv", row.names = FALSE)

up_entrez <- sig_res_annotated$ENTREZID[sig_res_annotated$log2FoldChange > 0]
down_entrez <- sig_res_annotated$ENTREZID[sig_res_annotated$log2FoldChange < 0]

# 5.1 GO Enrichment (Biological Process)
ego_hnsc <- enrichGO(
  gene = sig_res_annotated$ENTREZID,
  OrgDb = org.Hs.eg.db,
  keyType = "ENTREZID",
  ont = "BP",
  pAdjustMethod = "BH",
  pvalueCutoff = 0.05,
  readable = TRUE
)
write.csv(as.data.frame(ego_hnsc), "results/HNSC_HPV_GO_Enrichment.csv", row.names = FALSE)

ego_up <- enrichGO(gene = up_entrez, OrgDb = org.Hs.eg.db, keyType = "ENTREZID", ont = "BP", readable = TRUE)
write.csv(as.data.frame(ego_up), "results/HNSC_HPV_GO_Upregulated.csv", row.names = FALSE)

ego_down <- enrichGO(gene = down_entrez, OrgDb = org.Hs.eg.db, keyType = "ENTREZID", ont = "BP", readable = TRUE)
write.csv(as.data.frame(ego_down), "results/HNSC_HPV_GO_Downregulated.csv", row.names = FALSE)

# Generate publication-quality GO dotplot
go_sig <- as.data.frame(ego_up)
go_sig <- go_sig[order(go_sig$p.adjust), ]
go_sig <- head(go_sig, 20)
go_sig$GeneRatio_num <- sapply(strsplit(go_sig$GeneRatio, "/"), function(x) as.numeric(x[1]) / as.numeric(x[2]))

p_go_pub <- ggplot(go_sig, aes(x = GeneRatio_num, y = reorder(Description, GeneRatio_num), size = Count, color = -log10(p.adjust))) +
  geom_point() +
  scale_color_gradient(low = "blue", high = "red") +
  theme_bw(base_size = 12) +
  labs(x = "Gene Ratio", y = "GO Biological Process Description", color = expression(-log[10](FDR)), size = "Gene Count") +
  ggtitle("GO Enrichment - Upregulated in HPV+ HNSC")
ggsave("figures/Figure12_GO_BP.png", p_go_pub, width = 10, height = 8, dpi = 600)

# 5.2 KEGG Enrichment
ekegg_hnsc <- enrichKEGG(gene = sig_res_annotated$ENTREZID, organism = "hsa")
write.csv(as.data.frame(ekegg_hnsc), "results/HNSC_HPV_KEGG_Enrichment.csv", row.names = FALSE)

ekegg_down <- enrichKEGG(gene = down_entrez, organism = "hsa")
write.csv(as.data.frame(ekegg_down), "results/HNSC_HPV_KEGG_Downregulated.csv", row.names = FALSE)

ekegg_up <- enrichKEGG(gene = up_entrez, organism = "hsa")
write.csv(as.data.frame(ekegg_up), "results/HNSC_HPV_KEGG_Upregulated.csv", row.names = FALSE)

# 5.3 Gene Set Enrichment Analysis (GSEA)
# Order genes by Wald statistics
res$gene_id <- sub("\\..*", "", rownames(res))
res_annotated <- merge(as.data.frame(res), gene_map_hnsc, by.x = "gene_id", by.y = "ENSEMBL")
res_annotated <- res_annotated[!is.na(res_annotated$stat), ]

gene_list <- res_annotated$stat
names(gene_list) <- res_annotated$SYMBOL
gene_list <- sort(gene_list, decreasing = TRUE)

# Run GSEA BP
gse_res <- gseGO(
  geneList = sort(tapply(res_annotated$stat, res_annotated$gene_id, max), decreasing = TRUE),
  OrgDb = org.Hs.eg.db,
  keyType = "ENSEMBL",
  ont = "BP",
  pvalueCutoff = 0.25
)
write.csv(as.data.frame(gse_res), "results/HNSC_HPV_GSEA.csv", row.names = FALSE)

# -------------------------------------------------------------
# Part 6: Survival & Prognostic Modelling
# -------------------------------------------------------------
cat("\n--- Running Prognostic Survival Analysis ---\n")
# Load clinical patient full file
patient_clin_path <- "data_raw/data_clinical_patient_full.txt"
if (!file.exists(patient_clin_path)) {
  patient_clin_path <- "data_clinical_patient_full.txt"
}
if (!file.exists(patient_clin_path)) {
  stop("data_clinical_patient_full.txt not found.")
}

clinical_patient <- read.delim(patient_clin_path, sep = "\t", skip = 4, header = TRUE)
clinical_patient$Patient.ID <- clinical_patient$PATIENT_ID

# Match with meta_cohort
meta_cohort$Patient.ID <- substr(meta_cohort$barcode, 1, 12)
survival_meta <- merge(meta_cohort, clinical_patient, by = "Patient.ID")
rownames(survival_meta) <- survival_meta$barcode

# Parse survival parameters
survival_meta$status <- ifelse(grepl("DECEASED|DEAD|1", survival_meta$OS_STATUS), 1, 0)
survival_meta$time <- as.numeric(survival_meta$OS_MONTHS)
if (all(is.na(survival_meta$time))) {
  survival_meta$time <- as.numeric(survival_meta$OS_DAYS) / 30.4
}

# Keep valid records
survival_meta <- survival_meta[!is.na(survival_meta$time) & !is.na(survival_meta$status), ]
cat("Samples with survival data:", nrow(survival_meta), "\n")

# Align counts matrix
surv_counts <- assay(vsd)[, survival_meta$barcode]

# Candidate genes of interest
candidate_genes <- c("LOC375196", "STAG3", "TAF7L", "SMC1B", "ZFR2", "RAD9B", "TDRD10", "GBX1", "GRIN2C")

cox_results <- list()
cox_std_results <- list()

for (gene in candidate_genes) {
  ens_id <- res_annotated$gene_id[res_annotated$SYMBOL == gene][1]
  if (!is.na(ens_id) && ens_id %in% rownames(surv_counts)) {
    # 6.1 Unstandardized Cox model
    exp_val <- surv_counts[ens_id, ]
    cox_data <- data.frame(time = survival_meta$time, status = survival_meta$status, exp = exp_val)
    fit <- coxph(Surv(time, status) ~ exp, data = cox_data)
    s_fit <- summary(fit)
    cox_results[[gene]] <- data.frame(
      SYMBOL = gene,
      ENSEMBL = ens_id,
      HR = s_fit$conf.int[1],
      Lower95CI = s_fit$conf.int[3],
      Upper95CI = s_fit$conf.int[4],
      Pvalue = s_fit$coefficients[5]
    )
    
    # 6.2 Standardized Cox model
    exp_std <- scale(exp_val)
    cox_std_data <- data.frame(time = survival_meta$time, status = survival_meta$status, exp = exp_std)
    fit_std <- coxph(Surv(time, status) ~ exp, data = cox_std_data)
    s_fit_std <- summary(fit_std)
    cox_std_results[[gene]] <- data.frame(
      Gene = gene,
      HR = s_fit_std$conf.int[1],
      Lower95CI = s_fit_std$conf.int[3],
      Upper95CI = s_fit_std$conf.int[4],
      Pvalue = s_fit_std$coefficients[5]
    )
  }
}

# Export survival tables
write.csv(do.call(rbind, cox_results), "results/HNSC_Survival_Results.csv", row.names = FALSE)
write.csv(do.call(rbind, cox_std_results), "results/HNSC_Standardized_Cox_Results.csv", row.names = FALSE)
cat("Saved survival analysis metrics.\n")

# 6.3 Kaplan-Meier overall survival curve for ZFR2
zfr2_id <- res_annotated$gene_id[res_annotated$SYMBOL == "ZFR2"][1]
if (!is.na(zfr2_id) && zfr2_id %in% rownames(surv_counts)) {
  zfr2_exp <- surv_counts[zfr2_id, ]
  zfr2_group <- ifelse(zfr2_exp > median(zfr2_exp), "High ZFR2", "Low ZFR2")
  km_data <- data.frame(time = survival_meta$time, status = survival_meta$status, ZFR2 = factor(zfr2_group))
  
  km_fit <- survfit(Surv(time, status) ~ ZFR2, data = km_data)
  
  png("figures/HNSC_BestGene_KM.png", width = 1800, height = 1400, res = 300)
  plot(
    km_fit,
    col = c("#E41A1C", "#377EB8"),
    lwd = 2,
    xlab = "Overall Survival (Months)",
    ylab = "Survival Probability",
    main = "Kaplan-Meier Curve stratified by ZFR2"
  )
  legend("bottomleft", legend = c("High ZFR2", "Low ZFR2"), col = c("#E41A1C", "#377EB8"), lwd = 2)
  dev.off()
  cat("Kaplan-Meier curve for ZFR2 plotted.\n")
}

# 6.4 Forest Plot of prognostic candidate genes (from standardized Cox)
std_df <- do.call(rbind, cox_std_results)
# Keep significant ones for forest plotting
std_df$Significance <- ifelse(std_df$Pvalue < 0.05, "Significant", "Non-significant")

p_forest <- ggplot(std_df, aes(x = HR, y = reorder(Gene, HR), color = Significance)) +
  geom_point(size = 3.5) +
  geom_errorbarh(aes(xmin = Lower95CI, xmax = Upper95CI), height = 0.2, linewidth = 1.0) +
  geom_vline(xintercept = 1.0, linetype = "dashed", color = "black") +
  scale_color_manual(values = c("Significant" = "#E41A1C", "Non-significant" = "grey50")) +
  labs(x = "Standardized Hazard Ratio (HR)", y = "Candidate Genes", title = "Cox Prognostic Risk of Candidate Antigens") +
  theme_bw()
ggsave("figures/HNSC_Forest_Plot_Final.png", p_forest, width = 7, height = 5, dpi = 300)
cat("Forest Plot for survival analysis generated.\n")

cat("HPV_HNSC_Revision.R script run finished successfully.\n")
