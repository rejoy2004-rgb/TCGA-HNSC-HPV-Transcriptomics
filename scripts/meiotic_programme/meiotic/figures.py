"""Figure builders for the provenance panel, the three bulk figures and the GSE181919 figure."""
from __future__ import annotations

from .config import *  # noqa: F401,F403
from .helpers import *  # noqa: F401,F403

# ============================================================================
# FIGURES
# ============================================================================

def make_provenance_figure(prov, percat, top20, overlap, outdir):
    """Figure 1: the unbiased origin of the meiotic hypothesis."""
    log("rendering provenance figure")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "font.family": "sans-serif", "font.size": 8, "axes.labelsize": 8,
        "axes.titlesize": 8, "xtick.labelsize": 7, "ytick.labelsize": 7,
        "axes.spines.top": False, "axes.spines.right": False,
        "figure.dpi": 110, "savefig.bbox": "tight",
    })

    CORE, GREY, ALARM = "#1f6fb4", "#b9c2cb", "#c1443c"
    fig = plt.figure(figsize=(11.6, 3.5))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.20, 0.92, 0.92], wspace=0.42)
    axA, axB, axC = (fig.add_subplot(gs[i]) for i in range(3))

    tp = top20.iloc[::-1].reset_index(drop=True)
    y = np.arange(len(tp)); cols = [CORE if m else GREY for m in tp.meiotic]
    axA.hlines(y, 2.0, tp.NES, color=cols, lw=1.0, alpha=.75)
    axA.scatter(tp.NES, y, s=26, color=cols, zorder=3)
    axA.set_yticks(y)
    axA.set_yticklabels([d if len(d) <= 42 else d[:40] + "\u2026" for d in tp.Description], fontsize=6)
    axA.set_xlim(2.0, 3.02); axA.margins(y=0.03)
    axA.set_xlabel("GSEA normalised enrichment score"); axA.xaxis.labelpad = 6
    axA.set_title("Meiosis dominates the original\nHPV+ enrichment ranking", loc="left")
    axA.text(0.97, 0.06, f"blue = meiosis-related\n({prov['gsea_meio_top5']} of the top 5)",
             transform=axA.transAxes, ha="right", va="bottom", fontsize=6, color=CORE)

    pc = percat.sort_values("fold").reset_index(drop=True)
    lab = [c.replace("Cancer-testis antigen (MAGE/CTAG)", "Cancer-testis antigen\n(MAGE/CTAG)")
           for c in pc.category]
    y2 = np.arange(len(pc))
    cb = [ALARM if "Cancer-testis" in c else CORE for c in pc.category]
    axB.vlines(1.0, -0.6, len(pc) - 0.4, color="0.35", lw=0.8, ls=(0, (4, 3)))
    axB.hlines(y2, 1.0, pc.fold, color=cb, lw=1.1, alpha=.75)
    axB.scatter(pc.fold, y2, s=30, color=cb, zorder=3)
    for yy, f in zip(y2, pc.fold):
        axB.annotate(f"{f:.1f}x", (f, yy), xytext=(4, 0) if f >= 1 else (3, 8), textcoords="offset points",
                     va="center", ha="left" if f >= 1 else "center", fontsize=6)
    axB.set_yticks(y2); axB.set_yticklabels(lab, fontsize=6)
    axB.set_xlim(0, 4.5); axB.margins(y=0.05)
    axB.set_xlabel("Fold enrichment\n(upregulated DEGs)"); axB.xaxis.labelpad = 6
    axB.set_title("The specificity was already\nvisible in the DEG list", loc="left")
    axB.text(0.99, 0.01, "dashed = 1x", transform=axB.transAxes,
             ha="right", va="bottom", fontsize=6, color="0.35")

    x = np.arange(2); w = 0.34
    obs = overlap.hits.tolist(); exp = overlap.expected.tolist()
    axC.bar(x - w/2, exp, w, color=GREY, label="expected by chance")
    axC.bar(x + w/2, obs, w, color=CORE, label="observed")
    for xi, (o, e) in enumerate(zip(obs, exp)):
        axC.annotate(f"{o/e:.1f}x\np={overlap.hyper_p.iloc[xi]:.0e}", (xi + w/2, o),
                     xytext=(0, 3), textcoords="offset points", ha="center",
                     va="bottom", fontsize=6)
    axC.set_xticks(x)
    axC.set_xticklabels([f"padj<0.05\n({overlap.selected.iloc[0]:,} genes)",
                         f"padj<1e-10,\n|log2FC|>1\n({overlap.selected.iloc[1]} genes)"], fontsize=6)
    axC.set_ylabel("Panel genes in DEG set"); axC.yaxis.labelpad = 4
    axC.set_ylim(0, max(obs) * 1.55)
    axC.set_title("Panel overlaps the DEG list\nfar beyond chance", loc="left")
    axC.legend(frameon=False, fontsize=6, loc="upper left")

    for ax, L in ((axA, "a"), (axB, "b"), (axC, "c")):
        ax.text(-0.10, 1.06, L, transform=ax.transAxes, fontsize=9, fontweight="bold", va="bottom")
    fig.subplots_adjust(left=0.16, right=0.995, bottom=0.20, top=0.84)
    fig.savefig(outdir / "fig0_provenance.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    return outdir / "fig0_provenance.png"



def make_figures(val: dict, disc: dict, rep: dict, outdir: Path) -> None:
    log("rendering figures")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "font.family": "sans-serif", "font.size": 8, "axes.labelsize": 8,
        "axes.titlesize": 8, "xtick.labelsize": 7, "ytick.labelsize": 7,
        "axes.spines.top": False, "axes.spines.right": False,
        "figure.dpi": 110, "savefig.bbox": "tight",
    })
    GREY, BLUE, RED, ORANGE, PALE = "#6b7280", "#0369a1", "#c53030", "#dd8b3f", "#cbd5e1"
    gz, grp, score, core = val["gz"], val["groups"], val["score"], val["core"]
    A, S, N = "HPV+ active", "HPV+ silent", "HPV-"

    # ---- Figure 1: activation + specificity ----
    fig, axes = plt.subplots(1, 3, figsize=(12.6, 3.9))
    ax = axes[0]
    rng = np.random.default_rng(RANDOM_SEED)
    for i, (g, lab, c) in enumerate([(A, "HPV+\nvirus active", RED),
                                     (S, "HPV+\nvirus silent", ORANGE),
                                     (N, "HPV-", BLUE)]):
        v = score[grp == g].values
        ax.scatter(i + rng.uniform(-.17, .17, len(v)), v, s=13, c=c, alpha=.72,
                   lw=.25, edgecolor="white", zorder=3)
        ax.plot([i - .29, i + .29], [np.median(v)] * 2, lw=2.0, color="black", zorder=4)
    ax.set_xticks(range(3))
    ax.set_xticklabels(["HPV+\nvirus active", "HPV+\nvirus silent", "HPV-"], fontsize=7)
    ax.set_ylabel("Meiotic core score (mean z)")
    ax.axhline(0, lw=.6, ls=":", color=GREY)
    ax.set_title("The meiotic program switches on only when\nthe virus is transcribing", loc="left")
    yb = score.max()
    for (i, j), p, dy in [((0, 2), val["p_active_vs_neg"], .30),
                          ((0, 1), val["p_active_vs_silent"], .12),
                          ((1, 2), val["p_silent_vs_neg"], .0)]:
        yy = yb + (dy + .14) * abs(yb)
        ax.plot([i, i, j, j], [yy - .06 * abs(yb), yy, yy, yy - .06 * abs(yb)], lw=.7, color="black")
        ax.text((i + j) / 2, yy + .02 * abs(yb),
                "n.s." if p > .05 else f"p = {p:.0e}", ha="center", fontsize=6.2)
    ax.margins(y=.10)
    ax.text(-.16, 1.06, "a", transform=ax.transAxes, fontweight="bold", fontsize=10)

    ax = axes[1]
    pg = val["per_gene"].dropna(subset=["AUC"]).sort_values("AUC").tail(14)
    iscta = pg.category.str.contains("Cancer-testis")
    yy = np.arange(len(pg))
    ax.hlines(yy, .5, pg.AUC, color=GREY, lw=.8)
    ax.scatter(pg.AUC, yy, s=40, c=np.where(iscta, PALE, BLUE), lw=.5, edgecolor="white", zorder=3)
    ax.axvline(.5, lw=.8, ls="--", color="black")
    ax.set_yticks(yy)
    ax.set_yticklabels(pg.gene, fontsize=6.2, style="italic")
    ax.set_xlabel("AUC, virus-active HPV+ vs HPV-")
    ax.set_xlim(.45, 1.12); ax.set_xticks([.5, .6, .7, .8, .9, 1.0])
    ax.set_title("Meiotic machinery genes discriminate;\nclassic cancer-testis antigens do not", loc="left")
    ax.text(.985, .05, "grey = classic CTA\ndashed = chance", transform=ax.transAxes,
            ha="right", fontsize=6, color=GREY, linespacing=1.5)
    ax.margins(y=.045)
    ax.text(-.16, 1.06, "b", transform=ax.transAxes, fontweight="bold", fontsize=10)

    ax = axes[2]
    cd = val["categories"].sort_values("AUC")
    cols = [PALE if "Cancer-testis" in c else BLUE for c in cd.category]
    ax.hlines(np.arange(len(cd)), .5, cd.AUC, color=GREY, lw=.8)
    ax.scatter(cd.AUC, np.arange(len(cd)), s=52, c=cols, lw=.5, edgecolor="white", zorder=3)
    for i, a in enumerate(cd.AUC):
        ax.annotate(f"{a:.2f}", (a, i), xytext=(0, 7), textcoords="offset points",
                    ha="center", fontsize=6.1)
    ax.axvline(.5, lw=.8, ls="--", color="black")
    ax.set_yticks(np.arange(len(cd)))
    ax.set_yticklabels([f"{c}  (n={n})" for c, n in zip(cd.category, cd.n_genes)], fontsize=6.3)
    ax.set_xlabel("AUC, virus-active HPV+ vs HPV-")
    ax.set_xlim(.36, 1.0)
    ax.set_title("Specificity is confined to the meiotic\nmachinery, not testis antigens generally", loc="left")
    ax.margins(y=.09)
    ax.text(-.16, 1.06, "c", transform=ax.transAxes, fontweight="bold", fontsize=10)
    fig.tight_layout()
    fig.savefig(outdir / "fig1_activation.png", dpi=300)
    plt.close(fig)

    # ---- Figure 2: methylation mechanism ----
    mt, mg = disc["meth_table"], rep["cross"]
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.1))
    ax = axes[0]
    d = mt.dropna(subset=["delta_beta"]).sort_values("delta_beta").head(16)
    y = np.arange(len(d))
    ax.barh(y, d.delta_beta, height=.66,
            color=np.where(d.padj_meth < .05, BLUE, PALE), edgecolor="white", lw=.4)
    ax.axvline(0, lw=.7, color="black")
    ax.set_yticks(y)
    ax.set_yticklabels(d.gene, fontsize=6.2, style="italic")
    ax.set_xlabel("delta promoter methylation (HPV+ - HPV-)")
    ax.set_title(f"HPV+ tumours are hypomethylated at meiotic loci\n"
                 f"(TCGA, n={disc['n_mpos'] + disc['n_mneg']}; blue = FDR<0.05)", loc="left")
    ax.invert_yaxis()
    ax.text(-.16, 1.06, "a", transform=ax.transAxes, fontweight="bold", fontsize=10)

    ax = axes[1]
    mm2 = mt.dropna(subset=["rho_meth_expr", "delta_beta"])
    ax.scatter(mm2.delta_beta, mm2.rho_meth_expr, s=22,
               c=np.where(mm2.padj_meth < .05, BLUE, PALE), lw=.3, edgecolor="white", zorder=3)
    ax.axhline(0, lw=.6, color=GREY, ls=":")
    ax.axvline(0, lw=.6, color=GREY, ls=":")
    for _, r in mm2[mm2.gene.isin(CORE6)].iterrows():
        ax.annotate(r.gene, (r.delta_beta, r.rho_meth_expr), fontsize=5.9, style="italic",
                    xytext={"SYCE2": (4, 6), "SYCP2": (4, -12), "STAG3": (-32, 4)}.get(r.gene, (3.5, 3)),
                    textcoords="offset points", color="#0c4a6e")
    ax.set_xlabel("delta promoter methylation (HPV+ - HPV-)")
    ax.set_ylabel("Spearman rho\n(methylation vs expression)")
    ax.set_title(f"Hypomethylation tracks transcriptional activation\n"
                 f"({disc['n_neg_rho']} of {disc['n_hypo']} FDR-significant genes show rho < 0)",
                 loc="left")
    ax.text(-.16, 1.06, "b", transform=ax.transAxes, fontweight="bold", fontsize=10)

    ax = axes[2]
    ok = mg.dropna(subset=["delta_TCGA", "delta_GSE38266"])
    ts = ok.padj_meth < .05
    ax.scatter(ok.loc[~ts, "delta_TCGA"], ok.loc[~ts, "delta_GSE38266"], s=18,
               c=PALE, lw=.3, edgecolor="white")
    ax.scatter(ok.loc[ts, "delta_TCGA"], ok.loc[ts, "delta_GSE38266"], s=26,
               c=BLUE, lw=.3, edgecolor="white", zorder=3)
    lim = (-.55, .12)
    ax.plot(lim, lim, lw=.6, ls="--", color=GREY)
    ax.axhline(0, lw=.6, color=GREY, ls=":")
    ax.axvline(0, lw=.6, color=GREY, ls=":")
    offs = {"MEI1": (5, -2), "RAD9B": (-6, -6), "SMC1B": (5, 4), "STAG3": (5, -6), "SYCP2": (5, -3)}
    for _, r in ok[ok.gene.isin(offs)].iterrows():
        ax.annotate(r.gene, (r.delta_TCGA, r.delta_GSE38266), fontsize=5.9, style="italic",
                    xytext=offs[r.gene], textcoords="offset points", color="#0c4a6e",
                    ha="right" if r.gene == "RAD9B" else "left")
    ax.text(.04, .93, f"rho = {rep['cross_rho']:.2f}, p = {rep['cross_p']:.0e}\n"
                      f"set-level p = {rep['set_p']:.1e}",
            transform=ax.transAxes, fontsize=6.3, va="top",
            bbox=dict(fc="white", ec="none", alpha=.85, pad=2.2))
    ax.set_xlabel(f"delta methylation, TCGA (n={disc['n_mpos'] + disc['n_mneg']})")
    ax.set_ylabel(f"delta methylation, GSE38266 (n={rep['n_pos'] + rep['n_neg']})")
    ax.set_xlim(lim)
    ax.set_ylim(lim)
    ax.set_title(f"Replicates in an independent HM450 cohort\n"
                 f"({rep['n_pos']} HPV+ vs {rep['n_neg']} HPV-, all oropharyngeal)", loc="left")
    ax.text(-.16, 1.06, "c", transform=ax.transAxes, fontweight="bold", fontsize=10)
    fig.tight_layout()
    fig.savefig(outdir / "fig2_methylation.png", dpi=300)
    plt.close(fig)

    # ---- Figure 3: coordination ----
    fig, axes = plt.subplots(1, 3, figsize=(12.6, 3.9))
    ax = axes[0]
    coh = val["coherence"]
    mods = ["core meiotic", "all meiotic", "classic CTA"]
    MC = {"core meiotic": BLUE, "all meiotic": "#7ea8c4", "classic CTA": PALE}
    x = np.arange(3)
    w = .26
    for k, m in enumerate(mods):
        vals = [coh[(coh.group == g) & (coh.module == m)].mean_rho.iloc[0] for g in [A, S, N]]
        ax.bar(x + (k - 1) * w, vals, w, color=MC[m], edgecolor="white", lw=.5, label=m, zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(["HPV+\nactive", "HPV+\nsilent", "HPV-"], fontsize=7)
    ax.set_ylabel("Mean pairwise correlation (rho)")
    ax.axhline(0, lw=.6, color="black")
    ax.legend(frameon=False, fontsize=6.2, loc="upper right", handlelength=1.1)
    ax.set_title("The core meiotic genes move as one module;\nclassic CTAs never do", loc="left")
    ax.text(-.16, 1.06, "a", transform=ax.transAxes, fontweight="bold", fontsize=10)

    for k, (gname, lab, letter) in enumerate([(A, f"Virus-active HPV+ (n={val['n_active']}):\ntightly co-expressed", "b"),
                                              (N, f"HPV- (n={val['n_neg']}):\nno module", "c")]):
        axk = axes[k + 1]
        C = gz.loc[core, grp[grp == gname].index].T.corr(method="spearman")
        im = axk.imshow(C.values, vmin=-1, vmax=1, cmap="RdBu_r")
        axk.set_xticks(range(len(core)))
        axk.set_xticklabels(core, rotation=45, ha="right", fontsize=6.2, style="italic")
        axk.set_yticks(range(len(core)))
        axk.set_yticklabels(core, fontsize=6.2, style="italic")
        for i in range(len(core)):
            for j in range(len(core)):
                v = C.values[i, j]
                axk.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=5.4,
                         color="white" if abs(v) > .6 else "black")
        axk.set_title(lab, loc="left")
        axk.text(-.16, 1.06, letter, transform=axk.transAxes, fontweight="bold", fontsize=10)
    cb = fig.colorbar(im, ax=[axes[1], axes[2]], fraction=.022, pad=.02)
    cb.set_label("Spearman rho (0 = independent)", fontsize=6.5)
    cb.set_ticks([-1, -.5, 0, .5, 1])
    cb.ax.tick_params(labelsize=6)
    fig.savefig(outdir / "fig3_coordination.png", dpi=300)
    plt.close(fig)
    log("  wrote fig1_activation.png, fig2_methylation.png, fig3_coordination.png")


# ---------------------------------------------------------------------------
# single-cell figures
# ---------------------------------------------------------------------------

def make_singlecell_figures(scores, qct, hpvc, pt, pbm, pg, mm, summary, outdir):
    """Main single-cell figure (5 panels) plus the cell-type QC supplement."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    GREY, BLUE, RED, ORANGE, PALE = "#6b7280", "#0369a1", "#c53030", "#dd8b3f", "#cbd5e1"
    POS, NEG = RED, BLUE                       # HPV+ red, HPV- blue, matching fig3

    def frame(ax):
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.tick_params(length=2.4, width=0.6)

    def letter(ax, ch):
        ax.text(-0.16, 1.10, ch, transform=ax.transAxes, fontsize=10,
                fontweight="bold", va="top", ha="left")

    plt.rcParams.update({"font.size": 7, "axes.titlesize": 7, "axes.labelsize": 7,
                         "xtick.labelsize": 6, "ytick.labelsize": 6,
                         "axes.linewidth": 0.7, "figure.dpi": 300,
                         "font.family": "DejaVu Sans"})
    lab = lambda c: c.replace(".cells", "").replace("_", "/")
    mal = scores[scores["cell.type"] == "Malignant.cells"]

    fig = plt.figure(figsize=(11.6, 7.4))
    gs = fig.add_gridspec(2, 3, height_ratios=[1, 0.92],
                          width_ratios=[1.30, 0.80, 1.05], hspace=0.46, wspace=0.40)
    ax_a, ax_b, ax_c = (fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]),
                        fig.add_subplot(gs[0, 2]))
    ax_d, ax_e = fig.add_subplot(gs[1, 0:2]), fig.add_subplot(gs[1, 2])

    # (a) HPV effect per cell type
    d = hpvc.sort_values("delta", ascending=False).set_index("cell_type")
    yv = np.arange(len(d))
    ax_a.axvline(0, color="#94a3b8", lw=0.7, zorder=1)
    ax_a.barh(yv, d.delta, height=0.66, zorder=2,
              color=[RED if c == "Malignant.cells" else PALE for c in d.index])
    ax_a.set_yticks(yv)
    ax_a.set_yticklabels([lab(c) for c in d.index])
    ax_a.invert_yaxis()
    ax_a.set_xlabel("\u0394 meiotic score (HPV+ \u2212 HPV\u2212)")
    ax_a.set_title("The HPV effect is confined to\nthe malignant compartment", loc="left")
    for i, (v, au) in enumerate(zip(d.delta, d.auc)):
        ax_a.text(max(v, 0) + 0.005, i, f"{v:+.3f} (AUC {au:.2f})", va="center",
                  ha="left", fontsize=5.8,
                  color="#7f1d1d" if d.index[i] == "Malignant.cells" else "#475569")
    ax_a.set_xlim(-0.03, 0.20)
    frame(ax_a)

    # (b) malignant-cell score distributions
    mn_ = mal[mal.hpv == "HPV-"].score_core
    mp_ = mal[mal.hpv == "HPV+"].score_core
    parts = ax_b.violinplot([mn_, mp_], positions=[0, 1], showextrema=False, widths=0.78)
    for pc, c in zip(parts["bodies"], [NEG, POS]):
        pc.set_facecolor(c); pc.set_alpha(0.55)
        pc.set_edgecolor(c); pc.set_linewidth(0.7)
    for i, s in enumerate([mn_, mp_]):
        ax_b.hlines(s.median(), i - 0.20, i + 0.20, color="#1a1a1a", lw=1.1, zorder=3)
    ax_b.axhline(0, color="#94a3b8", lw=0.6, ls=":", zorder=1)
    ax_b.set_xticks([0, 1])
    ax_b.set_xticklabels([f"HPV\u2212\nn={len(mn_):,}", f"HPV+\nn={len(mp_):,}"])
    ax_b.set_ylabel("meiotic module score")
    ax_b.set_title("Malignant cells only", loc="left")
    ax_b.text(0.5, 0.965, f"AUC {summary['mal_auc']:.2f}", transform=ax_b.transAxes,
              ha="center", va="top", fontsize=6.5, color="#1a1a1a")
    frame(ax_b)

    # (c) per-patient pseudobulk - independent of the scoring method
    pbm2 = pbm.sort_values(["hpv", "log_core"])
    xs = {"HPV-": 0, "HPV+": 1}
    rng = np.random.default_rng(RANDOM_SEED)
    for _, r in pbm2.iterrows():
        ax_c.scatter(xs[r.hpv] + rng.uniform(-0.13, 0.13), r.log_core,
                     s=float(np.clip(r.n_cells / 14, 9, 78)),
                     color=POS if r.hpv == "HPV+" else NEG, alpha=0.82,
                     edgecolor="white", linewidth=0.5, zorder=3)
    for h, xx in xs.items():
        v = pbm2[pbm2.hpv == h].log_core
        ax_c.hlines(v.median(), xx - 0.26, xx + 0.26, color="#1a1a1a", lw=1.2, zorder=4)
    n_neg = int((pbm2.hpv == "HPV-").sum())
    n_pos = int((pbm2.hpv == "HPV+").sum())
    ax_c.set_xticks([0, 1])
    ax_c.set_xticklabels([f"HPV\u2212\n{n_neg} tumours", f"HPV+\n{n_pos} tumours"])
    ax_c.set_ylabel("core meiotic log$_2$(CPM+1)")
    ax_c.set_title(f"All {n_pos} HPV+ tumours exceed\nall {n_neg} HPV\u2212 tumours",
                   loc="left")
    ax_c.set_xlim(-0.5, 1.5)
    ax_c.margins(y=0.22)
    ax_c.text(0.5, 0.03,
              f"{summary['pb_core_fold']:.1f}\u00d7 \u00b7 P = {summary['pb_core_p']:.1e}",
              transform=ax_c.transAxes, ha="center", fontsize=6.2)
    frame(ax_c)

    # (d) per-gene detection rates, HPV+ vs HPV- malignant cells
    sel = pg[pg.category.isin(MEIOTIC_CATS + [CTA_CAT])].copy()
    sel["is_cta"] = sel.category == CTA_CAT
    sel["in_core"] = sel.gene.isin(CORE6)
    ax_d.plot([0, 0.42], [0, 0.42], color="#94a3b8", lw=0.7, ls="--", zorder=1)
    for sub, c, mk, lb2 in [(sel[~sel.is_cta], BLUE, "o", "meiotic"),
                            (sel[sel.is_cta], ORANGE, "s", "classic CTA")]:
        ax_d.scatter(sub.det_neg_malig, sub.det_pos_malig, s=17, color=c, marker=mk,
                     alpha=0.72, edgecolor="white", linewidth=0.4, zorder=3, label=lb2)
    core_pts = sel[sel.in_core]
    ax_d.scatter(core_pts.det_neg_malig, core_pts.det_pos_malig, s=44, facecolor="none",
                 edgecolor=RED, linewidth=1.1, zorder=4, label="core meiotic")
    offs = {"SYCP2": (7, -6), "SMC1B": (7, 2), "STAG3": (7, -2),
            "MEI1": (7, 0), "SYCE2": (7, 1)}
    for _, r in core_pts.iterrows():
        ax_d.annotate(f"$\\it{{{r.gene}}}$", (r.det_neg_malig, r.det_pos_malig),
                      xytext=offs.get(r.gene, (7, 0)), textcoords="offset points",
                      fontsize=6, color="#7f1d1d", va="center")
    ax_d.set_xlabel("detection rate, HPV\u2212 malignant cells")
    ax_d.set_ylabel("detection rate, HPV+ malignant cells")
    ax_d.set_title("Meiotic genes are detected in a far larger fraction of HPV+ "
                   "tumour cells;\nclassic cancer\u2013testis antigens are not", loc="left")
    ax_d.legend(frameon=False, fontsize=6, loc="lower right", handletextpad=0.4,
                borderpad=0.2, bbox_to_anchor=(1.0, 0.02))
    ax_d.set_xlim(-0.012, 0.30)
    ax_d.set_ylim(-0.015, 0.42)
    frame(ax_d)

    # (e) module comparison - meiotic vs generic germline de-repression
    cmp_df = pd.read_csv(outdir / "sc_module_comparison.csv").set_index("module")
    mods = ["core", "meiotic", "cta"]
    nice = {m: f"{n}\n({int(cmp_df.loc[m, 'n_genes'])} genes)"
            for m, n in zip(mods, ["core meiotic", "all meiotic", "classic CTA"])}
    xv = np.arange(len(mods))
    vals = [float(cmp_df.loc[m, "cell_mean_pos"] - cmp_df.loc[m, "cell_mean_neg"])
            for m in mods]
    ax_e.axhline(0, color="#94a3b8", lw=0.7)
    ax_e.bar(xv, vals, color=[RED, "#7ea8c4", PALE], width=0.62)
    ax_e.set_xticks(xv)
    ax_e.set_xticklabels([nice[m] for m in mods])
    ax_e.set_ylabel("\u0394 score in malignant cells\n(HPV+ \u2212 HPV\u2212)")
    ax_e.set_title("The contrast is meiotic,\nnot generic germline de-repression",
                   loc="left")
    for i, (m, v) in enumerate(zip(mods, vals)):
        pv = float(cmp_df.loc[m, "pt_p"])
        txt = "n.s." if pv > 0.05 else f"P = {pv:.1e}".replace("e-0", "e\u2212")
        ax_e.text(i, v + (0.004 if v >= 0 else -0.008), txt, ha="center",
                  va="bottom" if v >= 0 else "top", fontsize=6)
    ax_e.margins(y=0.26)
    frame(ax_e)

    for ax, ch in [(ax_a, "a"), (ax_b, "b"), (ax_c, "c"), (ax_d, "d"), (ax_e, "e")]:
        letter(ax, ch)
    fig.savefig(outdir / "fig4_singlecell.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # --- supplementary: cell-type QC --------------------------------------
    mk_flat = [g for v in SC_MARKERS.values() for g in v]
    order = qct.cell_type.tolist()
    figs = plt.figure(figsize=(11.5, 4.8))
    gss = figs.add_gridspec(2, 2, height_ratios=[1, 0.045],
                            width_ratios=[2.05, 1], hspace=0.32, wspace=0.30)
    axA, axB, axcb = (figs.add_subplot(gss[0, 0]), figs.add_subplot(gss[0, 1]),
                      figs.add_subplot(gss[1, 0]))
    hm = pd.DataFrame(
        {ct: [float(scores.loc[scores["cell.type"] == ct].shape[0])] for ct in order})
    # marker means recomputed from the QC table (mean in-group per cell type)
    im = axA.imshow(np.vstack([qct.set_index("cell_type").loc[order, "marker_mean_in"],
                               qct.set_index("cell_type").loc[order, "marker_mean_out"]]),
                    cmap="Blues", aspect="auto", vmin=0)
    axA.set_yticks([0, 1])
    axA.set_yticklabels(["own markers", "other cells"])
    axA.set_xticks(range(len(order)))
    axA.set_xticklabels([lab(c) for c in order], rotation=35, ha="right")
    axA.set_title("Published labels reproduce canonical lineage markers", loc="left")
    cb = figs.colorbar(im, cax=axcb, orientation="horizontal")
    cb.set_label("mean log-normalised expression", fontsize=6)
    cb.ax.tick_params(labelsize=5.5)

    axB.barh(np.arange(len(order)), qct.set_index("cell_type").loc[order, "enrichment"],
             color=[RED if c == "Malignant.cells" else PALE for c in order], height=0.66)
    axB.set_yticks(np.arange(len(order)))
    axB.set_yticklabels([lab(c) for c in order])
    axB.invert_yaxis()
    axB.set_xscale("log")
    axB.set_xlabel("marker enrichment (in / out), log scale")
    axB.set_title("Every label confirmed independently", loc="left")
    axB.margins(x=0.26)
    frame(axB)
    for ax, ch in [(axA, "a"), (axB, "b")]:
        letter(ax, ch)
    figs.savefig(outdir / "figS1_sc_qc.png", dpi=300, bbox_inches="tight")
    plt.close(figs)
