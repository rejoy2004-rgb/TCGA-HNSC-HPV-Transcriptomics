"""Single-cell normalisation, Tirosh control-binned module scoring and test helpers.

Scoring follows Tirosh et al. (2016) control-binned module scoring, the same
method scanpy's ``tl.score_genes`` implements and the same one used elsewhere
in this project, reimplemented here so the analysis carries no scanpy
dependency (its pins collide with Colab's pandas).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import scipy.sparse as sp
from scipy import stats

RANDOM_SEED = 0
CTRL_SIZE = 50
N_BINS = 25
# MAJIN was renamed from C11orf85 (2016); both single-cell matrices carry the old symbol.
ALIASES = {"MAJIN": ["C11orf85"]}


# --------------------------------------------------------------------------
# normalisation
# --------------------------------------------------------------------------
def normalize_log(counts_csr, target_sum=1e4):
    """CP10K-normalise then log1p. `counts_csr` is cells x genes, CSR."""
    X = counts_csr.tocsr().astype(np.float32)
    tot = np.zeros(X.shape[0], dtype=np.float32)
    np.add.reduceat(np.append(X.data, np.float32(0)),
                    np.minimum(X.indptr[:-1], len(X.data)), out=tot)
    tot[tot == 0] = 1.0
    div = (tot / target_sum).astype(np.float32)
    out = X.copy()
    out.data = np.true_divide(out.data, np.repeat(div, np.diff(X.indptr)))
    out.data = np.log1p(out.data)
    return out


# --------------------------------------------------------------------------
# module scoring
# --------------------------------------------------------------------------
def score_genes(Xln, var_names, gene_list, ctrl_size=CTRL_SIZE, n_bins=N_BINS,
                seed=RANDOM_SEED):
    """Tirosh control-binned module score.

    Xln : cells x genes, log-normalised CSR.  Returns float64 array (n_cells,).
    Control genes are drawn from expression-matched bins, excluding the gene
    set itself, matching scanpy's ``ctrl_as_ref=True`` behaviour.
    """
    idx = {g: i for i, g in enumerate(var_names)}
    use = [idx[g] for g in gene_list if g in idx]
    if not use:
        return np.zeros(Xln.shape[0]), []

    # mean expression per gene across all cells, used for binning
    means = np.asarray(Xln.mean(axis=0)).ravel()
    # rank-based binning, as scanpy does (cut on ranks, not raw values)
    ranked = pd.Series(means).rank(method="min")
    cuts = pd.cut(ranked, n_bins, labels=False)

    rng = np.random.default_rng(seed)
    control = set()
    gene_set = set(use)
    for b in pd.unique(cuts[use]):
        pool = np.flatnonzero(cuts.values == b)
        pool = np.setdiff1d(pool, list(gene_set))  # ctrl_as_ref: exclude the set
        n = min(ctrl_size, len(pool))
        if n:
            control.update(rng.choice(pool, n, replace=False).tolist())
    control = np.array(sorted(control), dtype=int)

    x_set = np.asarray(Xln[:, use].mean(axis=1)).ravel()
    x_ctl = np.asarray(Xln[:, control].mean(axis=1)).ravel() if len(control) else 0.0
    return np.asarray(x_set - x_ctl, dtype=np.float64), [var_names[i] for i in use]


# --------------------------------------------------------------------------
# statistics
# --------------------------------------------------------------------------
def auc_mw(a, b):
    """Mann-Whitney U test plus the AUC (probability a random `a` exceeds `b`)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) == 0 or len(b) == 0:
        return np.nan, np.nan
    u, p = stats.mannwhitneyu(a, b, alternative="two-sided")
    return u / (len(a) * len(b)), p


def mean_expr(Xln, var_names, gene_list, mask):
    """Mean log-normalised expression of `gene_list` over cells in `mask`."""
    idx = {g: i for i, g in enumerate(var_names)}
    use = [idx[g] for g in gene_list if g in idx]
    if not use or mask.sum() == 0:
        return np.nan
    return float(np.asarray(Xln[mask][:, use].mean()))


def frac_expr(Xln, var_names, gene, mask):
    """Fraction of cells in `mask` with non-zero expression of `gene`."""
    idx = {g: i for i, g in enumerate(var_names)}
    if gene not in idx or mask.sum() == 0:
        return np.nan
    col = Xln[mask][:, [idx[gene]]]
    return float((col > 0).sum() / mask.sum())


def resolve(g, uni):
    """Return whichever symbol for gene `g` is present in `uni`, else None.

    Tries the current symbol first, then registered aliases, so a matrix
    carrying either name resolves. MAJIN (renamed from C11orf85 in 2016) is
    absent from both matrices under its current symbol.
    """
    for c in [g] + ALIASES.get(g, []):
        if c in uni:
            return c
    return None
