"""GSE38266: independent replication of promoter hypomethylation (all oropharyngeal)."""
from __future__ import annotations

from .config import *  # noqa: F401,F403
from .helpers import *  # noqa: F401,F403


def analysis_methylation_replication(beta: pd.DataFrame, clin: pd.DataFrame,
                                     pm: pd.DataFrame, disc: dict,
                                     outdir: Path) -> dict:
    """GSE38266: per-gene, effect-size, and set-level replication."""
    log("GSE38266 methylation replication")
    pos = [s for s in clin.loc[clin.hpv == "positive", "gsm"] if s in beta.columns]
    neg = [s for s in clin.loc[clin.hpv == "negative", "gsm"] if s in beta.columns]
    log(f"  {len(pos)} HPV+ / {len(neg)} HPV- (all oropharyngeal: site is controlled)")

    rows = []
    for g, sub in pm.groupby("gene"):
        pr = [p for p in sub.probe if p in beta.index]
        if not pr:
            continue
        b = beta.loc[pr].mean(axis=0)
        bp, bn = b[pos].dropna(), b[neg].dropna()
        if len(bp) < 8 or len(bn) < 8:
            continue
        rows.append(dict(gene=g, category=GENE2CAT.get(g, "?"), n_probes=len(pr),
                         beta_HPVpos=round(float(bp.median()), 4),
                         beta_HPVneg=round(float(bn.median()), 4),
                         delta_beta=round(float(bp.median() - bn.median()), 4),
                         p=stats.mannwhitneyu(bp, bn, alternative="two-sided").pvalue))
    ex = pd.DataFrame(rows)
    ex["padj"] = np.minimum(ex.p * len(ex), 1.0)     # Bonferroni, as in the paper
    ex = ex.sort_values("delta_beta")
    ex.to_csv(outdir / "table4b_external_methylation.csv", index=False)

    mg = disc["meth_table"][["gene", "delta_beta", "padj_meth"]].rename(
        columns={"delta_beta": "delta_TCGA"}).merge(
        ex[["gene", "delta_beta", "p", "padj"]].rename(
            columns={"delta_beta": "delta_GSE38266", "p": "p_ext", "padj": "padj_ext"}),
        on="gene")
    mg.to_csv(outdir / "table4_cross_cohort.csv", index=False)

    sr = stats.spearmanr(mg.delta_TCGA, mg.delta_GSE38266)
    same = int((np.sign(mg.delta_TCGA) == np.sign(mg.delta_GSE38266)).sum())
    binom = stats.binomtest(same, len(mg), 0.5).pvalue

    # Set-level test: the honest unit of replication at n=42. Per-gene
    # Bonferroni across ~77 genes is underpowered here by construction.
    hp = [g for g in disc["hypo_genes"] if g in set(pm.gene)]
    prb = [p for p in pm[pm.gene.isin(hp)].probe if p in beta.index]
    sc = beta.loc[prb].mean(axis=0)
    sp, sn = sc[pos].dropna(), sc[neg].dropna()
    set_p = stats.mannwhitneyu(sp, sn, alternative="two-sided").pvalue

    log(f"  effect-size concordance over {len(mg)} shared genes: "
        f"rho={sr.statistic:.3f}, p={sr.pvalue:.2e}")
    log(f"  same direction: {same}/{len(mg)} (binomial p={binom:.3f})")
    log(f"  SET-LEVEL promoter methylation ({len(hp)} genes, {len(prb)} probes): "
        f"HPV+ {sp.median():.4f} vs HPV- {sn.median():.4f}, p={set_p:.2e}")
    n_bonf = int(((ex.padj < 0.05) & (ex.delta_beta < 0)).sum())
    log(f"  per-gene Bonferroni survivors: {n_bonf} (expected to be few at this n)")

    return dict(cross=mg, external=ex, cross_rho=float(sr.statistic),
                cross_p=float(sr.pvalue), same_dir=same, n_shared=len(mg),
                binom_p=float(binom), set_p=float(set_p), n_set_genes=len(hp),
                n_probes=len(prb), n_pos=len(pos), n_neg=len(neg), n_bonf=n_bonf)
