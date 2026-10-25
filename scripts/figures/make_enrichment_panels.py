"""Redraw Figure 1c and Supplementary Fig. S2a from the deposited enrichment re-run
(results/HNSC_HPV_GO_Upregulated.csv, results/HNSC_HPV_GSEA.csv) so that figures and text share one source."""
import csv, math, re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLUE, GREY, LGREY = "#1f6cb0", "#8a8a8a", "#bcc3cc"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False})

# Figure 1c: eight most significant GO biological-process terms among upregulated genes
go = sorted(csv.DictReader(open("results/HNSC_HPV_GO_Upregulated.csv", encoding="utf-8")), key=lambda x: float(x["p.adjust"]))[:8]
labels = [x["Description"] for x in go][::-1]
vals = [-math.log10(float(x["p.adjust"])) for x in go][::-1]
cols = [BLUE if "meio" in l else GREY for l in labels]
fig, ax = plt.subplots(figsize=(7.55, 2.25))
ax.barh(labels, vals, color=cols, height=0.68)
ax.set_xlim(0, 10); ax.set_xlabel(r"$-\log_{10}$ FDR", fontsize=9)
ax.tick_params(labelsize=7.5)
ax.set_title("Meiotic processes rank third and fourth among enriched upregulated terms", fontsize=9, loc="left")
ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=BLUE), plt.Rectangle((0, 0), 1, 1, color=GREY)], labels=["meiotic term", "other term"],
          frameon=False, fontsize=7.5, loc="lower right")
fig.text(0.02, 0.93, "c", fontsize=12, fontweight="bold")
fig.savefig("figures/source_panels_600dpi/Figure 1/Figure 1c.png", dpi=600, bbox_inches="tight")
fig.savefig("figures/source_panels_600dpi/Figure 1/Figure 1c.pdf", bbox_inches="tight")
fig.savefig("figures/source_panels_600dpi/Figure 1/Figure 1c.tif", dpi=600, bbox_inches="tight", pil_kwargs={"compression": "tiff_lzw"})
plt.close(fig)

# Supplementary Fig. S2a: 20 highest-NES GSEA biological-process terms
gs = [x for x in csv.DictReader(open("results/HNSC_HPV_GSEA.csv", encoding="utf-8")) if x["NES"] not in ("NA", "")]
gs.sort(key=lambda x: -float(x["NES"])); gs = gs[:20]
names = [x["Description"] for x in gs][::-1]; nes = [float(x["NES"]) for x in gs][::-1]
isb = [bool(re.search(r"meio|recombination", n)) and n != "recombinational repair" for n in names]
top5 = [bool(re.search(r"meio|recombination", x["Description"])) for x in gs[:5]]
trunc = lambda s: s if len(s) <= 40 else s[:39] + "…"
fig, ax = plt.subplots(figsize=(5.2, 3.06))
for i, (n, v, b) in enumerate(zip(names, nes, isb)):
    ax.plot([2.0, v], [i, i], color="#5b94c9" if b else "#c8cdd5", lw=1.3, zorder=1)
    ax.scatter([v], [i], s=34, color=BLUE if b else LGREY, zorder=2)
ax.set_yticks(range(len(names))); ax.set_yticklabels([trunc(n) for n in names], fontsize=6.5)
ax.set_xlim(2.0, 3.02); ax.set_xlabel("GSEA normalised enrichment score", fontsize=8); ax.tick_params(axis="x", labelsize=7)
ax.set_title("Meiosis dominates the original\nHPV+ enrichment ranking", fontsize=8.5, loc="left")
ax.text(0.97, 0.12, f"blue = meiosis-related\n({sum(top5)} of the top 5)", transform=ax.transAxes, ha="right", color=BLUE, fontsize=7)
fig.text(0.02, 0.93, "a", fontsize=11, fontweight="bold")
fig.savefig("figures/source_panels_600dpi/Figure 2/Figure 2a.png", dpi=600, bbox_inches="tight")
fig.savefig("figures/source_panels_600dpi/Figure 2/Figure 2a.pdf", bbox_inches="tight")
fig.savefig("figures/source_panels_600dpi/Figure 2/Figure 2a.tif", dpi=600, bbox_inches="tight", pil_kwargs={"compression": "tiff_lzw"})
print("ok", sum(top5), [ (n,round(v,2)) for n,v in zip(names[::-1][:5],nes[::-1][:5])])


# Figure 1a: volcano plot from the deposited DESeq2 results (nine of the twelve most significant genes are panel genes)
import numpy as np
allr = list(csv.DictReader(open("results/HNSC_DESeq2_All_Results.csv", encoding="utf-8")))
sym = {x["gene_id"]: x["SYMBOL"] for x in csv.DictReader(open("results/HNSC_HPV_DEGs_annotated.csv", encoding="utf-8"))}
pts = [(x[""], float(x["log2FoldChange"]), float(x["padj"])) for x in allr if x["padj"] not in ("NA", "")]
lfc = np.array([p[1] for p in pts]); y = -np.log10(np.array([max(p[2], 1e-300) for p in pts]))
up = (lfc > 1) & (y > -np.log10(0.05)); dn = (lfc < -1) & (y > -np.log10(0.05)); ns = ~(up | dn)
print("up", up.sum(), "down", dn.sum())
fig, ax = plt.subplots(figsize=(7.8, 3.9))
ax.scatter(lfc[ns], y[ns], s=3, color="#d0d0d0", lw=0)
ax.scatter(lfc[dn], y[dn], s=4, color="#5b8fbf", lw=0)
ax.scatter(lfc[up], y[up], s=4, color="#c4583c", lw=0)
ax.axvline(-1, ls="--", c="#666", lw=0.8); ax.axvline(1, ls="--", c="#666", lw=0.8); ax.axhline(-np.log10(0.05), ls="--", c="#666", lw=0.8)
lab = ["STAG3", "SMC1B", "ZFR2", "RAD9B", "TDRD10", "CNTD1", "SYCP2", "MAJIN", "SYCE2", "MEI1"]
alias = {"MAJIN": ("MAJIN", "C11orf85")}
ids = {}
for gid, s in sym.items():
    for L_ in lab:
        if s in alias.get(L_, (L_,)): ids[L_] = gid
pos = {p[0].split(".")[0]: (p[1], yy) for p, yy in zip(pts, y)}
order = sorted(lab, key=lambda g: -pos[ids[g]][1])
ytxt = np.linspace(105, 12, len(order))
for g, yt in zip(order, ytxt):
    x0, y0 = pos[ids[g]]
    ax.scatter([x0], [y0], s=42, facecolors="none", edgecolors=BLUE, lw=1.4, zorder=3)
    ax.plot([x0, 7.7], [y0, yt], color="#0b5ea8", lw=0.5)
    ax.text(7.8, yt, g, color="#0b5ea8", fontsize=7, style="italic", va="center")
ax.set_xlim(-8.6, 10.6); ax.set_ylim(-4, 115)
ax.set_xlabel(r"$\log_2$ fold change, HPV+ vs HPV$-$", fontsize=9); ax.set_ylabel(r"$-\log_{10}$ FDR", fontsize=9)
ax.tick_params(labelsize=7.5)
ax.set_title("4,744 genes differentially expressed; nine of the twelve most significant are panel genes", fontsize=9, loc="left")
ax.legend(handles=[plt.Line2D([], [], marker="o", ls="", color="#c4583c", ms=2.5), plt.Line2D([], [], marker="o", ls="", color="#5b8fbf", ms=2.5),
                   plt.Line2D([], [], marker="o", ls="", mfc="none", mec=BLUE, ms=6, mew=1.4)],
          labels=[f"up in HPV+ ({up.sum():,})", f"down in HPV+ ({dn.sum():,})", "selected meiotic gene (10)"], frameon=False, fontsize=7.5, loc="upper left")
fig.text(0.01, 0.95, "a", fontsize=12, fontweight="bold")
for ext, kw in (("png", {"dpi": 600}), ("pdf", {}), ("tif", {"dpi": 600, "pil_kwargs": {"compression": "tiff_lzw"}})):
    fig.savefig(f"figures/source_panels_600dpi/Figure 1/Figure 1a.{ext}", bbox_inches="tight", **kw)
plt.close(fig)
print("1a done", ids.keys())
