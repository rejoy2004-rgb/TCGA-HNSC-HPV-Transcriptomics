"""Spearman correlation of CIBERSORTx (Job14) fractions with marker-gene expression in the
279-tumour cohort, using the TPM mixture that was supplied to CIBERSORTx
(data_processed/HNSC_CIBERSORT_Input_Final.txt). Only markers present in that matrix
are tested. CD8A/CD8B correlations on variance-stabilised expression come from
scripts/HPV_HNSC_Revision.R (Part 4) and are added here as reported by that script.
P values follow R's cor.test for tied data (t approximation)."""
import numpy as np
import pandas as pd
from scipy import stats

x = pd.read_csv("data_processed/HNSC_CIBERSORT_Input_Final.txt", sep="\t", index_col=0)
x.columns = [c[:15] for c in x.columns]
j = pd.read_csv("data_processed/CIBERSORTx_Job14_Results.csv"); j.index = j["Mixture"].str[:15]
cohort = pd.read_csv("data_processed/HNSC_HPV_status.csv")["Sample ID"]
s = [i for i in cohort if i in j.index and i in x.columns]
assert len(s) == 279

def t_approx_p(r, n):
    t = r * np.sqrt((n - 2) / (1 - r ** 2))
    return 2 * stats.t.sf(abs(t), n - 2)

rows = []
for gene, cell in [("IGHM", "Plasma cells"), ("MS4A1", "Plasma cells")]:
    r = stats.spearmanr(x.loc[gene, s].astype(float), j.loc[s, cell]).statistic
    rows.append([cell, gene, "TPM (CIBERSORTx input)", round(r, 3), t_approx_p(r, len(s))])
for gene, r in [("CD8A", 0.735), ("CD8B", 0.689)]:   # from HPV_HNSC_Revision.R (VST)
    rows.append(["T cells CD8", gene, "VST (DESeq2)", r, t_approx_p(r, len(s))])
out = pd.DataFrame(rows, columns=["CellType", "Marker", "Expression", "Spearman_rho", "Pvalue"])
out.to_csv("results/Deconvolution_Marker_Validation.csv", index=False)
print(out.to_string(index=False))
