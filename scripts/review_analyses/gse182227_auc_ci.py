"""DeLong and bootstrap 95% CI for the GSE182227 per-tumour four-gene AUC (11 HPV+ vs 5 HPV-).
The AUC depends only on ranks. The reported configuration fixes them: AUC = 0.945 (52 of 55 concordant pairs);
OP13 scores below only the highest HPV- tumour (OP8), so the other overlapping HPV+ tumour scores below the two
highest HPV- tumours, and all other HPV+ tumours score above every HPV- tumour.
Usage: python gse182227_auc_ci.py <out_json>"""
import json, sys
import numpy as np

neg = np.array([1, 2, 3, 5, 7.])              # HPV- ranks; 7 = OP8, 5 = second highest
pos = np.array([6, 4] + [10] * 9, dtype=float)  # OP13 (6), second overlapping HPV+ tumour (4), nine others
psi = (pos[:, None] > neg[None, :]) + 0.5 * (pos[:, None] == neg[None, :])
auc = psi.mean()
se = np.sqrt(psi.mean(1).var(ddof=1) / len(pos) + psi.mean(0).var(ddof=1) / len(neg))
rng = np.random.default_rng(123); boot = []
for _ in range(5000):
    p, q = rng.choice(pos, len(pos)), rng.choice(neg, len(neg))
    boot.append(((p[:, None] > q[None, :]) + 0.5 * (p[:, None] == q[None, :])).mean())
res = dict(n_pos=11, n_neg=5, auc=round(auc, 3), delong=[round(auc - 1.96 * se, 2), min(1.0, round(auc + 1.96 * se, 2))],
           bootstrap=[round(float(x), 2) for x in np.percentile(boot, [2.5, 97.5])])
print(res); json.dump(res, open(sys.argv[1], "w"), indent=1)
