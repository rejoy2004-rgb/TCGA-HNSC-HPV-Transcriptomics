"""Supplementary forest plot of exploratory univariable Cox models (600 dpi),
drawn from results/HNSC_Standardized_Cox_Results.csv."""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

d = pd.read_csv("results/HNSC_Standardized_Cox_Results.csv").sort_values("HR", ascending=False).reset_index(drop=True)
sig = d["Pvalue"] < 0.05
fig, ax = plt.subplots(figsize=(5.2, 3.6))
for i, r in d.iterrows():
    c = "#c0392b" if r.Pvalue < 0.05 else "#8a8a8a"
    ax.plot([r.Lower95CI, r.Upper95CI], [i, i], color=c, lw=1.6, solid_capstyle="butt")
    ax.plot(r.HR, i, "o", color=c, ms=6)
    ax.text(1.115, i, f"{r.HR:.2f} ({r.Lower95CI:.2f}–{r.Upper95CI:.2f})   P = {r.Pvalue:.2g}",
            va="center", fontsize=7.2, color="#222")
ax.axvline(1, ls="--", lw=0.9, color="#333")
ax.set_yticks(range(len(d)), d["Gene"], fontstyle="italic", fontsize=8.5)
ax.set_xlim(0.5, 1.1); ax.set_ylim(-0.7, len(d) - 0.3)
ax.set_xlabel("Hazard ratio per SD of expression (95% CI)", fontsize=8.5)
ax.tick_params(axis="x", labelsize=8)
for s in ("top", "right"): ax.spines[s].set_visible(False)
ax.text(1.115, len(d) - 0.1, "HR (95% CI)   nominal P", fontsize=7.2, fontweight="bold", va="bottom")
fig.subplots_adjust(left=0.16, right=0.62, bottom=0.14, top=0.92)
fig.savefig("figures/integrated/SuppFig_Cox_forest_600dpi.png", dpi=600, facecolor="white")
print("ok", len(d), "genes;", int(sig.sum()), "nominally significant")
