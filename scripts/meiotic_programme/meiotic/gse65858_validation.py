"""GSE65858: viral-activity dependence, per-gene and per-category specificity,
module coherence with size-matched permutation nulls, and confounder controls."""
from __future__ import annotations

from .config import *  # noqa: F401,F403
from .helpers import *  # noqa: F401,F403


def analysis_validation(expr: pd.DataFrame, clin: pd.DataFrame, outdir: Path) -> dict:
    """GSE65858: three-group activation, per-category AUC, confounders, module."""
    log("GSE65858 validation analysis")
    import statsmodels.api as sm

    clin = clin[clin.hpv_group != "unknown"].copy()
    ids = [s for s in clin.gsm if s in expr.columns]
    clin = clin.set_index("gsm").loc[ids]
    gz = zscore_rows(expr[ids])
    grp = clin.hpv_group
    core = [g for g in CORE6 if g in gz.index]
    score = gz.loc[core].mean(axis=0)
    log(f"  core module genes present: {core}")

    A, S, N = "HPV+ active", "HPV+ silent", "HPV-"
    kw = stats.kruskal(score[grp == A], score[grp == S], score[grp == N])
    m_an = grp.isin([A, N])
    res = dict(
        n_active=int((grp == A).sum()), n_silent=int((grp == S).sum()),
        n_neg=int((grp == N).sum()),
        med_active=float(np.median(score[grp == A])),
        med_silent=float(np.median(score[grp == S])),
        med_neg=float(np.median(score[grp == N])),
        kruskal_H=float(kw.statistic), kruskal_p=float(kw.pvalue),
        p_active_vs_neg=float(stats.mannwhitneyu(score[grp == A], score[grp == N]).pvalue),
        p_silent_vs_neg=float(stats.mannwhitneyu(score[grp == S], score[grp == N]).pvalue),
        p_active_vs_silent=float(stats.mannwhitneyu(score[grp == A], score[grp == S]).pvalue),
        auc_active_vs_neg=auc((grp[m_an] == A).values, score[m_an].values),
        auc_dna_only=auc(clin.hpv_dna_pos.values, score.values),
    )
    log(f"  active vs HPV-: AUC={res['auc_active_vs_neg']:.3f}, "
        f"p={res['p_active_vs_neg']:.2e}")
    log(f"  silent vs HPV-: p={res['p_silent_vs_neg']:.3f} "
        f"(the program needs the virus transcribing)")
    log(f"  DNA-only grouping: AUC={res['auc_dna_only']:.3f} "
        f"(weaker than transcriptional activity)")

    # per-gene and per-category discrimination
    y = (grp[m_an] == A).values
    per_gene = []
    for g in ALL_GENES:
        if g in gz.index:
            per_gene.append(dict(gene=g, category=GENE2CAT[g],
                                 AUC=auc(y, gz.loc[g, m_an].values),
                                 p=stats.mannwhitneyu(gz.loc[g, m_an][y],
                                                      gz.loc[g, m_an][~y]).pvalue))
    pg = pd.DataFrame(per_gene).sort_values("AUC", ascending=False)
    pg["padj"] = bh_fdr(pg.p.values)
    pg.to_csv(outdir / "table2b_per_gene_auc.csv", index=False)

    cats = []
    for cat, genes in GENE_SET.items():
        present = [g for g in genes if g in gz.index]
        if len(present) < 3:
            continue
        cs = gz.loc[present, m_an].mean(axis=0)
        cats.append(dict(category=cat, n_genes=len(present), AUC=auc(y, cs.values),
                         p=stats.mannwhitneyu(cs[y], cs[~y]).pvalue))
    cat_df = pd.DataFrame(cats).sort_values("AUC", ascending=False)
    cat_df.to_csv(outdir / "table2_category_auc.csv", index=False)
    log("  per-category AUC:\n" + cat_df.to_string(index=False))

    # confounders: anatomical site, proliferation, p16
    conf = []
    site = clin.tumor_site.astype(str).str.lower()
    op = site.str.contains("oropharyn")
    m_op = op & m_an
    if (op & (grp == A)).sum() >= 10 and (op & (grp == N)).sum() >= 10:
        conf.append(dict(test="within oropharynx only",
                         n=f"{int((op & (grp == A)).sum())} vs {int((op & (grp == N)).sum())}",
                         statistic=f"AUC={auc((grp[m_op] == A).values, score[m_op].values):.3f}",
                         p=stats.mannwhitneyu(score[op & (grp == A)],
                                              score[op & (grp == N)]).pvalue))
    pro = [g for g in PROLIFERATION if g in gz.index]
    X = pd.DataFrame({"meiotic": score, "proliferation": gz.loc[pro].mean(axis=0)})
    if "CDKN2A" in gz.index:
        X["p16"] = gz.loc["CDKN2A"]
    yb = pd.Series((grp == A).astype(int))[m_an]
    for label, cols in [("meiotic alone", ["meiotic"]),
                        ("+ proliferation", ["meiotic", "proliferation"]),
                        ("+ proliferation + p16", list(X.columns))]:
        cc = [c for c in cols if c in X.columns]
        Xb = sm.add_constant(X.loc[yb.index, cc])
        fit = sm.Logit(yb, Xb).fit(disp=0)
        conf.append(dict(test=f"logistic, {label}", n=str(len(yb)),
                         statistic=f"beta={fit.params['meiotic']:.2f}, "
                                   f"model AUC={auc(yb.values.astype(bool), fit.predict(Xb).values):.3f}",
                         p=float(fit.pvalues["meiotic"])))
    cdf = pd.DataFrame(conf)
    cdf.to_csv(outdir / "table6_confounders.csv", index=False)
    log("  confounder controls:\n" + cdf.to_string(index=False))

    # module coherence
    mods = {"core meiotic": core,
            "all meiotic": [g for g in ALL_GENES
                            if GENE2CAT[g].startswith(("Meiotic", "Synaptonemal"))
                            and g in gz.index],
            "classic CTA": [g for g in GENE_SET["Cancer-testis antigen (MAGE/CTAG)"]
                            if g in gz.index]}
    coh = []
    for gname, gmask in [(A, grp == A), (S, grp == S), (N, grp == N)]:
        for mname, genes in mods.items():
            coh.append(dict(group=gname, module=mname, n_samples=int(gmask.sum()),
                            n_genes=len(genes),
                            mean_rho=round(mean_pairwise_rho(gz.loc[genes, gmask[gmask].index]), 3)))
    coh_df = pd.DataFrame(coh)
    coh_df.to_csv(outdir / "table5_coexpression.csv", index=False)
    log("  module coherence:\n" + coh_df.to_string(index=False))

    # permutation control: is coherence just a sample-size artefact?
    rng = np.random.default_rng(123)                 # same seed and number of draws as scripts/review_analyses/gse65858_stats.py
    n_act = int((grp == A).sum())
    neg_ids = grp[grp == N].index
    null = [mean_pairwise_rho(gz.loc[core, rng.choice(neg_ids, n_act, replace=False)])
            for _ in range(1000)]
    obs = mean_pairwise_rho(gz.loc[core, grp[grp == A].index])
    perm_p = (np.sum(np.asarray(null) >= obs) + 1) / (len(null) + 1)
    log(f"  coherence permutation (equal n): observed={obs:.3f}, "
        f"HPV- null 95% CI [{np.percentile(null, 2.5):.3f}, {np.percentile(null, 97.5):.3f}], "
        f"p={perm_p:.4f}")

    res.update(per_gene=pg, categories=cat_df, coherence=coh_df, confounders=cdf,
               perm_p=float(perm_p), perm_obs=float(obs),
               perm_ci=(float(np.percentile(null, 2.5)), float(np.percentile(null, 97.5))),
               score=score, groups=grp, gz=gz, core=core)
    return res
