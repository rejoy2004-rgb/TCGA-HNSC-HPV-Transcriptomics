import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

all_results_file = r"C:\Users\rejoy\Documents\Intern_Project\HNSC_DESeq2_All_Results.csv"
project_dir = r"C:\Users\rejoy\.gemini\antigravity\scratch\hnsc_docx_generator"

# Load data
df = pd.read_csv(all_results_file)

# Drop rows with missing padj or log2FoldChange
df = df.dropna(subset=["log2FoldChange", "padj"])

# Calculate -log10(padj)
tiny = 1e-300
df["minus_log10_padj"] = -np.log10(df["padj"] + tiny)

# Define significance groups
df["color_group"] = "Non-significant"
df.loc[(df["log2FoldChange"] > 1) & (df["padj"] < 0.05), "color_group"] = "Upregulated"
df.loc[(df["log2FoldChange"] < -1) & (df["padj"] < 0.05), "color_group"] = "Downregulated"

# Set up plot style
plt.figure(figsize=(7, 7), dpi=300)
ax = plt.subplot(111)

# Plot groups
colors = {
    "Non-significant": "#D3D3D3", # Light Grey
    "Upregulated": "#3182bd",  # Beautiful Slate Blue
    "Downregulated": "#de2d26" # Beautiful Muted Red
}

# Plot non-significant points first (background)
ns_df = df[df["color_group"] == "Non-significant"]
plt.scatter(ns_df["log2FoldChange"], ns_df["minus_log10_padj"], 
            c=colors["Non-significant"], alpha=0.5, s=6, label="Non-significant")

# Plot upregulated points
up_df = df[df["color_group"] == "Upregulated"]
plt.scatter(up_df["log2FoldChange"], up_df["minus_log10_padj"], 
            c=colors["Upregulated"], alpha=0.7, s=12, label="Upregulated (log2FC > 1, FDR < 0.05)")

# Plot downregulated points
down_df = df[df["color_group"] == "Downregulated"]
plt.scatter(down_df["log2FoldChange"], down_df["minus_log10_padj"], 
            c=colors["Downregulated"], alpha=0.7, s=12, label="Downregulated (log2FC < -1, FDR < 0.05)")

# Add thresholds lines
plt.axhline(-np.log10(0.05), color="gray", linestyle="--", linewidth=0.8, alpha=0.7)
plt.axvline(1, color="gray", linestyle="--", linewidth=0.8, alpha=0.7)
plt.axvline(-1, color="gray", linestyle="--", linewidth=0.8, alpha=0.7)

# Coordinates of specific genes to label
labels = {
    "STAG3": (4.629281, 100.0, (10, 15)),
    "SMC1B": (5.905489, 89.96, (12, 10)),
    "ZFR2": (6.517135, 85.16, (15, -10)),
    "CD79A": (1.363353, 3.04, (-35, 12)),
    "MS4A1": (2.071974, 4.60, (-35, 20)),
    "IGKC": (1.135499, 1.97, (-30, -15)),
    "S100A7": (-1.917265, 4.83, (-45, -15)),
    "TACSTD2": (0.603686, 3.24, (12, 15))
}

for gene, (x, y, text_offset) in labels.items():
    plt.scatter(x, y, color="black", edgecolor="white", s=30, zorder=5)
    ax.annotate(
        gene,
        xy=(x, y),
        xytext=text_offset,
        textcoords="offset points",
        arrowprops=dict(arrowstyle="->", color="black", lw=0.6, shrinkA=0, shrinkB=2),
        fontname="DejaVu Sans",
        fontsize=9,
        fontweight="bold",
        zorder=6,
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="gray", lw=0.4, alpha=0.95)
    )

# Formatting
plt.title("Differential Gene Expression (HPV+ vs. HPV- HNSC)", fontsize=12, fontweight="bold", pad=15)
plt.xlabel("log2 Fold Change", fontsize=10, labelpad=8)
plt.ylabel("-log10(FDR-adjusted P-value)", fontsize=10, labelpad=8)
plt.xlim(-8.5, 8.5)
plt.ylim(0, 110)
plt.grid(True, linestyle=":", alpha=0.5)
plt.legend(loc="upper left", frameon=True, facecolor="white", edgecolor="none", fontsize=8.5)

# Tight layout
plt.tight_layout()

# Save path
project_save = os.path.join(project_dir, "Figure8_Volcano_DESeq2.png")
plt.savefig(project_save, dpi=300)
plt.close()

print(f"Successfully generated custom volcano plot at: {project_save}")
