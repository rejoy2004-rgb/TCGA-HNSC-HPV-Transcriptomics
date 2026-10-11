"""Origin of the meiotic hypothesis: GSEA ranking, panel-category enrichment and
hypergeometric panel/DEG overlap, re-tested on the frozen DESeq2/GSEA/GO outputs."""
from __future__ import annotations

from .config import *  # noqa: F401,F403
from .helpers import *  # noqa: F401,F403

def analysis_provenance(cachedir, panel_genes):
    """Re-test the pre-existing DEG/GO/GSEA output against the final panel.

    Returns (summary dict, per-category frame, gsea top-20 frame, overlap frame).
    Requires the three files in PROV_FILES to be present in `cachedir`; these
    ship with the replication archive rather than being downloaded.
    """
    cachedir = Path(cachedir)
    missing = [f for f in PROV_FILES.values() if not (cachedir / f).exists()]
    if missing:
        print("  provenance inputs absent, skipping:", ", ".join(missing))
        return None, None, None, None

    gsea = pd.read_csv(cachedir / PROV_FILES["gsea"])
    gou  = pd.read_csv(cachedir / PROV_FILES["go_up"])
    deg  = pd.read_csv(cachedir / PROV_FILES["deg"])

    # --- GSEA: how high do meiosis terms rank among positively enriched terms?
    gp = (gsea[(gsea["p.adjust"] < 0.05) & (gsea.NES > 0)]
          .sort_values("NES", ascending=False).reset_index(drop=True))
    gp["meiotic"] = gp.Description.str.contains(MEIO_RE)
    top20 = (gp.head(20)[["ID", "Description", "NES", "p.adjust", "meiotic"]]
               .rename(columns={"p.adjust": "padj"}))

    # --- GO over-representation on upregulated genes
    gou = gou.copy()
    gou["meiotic"] = gou.Description.str.contains(MEIO_RE)
    gs = gou[gou["p.adjust"] < 0.05].sort_values("p.adjust").reset_index(drop=True)

    # --- hypergeometric overlap of the panel with the DEG output
    d = deg.dropna(subset=["SYMBOL", "padj"]).drop_duplicates("SYMBOL")
    universe = set(d.SYMBOL)
    panel_u = set(panel_genes) & universe
    S_loose = set(d[(d.padj < 0.05) & (d.log2FoldChange > 0)].SYMBOL)
    S_str   = set(d[(d.padj < 1e-10) & (d.log2FoldChange > 1)].SYMBOL)

    rows = []
    for label, S in [("Loose (padj<0.05, log2FC>0)", S_loose),
                     ("Stringent (padj<1e-10, log2FC>1)", S_str)]:
        k, M, n, N = len(panel_u & S), len(universe), len(panel_u), len(S)
        exp = n * N / M
        rows.append(dict(threshold=label, universe=M, selected=N, set_size=n, hits=k,
                         expected=round(exp, 2), fold=round(k / exp, 2),
                         hyper_p=hypergeom.sf(k - 1, M, n, N)))
    overlap = pd.DataFrame(rows)
    o = overlap.threshold.map(ORIG_PROV)
    for c in ("wt_selected", "wt_hits", "wt_testable", "wt_fold"):
        overlap[c] = [r[c] for r in o]
    overlap["fold_ratio"] = (overlap.fold / overlap.wt_fold).round(2)

    # --- per-category: is the CTA comparator enriched too? It must not be.
    cat = pd.DataFrame({"gene": sorted(panel_u)})
    g2c = {g: c for c, gs in GENE_SET.items() for g in gs}
    cat["category"] = cat.gene.map(g2c)
    cat["is_up"] = cat.gene.isin(S_loose)
    prows = []
    for c, sub in cat.groupby("category"):
        n, k = len(sub), int(sub.is_up.sum())
        exp = n * len(S_loose) / len(universe)
        prows.append(dict(category=c, n_testable=n, n_up=k, expected=round(exp, 2),
                          fold=round(k / exp, 2) if exp else np.nan,
                          hyper_p=hypergeom.sf(k - 1, len(universe), n, len(S_loose))))
    percat = pd.DataFrame(prows).sort_values("fold", ascending=False)
    percat["fdr"] = np.minimum(1.0, percat.hyper_p * len(percat))

    mei = cat[~cat.category.str.contains("Cancer-testis")]
    cta = cat[cat.category.str.contains("Cancer-testis")]
    or_, p_ = fisher_exact([[int(mei.is_up.sum()), len(mei) - int(mei.is_up.sum())],
                            [int(cta.is_up.sum()), len(cta) - int(cta.is_up.sum())]])

    summ = dict(
        gsea_n_pos=len(gp),
        gsea_meio_top5=int(gp.head(5).meiotic.sum()),
        gsea_meio_top10=int(gp.head(10).meiotic.sum()),
        gsea_top_meio_term=str(gp[gp.meiotic].Description.iloc[0]),
        gsea_top_meio_nes=float(gp[gp.meiotic].NES.iloc[0]),
        gsea_top_meio_padj=float(gp[gp.meiotic]["p.adjust"].iloc[0]),
        go_up_n_terms=len(gs), go_up_n_meio=int(gs.meiotic.sum()),
        go_up_top_meio=str(gs[gs.meiotic].Description.iloc[0]),
        go_up_top_meio_fold=float(gs[gs.meiotic].FoldEnrichment.iloc[0]),
        go_up_top_meio_padj=float(gs[gs.meiotic]["p.adjust"].iloc[0]),
        universe=len(universe), panel_testable=len(panel_u),
        wt_testable=int(overlap.wt_testable.iloc[0]),
        wt_loose_fold=float(overlap.wt_fold.iloc[0]),
        wt_str_fold=float(overlap.wt_fold.iloc[1]),
        panel_not_deg=len(panel_u - S_loose),
        loose_fold=float(overlap.fold.iloc[0]), loose_p=float(overlap.hyper_p.iloc[0]),
        loose_hits=int(overlap.hits.iloc[0]),
        str_hits=int(overlap.hits.iloc[1]),
        str_n_sel=int(overlap.selected.iloc[1]),
        str_fold=float(overlap.fold.iloc[1]), str_p=float(overlap.hyper_p.iloc[1]),
        mei_up=int(mei.is_up.sum()), mei_n=len(mei),
        cta_up=int(cta.is_up.sum()), cta_n=len(cta),
        mei_vs_cta_or=float(or_), mei_vs_cta_p=float(p_),
    )
    return summ, percat, top20, overlap
