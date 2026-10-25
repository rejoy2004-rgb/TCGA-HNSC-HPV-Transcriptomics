"""Figure builder for the GSE182227 single-cell replication and the two-cohort comparison."""
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy import stats

BLUE, RED, GREY = "#3B75AF", "#C4443C", "#B8BFC9"


def build(emb, lineage, is_mal, grp, t6, t4, tc, tp, det, meta,
          pt227, comb, reg, out_png):
    apply = globals().get("apply_figure_style")
    if apply:
        apply(sizes=(8, 7, 6))
    fig = plt.figure(figsize=(13.5, 9.0))
    gs = fig.add_gridspec(2, 3, hspace=0.44, wspace=0.31,
                          left=0.06, right=0.985, top=0.90, bottom=0.075)

    # ---- (a) UMAP: lineage, malignant highlighted ------------------------
    ax = fig.add_subplot(gs[0, 0])
    lab = np.where(is_mal, "Malignant",
                   np.where(lineage == "Epithelial", "Normal epithelium", lineage))
    order = list(pd.Series(lab).value_counts().index)
    cmap = plt.get_cmap("tab20")
    col = {c: cmap(i % 20) for i, c in enumerate(order)}
    col["Malignant"] = RED
    col["Normal epithelium"] = "#7BA05B"
    for c in order:
        m = lab == c
        ax.scatter(emb[m, 0], emb[m, 1], s=0.7, lw=0, c=[col[c]],
                   rasterized=True, alpha=0.85 if c == "Malignant" else 0.4)
    OFF = {"Normal epithelium": (34, -12), "Mast": (24, -8), "Plasma": (-26, -12)}
    for c in order:
        m = lab == c
        if m.sum() < 400 and c not in OFF:
            continue
        x, y = np.median(emb[m, 0]), np.median(emb[m, 1])
        if c in OFF:
            ax.annotate(c, (x, y), textcoords="offset points", xytext=OFF[c],
                        fontsize=6, ha="center", va="center",
                        arrowprops=dict(arrowstyle="-", lw=0.5, color="0.45",
                                        shrinkA=0, shrinkB=2),
                        bbox=dict(fc="white", ec="none", alpha=0.8, pad=0.8))
        else:
            ax.annotate(c, (x, y), fontsize=6, ha="center", va="center",
                        bbox=dict(fc="white", ec="none", alpha=0.72, pad=0.8))
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title("Malignant epithelium identified\nde novo (no labels supplied)", loc="left")
    _umap_arrows(ax)

    # ---- (b) malignant cells split by HPV --------------------------------
    ax = fig.add_subplot(gs[0, 1])
    hp = meta["hpv"].values
    base = ~is_mal
    ax.scatter(emb[base, 0], emb[base, 1], s=0.6, lw=0, c=GREY,
               rasterized=True, alpha=0.35)
    for h, c in [("HPV-", BLUE), ("HPV+", RED)]:
        m = is_mal & (hp == h)
        ax.scatter(emb[m, 0], emb[m, 1], s=1.0, lw=0, c=[c],
                   rasterized=True, alpha=0.75, label=f"{h} malignant")
    ax.set_xticks([]); ax.set_yticks([])
    ax.legend(frameon=False, fontsize=6, loc="upper left", markerscale=6,
              handletextpad=0.3, borderpad=0.2)
    ax.set_title("Malignant cells cluster by patient\nand by HPV status", loc="left")
    _umap_arrows(ax)

    # ---- (c) detection by group ------------------------------------------
    ax = fig.add_subplot(gs[0, 2])
    d = (pd.DataFrame({"g": grp, "det": det}).groupby("g")["det"]
         .agg(["mean", "size"]).sort_values("mean"))
    cols = [RED if g == "Malignant" else ("#7BA05B" if g == "Normal epithelium" else GREY)
            for g in d.index]
    ax.barh(np.arange(len(d)), 100 * d["mean"].values, color=cols, height=0.72)
    ax.set_yticks(np.arange(len(d))); ax.set_yticklabels(d.index)
    for i, v in enumerate(100 * d["mean"].values):
        ax.text(v + 0.9, i, f"{v:.0f}%", va="center", fontsize=6)
    ax.set_xlabel("cells detecting any meiosis-specific gene (%)")
    ax.set_xlim(0, 45); ax.set_xticks([0, 10, 20, 30, 40])
    ax.set_title("Detection is specific to malignant\ncells (3.9% in normal epithelium)", loc="left")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)

    # ---- (d) per-tumour, this dataset ------------------------------------
    ax = fig.add_subplot(gs[1, 0])
    _strip(ax, pt227, "mean_meiotic4", "meiotic score (4 specific genes)",
           "Effect replicates; two HPV+ tumours\noverlap the HPV- range")

    # ---- (e) cross-dataset ------------------------------------------------
    ax = fig.add_subplot(gs[1, 1])
    xs = {"GSE181919": 0, "GSE182227": 1}
    rng = np.random.default_rng(0)
    for ds, x0 in xs.items():
        for h, c, dx in [("HPV-", BLUE, -0.17), ("HPV+", RED, 0.17)]:
            v = comb.loc[(comb.dataset == ds) & (comb.hpv == h), "mean_meiotic4"].values
            ax.scatter(np.full(len(v), x0 + dx) + rng.uniform(-0.055, 0.055, len(v)),
                       v, s=13, c=c, alpha=0.85, lw=0.4, ec="white", zorder=3)
            ax.plot([x0 + dx - 0.11, x0 + dx + 0.11], [np.median(v)] * 2,
                    lw=1.6, c="0.15", zorder=4)
    ax.axhline(0, lw=0.6, ls=":", c="0.55", zorder=1)
    ax.set_xticks([0, 1])
    ax.set_xticklabels([f"{ds}\n({int((comb.dataset == ds).sum())} tumours)" for ds in xs])
    ax.set_ylabel("meiotic score (4 specific genes)")
    ax.set_title("The same effect in two independent\ncohorts", loc="left")
    h1 = [plt.Line2D([], [], marker="o", ls="", c=BLUE, ms=4),
          plt.Line2D([], [], marker="o", ls="", c=RED, ms=4)]
    ax.legend(h1, ["HPV-", "HPV+"], frameon=False, fontsize=6, loc="upper left",
              handletextpad=0.3, borderpad=0.2)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)

    # ---- (f) adjusted vs unadjusted effect --------------------------------
    ax = fig.add_subplot(gs[1, 2])
    sel = reg[(reg.outcome == "mean_meiotic4")].copy()
    lbl, beta, se, cl = [], [], [], []
    for ds in ["GSE181919", "GSE182227", "both"]:
        for mdl, c in [("unadjusted", GREY), ("adjusted for proliferation", RED)]:
            r = sel[(sel.dataset == ds) & (sel.model == mdl)].iloc[0]
            lbl.append(f"{'pooled' if ds=='both' else ds}\n{mdl.split(' for')[0]}")
            beta.append(r.beta_HPV); se.append(r.se); cl.append(c)
    y = np.arange(len(beta))[::-1]
    ax.errorbar(beta, y, xerr=1.96 * np.array(se), fmt="o", ms=4.5,
                ecolor="0.45", elinewidth=1.0, capsize=2.5,
                mfc="none", mec="none", ls="none", zorder=2)
    ax.scatter(beta, y, s=26, c=cl, zorder=3, lw=0.5, ec="0.25")
    ax.axvline(0, lw=0.8, c="0.35", zorder=1)
    ax.set_yticks(y); ax.set_yticklabels(lbl, fontsize=5.5)
    ax.set_xlabel("HPV effect on meiotic score (95% CI)")
    ax.set_title("The effect survives adjustment for\nproliferation", loc="left")
    ax.set_ylim(-0.7, len(beta) - 0.3)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)

    for letter, ax in zip("abcdef", fig.axes[:6]):
        ax.text(-0.085, 1.13, letter, transform=ax.transAxes,
                fontsize=11, fontweight="bold", va="top", ha="right")
    fig.savefig(out_png, dpi=300)
    return fig


def _umap_arrows(ax):
    ax.annotate("", xy=(0.16, 0.02), xytext=(0.02, 0.02), xycoords="axes fraction",
                arrowprops=dict(arrowstyle="->", lw=0.8, color="0.35"))
    ax.annotate("", xy=(0.02, 0.16), xytext=(0.02, 0.02), xycoords="axes fraction",
                arrowprops=dict(arrowstyle="->", lw=0.8, color="0.35"))
    ax.text(0.175, 0.02, "UMAP 1", transform=ax.transAxes, fontsize=5.5, va="center")
    ax.text(0.028, 0.175, "UMAP 2", transform=ax.transAxes, fontsize=5.5, rotation=90)


def _strip(ax, pt, col, ylab, title):
    rng = np.random.default_rng(0)
    for x, (h, c) in enumerate([("HPV-", BLUE), ("HPV+", RED)]):
        v = pt.loc[pt.hpv == h, col].values
        n = pt.loc[pt.hpv == h, "n_cells"].values
        ax.scatter(np.full(len(v), x) + rng.uniform(-0.11, 0.11, len(v)), v,
                   s=8 + 34 * (n / n.max()), c=c, alpha=0.85, lw=0.4,
                   ec="white", zorder=3)
        ax.plot([x - 0.24, x + 0.24], [np.median(v)] * 2, lw=1.6, c="0.15", zorder=4)
    a = pt.loc[pt.hpv == "HPV+", col].values
    b = pt.loc[pt.hpv == "HPV-", col].values
    p = stats.mannwhitneyu(a, b, alternative="two-sided")[1]
    ax.set_xticks([0, 1])
    ax.set_xticklabels([f"HPV-\n{len(b)} tumours", f"HPV+\n{len(a)} tumours"])
    ax.set_ylabel(ylab); ax.set_title(title, loc="left"); ax.set_xlim(-0.55, 1.55)
    lo, hi = ax.get_ylim(); r = hi - lo
    ax.set_ylim(lo - 0.05 * r, hi + 0.16 * r)
    ax.text(0.5, 0.965, f"P = {p:.3g}", transform=ax.transAxes,
            ha="center", va="top", fontsize=6.5)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
