"""Regenerate the tumour-immune-microenvironment figure from the canonical
CIBERSORTx Job14 output (used by scripts/HPV_HNSC_Revision.R) so that the
plotted medians match results/HNSC_HPV_Immune_Comparison.csv. FDR labels come
from results/HNSC_HPV_Immune_Comparison_All22_BH.csv (BH across all 22 LM22
cell types; the R script corrects across only 5 pre-selected cell types)."""
import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

job = pd.read_csv("data_processed/CIBERSORTx_Job14_Results.csv")
job["Sample ID"] = job["Mixture"].str[:15]
hpv = pd.read_csv("data_processed/HNSC_HPV_status.csv")
d = hpv.merge(job, on="Sample ID")
stats = pd.read_csv("results/HNSC_HPV_Immune_Comparison_All22_BH.csv").set_index("CellType")
ratio = pd.read_csv("results/HNSC_CD8_M2_ratio_data.csv")

# sanity check: medians must reproduce the canonical comparison table
for c in stats.index:
    med = d.groupby("HPV Status")[c].median()
    assert abs(med["positive"] - stats.loc[c, "Median_HPV_Positive"]) < 1e-9, c
    assert abs(med["negative"] - stats.loc[c, "Median_HPV_Negative"]) < 1e-9, c

COL = {"negative": "#2a78d6", "positive": "#eb6834"}
panels = [("Plasma cells", "Plasma cells"), ("T cells CD8", "CD8+ T cells"),
          ("Macrophages M0", "M0 macrophages"), ("NK cells resting", "Resting NK cells"),
          ("T cells CD4 memory resting", "Resting CD4+ memory T cells"), (None, "log2(CD8 / M2) ratio")]
n = d["HPV Status"].value_counts()
fig, axes = plt.subplots(2, 3, figsize=(10.5, 6.6), dpi=300)
rng = np.random.default_rng(1)
for ax, (col, title), letter in zip(axes.flat, panels, "abcdef"):
    if col is None:
        src, y, ylab = ratio, "log2_CD8_M2_Ratio", "log2 ratio"
        grp = "HPV.Status"
        note = "exploratory score"
    else:
        src, y, ylab, grp = d, col, "Estimated fraction", "HPV Status"
        note = f"FDR = {stats.loc[col, 'FDR']:.1e}"
    for i, g in enumerate(["negative", "positive"]):
        v = src.loc[src[grp] == g, y].dropna().values
        ax.boxplot(v, positions=[i], widths=0.5, showfliers=False,
                   medianprops=dict(color="#222", lw=2), boxprops=dict(color="#555", lw=1),
                   whiskerprops=dict(color="#555", lw=1), capprops=dict(color="#555", lw=1))
        ax.scatter(i + rng.uniform(-0.17, 0.17, len(v)), v, s=9, color=COL[g], alpha=0.65,
                   edgecolors="white", linewidths=0.3, zorder=3)
    ax.set_xticks([0, 1], [f"HPV−\n(n = {n['negative']})", f"HPV+\n(n = {n['positive']})"], fontsize=8)
    ax.set_title(f"{letter}  {title}", loc="left", fontsize=9.5, fontweight="bold")
    ax.text(1.0, 1.02, note, transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, color="#444")
    ax.set_ylabel(ylab, fontsize=8); ax.tick_params(labelsize=7.5)
    ax.grid(axis="y", color="#e6e6e6", lw=0.6); ax.set_axisbelow(True)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig("figures/integrated/Figure4_TME_CIBERSORTx_Job14.png", dpi=600)
print("ok", n.to_dict())
