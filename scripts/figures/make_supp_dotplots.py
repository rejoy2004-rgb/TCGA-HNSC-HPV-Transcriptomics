"""Supplementary Fig. S3: GO biological-process and KEGG over-representation among genes downregulated in HPV+ tumours,
redrawn from results/HNSC_HPV_GO_Downregulated.csv and results/HNSC_HPV_KEGG_Downregulated.csv."""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False})
def ratio(s):
    a, b = s.split("/"); return int(a) / int(b)

def prep(path, n):
    d = pd.read_csv(path)
    d = d.sort_values("p.adjust").head(n).copy()
    d["ratio"] = d.GeneRatio.map(ratio); d["nlp"] = -np.log10(d["p.adjust"])
    return d.sort_values("ratio")

go = prep("results/HNSC_HPV_GO_Downregulated.csv", 20)
kg = prep("results/HNSC_HPV_KEGG_Downregulated.csv", 15)
fig, axes = plt.subplots(1, 2, figsize=(9.4, 4.6), gridspec_kw={"width_ratios": [1.15, 1]}, layout="constrained")
vmax = max(go.nlp.max(), kg.nlp.max())
allcount = pd.concat([go.Count, kg.Count])
smin, smax = allcount.min(), allcount.max()
size = lambda c: 18 + 110 * (c - smin) / (smax - smin)
for ax, d, title, letter, wrap in ((axes[0], go, "GO biological process", "a", 38), (axes[1], kg, "KEGG pathway", "b", 30)):
    sc = ax.scatter(d.ratio, range(len(d)), s=size(d.Count), c=d.nlp, cmap="viridis_r", vmin=0, vmax=vmax, edgecolor="#333", lw=0.4, zorder=3)
    ax.set_yticks(range(len(d)))
    import textwrap
    ax.set_yticklabels(["\n".join(textwrap.wrap(t, wrap)) for t in d.Description], fontsize=7.5)
    ax.set_xlabel("Gene ratio", fontsize=8.5); ax.tick_params(axis="x", labelsize=8)
    ax.grid(axis="both", color="#e8e8e8", lw=0.6, zorder=0); ax.set_axisbelow(True)
    ax.set_title(title, loc="left", fontsize=9, fontweight="bold", pad=6)
    ax.text(-0.02, 1.07, letter, transform=ax.transAxes, fontsize=12, fontweight="bold", va="bottom", ha="right")
    ax.margins(y=0.03, x=0.08)
cb = fig.colorbar(sc, ax=axes, fraction=0.025, pad=0.02)
cb.set_label(r"$-\log_{10}$ FDR", fontsize=8.5); cb.ax.tick_params(labelsize=8)
hs = [Line2D([], [], marker="o", ls="", mfc="#999", mec="#333", ms=np.sqrt(size(c)), label=str(c)) for c in (25, 50, 100)]
axes[1].legend(handles=hs, title="Gene count", fontsize=8, title_fontsize=8, frameon=False, loc="lower right")
fig.savefig("figures/integrated/SuppFig_Down_GO_KEGG.png", dpi=600, bbox_inches="tight")
print("ok", go.Count.max(), kg.Count.max())
