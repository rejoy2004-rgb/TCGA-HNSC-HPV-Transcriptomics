"""GSE65858: DeLong and bootstrap AUC CIs, size-matched coherence nulls (n = 35 and n = 25), four-gene score.
Usage: python gse65858_stats.py <data_dir>/geo [out_json]   (after gse65858_prep.py)"""
import sys, json
import numpy as np, pandas as pd
from scipy.stats import mannwhitneyu, spearmanr, norm

D = sys.argv[1]
g = pd.read_parquet(f"{D}/gse65858_gene.parquet"); m = pd.read_csv(f"{D}/gse65858_meta.csv", index_col=0)
CORE = ["MEI1", "SMC1B", "STAG3", "SYCP2", "SYCE2", "MAJIN"]
FOUR = ["SMC1B", "SYCP2", "SYCE2", "MAJIN"]
z = g.sub(g.mean(1), axis=0).div(g.std(1, ddof=1), axis=0)


def delong(pos, neg):
    pos, neg = np.asarray(pos), np.asarray(neg)
    m_, n_ = len(pos), len(neg)
    psi = (pos[:, None] > neg[None, :]) + 0.5 * (pos[:, None] == neg[None, :])
    auc = psi.mean(); v10 = psi.mean(1); v01 = psi.mean(0)
    se = np.sqrt(v10.var(ddof=1) / m_ + v01.var(ddof=1) / n_)
    lo, hi = auc - 1.959964 * se, auc + 1.959964 * se
    return auc, max(lo, 0.0), min(hi, 1.0)


def boot(pos, neg, B=2000, seed=123):
    rng = np.random.default_rng(seed); pos, neg = np.asarray(pos), np.asarray(neg); out = []
    for _ in range(B):
        p = rng.choice(pos, len(pos)); q = rng.choice(neg, len(neg))
        out.append(((p[:, None] > q[None, :]) + 0.5 * (p[:, None] == q[None, :])).mean())
    return np.percentile(out, [2.5, 97.5])


def coh(genes, samples):
    r = spearmanr(g.loc[genes, samples].T).correlation
    return r[np.triu_indices(len(genes), 1)].mean()


res = {}
oro = m.tumor_site.eq("Oropharynx")
for name, genes in [("core6", CORE), ("four", FOUR)]:
    s = z.loc[genes].mean()
    A, N, S = s[m.group == "active"], s[m.group == "neg"], s[m.group == "silent"]
    comps = {"active_vs_neg": (A, N), "silent_vs_neg": (S, N), "dna_vs_neg": (pd.concat([A, S]), N),
             "active_vs_neg_oropharynx": (A[oro[A.index]], N[oro[N.index]])}
    for k, (p, q) in comps.items():
        auc, lo, hi = delong(p, q); b = boot(p, q)
        res[f"{name}|{k}"] = dict(n_pos=len(p), n_neg=len(q), auc=round(auc, 3), delong=[round(lo, 2), round(hi, 2)],
                                 boot=[round(b[0], 2), round(b[1], 2)], mw_p=float(mannwhitneyu(p, q).pvalue))
    neg_ids = m.index[m.group == "neg"].to_numpy()
    rng = np.random.default_rng(123)
    for grp in ["active", "silent"]:
        ids = m.index[m.group == grp]; obs = coh(genes, ids)
        null = np.array([coh(genes, rng.choice(neg_ids, len(ids), replace=False)) for _ in range(1000)])
        res[f"{name}|coherence_{grp}"] = dict(n=len(ids), observed=round(obs, 3), null_95=[round(np.percentile(null, 2.5), 3), round(np.percentile(null, 97.5), 3)],
                                             perm_p=round((1 + (null >= obs).sum()) / 1001, 4))
    res[f"{name}|coherence_neg"] = round(coh(genes, m.index[m.group == "neg"]), 3)
print(json.dumps(res, indent=1))
json.dump(res, open(sys.argv[2] if len(sys.argv) > 2 else f"{D}/gse65858_results.json", "w"), indent=1)
