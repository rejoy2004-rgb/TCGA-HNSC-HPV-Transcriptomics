"""Supplementary Fig. S5: CIBERSORTx CD8+ T-cell fraction against CD8A and CD8B expression (TCGA-HNSC, n = 279).
Input: results/review_sensitivity/CD8_validation_input.csv (DESeq2-normalised counts from GDC STAR counts; Spearman rho is rank-based,
so it is the same as with variance-stabilised values)."""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import spearmanr, linregress

d = pd.read_csv("results/review_sensitivity/CD8_validation_input.csv")
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False})
fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.3), layout="constrained")
for ax, g, letter in zip(axes, ("CD8A", "CD8B"), "ab"):
    x = d.CIBERSORTx_CD8_T_cells.values; y = np.log2(d[f"{g}_normalised_count"].values + 1)
    rho, p = spearmanr(x, y)
    ax.scatter(x, y, s=12, color="#2a78d6", alpha=0.6, edgecolor="white", lw=0.3, zorder=3)
    lr = linregress(x, y); xs = np.linspace(x.min(), x.max(), 50)
    ax.plot(xs, lr.intercept + lr.slope * xs, color="#c0392b", lw=1.4, zorder=4)
    ax.set_xlabel("CIBERSORTx CD8$^{+}$ T-cell fraction", fontsize=8.5)
    ax.set_ylabel(f"{g} expression, log$_2$(normalised count + 1)", fontsize=8.5)
    ax.tick_params(labelsize=8); ax.grid(color="#ececec", lw=0.6); ax.set_axisbelow(True)
    ax.set_title(f"{g}  (Spearman \u03c1 = {rho:.3f})", loc="left", fontsize=9, fontweight="bold", pad=6)
    ax.text(-0.02, 1.10, letter, transform=ax.transAxes, fontsize=12, fontweight="bold", va="bottom", ha="right")
    print(g, round(rho, 4), p)
fig.savefig("figures/integrated/SuppFig_CD8_Validation.png", dpi=600)
