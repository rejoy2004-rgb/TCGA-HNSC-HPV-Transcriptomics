"""GSE181919: malignant-cell localisation, mixed models, pseudobulk and detection rates."""
from __future__ import annotations

from .config import *  # noqa: F401,F403
from .helpers import *  # noqa: F401,F403
from .data_geo import *  # noqa: F401,F403
from .figures import *  # noqa: F401,F403


def analysis_singlecell(cache: Path, outdir: Path) -> dict | None:
    """Test whether the meiotic module is specific to malignant cells.

    Bulk cohorts cannot separate "tumour cells reactivate meiosis" from "HPV+
    tumours contain more of some meiosis-expressing minority population". This
    stage scores the module per cell in GSE181919 and asks where the HPV
    contrast lives.
    """
    try:
        import anndata as ad
        import scanpy as sc_
        import statsmodels.formula.api as smf
    except ImportError as exc:
        log(f"  single-cell stage skipped: {exc}")
        return None

    X, genes, meta = build_sc_matrix(cache)

    A = ad.AnnData(sp_sparse.csr_matrix(X.T.astype(np.float32)))
    A.var_names = pd.Index(genes).astype(str)
    A.var_names_make_unique()
    A.obs = meta.set_index("barcode")
    hcol = next(c for c in A.obs.columns if c.lower() == "hpv")
    A.obs["hpv"] = np.where(
        A.obs[hcol].astype(str).str.upper().str.replace(" ", "").str.startswith("HPV+"),
        "HPV+", "HPV-")
    counts = A.copy()                             # raw counts for detection rates
    A.obs["n_umi"] = np.asarray(counts.X.sum(1)).ravel().astype(int)
    A.obs["n_genes"] = np.asarray((counts.X > 0).sum(1)).ravel().astype(int)
    sc_.pp.normalize_total(A, target_sum=1e4)
    sc_.pp.log1p(A)

    # --- re-verify the published labels against canonical markers -----------
    qc_rows = []
    for ct, mk in SC_MARKERS.items():
        mk = [g for g in mk if g in A.var_names]
        if not mk or (A.obs["cell.type"] == ct).sum() == 0:
            continue
        inm = A.obs["cell.type"].values == ct
        vals = np.asarray(A[:, mk].X.todense()).mean(1)
        a, b = vals[inm].mean(), vals[~inm].mean()
        qc_rows.append(dict(cell_type=ct, n_cells=int(inm.sum()),
                            marker_mean_in=round(float(a), 4),
                            marker_mean_out=round(float(b), 4),
                            enrichment=round(float(a / b) if b > 0 else np.inf, 1),
                            median_umi=int(np.median(A.obs.n_umi[inm])),
                            median_genes=int(np.median(A.obs.n_genes[inm])),
                            label_confirmed=bool(a > b)))
    qct = pd.DataFrame(qc_rows)
    qct.to_csv(outdir / "sc_qc_celltypes.csv", index=False)
    assert qct.label_confirmed.all(), "a published cell-type label failed marker check"

    # --- module scores per cell (Tirosh control-binned) ---------------------
    present = set(A.var_names)
    panel = panel_frame()
    sets = {
        "core": [g for g in CORE6 if g in present],
        "meiotic": [g for g in panel.loc[panel.category.isin(MEIOTIC_CATS), "gene"]
                    if g in present],
        "cta": [g for g in panel.loc[panel.category == CTA_CAT, "gene"] if g in present],
        "germline": [g for g in panel.loc[panel.category.isin(GERMLINE_CATS), "gene"]
                     if g in present],
    }
    for k, v in sets.items():
        sc_.tl.score_genes(A, v, score_name=f"score_{k}", ctrl_size=SC_CTRL_SIZE,
                           n_bins=SC_N_BINS, ctrl_as_ref=True, random_state=RANDOM_SEED,
                           use_raw=False)
    scores = A.obs[["patient.id", "hpv", "cell.type", "subsite", "n_umi", "n_genes"]
                   + [f"score_{k}" for k in sets]].copy()
    scores.to_csv(outdir / "sc_cell_scores.csv")

    # --- HPV contrast within each cell type ---------------------------------
    rows = []
    for ct, sub in scores.groupby("cell.type"):
        a = sub.loc[sub.hpv == "HPV+", "score_core"].values
        b = sub.loc[sub.hpv == "HPV-", "score_core"].values
        if len(a) < 10 or len(b) < 10:
            continue
        U, p = stats.mannwhitneyu(a, b, alternative="two-sided")
        rows.append(dict(cell_type=ct, n_hpv_pos=len(a), n_hpv_neg=len(b),
                         mean_pos=round(float(a.mean()), 4),
                         mean_neg=round(float(b.mean()), 4),
                         delta=round(float(a.mean() - b.mean()), 4),
                         auc=round(float(U / (len(a) * len(b))), 3), p=p))
    hpvc = pd.DataFrame(rows).sort_values("delta", ascending=False)
    hpvc.to_csv(outdir / "sc_hpv_contrast.csv", index=False)

    mal = scores[scores["cell.type"] == "Malignant.cells"]
    mrow = hpvc[hpvc.cell_type == "Malignant.cells"].iloc[0]
    nonmal = hpvc[hpvc.cell_type != "Malignant.cells"]

    # --- module comparison within malignant cells ---------------------------
    mrows = []
    for k in sets:
        a = mal.loc[mal.hpv == "HPV+", f"score_{k}"].values
        b = mal.loc[mal.hpv == "HPV-", f"score_{k}"].values
        U, p = stats.mannwhitneyu(a, b, alternative="two-sided")
        # Patient-level repeat: cells within a tumour are not independent, so the
        # cell-level P is pseudoreplicated. One value per tumour, one-sided.
        ppt = mal.groupby(["patient.id", "hpv"])[f"score_{k}"].mean().reset_index()
        pa_, pb2 = (ppt.loc[ppt.hpv == "HPV+", f"score_{k}"].values,
                    ppt.loc[ppt.hpv == "HPV-", f"score_{k}"].values)
        _, ppv = stats.mannwhitneyu(pa_, pb2, alternative="greater")
        mrows.append(dict(module=k, n_genes=len(sets[k]),
                          cell_mean_pos=round(float(a.mean()), 4),
                          cell_mean_neg=round(float(b.mean()), 4),
                          delta=round(float(a.mean() - b.mean()), 4),
                          cell_auc=round(float(U / (len(a) * len(b))), 3), cell_p=p,
                          pt_mean_pos=round(float(pa_.mean()), 4),
                          pt_mean_neg=round(float(pb2.mean()), 4),
                          pt_p_onesided=round(float(ppv), 6),
                          pts_pos_above_zero=f"{int((pa_ > 0).sum())}/{len(pa_)}"))
    pd.DataFrame(mrows).to_csv(outdir / "sc_module_comparison.csv", index=False)

    # --- mixed models: patient as random effect, depth as covariate ---------
    md = mal[["score_core", "hpv", "patient.id", "n_genes"]].copy()
    md["hpv_pos"] = (md.hpv == "HPV+").astype(int)
    md["log_genes"] = np.log10(md.n_genes)
    m1 = smf.mixedlm("score_core ~ hpv_pos + log_genes", md,
                     groups=md["patient.id"]).fit()
    alld = scores.copy()
    alld["hpv_pos"] = (alld.hpv == "HPV+").astype(int)
    alld["malig"] = (alld["cell.type"] == "Malignant.cells").astype(int)
    alld["log_genes"] = np.log10(alld.n_genes)
    m2 = smf.mixedlm("score_core ~ hpv_pos * malig + log_genes", alld,
                     groups=alld["patient.id"]).fit()
    mm = []
    for name, mod, term in [("malignant only", m1, "hpv_pos"),
                            ("all cells", m2, "hpv_pos:malig")]:
        b_, se_ = mod.params[term], mod.bse[term]
        mm.append(dict(model=name, term=term, coef=round(float(b_), 4),
                       ci_lo=round(float(b_ - 1.96 * se_), 4),
                       ci_hi=round(float(b_ + 1.96 * se_), 4), p=float(mod.pvalues[term])))
    pd.DataFrame(mm).to_csv(outdir / "sc_mixedmodels.csv", index=False)

    # --- patient level: one value per tumour, plus leave-one-out ------------
    pt = (mal.groupby(["patient.id", "hpv"])
          .agg(n_cells=("score_core", "size"), mean_core=("score_core", "mean"),
               median_core=("score_core", "median"),
               frac_pos=("score_core", lambda s: float((s > 0).mean())))
          .reset_index())
    pt.to_csv(outdir / "sc_per_patient.csv", index=False)
    pa = pt.loc[pt.hpv == "HPV+", "mean_core"].values
    pb_ = pt.loc[pt.hpv == "HPV-", "mean_core"].values
    _, pt_p = stats.mannwhitneyu(pa, pb_, alternative="greater")
    loo = [stats.mannwhitneyu(np.delete(pa, i), pb_, alternative="greater")[1]
           for i in range(len(pa))]

    # --- pseudobulk: CPM per patient x cell type, independent of scoring ----
    cnt = counts.X.tocsr()
    idx = {g: A.var_names.get_loc(g) for k in sets for g in sets[k]}
    pbrows = []
    for (pid, hv, ct), sub in A.obs.groupby(["patient.id", "hpv", "cell.type"],
                                            observed=True):
        if len(sub) < SC_MIN_CELLS:
            continue
        rowsel = A.obs.index.get_indexer(sub.index)
        block = cnt[rowsel]
        tot = block.sum()
        if tot <= 0:
            continue
        cpm_all = np.asarray(block.sum(0)).ravel() / tot * 1e6
        rec = dict(patient=pid, hpv=hv, cell_type=ct, n_cells=len(sub))
        for k, gl in sets.items():
            v = np.array([cpm_all[idx[g]] for g in gl])
            rec[f"cpm_{k}"] = round(float(v.mean()), 4)
            rec[f"log_{k}"] = round(float(np.log2(v + 1).mean()), 4)
        pbrows.append(rec)
    pbdf = pd.DataFrame(pbrows)
    pbdf.to_csv(outdir / "sc_pseudobulk.csv", index=False)
    pbm = pbdf[pbdf.cell_type == "Malignant.cells"]
    pb_stats = {}
    for k in ("core", "meiotic", "cta"):
        a = pbm.loc[pbm.hpv == "HPV+", f"log_{k}"].values
        b = pbm.loc[pbm.hpv == "HPV-", f"log_{k}"].values
        _, p = stats.mannwhitneyu(a, b, alternative="greater")
        pb_stats[k] = (float(2 ** (a.mean() - b.mean())), float(p))

    # --- per-gene detection rates -------------------------------------------
    allg = sorted({g for gl in sets.values() for g in gl})
    ct_arr = A.obs["cell.type"].values
    hv_arr = A.obs["hpv"].values
    masks = {
        "HPV+ malignant": (ct_arr == "Malignant.cells") & (hv_arr == "HPV+"),
        "HPV- malignant": (ct_arr == "Malignant.cells") & (hv_arr == "HPV-"),
        "HPV+ non-malignant": (ct_arr != "Malignant.cells") & (hv_arr == "HPV+"),
    }
    cat_of = dict(zip(panel.gene, panel.category))
    grows = []
    for g in allg:
        v = np.asarray(cnt[:, A.var_names.get_loc(g)].todense()).ravel() > 0
        mp, mn, npm = masks["HPV+ malignant"], masks["HPV- malignant"], masks["HPV+ non-malignant"]
        orr, p1 = stats.fisher_exact([[v[mp].sum(), (~v[mp]).sum()],
                                      [v[mn].sum(), (~v[mn]).sum()]])
        or2, p2 = stats.fisher_exact([[v[mp].sum(), (~v[mp]).sum()],
                                      [v[npm].sum(), (~v[npm]).sum()]])
        grows.append(dict(gene=g, category=cat_of.get(g, "?"),
                          det_pos_malig=round(float(v[mp].mean()), 4),
                          det_neg_malig=round(float(v[mn].mean()), 4),
                          det_pos_nonmalig=round(float(v[npm].mean()), 4),
                          or_hpv=round(float(orr), 2) if np.isfinite(orr) else np.inf,
                          p_hpv=p1,
                          or_malig=round(float(or2), 2) if np.isfinite(or2) else np.inf,
                          p_malig=p2))
    pg = pd.DataFrame(grows)
    for src, dst in (("p_hpv", "fdr_hpv"), ("p_malig", "fdr_malig")):
        pg[dst] = multipletests(pg[src], method="fdr_bh")[1]
    pg.to_csv(outdir / "sc_per_gene.csv", index=False)

    # Full detection matrix: every panel gene x every cell type, split by HPV.
    # Long format so it stays readable at 57 genes x 9 types x 2 HPV strata.
    gidx = {g: A.var_names.get_loc(g) for g in allg}
    det_rows = []
    for ct in qct.cell_type:
        for hv in ("HPV+", "HPV-"):
            m = (ct_arr == ct) & (hv_arr == hv)
            n = int(m.sum())
            if n == 0:
                continue
            sub = (cnt[m][:, [gidx[g] for g in allg]] > 0)
            rates = np.asarray(sub.sum(0)).ravel() / n
            for g, r in zip(allg, rates):
                det_rows.append(dict(cell_type=ct, hpv=hv, n_cells=n, gene=g,
                                     category=cat_of.get(g, "?"),
                                     detection_rate=round(float(r), 4)))
    det = pd.DataFrame(det_rows)
    det.to_csv(outdir / "sc_detection_by_celltype.csv", index=False)

    meio_mask = pg.category.isin(MEIOTIC_CATS)
    cta_mask = pg.category == CTA_CAT
    spec = pg[pg.gene.isin(CORE6)][["gene", "det_pos_malig", "det_pos_nonmalig",
                                    "or_malig", "fdr_malig"]]
    spec.to_csv(outdir / "sc_specificity.csv", index=False)

    def det(g, col):
        r = pg[pg.gene == g]
        return float(r[col].iloc[0]) if len(r) else float("nan")

    core_present = [g for g in CORE6 if g in present]
    values = dict(
        dataset="GSE181919",
        n_cells_total=int(A.n_obs), n_genes=int(A.n_vars),
        n_mal_pos=int(mrow.n_hpv_pos), n_mal_neg=int(mrow.n_hpv_neg),
        n_nonmal=int((ct_arr != "Malignant.cells").sum()),
        n_pt_pos=int((pt.hpv == "HPV+").sum()), n_pt_neg=int((pt.hpv == "HPV-").sum()),
        mal_median_umi=int(qct.loc[qct.cell_type == "Malignant.cells",
                                   "median_umi"].iloc[0]),
        mal_median_genes=int(qct.loc[qct.cell_type == "Malignant.cells",
                                     "median_genes"].iloc[0]),
        mal_delta=float(mrow.delta), mal_auc=float(mrow.auc),
        nonmal_delta_max=float(nonmal.delta.abs().max()),
        mm_hpv_coef=mm[0]["coef"], mm_hpv_lo=mm[0]["ci_lo"], mm_hpv_hi=mm[0]["ci_hi"],
        mm_interaction=mm[1]["coef"], mm_interaction_p=mm[1]["p"],
        pt_p=float(pt_p), pt_loo_max_p=float(max(loo)),
        pt_separation=bool(pa.min() > pb_.max()),
        n_pb_pos=int(pbm[pbm.hpv == "HPV+"].patient.nunique()),
        n_pb_neg=int(pbm[pbm.hpv == "HPV-"].patient.nunique()),
        pb_min_cells=SC_MIN_CELLS,
        pb_core_fold=pb_stats["core"][0], pb_core_p=pb_stats["core"][1],
        pb_cta_fold=pb_stats["cta"][0], pb_cta_p=pb_stats["cta"][1],
        sycp2_det_pos=det("SYCP2", "det_pos_malig"),
        sycp2_det_neg=det("SYCP2", "det_neg_malig"),
        smc1b_det_pos=det("SMC1B", "det_pos_malig"),
        smc1b_det_neg=det("SMC1B", "det_neg_malig"),
        meio_sig=int(((pg.fdr_hpv < 0.05) & (pg.or_hpv > 1) & meio_mask).sum()),
        meio_n=int(meio_mask.sum()),
        cta_sig=int(((pg.fdr_hpv < 0.05) & (pg.or_hpv > 1) & cta_mask).sum()),
        cta_n=int(cta_mask.sum()),
        core_genes_present=len(core_present),
        core_missing=",".join(g for g in CORE6 if g not in present) or "none",
    )
    with open(outdir / "sc_values.json", "w") as fh:
        json.dump(values, fh, indent=1, default=str)

    make_singlecell_figures(scores, qct, hpvc, pt, pbm, pg, mm, values, outdir)
    return values
