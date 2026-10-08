"""TCGA-HNSC and GSE38266 core-module analyses requested in review:
(1) one promoter definition (CpGs 1,500 bp upstream to 500 bp downstream of an annotated TSS) applied to both cohorts,
    alongside the all-annotated-probe summary;
(2) six-gene versus four-gene (SMC1B, SYCP2, SYCE2, MAJIN) methylation composite and its coupling to expression;
(3) HPV effect on core-module methylation with and without adjustment for CIBERSORTx B-cell + plasma-cell fraction;
(4) HPV-definition sensitivity: p16-or-ISH (main), ISH-only, and p16-or-ISH restricted to oropharyngeal tumours.
Inputs: GDC SeSAMe HM450 betas (core-gene probes), cBioPortal RSEM all-sample Z-scores, GSE38266 series matrix.
Usage: python tcga_methylation_sensitivity.py <data_dir> <repo>   (after tcga_fetch.py, core_probes_and_gse38266.py, gdc_fetch.py)"""
import json, sys
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import mannwhitneyu, spearmanr
from statsmodels.stats.multitest import multipletests

S, REPO = sys.argv[1], sys.argv[2]
CORE = ["MEI1", "SMC1B", "STAG3", "SYCP2", "SYCE2", "MAJIN"]
FOUR = ["SMC1B", "SYCP2", "SYCE2", "MAJIN"]
ORO = {"Tonsil", "Base of tongue", "Oropharynx"}

probes = pd.read_csv(f"{S}/geo/gpl13534_core.tsv", sep="\t")
sets = {"all": probes, "promoter": probes[probes.prom]}


def gene_level(betas, defn):
    p = sets[defn]
    out = {}
    for g in CORE:
        ids = [i for i in p.ID[p.gene == g] if i in betas.index]
        out[g] = betas.loc[ids].mean()
    return pd.DataFrame(out), {g: int(sum(i in betas.index for i in p.ID[p.gene == g])) for g in CORE}


def delong(pos, neg):
    pos, neg = np.asarray(pos), np.asarray(neg)
    psi = (pos[:, None] > neg[None, :]) + 0.5 * (pos[:, None] == neg[None, :])
    auc = psi.mean(); se = np.sqrt(psi.mean(1).var(ddof=1) / len(pos) + psi.mean(0).var(ddof=1) / len(neg))
    return round(auc, 3), round(max(auc - 1.96 * se, 0), 2), round(min(auc + 1.96 * se, 1), 2)


def zc(df):
    return (df - df.mean()) / df.std()


# clinical and HPV rules
cl = pd.read_csv(f"{REPO}/data_raw/data_clinical_patient_full.txt", sep="\t", comment="#", dtype=str).set_index("PATIENT_ID")
p16, ish, site = cl.HPV_STATUS_P16, cl.HPV_STATUS_ISH, cl.PRIMARY_SITE_PATIENT
main = pd.Series(np.where((p16 == "Positive") | (ish == "Positive"), 1.0, np.where((p16 == "Negative") | (ish == "Negative"), 0.0, np.nan)), index=cl.index)
rules = {
    "p16_or_ISH (main)": main,
    "ISH_only": pd.Series(np.where(ish == "Positive", 1.0, np.where(ish == "Negative", 0.0, np.nan)), index=cl.index),
    "p16_or_ISH_oropharynx_only": main.where(site.isin(ORO)),
}

# data
tb = pd.read_csv(f"{S}/gdc/tcga_core_probe_betas.csv", index_col=0)
tb.columns = tb.columns.str[:15]
ex = pd.read_csv(f"{S}/tcga/hnsc_tcga_rna_seq_v2_mrna_median_all_sample_Zscores.csv", index_col=0)
ex = ex[ex.index.str.endswith("-01")]
cib = pd.read_csv(f"{REPO}/data_processed/CIBERSORTx_Job14_Results.csv")
cib.index = cib.Mixture.str[:15]
bplasma = (cib["B cells naive"] + cib["B cells memory"] + cib["Plasma cells"]).groupby(level=0).mean()

bmk = pd.read_csv(f"{S}/tcga/hnsc_tcga_rna_seq_v2_mrna_median_all_sample_Zscores_bmarkers.csv", index_col=0)
bmk = bmk[bmk.index.str.endswith("-01")]
bmark = bmk[["CD19", "CD79A", "JCHAIN", "MS4A1", "MZB1"]].mean(1)
ov = bmark.index.intersection(bplasma.index)
r = spearmanr(bmark[ov], bplasma[ov])

g38 = pd.read_csv(f"{S}/geo/gse38266_core_probes.csv", index_col=0)
g38grp = pd.read_csv(f"{S}/geo/gse38266_groups.csv", index_col=0).iloc[:, 0]

res = {"promoter_definition": "CpGs 1,500 bp upstream to 500 bp downstream of any annotated TSS of the gene (GENCODE v36, hg38; SeSAMe HM450 manifest)",
       "bmarker_vs_cibersortx_bplasma": dict(n=len(ov), rho=round(r.correlation, 3), p=r.pvalue)}

for defn in ["all", "promoter"]:
    T, nprobe_t = gene_level(tb, defn)
    G, nprobe_g = gene_level(g38, defn)
    hpv = main.reindex(T.index.str[:12]).values
    T = T.assign(hpv=hpv).dropna(subset=["hpv"])
    gg = g38grp.reindex(G.index)
    rows = []
    for g in CORE:
        a, b = T.loc[T.hpv == 1, g].dropna(), T.loc[T.hpv == 0, g].dropna()
        c, d = G.loc[gg == "HPV+", g].dropna(), G.loc[gg == "HPV-", g].dropna()
        rows.append(dict(gene=g, probes_tcga=nprobe_t[g], probes_gse38266=nprobe_g[g],
                         tcga_delta=round(a.mean() - b.mean(), 3), tcga_p=mannwhitneyu(a, b).pvalue,
                         gse38266_delta=round(c.mean() - d.mean(), 3), gse38266_p=mannwhitneyu(c, d).pvalue))
    tab = pd.DataFrame(rows)
    tab["tcga_fdr"] = multipletests(tab.tcga_p, method="fdr_bh")[1]
    tab["gse38266_fdr"] = multipletests(tab.gse38266_p, method="fdr_bh")[1]
    tab["same_sign"] = np.sign(tab.tcga_delta) == np.sign(tab.gse38266_delta)
    res[f"{defn}|per_gene"] = tab.to_dict(orient="records")
    res[f"{defn}|n_tcga"] = {"HPV+": int((T.hpv == 1).sum()), "HPV-": int((T.hpv == 0).sum())}
    # set-level GSE38266 test over the definition's probes
    pr = sets[defn]; pr = pr[pr.ID.isin(g38.index)]
    sm = g38.loc[pr.ID.unique()].mean()
    res[f"{defn}|gse38266_setlevel"] = dict(n_probes=int(pr.ID.nunique()), hpvpos_mean=round(sm[g38grp == "HPV+"].mean(), 3),
                                          hpvneg_mean=round(sm[g38grp == "HPV-"].mean(), 3), p=mannwhitneyu(sm[g38grp == "HPV+"], sm[g38grp == "HPV-"]).pvalue)
    # composites and coupling to expression (samples with both)
    both = T.index[T.index.isin(ex.index)]
    for name, genes in [("core6", CORE), ("four", FOUR)]:
        hyp = (-zc(T.loc[both, genes])).mean(1)
        exs = zc(ex.loc[both, genes]).mean(1)
        r = spearmanr(-hyp, exs)
        res[f"{defn}|{name}|methylation_vs_expression"] = dict(n=len(both), rho_beta_vs_expr=round(r.correlation, 3), p=r.pvalue)
        comp = T[genes].mean(1)
        a, b = comp[T.hpv == 1], comp[T.hpv == 0]
        res[f"{defn}|{name}|composite_beta_HPV"] = dict(delta=round(a.mean() - b.mean(), 3), p=mannwhitneyu(a, b).pvalue)
    # B/plasma adjustment (samples with CIBERSORTx fractions)
    T2 = T.assign(bp=bplasma.reindex(T.index).values).dropna(subset=["bp"])
    adj = {}
    for target in ["MEI1", "STAG3"]:
        d = T2.rename(columns={target: "y"})
        m0, m1 = smf.ols("y ~ hpv", d).fit(), smf.ols("y ~ hpv + bp", d).fit()
        adj[target] = dict(n=int(len(d)), hpv_beta_unadjusted=round(m0.params.hpv, 4), p_unadjusted=m0.pvalues.hpv,
                           hpv_beta_adjusted=round(m1.params.hpv, 4), p_adjusted=m1.pvalues.hpv, bplasma_beta=round(m1.params.bp, 4), bplasma_p=m1.pvalues.bp)
    for name, genes in [("core6", CORE), ("four", FOUR)]:
        d = T2.assign(y=T2[genes].mean(1))
        m0, m1 = smf.ols("y ~ hpv", d).fit(), smf.ols("y ~ hpv + bp", d).fit()
        adj[f"composite_{name}"] = dict(n=int(len(d)), hpv_beta_unadjusted=round(m0.params.hpv, 4), p_unadjusted=m0.pvalues.hpv,
                                        hpv_beta_adjusted=round(m1.params.hpv, 4), p_adjusted=m1.pvalues.hpv, bplasma_beta=round(m1.params.bp, 4), bplasma_p=m1.pvalues.bp)
    res[f"{defn}|bplasma_adjustment"] = adj
    # B/plasma marker-expression score (mean all-sample Z of CD19, CD79A, JCHAIN, MS4A1, MZB1) available for all samples with expression
    T3 = T.assign(bm=bmark.reindex(T.index).values).dropna(subset=["bm"])
    adj2 = {}
    for target, genes in [("MEI1", ["MEI1"]), ("STAG3", ["STAG3"]), ("composite_core6", CORE), ("composite_four", FOUR)]:
        d = T3.assign(y=T3[genes].mean(1))
        m0, m1 = smf.ols("y ~ hpv", d).fit(), smf.ols("y ~ hpv + bm", d).fit()
        adj2[target] = dict(n=int(len(d)), hpv_beta_unadjusted=round(m0.params.hpv, 4), p_unadjusted=m0.pvalues.hpv,
                            hpv_beta_adjusted=round(m1.params.hpv, 4), p_adjusted=m1.pvalues.hpv, marker_beta=round(m1.params.bm, 4), marker_p=m1.pvalues.bm)
    res[f"{defn}|bmarker_adjustment"] = adj2

# HPV-definition sensitivity (expression score AUC with DeLong CI; promoter-methylation composite)
Tp, _ = gene_level(tb, "promoter")
sens = {}
for rname, rule in rules.items():
    e = ex.assign(hpv=rule.reindex(ex.index.str[:12]).values).dropna(subset=["hpv"])
    t = Tp.assign(hpv=rule.reindex(Tp.index.str[:12]).values).dropna(subset=["hpv"])
    row = {}
    for name, genes in [("core6", CORE), ("four", FOUR)]:
        s = zc(e[genes]).mean(1)
        row[f"{name}_expression"] = dict(n_pos=int((e.hpv == 1).sum()), n_neg=int((e.hpv == 0).sum()), auc_delong=delong(s[e.hpv == 1], s[e.hpv == 0]),
                                         p=mannwhitneyu(s[e.hpv == 1], s[e.hpv == 0]).pvalue)
        c = t[genes].mean(1)
        row[f"{name}_promoter_methylation"] = dict(n_pos=int((t.hpv == 1).sum()), n_neg=int((t.hpv == 0).sum()),
                                                   delta_beta=round(c[t.hpv == 1].mean() - c[t.hpv == 0].mean(), 3),
                                                   auc_hypomethylation=delong(-c[t.hpv == 1], -c[t.hpv == 0]), p=mannwhitneyu(c[t.hpv == 1], c[t.hpv == 0]).pvalue)
    sens[rname] = row
res["hpv_definition_sensitivity"] = sens

print(json.dumps(res, indent=1, default=float))
json.dump(res, open(f"{REPO}/results/review_sensitivity/TCGA_GSE38266_methylation_sensitivity.json", "w"), indent=1, default=float)
