#!/usr/bin/env python3
"""GSE182227 single-cell replication and the two-cohort per-tumour comparison.

GSE182227 (oropharyngeal SCC, 16 primary tumours: 11 HPV+, 5 HPV-) is deposited
without cell-type or malignant-cell labels, so both are derived here:

  1. counts      MatrixMarket matrix streamed twice: gene/cell totals, then a
                 gene subset (3,000 highest-mean genes + every scoring/marker gene)
  2. clusters    CP10K-log normalisation, 2,000 HVGs, PCA (40), kNN (k = 15),
                 Leiden (RBConfiguration, resolution 1.0, seed 0)
  3. lineages    marker means per cluster (epithelial: EPCAM/KRT8/KRT18/KRT19 high,
                 PTPRC low; otherwise the strongest immune/stromal panel)
  4. malignant   inferred CNV (22 autosomes, immune + stromal cells as the diploid
                 reference, gene positions from Ensembl REST). Epithelial clusters
                 that hold >= 10 % of all adjacent-normal epithelial cells AND have
                 CNV <= the 55th percentile of the reference are normal epithelium;
                 every other primary-tumour epithelial cell is malignant. The rule
                 uses tissue of origin and CNV only - never the meiotic genes.
  5. scores      Tirosh control-binned scores: 6-gene core, 4-gene meiosis-specific
                 (SMC1B, SYCP2, SYCE2, MAJIN/C11orf85), 10-gene CTA, 6-gene proliferation
  6. tumours     per-tumour means over malignant cells (>= 10 cells); HPV contrasts,
                 and pooled OLS with GSE181919 (dataset fixed effect, +/- proliferation),
                 HC3 and Huber robust fits, leave-one-tumour-out

The GSE181919 half reuses the deposited cell-type labels (primary tumours only),
built by meiotic.data_geo.build_sc_matrix.

Usage (from the repository root):
    python scripts/meiotic_programme/gse182227_singlecell.py --data DATA/meiotic [--panels]
Downloads ~0.6 GB (GSE182227) and, if not already cached by run_meiotic_analysis.py,
~1.2 GB (GSE181919). Peak RAM ~5 GB. Runtime ~20-30 min.
"""
import argparse, gzip, json, os, sys, tarfile, time
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
REPO = HERE.parents[1]
os.environ.setdefault("KMP_AFFINITY", "disabled"); os.environ.setdefault("OMP_NUM_THREADS", "1")

import numpy as np
import pandas as pd
import scipy.sparse as sp
import requests
from scipy import stats
import statsmodels.api as sm_api
import statsmodels.formula.api as smf

from meiotic.helpers import download, log
from meiotic.data_geo import build_sc_matrix, fetch_gse181919
from meiotic import sc_scoring as pa
from meiotic.sc_scoring import resolve
from meiotic import fig_gse182227
from meiotic.panel_export import install_export_hook

RANDOM_SEED = 0
GEO_227 = "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE182nnn/GSE182227"
F227 = {"mtx": "GSE182227_OPSCC.mtx.gz", "barcodes": "GSE182227_barcodes.txt.gz",
        "genes": "GSE182227_genes.txt.gz", "family": "GSE182227_family.xml.tgz"}
NNZ_227 = 179053703

CORE6 = ["MEI1", "SMC1B", "STAG3", "SYCP2", "SYCE2", "MAJIN"]
SPECIFIC4 = ["SMC1B", "SYCP2", "SYCE2", "C11orf85"]   # meiosis-specific: no somatic expression in GSE181919
CTA_PROF = ["MAGEA1", "MAGEA3", "MAGEA4", "MAGEA6", "MAGEA10", "MAGEC1", "MAGEC2", "CTAG1A", "CTAG1B", "CTAG2"]
PROLIF = ["MKI67", "PCNA", "TOP2A", "CCNB1", "BUB1", "AURKA"]
MARKERS_PROF = {"Epithelial": ["EPCAM", "KRT5", "KRT14", "KRT17", "TP63"],
                "T": ["CD3D", "CD3E"], "B": ["MS4A1", "CD79A"], "Plasma": ["JCHAIN", "MZB1", "IGKC"],
                "Myeloid": ["LST1", "CD68"], "Fibroblast": ["COL1A1", "DCN"], "Endothelial": ["PECAM1", "VWF"]}
EXTRA_GENES = {"PTPRC", "KRT8", "KRT18", "KRT19", "SOX2", "CDH1", "MKI67", "COL1A2", "ACTA2", "CD14", "FCGR3A",
               "NKG7", "GNLY", "TPSAB1", "CPA3", "LYZ", "CD8A", "CD4", "FOXP3", "SFRP1", "MGP"}
# barcode prefix -> GEO sample title
PREF2SAMPLE = {
    "OP4": "OP4-CD45-", "OP4CD45P": "OP4-CD45+", "OP5": "OP5",
    "OP6": "OP6-CD45-", "OP6CD45P": "OP6-CD45+", "OP8": "OP8",
    "OP9GEX": "OP9-CD45-", "OP9": "OP9-CD45+", "OP10": "OP10", "OP12": "OP12",
    "OP13": "OP13", "OP14": "OP14-CD45-", "OP14CD45P": "OP14-CD45+",
    "OP16": "OP16", "OP17": "OP17", "OP19": "OP19", "OP20": "OP20",
    "OP33": "OP33-tumor", "OP33norm": "OP33-normal",
    "OP34": "OP34-tumor", "OP34norm": "OP34-normal",
    "OP35BOT": "OP35-tumor", "OP35LN": "OP35-LN", "OP35norm": "OP35-normal"}
SCORES = [("mean_meiotic6", "meiotic core (6 genes)"), ("mean_meiotic4", "meiotic specific (4 genes)"),
          ("mean_cta", "CTA control (10 genes)"), ("mean_prolif", "proliferation control (6 genes)")]
PT_COLS = ["patient", "hpv", "n_cells", "mean_meiotic6", "mean_meiotic4", "mean_cta", "mean_prolif",
           "pct_detect", "is_hpv_positive", "dataset"]


def contrasts(pt):
    rows = []
    for col, lab in SCORES:
        a, b = pt.loc[pt.hpv == "HPV+", col], pt.loc[pt.hpv == "HPV-", col]
        auc, p = pa.auc_mw(a, b)
        rows.append({"score": lab, "delta": a.mean() - b.mean(), "auc": auc, "p": p,
                     "complete_separation": bool(a.min() > b.max()), "n_pos": len(a), "n_neg": len(b)})
    return pd.DataFrame(rows)


def per_tumour(meta, mask, arrays, min_cells=10):
    M = meta[mask].copy()
    for nm, arr in arrays.items():
        M[nm] = arr[mask]
    pt = (M.groupby(["patient", "hpv"]).agg(
        n_cells=("core6", "size"), mean_meiotic6=("core6", "mean"), mean_meiotic4=("spec4", "mean"),
        mean_cta=("cta", "mean"), mean_prolif=("prolif", "mean"),
        pct_detect=("det", lambda v: 100 * v.mean())).reset_index())
    pt = pt[pt.n_cells >= min_cells].copy()
    pt["is_hpv_positive"] = (pt.hpv == "HPV+").astype(int)
    return pt


# =============================================================================
# GSE181919: per-tumour scores from the deposited labels
# =============================================================================
def gse181919_per_tumour(cache):
    if not all((cache / f).exists() for f in ("sc_CA_counts.npz", "sc_CA_genes.npy", "sc_CA_meta.csv")):
        fetch_gse181919(cache)
    X919, genes919, meta919 = build_sc_matrix(cache)
    genes919 = np.asarray(genes919).astype(str); u919 = set(genes919)
    Xln = pa.normalize_log(sp.csr_matrix(X919.T))
    sets = {"core6": [resolve(g, u919) for g in CORE6 if resolve(g, u919)],
            "spec4": SPECIFIC4,
            "cta": [resolve(g, u919) for g in CTA_PROF if resolve(g, u919)],
            "prolif": [resolve(g, u919) for g in PROLIF if resolve(g, u919)]}
    arr = {k: pa.score_genes(Xln, genes919, v)[0] for k, v in sets.items()}
    idx = {g: i for i, g in enumerate(genes919)}
    arr["det"] = np.asarray((Xln[:, [idx[g] for g in SPECIFIC4]] > 0).sum(axis=1)).ravel() > 0
    ct = meta919["cell.type"].values
    meta = pd.DataFrame({"patient": meta919["patient.id"].values, "hpv": meta919["hpv"].values})
    pt = per_tumour(meta, ct == "Malignant.cells", arr)
    pt["dataset"] = "GSE181919"
    log(f"  GSE181919: {len(pt)} tumours ({int(pt.is_hpv_positive.sum())} HPV+)")
    return pt


# =============================================================================
# GSE182227: annotation from scratch
# =============================================================================
def fetch_182227(cache):
    for k, fn in F227.items():
        url = f"{GEO_227}/{'miniml' if k == 'family' else 'suppl'}/{fn}"
        download(url, cache / fn)


def sample_sheet(cache):
    with tarfile.open(cache / F227["family"]) as t:
        xml = t.extractfile("GSE182227_family.xml").read().decode()
    ns = {"m": "http://www.ncbi.nlm.nih.gov/geo/info/MINiML"}
    rows = []
    for s in ET.fromstring(xml).findall("m:Sample", ns):
        d = {"gsm": s.get("iid"), "title": s.find("m:Title", ns).text}
        for ch in s.findall(".//m:Characteristics", ns):
            d[ch.get("tag")] = (ch.text or "").strip()
        rows.append(d)
    return pd.DataFrame(rows).set_index("title")


def load_counts(cache, bc, gn):
    """Two streaming passes over the MatrixMarket file (genes x cells, 1-based)."""
    NG, NC = len(gn), len(bc)
    g_sum = np.zeros(NG); g_nnz = np.zeros(NG, dtype=np.int64)
    tot = 0
    with gzip.open(cache / F227["mtx"], "rt") as fh:
        h1 = fh.readline(); h2 = fh.readline()
        assert h1.startswith("%%MatrixMarket") and h2.split() == [str(NG), str(NC), str(NNZ_227)], (h1, h2)
        for ch in pd.read_csv(fh, sep=" ", header=None, names=["g", "c", "v"],
                              dtype={"g": np.int32, "c": np.int32, "v": np.float32}, chunksize=30_000_000):
            gi = ch["g"].values - 1; v = ch["v"].values.astype(np.float64)
            np.add.at(g_sum, gi, v); np.add.at(g_nnz, gi, 1)
            tot += len(ch); del ch, gi, v
    assert tot == NNZ_227, tot
    u227 = set(gn)
    mean_g = g_sum / NC
    expressed = np.where(g_nnz >= 30)[0]
    hv = expressed[np.argsort(mean_g[expressed])[::-1][:3000]]
    need = set()
    for g in CORE6 + CTA_PROF + PROLIF:
        r = resolve(g, u227)
        if r: need.add(r)
    for v in MARKERS_PROF.values():
        need |= {x for x in v if x in u227}
    need |= EXTRA_GENES & u227
    keep = np.array(sorted(set(hv.tolist()) | {i for i, g in enumerate(gn) if g in need}))

    rows_l, cols_l, vals_l = [], [], []
    with gzip.open(cache / F227["mtx"], "rt") as fh:
        fh.readline(); fh.readline()
        for ch in pd.read_csv(fh, sep=" ", header=None, names=["g", "c", "v"],
                              dtype={"g": np.int32, "c": np.int32, "v": np.float32}, chunksize=30_000_000):
            gi = ch["g"].values - 1
            m = np.isin(gi, keep)
            if m.any():
                rows_l.append(gi[m]); cols_l.append(ch["c"].values[m] - 1); vals_l.append(ch["v"].values[m])
            del ch, gi, m
    gi_all = np.concatenate(rows_l); ci_all = np.concatenate(cols_l); v_all = np.concatenate(vals_l)
    del rows_l, cols_l, vals_l
    remap = np.full(NG, -1, dtype=np.int32); remap[keep] = np.arange(len(keep))
    X = sp.csr_matrix((v_all, (remap[gi_all], ci_all)), shape=(len(keep), NC))
    return X, gn[keep]


def gene_positions(genes, cache):
    posf = cache / "gse182227_gene_positions.json"
    if posf.exists():
        return json.load(open(posf))
    pos_map, gl = {}, list(genes)
    for i in range(0, len(gl), 500):
        batch = gl[i:i + 500]
        for attempt in range(3):
            try:
                rr = requests.post("https://rest.ensembl.org/lookup/symbol/homo_sapiens",
                                   headers={"Content-Type": "application/json"},
                                   data=json.dumps({"symbols": batch}), timeout=120)
                if rr.status_code == 200:
                    for k, v in rr.json().items():
                        if isinstance(v, dict) and v.get("seq_region_name"):
                            pos_map[k] = (v["seq_region_name"], v["start"])
                    break
            except Exception:
                time.sleep(3)
        time.sleep(0.4)
    json.dump(pos_map, open(posf, "w"))
    return pos_map


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", default="DATA/meiotic")
    ap.add_argument("--out", default=str(REPO / "results" / "meiotic_programme" / "gse182227"))
    ap.add_argument("--panels", action="store_true", help="also write per-panel 600 dpi files (Figure 7 folder)")
    a = ap.parse_args()
    cache, out = Path(a.data), Path(a.out)
    cache.mkdir(parents=True, exist_ok=True); out.mkdir(parents=True, exist_ok=True)
    install_export_hook(out, str(REPO / "figures" / "source_panels_600dpi") if a.panels else None,
                        {"fig_182227": "Figure 7"}, dpi=600)
    T0 = time.time()

    log("GSE181919 - per-tumour scores")
    PT = gse181919_per_tumour(cache)
    PT.to_csv(out / "per_tumour_181919.csv", index=False)

    log("GSE182227 - download and sample sheet")
    fetch_182227(cache)
    bc = [l.decode().strip() for l in gzip.open(cache / F227["barcodes"])]
    gn = np.array([l.decode().strip() for l in gzip.open(cache / F227["genes"])])
    smi = sample_sheet(cache)
    bpref = [b.rsplit("_", 1)[0] for b in bc]
    assert set(PREF2SAMPLE) == set(bpref), set(PREF2SAMPLE) ^ set(bpref)
    meta227 = pd.DataFrame({"barcode": bc, "prefix": bpref, "sample": [PREF2SAMPLE[p] for p in bpref]})
    meta227["patient"] = meta227["sample"].str.split("-").str[0]
    meta227["hpv"] = smi.loc[meta227["sample"], "hpv status"].values
    meta227["tissue"] = smi.loc[meta227["sample"], "tissue"].values

    log("GSE182227 - counts (two passes over the matrix)")
    X227, genes227 = load_counts(cache, bc, gn)
    u227 = set(genes227)
    Xln227 = pa.normalize_log(sp.csr_matrix(X227.T))            # cells x genes
    del X227

    log("GSE182227 - PCA and Leiden clustering")
    from sklearn.decomposition import PCA
    from sklearn.neighbors import NearestNeighbors
    import igraph as ig, leidenalg as la
    mu = np.asarray(Xln227.mean(axis=0)).ravel()
    sq = np.asarray(Xln227.multiply(Xln227).mean(axis=0)).ravel()
    hvi = np.argsort(sq - mu ** 2)[::-1][:2000]
    Xh = np.asarray(Xln227[:, hvi].todense())
    Xh = (Xh - Xh.mean(0)) / (Xh.std(0) + 1e-8)
    np.clip(Xh, -10, 10, out=Xh)
    pcs227 = PCA(n_components=40, random_state=RANDOM_SEED).fit_transform(Xh)
    del Xh
    idx = NearestNeighbors(n_neighbors=15, n_jobs=4).fit(pcs227).kneighbors(pcs227)[1]
    src = np.repeat(np.arange(pcs227.shape[0]), 14); dst = idx[:, 1:].ravel()
    g = ig.Graph(n=pcs227.shape[0], edges=list(zip(src.tolist(), dst.tolist())), directed=False)
    g.simplify()
    clust = np.array(la.find_partition(g, la.RBConfigurationVertexPartition,
                                       resolution_parameter=1.0, seed=RANDOM_SEED).membership)
    log(f"  {clust.max() + 1} clusters")

    # ---- lineages from marker means per cluster
    idx227 = {g_: i for i, g_ in enumerate(genes227)}
    def clust_mean(gene_list):
        cols = [idx227[x] for x in gene_list if x in idx227]
        if not cols: return np.zeros(clust.max() + 1)
        v = np.asarray(Xln227[:, cols].mean(axis=1)).ravel()
        return np.array([v[clust == k].mean() for k in range(clust.max() + 1)])
    LIN = dict(MARKERS_PROF)
    LIN["Myeloid"] = ["LST1", "CD68", "LYZ", "CD14"]; LIN["Mast"] = ["TPSAB1", "CPA3"]; LIN["NK"] = ["NKG7", "GNLY"]
    S = pd.DataFrame({k: clust_mean(v) for k, v in LIN.items()})
    ptprc = clust_mean(["PTPRC"]); epi = clust_mean(["EPCAM", "KRT8", "KRT18", "KRT19"])
    def assign_lineage(k):
        e, p = epi[k], ptprc[k]; raw = S.iloc[k]
        if e > 0.5 and p < 0.4: return "Epithelial"
        if p < 0.3 and e < 0.5: return "Fibroblast" if raw["Fibroblast"] > raw["Endothelial"] else "Endothelial"
        return raw[["T", "B", "Plasma", "Myeloid", "Mast", "NK"]].idxmax()
    lineage = np.array([assign_lineage(k) for k in range(clust.max() + 1)])[clust]
    meta227["cluster"] = clust; meta227["lineage"] = lineage
    mk = []
    for lin, gl in LIN.items():
        present = [x for x in gl if x in idx227]
        if not present: continue
        v = np.asarray(Xln227[:, [idx227[x] for x in present]].mean(axis=1)).ravel()
        inn, outv = v[lineage == lin].mean(), v[lineage != lin].mean()
        mk.append({"lineage": lin, "genes": ",".join(present), "n_cells": int((lineage == lin).sum()),
                   "mean_in": inn, "mean_out": outv, "enrichment": inn / max(outv, 1e-9)})
    pd.DataFrame(mk).sort_values("enrichment", ascending=False).to_csv(out / "marker_check_182227.csv", index=False)

    # ---- inferred CNV for epithelial cells
    log("GSE182227 - inferred CNV and malignant-cell calls")
    ep = lineage == "Epithelial"
    ed = meta227[ep].copy()
    pos_map = gene_positions(genes227, cache)
    CHRS = [str(i) for i in range(1, 23)]
    mapped = {x: pos_map[x] for x in genes227 if x in pos_map and pos_map[x][0] in CHRS}
    ord_g = sorted(mapped, key=lambda x: (CHRS.index(mapped[x][0]), mapped[x][1]))
    chrom = np.array([mapped[x][0] for x in ord_g])
    ref_mask = np.isin(lineage, ["T", "B", "Myeloid", "NK", "Plasma", "Mast", "Endothelial", "Fibroblast"])
    E = Xln227[:, [idx227[x] for x in ord_g]]
    ref_mean = np.asarray(E[ref_mask].mean(axis=0)).ravel()
    def cnv_profile(rows):
        Am = np.asarray(E[rows].todense()) - ref_mean
        np.clip(Am, -3, 3, out=Am)
        o = np.zeros((Am.shape[0], len(CHRS)), dtype=np.float32)
        for j, c in enumerate(CHRS):
            m = chrom == c
            if m.sum() >= 20: o[:, j] = Am[:, m].mean(axis=1)
        return o
    ep_idx = np.where(ep)[0]
    cnv_score = np.abs(np.vstack([cnv_profile(ep_idx[i:i + 4000]) for i in range(0, len(ep_idx), 4000)])).mean(axis=1)
    sub_ref = np.random.default_rng(0).choice(np.where(ref_mask)[0], 6000, replace=False)
    ref_score = np.abs(cnv_profile(sub_ref)).mean(axis=1)

    nrm_ep = ed[ed.tissue == "adjacent normal tissue"]
    crit = []
    for k in sorted(ed.cluster.unique()):
        s = meta227[meta227.cluster == k]
        n_adjn = int((s.tissue == "adjacent normal tissue").sum())
        crit.append({"cluster": k, "n": len(s), "n_patients": s.patient.nunique(), "n_adj_normal": n_adjn,
                     "frac_of_all_adjnormal": n_adjn / len(nrm_ep),
                     "pct_tumour_tissue": 100 * (s.tissue == "tumor").mean(),
                     "cnv": cnv_score[ed.cluster.values == k].mean()})
    cr = pd.DataFrame(crit)
    cr["is_normal"] = (cr.frac_of_all_adjnormal >= 0.10) & (cr.cnv <= np.quantile(ref_score, 0.55))
    cr.to_csv(out / "epithelial_cluster_calls_182227.csv", index=False)
    is_mal = ep & ~np.isin(clust, cr.loc[cr.is_normal, "cluster"].tolist()) & (meta227.tissue.values == "tumor")
    meta227["is_malignant"] = is_mal
    log(f"  malignant cells {int(is_mal.sum())} | normal epithelium {int((ep & ~is_mal).sum())} | "
        f"non-tumour cells called malignant {int(((meta227.tissue != 'tumor') & is_mal).sum())}")

    # ---- module scores
    sets = {"core6": [resolve(x, u227) for x in CORE6], "spec4": [resolve(x, u227) for x in SPECIFIC4],
            "cta": [resolve(x, u227) for x in CTA_PROF], "prolif": [resolve(x, u227) for x in PROLIF]}
    arr = {k: pa.score_genes(Xln227, genes227, v)[0] for k, v in sets.items()}
    arr["det"] = np.asarray((Xln227[:, [idx227[x] for x in sets["spec4"]]] > 0).sum(axis=1)).ravel() > 0
    grp = np.where(is_mal, "Malignant", np.where(ep, "Normal epithelium", lineage))
    gt = pd.DataFrame({"group": grp, "core6": arr["core6"], "spec4": arr["spec4"], "det": arr["det"]}).groupby("group").agg(
        n=("core6", "size"), mean_core6=("core6", "mean"), mean_spec4=("spec4", "mean"),
        pct_detect=("det", lambda v: 100 * v.mean())).sort_values("mean_spec4", ascending=False)
    gt.to_csv(out / "celltype_scores_182227.csv")

    # ---- tumours, contrasts, pooled models
    pt227 = per_tumour(meta227, is_mal, arr); pt227["dataset"] = "GSE182227"
    pt227.to_csv(out / "per_tumour_182227.csv", index=False)
    h27 = contrasts(pt227); h19 = contrasts(PT)
    contr = pd.concat([h19.assign(dataset="GSE181919"), h27.assign(dataset="GSE182227")], ignore_index=True)
    contr.to_csv(out / "hpv_contrast_both.csv", index=False)
    comb = pd.concat([PT[PT_COLS], pt227[PT_COLS]], ignore_index=True)
    comb.to_csv(out / "per_tumour_combined.csv", index=False)
    rows = []
    for ds, d in [("GSE181919", PT), ("GSE182227", pt227), ("both", comb)]:
        for yv in ["mean_meiotic6", "mean_meiotic4"]:
            for form, lab in [(f"{yv} ~ is_hpv_positive", "unadjusted"),
                              (f"{yv} ~ is_hpv_positive + mean_prolif", "adjusted for proliferation")]:
                mm = smf.ols(form + (" + C(dataset)" if ds == "both" else ""), data=d).fit()
                rows.append({"dataset": ds, "outcome": yv, "model": lab, "n": int(mm.nobs),
                             "beta_HPV": mm.params["is_hpv_positive"], "se": mm.bse["is_hpv_positive"],
                             "p_HPV": mm.pvalues["is_hpv_positive"],
                             "beta_prolif": mm.params.get("mean_prolif", np.nan),
                             "p_prolif": mm.pvalues.get("mean_prolif", np.nan), "r2": mm.rsquared})
    reg = pd.DataFrame(rows); reg.to_csv(out / "regression_adjusted.csv", index=False)
    F = "mean_meiotic4 ~ is_hpv_positive + mean_prolif + C(dataset)"
    m = smf.ols(F, data=comb).fit(); i = list(m.params.index).index("is_hpv_positive")
    hc3 = m.get_robustcov_results(cov_type="HC3")
    mr = smf.rlm(F, data=comb, M=sm_api.robust.norms.HuberT()).fit()
    loo = [smf.ols(F, data=comb.drop(k)).fit().params["is_hpv_positive"] for k in comb.index]
    pd.DataFrame([
        {"estimator": "OLS", "beta": m.params["is_hpv_positive"], "se": m.bse["is_hpv_positive"], "p": m.pvalues["is_hpv_positive"]},
        {"estimator": "OLS + HC3 robust SE", "beta": hc3.params[i], "se": hc3.bse[i], "p": hc3.pvalues[i]},
        {"estimator": "Huber robust regression", "beta": mr.params["is_hpv_positive"], "se": mr.bse["is_hpv_positive"],
         "p": mr.pvalues["is_hpv_positive"]},
        {"estimator": "leave-one-tumour-out OLS (min..max)", "beta": min(loo), "se": max(loo), "p": np.nan},
    ]).to_csv(out / "regression_diagnostics.csv", index=False)
    ms = (meta227[is_mal].groupby(["patient", "hpv"]).size().reset_index(name="n_malignant"))
    allp = meta227[meta227.tissue == "tumor"].groupby(["patient", "hpv"]).size().reset_index(name="n_total")
    ms = allp.merge(ms, on=["patient", "hpv"], how="left").fillna({"n_malignant": 0})
    ms["pct_malignant"] = 100 * ms.n_malignant / ms.n_total
    ms.to_csv(out / "malignant_calls_182227.csv", index=False)

    # ---- headline values quoted in the manuscript
    pm = reg[(reg.dataset == "both") & (reg.outcome == "mean_meiotic4")]
    u_, a_ = pm[pm.model == "unadjusted"].iloc[0], pm[pm.model != "unadjusted"].iloc[0]
    att = lambda ds: float(100 * (1 - reg[(reg.dataset == ds) & (reg.outcome == "mean_meiotic4") & (reg.model != "unadjusted")].beta_HPV.iloc[0]
                                  / reg[(reg.dataset == ds) & (reg.outcome == "mean_meiotic4") & (reg.model == "unadjusted")].beta_HPV.iloc[0]))
    V = {"n_cells": int(len(meta227)), "n_malignant": int(is_mal.sum()),
         "n_normal_epithelium": int((ep & ~is_mal).sum()),
         "pct_detect_malignant": float(gt.loc["Malignant", "pct_detect"]),
         "pct_detect_normal_epithelium": float(gt.loc["Normal epithelium", "pct_detect"]),
         "n_tumours_182227": int(len(pt227)), "n_tumours_181919": int(len(PT)),
         "contrasts": contr.to_dict(orient="records"),
         "pooled_m4_beta_unadjusted": float(u_.beta_HPV), "pooled_m4_p_unadjusted": float(u_.p_HPV),
         "pooled_m4_beta_adjusted": float(a_.beta_HPV), "pooled_m4_p_adjusted": float(a_.p_HPV),
         "pooled_prolif_beta": float(a_.beta_prolif), "pooled_prolif_p": float(a_.p_prolif),
         "attenuation_pct_pooled": float(100 * (1 - a_.beta_HPV / u_.beta_HPV)),
         "attenuation_pct_182227": att("GSE182227"), "attenuation_pct_181919": att("GSE181919"),
         "hc3_p": float(hc3.pvalues[i]), "huber_beta": float(mr.params["is_hpv_positive"]),
         "huber_p": float(mr.pvalues["is_hpv_positive"]), "loo_beta_range": [float(min(loo)), float(max(loo))]}
    json.dump(V, open(out / "gse182227_values.json", "w"), indent=1, default=float)

    # ---- figure
    log("GSE182227 - UMAP and figure")
    import umap
    emb227 = umap.UMAP(n_neighbors=15, min_dist=0.3, random_state=RANDOM_SEED).fit_transform(pcs227)
    fig_gse182227.build(emb227, lineage, is_mal, grp, arr["core6"], arr["spec4"], arr["cta"], arr["prolif"],
                        arr["det"], meta227, pt227, comb, reg, str(out / "fig_182227.png"))
    log(f"done in {time.time() - T0:.0f} s; outputs in {out}/")


if __name__ == "__main__":
    main()
