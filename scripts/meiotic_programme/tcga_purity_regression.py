#!/usr/bin/env python3
"""TCGA-HNSC tumour-purity and proliferation adjustment of the meiotic core score.

Inputs (from the repository):
  data_raw/TCGA_mastercalls.abs_tables_JSedit.fixed.txt         ABSOLUTE purity calls (TCGA PanCanAtlas)
  data_processed/meiotic_programme/TCGA_HNSC_per_sample_scores.csv  per-sample core-6 score and HPV status (n = 279)
Proliferation genes are fetched from cBioPortal (hnsc_tcga_rna_seq_v2_mrna).

Outputs in results/meiotic_programme/purity/:
  TCGA_HNSC_analysis_table_with_purity.csv, purity_regression_results.csv, purity_regression_summary.txt

Usage (from the repository root):
    python scripts/meiotic_programme/tcga_purity_regression.py
"""
import os
os.environ.setdefault("KMP_AFFINITY", "disabled")
os.environ.setdefault("OMP_NUM_THREADS", "1")
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
ABS = REPO / "data_raw" / "TCGA_mastercalls.abs_tables_JSedit.fixed.txt"
PER_SAMPLE = REPO / "data_processed" / "meiotic_programme" / "TCGA_HNSC_per_sample_scores.csv"
OUT = REPO / "results" / "meiotic_programme" / "purity"
OUT.mkdir(parents=True, exist_ok=True)
os.chdir(OUT)
import json, requests
import numpy as np, pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats

B = "https://www.cbioportal.org/api"
CORE6 = ["MEI1", "SMC1B", "STAG3", "SYCP2", "SYCE2", "MAJIN"]
PROLIFERATION = ["MKI67", "CCNB1", "TOP2A", "BUB1", "CDK1", "AURKA", "PLK1", "TYMS"]


def post(path, payload, params=None):
    r = requests.post(B + path, json=payload, params=params,
                      headers={"Content-Type": "application/json"}, timeout=300)
    r.raise_for_status()
    return r.json()


# ---------------------------------------------------------------- purity
ab = pd.read_csv(ABS, sep="\t")
ab["bc12"] = ab["array"].str[:12]
pu = (ab.dropna(subset=["purity"]).groupby("bc12")
        .agg(tumor_purity=("purity", "mean"), ploidy=("ploidy", "mean")).reset_index())

# ---------------------------------------------------------------- our table
S = pd.read_csv(PER_SAMPLE)
S["bc12"] = S.sample_ID.str[:12]

# ---------------------------------------------------------- proliferation
g = post("/genes/fetch", PROLIFERATION, params={"geneIdType": "HUGO_GENE_SYMBOL"})
eid = {x["hugoGeneSymbol"]: x["entrezGeneId"] for x in g}
e2s = {v: k for k, v in eid.items()}
data = post("/molecular-profiles/hnsc_tcga_rna_seq_v2_mrna/molecular-data/fetch",
            {"entrezGeneIds": sorted(eid.values()), "sampleListId": "hnsc_tcga_all"},
            params={"projection": "SUMMARY"})
E = (pd.DataFrame([(d["sampleId"], e2s[d["entrezGeneId"]], d["value"]) for d in data
                   if d.get("value") is not None], columns=["sample", "gene", "value"])
       .pivot_table(index="gene", columns="sample", values="value"))
lg = np.log2(E + 1)
prolif = lg.sub(lg.mean(axis=1), axis=0).div(lg.std(axis=1), axis=0).mean(axis=0)

T = S.merge(pu, on="bc12", how="left")
T["proliferation_score"] = T.sample_ID.map(prolif)
T.to_csv("TCGA_HNSC_analysis_table_with_purity.csv", index=False)

# ---------------------------------------------------------------- models
D = T.dropna(subset=["tumor_purity", "proliferation_score"]).copy()
D["hpv"] = (D.HPV_status == "positive").astype(int)
D = D.rename(columns={"meiotic_core6_score": "meiotic"})

models = {
    "meiotic ~ hpv": "meiotic ~ hpv",
    "meiotic ~ hpv + purity": "meiotic ~ hpv + tumor_purity",
    "meiotic ~ hpv + proliferation": "meiotic ~ hpv + proliferation_score",
    "meiotic ~ hpv + purity + proliferation": "meiotic ~ hpv + tumor_purity + proliferation_score",
}
rows = []
fits = {}
for label, f in models.items():
    fit = smf.ols(f, data=D).fit()
    fits[label] = fit
    for term in fit.params.index:
        if term == "Intercept":
            continue
        ci = fit.conf_int().loc[term]
        rows.append(dict(model=label, n=int(fit.nobs), term=term,
                         beta=fit.params[term], se=fit.bse[term],
                         ci_lo=ci[0], ci_hi=ci[1], t=fit.tvalues[term],
                         p=fit.pvalues[term], adj_r2=fit.rsquared_adj))
R = pd.DataFrame(rows)
R.to_csv("purity_regression_results.csv", index=False)

# VIF + descriptives
X = sm.add_constant(D[["hpv", "tumor_purity", "proliferation_score"]])
from statsmodels.stats.outliers_influence import variance_inflation_factor as vif
V = pd.DataFrame({"term": X.columns,
                  "VIF": [vif(X.values, i) for i in range(X.shape[1])]})

desc = D.groupby("HPV_status").agg(
    n=("sample_ID", "size"),
    purity_mean=("tumor_purity", "mean"), purity_sd=("tumor_purity", "std"),
    prolif_mean=("proliferation_score", "mean"),
    meiotic_mean=("meiotic", "mean")).reset_index()
mw = stats.mannwhitneyu(D.loc[D.hpv == 1, "tumor_purity"], D.loc[D.hpv == 0, "tumor_purity"])
rho_pm = stats.spearmanr(D.tumor_purity, D.meiotic)
rho_pp = stats.spearmanr(D.tumor_purity, D.proliferation_score)

with open("purity_regression_summary.txt", "w") as fh:
    fh.write(f"n analysed = {len(D)} (of {len(T)}; {T.tumor_purity.isna().sum()} without ABSOLUTE purity)\n\n")
    fh.write(desc.to_string(index=False) + "\n\n")
    fh.write(f"purity HPV+ vs HPV-: Mann-Whitney U={mw.statistic:.0f}, P={mw.pvalue:.3g}\n")
    fh.write(f"Spearman purity~meiotic: rho={rho_pm.statistic:.3f}, P={rho_pm.pvalue:.3g}\n")
    fh.write(f"Spearman purity~proliferation: rho={rho_pp.statistic:.3f}, P={rho_pp.pvalue:.3g}\n\n")
    fh.write(V.to_string(index=False) + "\n\n")
    fh.write(R.to_string(index=False) + "\n\n")
    fh.write(fits["meiotic ~ hpv + purity + proliferation"].summary().as_text() + "\n")

print(desc.to_string(index=False))
print()
print(R.to_string(index=False))
print()
print(V.to_string(index=False))
print("\npurity MW P=%.3g | rho purity~meiotic=%.3f (P=%.3g) | rho purity~prolif=%.3f (P=%.3g)"
      % (mw.pvalue, rho_pm.statistic, rho_pm.pvalue, rho_pp.statistic, rho_pp.pvalue))
