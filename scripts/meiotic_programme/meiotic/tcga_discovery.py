"""TCGA-HNSC discovery: promoter hypomethylation and methylation-expression coupling."""
from __future__ import annotations

from .config import *  # noqa: F401,F403
from .helpers import *  # noqa: F401,F403


def analysis_discovery(expr: pd.DataFrame, meth: pd.DataFrame,
                       hpv: pd.DataFrame, outdir: Path) -> dict:
    """TCGA: methylation differences, methylation-expression coupling."""
    log("TCGA discovery analysis")
    ez = zscore_rows(expr.T)                     # genes x samples
    hpv = hpv.set_index("sample").HPV_status
    common = sorted(set(ez.columns) & set(hpv.index))
    ez, hs = ez[common], hpv.loc[common]
    pos, neg = hs[hs == "positive"].index, hs[hs == "negative"].index
    log(f"  expression: {len(pos)} HPV+ / {len(neg)} HPV-")

    mm = meth.copy()
    mm.index = [s[:15] for s in mm.index]
    mcommon = sorted(set(mm.index) & set(hpv.index))
    mm, mhs = mm.loc[mcommon], hpv.loc[mcommon]
    mpos, mneg = mhs[mhs == "positive"].index, mhs[mhs == "negative"].index
    log(f"  methylation: {len(mpos)} HPV+ / {len(mneg)} HPV-")

    rows = []
    for g in ALL_GENES:
        if g not in mm.columns:
            continue
        bp, bn = mm.loc[mpos, g].dropna(), mm.loc[mneg, g].dropna()
        if len(bp) < 10 or len(bn) < 10:
            continue
        p_meth = stats.mannwhitneyu(bp, bn, alternative="two-sided").pvalue
        rho = np.nan
        if g in ez.index:
            shared = sorted(set(mm.index) & set(ez.columns))
            a, b = mm.loc[shared, g], ez.loc[g, shared]
            ok = a.notna() & b.notna()
            if ok.sum() > 20:
                rho = stats.spearmanr(a[ok], b[ok]).statistic
        rows.append(dict(gene=g, category=GENE2CAT.get(g, "?"),
                         beta_HPVpos=round(float(bp.median()), 4),
                         beta_HPVneg=round(float(bn.median()), 4),
                         delta_beta=round(float(bp.median() - bn.median()), 4),
                         p_meth=p_meth, rho_meth_expr=rho))
    mt = pd.DataFrame(rows)
    mt["padj_meth"] = bh_fdr(mt.p_meth.values)
    mt = mt.sort_values("delta_beta")
    mt.to_csv(outdir / "table3_methylation.csv", index=False)

    hypo = mt[(mt.padj_meth < 0.05) & (mt.delta_beta < 0)]
    n_neg_rho = int((hypo.rho_meth_expr < 0).sum())
    log(f"  {len(hypo)}/{len(mt)} genes hypomethylated in HPV+ (FDR<0.05); "
        f"{n_neg_rho}/{len(hypo)} with rho<0")

    # composite hypomethylation score vs expression score
    hg = [g for g in hypo.gene if g in mm.columns]
    both = sorted(set(mm.index) & set(ez.columns))
    hypo_score = zscore_rows(mm.loc[both, hg].T).mean(axis=0)
    core_present = [g for g in CORE6 if g in ez.index]
    expr_score = ez.loc[core_present, both].mean(axis=0)
    sr = stats.spearmanr(hypo_score, expr_score, nan_policy="omit")
    log(f"  hypomethylation score vs meiotic expression score: "
        f"rho={sr.statistic:.3f}, p={sr.pvalue:.2e}")

    return dict(meth_table=mt, hypo_genes=list(hypo.gene), n_hypo=len(hypo),
                n_tested=len(mt), n_neg_rho=n_neg_rho,
                median_rho=float(hypo.rho_meth_expr.median()),
                coupling_rho=float(sr.statistic), coupling_p=float(sr.pvalue),
                n_pos=len(pos), n_neg=len(neg), n_mpos=len(mpos), n_mneg=len(mneg))
