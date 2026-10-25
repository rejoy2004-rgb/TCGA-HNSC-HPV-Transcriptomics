"""Exploratory ZFR2 Kaplan-Meier plot (Supplementary Fig. S7) with number-at-risk table, group sizes and log-rank P.
Input: results/review_sensitivity/ZFR2_KM_input.csv (made by scripts/review_analyses/km_zfr2_counts.py; groups = median split
of DESeq2-normalised ZFR2 counts, equivalent to a median split of VST values)."""
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test

d = pd.read_csv("results/review_sensitivity/ZFR2_KM_input.csv")
COL = {"High ZFR2": "#E41A1C", "Low ZFR2": "#377EB8"}
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False})
fig = plt.figure(figsize=(6.2, 4.9))
ax = fig.add_axes([0.13, 0.37, 0.84, 0.55])
at = [0, 50, 100, 150, 200]
risk = {}
for g in ("High ZFR2", "Low ZFR2"):
    s = d[d.group == g]
    km = KaplanMeierFitter().fit(s.OS_months, s.OS_event, label=f"{g} (n = {len(s)})")
    km.plot_survival_function(ax=ax, ci_show=False, color=COL[g], lw=1.8, show_censors=True,
                              censor_styles={"ms": 4, "marker": "|", "mew": 0.8})
    risk[g] = [int((s.OS_months >= t).sum()) for t in at]
h, l = d[d.group == "High ZFR2"], d[d.group == "Low ZFR2"]
p = logrank_test(h.OS_months, l.OS_months, h.OS_event, l.OS_event).p_value
ax.set_xlim(-5, 215); ax.set_ylim(0, 1.02); ax.set_xticks(at)
ax.set_xlabel("Overall survival (months)", fontsize=9); ax.set_ylabel("Survival probability", fontsize=9)
ax.tick_params(labelsize=8); ax.legend(loc="lower left", frameon=False, fontsize=8)
ax.text(0.98, 0.95, f"Log-rank P = {p:.2g}\n(exploratory, unadjusted)", transform=ax.transAxes, ha="right", va="top", fontsize=8)
ax.set_title("Kaplan\u2013Meier curve stratified by ZFR2 (median split, n = %d)" % len(d), fontsize=9, loc="left")
tab = fig.add_axes([0.13, 0.05, 0.84, 0.17]); tab.set_xlim(ax.get_xlim()); tab.set_ylim(0, 3); tab.axis("off")
tab.text(-5, 2.75, "Number at risk", fontsize=8, fontweight="bold", va="center", ha="left")
for row, g in enumerate(("High ZFR2", "Low ZFR2")):
    y = 1.75 - row
    tab.text(-14, y, g.split()[0], color=COL[g], fontsize=8, ha="right", va="center")
    for t, n in zip(at, risk[g]): tab.text(t, y, str(n), color=COL[g], fontsize=8, ha="center", va="center")
fig.savefig("figures/HNSC_BestGene_KM.png", dpi=600)
fig.savefig("figures/HNSC_BestGene_KM.pdf")  # vector copy for submission
print("P", p, risk)
