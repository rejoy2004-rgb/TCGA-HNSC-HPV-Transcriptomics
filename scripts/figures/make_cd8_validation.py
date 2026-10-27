"""Supplementary Fig. S5: CIBERSORTx fractions against marker-gene expression (TCGA-HNSC, n = 279), the four pairs in Supplementary Table S8.
a, b  CD8+ T-cell fraction vs CD8A, CD8B: results/review_sensitivity/CD8_validation_input.csv (DESeq2-normalised counts from GDC STAR counts).
c, d  plasma-cell fraction vs IGHM, MS4A1: TPM supplied to CIBERSORTx (data_processed/HNSC_CIBERSORT_Input_Final.txt).
Spearman rho is rank-based, so it does not depend on the transformation plotted."""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import spearmanr, linregress

d = pd.read_csv("results/review_sensitivity/CD8_validation_input.csv")
x = pd.read_csv("data_processed/HNSC_CIBERSORT_Input_Final.txt", sep="\t", index_col=0); x.columns = [c[:15] for c in x.columns]
j = pd.read_csv("data_processed/CIBERSORTx_Job14_Results.csv"); j.index = j["Mixture"].str[:15]
s = [i for i in pd.read_csv("data_processed/HNSC_HPV_status.csv")["Sample ID"] if i in j.index and i in x.columns]
assert len(s) == 279
panels = [("CD8$^{+}$ T-cell", d.CIBERSORTx_CD8_T_cells.values, g, np.log2(d[f"{g}_normalised_count"].values + 1), "log$_2$(normalised count + 1)") for g in ("CD8A", "CD8B")]
panels += [("plasma-cell", j.loc[s, "Plasma cells"].values, g, np.log2(x.loc[g, s].astype(float).values + 1), "log$_2$(TPM + 1)") for g in ("IGHM", "MS4A1")]
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False})
fig, axes = plt.subplots(2, 2, figsize=(7.4, 6.4), layout="constrained")
for ax, (cell, xv, g, y, unit), letter in zip(axes.flat, panels, "abcd"):
    rho, p = spearmanr(xv, y)
    ax.scatter(xv, y, s=12, color="#2a78d6", alpha=0.6, edgecolor="white", lw=0.3, zorder=3)
    lr = linregress(xv, y); xs = np.linspace(xv.min(), xv.max(), 50)
    ax.plot(xs, lr.intercept + lr.slope * xs, color="#c0392b", lw=1.4, zorder=4)
    ax.set_xlabel(f"CIBERSORTx {cell} fraction", fontsize=8.5)
    ax.set_ylabel(f"{g} expression, {unit}", fontsize=8.5)
    ax.tick_params(labelsize=8); ax.grid(color="#ececec", lw=0.6); ax.set_axisbelow(True)
    ax.set_title(f"{g}  (Spearman ρ = {rho:.3f})", loc="left", fontsize=9, fontweight="bold", pad=6)
    ax.text(-0.02, 1.10, letter, transform=ax.transAxes, fontsize=12, fontweight="bold", va="bottom", ha="right")
    print(g, round(rho, 3), p)
fig.savefig("figures/integrated/SuppFig_CD8_Validation.png", dpi=600)
fig.savefig("figures/integrated/SuppFig_CD8_Validation.pdf")  # vector copy for submission
