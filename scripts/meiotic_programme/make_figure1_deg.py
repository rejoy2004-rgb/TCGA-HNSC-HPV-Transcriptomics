#!/usr/bin/env python3
"""Figure 1 - differential expression in HPV+ vs HPV- TCGA-HNSC places the meiotic
machinery among the most strongly induced programmes.

  (a) volcano plot, the ten meiotic panel genes ringed and labelled
  (b) log2 fold change of the ten meiotic panel genes
  (c) the eight most significant GO-BP terms among upregulated genes, meiotic terms in blue

Inputs (produced by scripts/HPV_HNSC_Revision.R, or shipped in the repository):
  results/HNSC_DESeq2_All_Results.csv                     DESeq2, HPV+ vs HPV- (279 tumours)
  results/HNSC_HPV_DEGs_annotated.csv                     Ensembl -> symbol annotation
  data_processed/meiotic_programme/GO_BP_upregulated_ORA.csv  GO-BP ORA on upregulated genes

Outputs: results/meiotic_programme/Fig1_deg.png/.pdf (600 dpi) and, with --panels,
figures/source_panels_600dpi/Figure 1/Figure 1{a,b,c}.tif/.png/.pdf

Usage (from the repository root):
    python scripts/meiotic_programme/make_figure1_deg.py [--panels]
"""
import argparse, os, sys
os.environ.setdefault("KMP_AFFINITY", "disabled")
os.environ.setdefault("OMP_NUM_THREADS", "1")
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
REPO = HERE.parents[1]
from meiotic.panel_export import export_panels

PANEL10 = ["STAG3", "SMC1B", "ZFR2", "RAD9B", "TDRD10", "CNTD1", "SYCP2", "MAJIN", "SYCE2", "MEI1"]
FOCAL, UP, DN, OTHER = "#1b6ca8", "#c2553a", "#5a8fbb", "#888888"


def apply_figure_style(*, frame="open", font=None, sizes=(8, 7, 6), grid=False):
    """Set matplotlib rcParams for publication-grade output. Call once before plotting.

    This sets mechanics (role-mapped font-size ladder, outward ticks, frameless
    legends, 300-dpi save, Type-42 embedded fonts) — not a house aesthetic.
    Frame, font and the size ladder are parameters.

    frame : 'open' (bottom+left spines, default) | 'boxed' (all four) | 'none'
    font  : sans-serif family name; None = system default sans-serif
    sizes : (base, secondary, tick) — titles/axis-labels, legend/annotation, ticks
    grid  : whether to draw axes.grid (default False)
    """
    import matplotlib as mpl
    if frame not in ("open", "boxed", "none"):
        raise ValueError(f"frame must be 'open'|'boxed'|'none', got {frame!r}")

    try:
        import os, sys, glob, matplotlib.font_manager as fm
        fdir = os.path.join(os.environ.get("CONDA_PREFIX") or sys.prefix, "fonts")
        if os.path.isdir(fdir):
            known = {f.fname for f in fm.fontManager.ttflist}
            for f in glob.glob(os.path.join(fdir, "*.ttf")):
                if f not in known:
                    fm.fontManager.addfont(f)
    except Exception:
        pass
    base, secondary, tick = sizes
    boxed = (frame == "boxed")
    rc = {
        "font.family": "sans-serif",
        "font.size": base,
        "axes.labelsize": base,
        "axes.titlesize": base,
        "legend.fontsize": secondary,
        "xtick.labelsize": tick,
        "ytick.labelsize": tick,
        "axes.linewidth": 0.6,
        "xtick.direction": "out", "ytick.direction": "out",
        "xtick.major.size": 3, "ytick.major.size": 3,
        "xtick.major.width": 0.6, "ytick.major.width": 0.6,
        "axes.spines.top": boxed, "axes.spines.right": boxed,
        "axes.spines.left": frame != "none", "axes.spines.bottom": frame != "none",
        "axes.grid": bool(grid),
        "legend.frameon": False,
        "figure.dpi": 200,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "axes.titleweight": "normal",
        "axes.titlelocation": "left",
        "axes.labelweight": "normal",
        "lines.linewidth": 1.2,
        "patch.linewidth": 0.6,
        "pdf.fonttype": 42, "ps.fonttype": 42,
    }
    if font:
        rc["font.sans-serif"] = [font, "DejaVu Sans"]
    mpl.rcParams.update(rc)


def panel_letter(ax, letter, dx=-0.18, dy=1.02, case="lower", fontsize=None):
    """§5.7: bold panel letter outside top-left of axes. case ∈ {'lower','upper'}."""
    import matplotlib.pyplot as plt
    if fontsize is None:
        fontsize = plt.rcParams.get("font.size", 8) + 1
    s = letter.lower() if case == "lower" else letter.upper()
    ax.text(dx, dy, s, transform=ax.transAxes,
            fontweight="bold", fontsize=fontsize, va="bottom", ha="left")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--panels", action="store_true")
    a = ap.parse_args()
    out = REPO / "results" / "meiotic_programme"; out.mkdir(parents=True, exist_ok=True)

    res = pd.read_csv(REPO / "results" / "HNSC_DESeq2_All_Results.csv")
    res = res.rename(columns={res.columns[0]: "gene_id"}) if "gene_id" not in res.columns else res
    ann = pd.read_csv(REPO / "results" / "HNSC_HPV_DEGs_annotated.csv")
    GU = pd.read_csv(REPO / "data_processed" / "meiotic_programme" / "GO_BP_upregulated_ORA.csv")

    strip = lambda s: s.astype(str).str.split(".").str[0]
    ann = ann.assign(g=strip(ann.gene_id))[["g", "SYMBOL"]].drop_duplicates("g")
    V = (res.assign(g=strip(res.gene_id)).drop_duplicates("g")
            .merge(ann, on="g", how="left").dropna(subset=["padj"]))
    V["sig"] = (V.padj < 0.05) & (V.log2FoldChange.abs() > 1)
    V["mei"] = V.SYMBOL.isin(PANEL10)
    nup = int((V.sig & (V.log2FoldChange > 0)).sum()); ndn = int((V.sig & (V.log2FoldChange < 0)).sum())
    print(f"DEGs (FDR < 0.05, |log2FC| > 1): {nup + ndn} ({nup} up, {ndn} down)")

    apply_figure_style(sizes=(8, 7, 6))
    pu = "p.adjust"
    gu8 = GU.nsmallest(8, pu)[["Description", "Count", pu]].iloc[::-1]
    gu8["mei"] = gu8.Description.str.contains("meio", case=False)
    gd10 = V[V.mei][["SYMBOL", "log2FoldChange", "padj"]].sort_values("log2FoldChange")
    Y = -np.log10(V.padj.clip(lower=1e-110))

    fig = plt.figure(figsize=(7.0, 9.4))
    gs = fig.add_gridspec(3, 1, height_ratios=[1.35, 0.85, 0.85], hspace=0.34)
    axA, axB, axC = (fig.add_subplot(gs[i, 0]) for i in range(3))
    ns = ~V.sig
    axA.scatter(V.log2FoldChange[ns], Y[ns], s=3, c="0.82", lw=0, rasterized=True)
    for msk, col, lab in [((V.sig) & (V.log2FoldChange > 0), UP, f"up in HPV+ ({nup:,})"),
                          ((V.sig) & (V.log2FoldChange < 0), DN, f"down in HPV+ ({ndn:,})")]:
        axA.scatter(V.log2FoldChange[msk], Y[msk], s=4, c=col, lw=0, rasterized=True, label=lab)
    axA.scatter(gd10.log2FoldChange, -np.log10(gd10.padj), s=34, facecolor="none", edgecolor=FOCAL,
                lw=1.3, zorder=5, label="meiotic panel gene (10)")
    axA.axhline(-np.log10(0.05), color="0.45", lw=0.7, ls=(0, (4, 3)))
    for xv in (-1, 1):
        axA.axvline(xv, color="0.45", lw=0.7, ls=(0, (4, 3)))
    order = gd10.sort_values("padj").reset_index(drop=True); ytop, step = 104, 9.5
    for k, row in order.iterrows():
        axA.annotate(row.SYMBOL, (row.log2FoldChange, -np.log10(row.padj)), xytext=(7.55, ytop - k * step),
                     textcoords="data", fontsize=6, style="italic", va="center", ha="left", color=FOCAL,
                     arrowprops=dict(arrowstyle="-", lw=0.45, color=FOCAL, shrinkA=0, shrinkB=1.5))
    axA.set_xlim(-8.6, 10.6); axA.set_ylim(-4, 114)
    axA.set_xlabel("log$_2$ fold change, HPV+ vs HPV\u2212"); axA.set_ylabel("\u2212log$_{10}$ FDR")
    axA.set_title(f"{nup + ndn:,} genes differentially expressed; six of the twelve most significant are meiotic", loc="left")
    axA.legend(loc="upper left", frameon=False, fontsize=6, handletextpad=0.4, borderaxespad=0.5)

    axB.hlines(range(len(gd10)), 0, gd10.log2FoldChange, color=FOCAL, lw=1.1, zorder=1)
    axB.plot(gd10.log2FoldChange, range(len(gd10)), "o", ms=5.5, color=FOCAL, zorder=2)
    axB.set_yticks(range(len(gd10))); axB.set_yticklabels(gd10.SYMBOL, style="italic")
    axB.axvline(0, color="0.3", lw=0.8); axB.margins(x=0.17, y=0.06)
    axB.set_xlabel("log$_2$ fold change, HPV+ vs HPV\u2212")
    for y, v in enumerate(gd10.log2FoldChange):
        axB.annotate(f"{v:.1f}", (v, y), xytext=(5, 0), textcoords="offset points", va="center", fontsize=6)
    axB.set_title("Every meiotic panel gene is induced, by 2.8 to 6.5 doublings", loc="left")

    axC.barh(range(len(gu8)), -np.log10(gu8[pu]), color=[FOCAL if m else OTHER for m in gu8.mei], height=0.66)
    axC.set_yticks(range(len(gu8))); axC.set_yticklabels(gu8.Description)
    axC.set_xlabel("\u2212log$_{10}$ FDR"); axC.margins(x=0.08, y=0.04)
    axC.set_title("Meiotic processes rank third and fourth among enriched upregulated terms", loc="left")
    axC.legend([mpl.patches.Patch(fc=FOCAL, ec="none"), mpl.patches.Patch(fc=OTHER, ec="none")],
               ["meiotic term", "other term"], loc="lower right", frameon=False, fontsize=6,
               handlelength=1.1, borderaxespad=0.6)
    for L_, ax in zip("abc", [axA, axB, axC]):
        panel_letter(ax, L_)
    fig.savefig(out / "Fig1_deg.png", dpi=600, bbox_inches="tight")
    fig.savefig(out / "Fig1_deg.pdf", dpi=600, bbox_inches="tight")
    if a.panels:
        export_panels(fig, str(REPO / "figures" / "source_panels_600dpi" / "Figure 1"), "Figure 1", dpi=600)
    print("wrote", out / "Fig1_deg.png")


if __name__ == "__main__":
    main()
