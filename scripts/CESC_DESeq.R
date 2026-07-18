# CESC Differential Gene Expression and Pathway Analysis Script
# Subtype Comparison: Squamous Cell Carcinoma vs. Adenocarcinoma

set.seed(123)

# Load libraries
library(TCGAbiolinks)
library(DESeq2)
library(SummarizedExperiment)
library(clusterProfiler)
library(org.Hs.eg.db)
library(AnnotationDbi)
library(EnhancedVolcano)
library(pheatmap)
library(ggplot2)

# Create folders if they do not exist
dir.create("results", showWarnings = FALSE)
dir.create("figures", showWarnings = FALSE)

# Load Data
data_path <- "data_raw/CESC_data.rds"
if (!file.exists(data_path)) {
  data_path <- "CESC_data.rds"
}
if (!file.exists(data_path)) {
  stop("CESC_data.rds not found. Please place it in data_raw/ or the current working directory.")
}

cat("Loading data from:", data_path, "\n")
cesc_data <- readRDS(data_path)

# Extract Metadata
metadata <- as.data.frame(colData(cesc_data))
cat("Initial samples count:", nrow(metadata), "\n")
print(table(metadata$sample_type, useNA = "always"))
print(table(metadata$primary_diagnosis, useNA = "always"))

# Create Histological Subtype Groups
metadata$Group <- NA

metadata$Group[
  grepl("Squamous",
        metadata$primary_diagnosis,
        ignore.case = TRUE)
] <- "Squamous"

metadata$Group[
  grepl("Adeno",
        metadata$primary_diagnosis,
        ignore.case = TRUE)
] <- "Adenocarcinoma"

# Remove unclassified samples
metadata <- metadata[!is.na(metadata$Group), ]
cat("Samples after subtype classification:", nrow(metadata), "\n")
print(table(metadata$Group))

# Extract Counts
counts <- assay(cesc_data, "unstranded")
counts <- counts[, rownames(metadata)]

# Filter Low Count Genes
# Roadmap requirement: keep genes with counts >= 10 in at least 10 samples
keep <- rowSums(counts >= 10) >= 10
counts <- counts[keep, ]
cat("Genes remaining after low-count filtering:", nrow(counts), "\n")

# Setup DESeq2 model
metadata$Group <- factor(metadata$Group)
metadata$Group <- relevel(metadata$Group, ref = "Adenocarcinoma")

dds <- DESeqDataSetFromMatrix(
  countData = counts,
  colData = metadata,
  design = ~ Group
)

# Run DESeq2
cat("Running DESeq2...\n")
dds <- DESeq(dds)

# Get Results
res <- results(dds)
summary(res)

# Save all results
all_res_path <- "results/CESC_All_Results.csv"
write.csv(as.data.frame(res), all_res_path)
cat("Saved all results to:", all_res_path, "\n")

# Significant DEGs (FDR < 0.05 & |log2FC| > 1)
sig_genes <- subset(
  as.data.frame(res),
  padj < 0.05 & abs(log2FoldChange) > 1
)
cat("Significant DEGs count (FDR < 0.05, |log2FC| > 1):", nrow(sig_genes), "\n")

sig_genes_path <- "results/CESC_Subtype_DEGs.csv"
write.csv(sig_genes, sig_genes_path)
cat("Saved significant DEGs to:", sig_genes_path, "\n")

# Upregulated and Downregulated genes (Upregulated in Squamous compared to Adenocarcinoma)
up_genes <- subset(sig_genes, log2FoldChange > 1)
down_genes <- subset(sig_genes, log2FoldChange < -1)
cat("Upregulated in Squamous:", nrow(up_genes), "\n")
cat("Downregulated in Squamous:", nrow(down_genes), "\n")

write.csv(up_genes, "results/CESC_Subtype_Upregulated.csv")
write.csv(down_genes, "results/CESC_Subtype_Downregulated.csv")

# Volcano Plot
volcano_path <- "figures/CESC_Subtype_Volcano.png"
cat("Generating Volcano Plot...\n")
png(volcano_path, width = 1800, height = 1400, res = 300)
print(
  EnhancedVolcano(
    res,
    lab = rownames(res),
    x = "log2FoldChange",
    y = "padj",
    pCutoff = 0.05,
    FCcutoff = 1,
    title = "CESC Histological Subtype DEGs",
    subtitle = "Squamous vs. Adenocarcinoma",
    legendPosition = "right"
  )
)
dev.off()
cat("Saved Volcano Plot to:", volcano_path, "\n")

# Heatmap of top 50 significant genes
cat("Generating Heatmap of top 50 DEGs...\n")
vsd <- vst(dds, blind = TRUE)
resOrdered <- res[order(res$padj), ]
top50 <- rownames(resOrdered)[1:50]

zmat <- assay(vsd)[top50, ]
zmat <- t(scale(t(zmat))) # Z-score normalization

heatmap_path <- "figures/CESC_Subtype_Heatmap.png"
png(heatmap_path, width = 1800, height = 1400, res = 300)
pheatmap(
  zmat,
  show_rownames = TRUE,
  show_colnames = FALSE,
  main = "Top 50 Differentially Expressed Genes",
  annotation_col = data.frame(Subtype = metadata$Group, row.names = rownames(metadata))
)
dev.off()
cat("Saved Heatmap to:", heatmap_path, "\n")

# Gene Annotation (mapping Ensembl IDs to Gene Symbols)
cat("Annotating genes...\n")
gene_ids <- rownames(sig_genes)
gene_ids_clean <- sub("\\..*", "", gene_ids) # Remove transcript version suffix

gene_map <- AnnotationDbi::select(
  org.Hs.eg.db,
  keys = gene_ids_clean,
  columns = c("SYMBOL", "ENTREZID"),
  keytype = "ENSEMBL"
)
gene_map <- na.omit(gene_map)
write.csv(gene_map, "results/CESC_Gene_Annotations.csv", row.names = FALSE)

# GO Enrichment Analysis (Biological Process)
cat("Running GO enrichment...\n")
ego <- enrichGO(
  gene = gene_map$ENTREZID,
  OrgDb = org.Hs.eg.db,
  keyType = "ENTREZID",
  ont = "BP",
  pAdjustMethod = "BH",
  pvalueCutoff = 0.05,
  qvalueCutoff = 0.05,
  readable = TRUE
)
write.csv(as.data.frame(ego), "results/CESC_GO.csv", row.names = FALSE)

go_dotplot_path <- "figures/CESC_GO_Dotplot.png"
png(go_dotplot_path, width = 1800, height = 1400, res = 300)
print(dotplot(ego, showCategory = 20, title = "GO Biological Process Enrichment"))
dev.off()
cat("Saved GO dotplot to:", go_dotplot_path, "\n")

# KEGG Pathway Enrichment
cat("Running KEGG enrichment...\n")
ekegg <- enrichKEGG(
  gene = gene_map$ENTREZID,
  organism = "hsa",
  pvalueCutoff = 0.05
)
write.csv(as.data.frame(ekegg), "results/CESC_KEGG.csv", row.names = FALSE)

kegg_dotplot_path <- "figures/CESC_KEGG_Dotplot.png"
png(kegg_dotplot_path, width = 1800, height = 1400, res = 300)
print(dotplot(ekegg, showCategory = 20, title = "KEGG Pathway Enrichment"))
dev.off()
cat("Saved KEGG dotplot to:", kegg_dotplot_path, "\n")

# Top 10 genes annotation
top10 <- rownames(resOrdered)[1:10]
top10_clean <- sub("\\..*", "", top10)

top10_genes <- AnnotationDbi::select(
  org.Hs.eg.db,
  keys = top10_clean,
  columns = c("SYMBOL"),
  keytype = "ENSEMBL"
)
write.csv(top10_genes, "results/Top10_DEGs_GeneSymbols.csv", row.names = FALSE)
cat("Saved Top 10 gene symbols.\n")
cat("CESC_DESeq.R script run finished successfully.\n")
