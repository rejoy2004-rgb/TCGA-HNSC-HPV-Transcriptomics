"""Fetch GDC STAR unstranded counts for the 279 TCGA-HNSC tumours of the final cohort and write the normalised
ZFR2 expression (DESeq2 median-of-ratios) with overall-survival time/status, for the exploratory ZFR2 Kaplan-Meier plot.
Because DESeq2's variance-stabilising transformation is monotone in normalised counts, a median split on normalised
counts gives the same High/Low ZFR2 groups as a median split on VST values.
Usage: python km_zfr2_counts.py <repo> <work_dir>
Writes <work_dir>/counts.pkl (genes x samples) and, in <repo>/results/review_sensitivity/, ZFR2_KM_input.csv (Supplementary Fig. S7)
and CD8_validation_input.csv (Supplementary Fig. S5). Counts are cached in <work_dir>, so a second run needs no download."""
import json, os, sys, urllib.parse, urllib.request, concurrent.futures as cf
import numpy as np, pandas as pd

REPO, W = sys.argv[1], sys.argv[2]
os.makedirs(W, exist_ok=True)
cohort = pd.read_csv(f"{REPO}/results/HNSC_Final_Cohort.csv", dtype=str)
bc = list(cohort["barcode"])
print(len(bc), bc[:2], flush=True)
UA = {"User-Agent": "Mozilla/5.0"}
if not os.path.exists(f"{W}/files.json"):
    flt = {"op": "and", "content": [
        {"op": "=", "content": {"field": "cases.project.project_id", "value": "TCGA-HNSC"}},
        {"op": "=", "content": {"field": "data_type", "value": "Gene Expression Quantification"}},
        {"op": "=", "content": {"field": "analysis.workflow_type", "value": "STAR - Counts"}},
        {"op": "in", "content": {"field": "cases.samples.portions.analytes.aliquots.submitter_id", "value": bc}}]}
    q = {"filters": flt, "size": "1000", "format": "JSON", "fields": "file_id,cases.samples.portions.analytes.aliquots.submitter_id"}
    req = urllib.request.Request("https://api.gdc.cancer.gov/files", data=json.dumps(q).encode(), headers={**UA, "Content-Type": "application/json"})
    hits = json.load(urllib.request.urlopen(req))["data"]["hits"]
    json.dump(hits, open(f"{W}/files.json", "w"))
hits = json.load(open(f"{W}/files.json"))
fmap = {}
for h in hits:
    for s in h["cases"][0]["samples"]:
        for p in s["portions"]:
            for a in p["analytes"]:
                for al in a["aliquots"]:
                    if al["submitter_id"] in bc: fmap[al["submitter_id"]] = h["file_id"]
print("files matched", len(fmap), "of", len(bc), flush=True)


def get(item):
    b, fid = item
    for _ in range(4):
        try:
            txt = urllib.request.urlopen(urllib.request.Request(f"https://api.gdc.cancer.gov/data/{fid}", headers=UA), timeout=600).read().decode()
            d = {}
            for line in txt.splitlines():
                if line.startswith("ENSG"):
                    f = line.split("\t"); d[f[0]] = float(f[3])   # unstranded counts
            return b, d
        except Exception:
            pass
    return b, None


cols = {}
if os.path.exists(f"{W}/counts.pkl"):
    fmap = {}
with cf.ThreadPoolExecutor(8) as ex:
    for i, (b, d) in enumerate(ex.map(get, list(fmap.items()))):
        if d is None: print("FAILED", b, flush=True)
        else: cols[b] = d
        if i % 25 == 0: print(i, flush=True)
if os.path.exists(f"{W}/counts.pkl") and not cols:
    M = pd.read_pickle(f"{W}/counts.pkl")
else:
    M = pd.DataFrame(cols)
    M.to_pickle(f"{W}/counts.pkl")
print(M.shape)

# ---- DESeq2 median-of-ratios size factors (genes with non-zero counts in every sample) and normalised counts
M.index = [i.split(".")[0] for i in M.index]
nz = M[(M > 0).all(axis=1)]
lg = np.log(nz)
sf = np.exp(lg.sub(lg.mean(axis=1), axis=0).median(axis=0))
N = M / sf
ZFR2, CD8A, CD8B = "ENSG00000105278", "ENSG00000153563", "ENSG00000172116"

# ---- overall survival (same rule as scripts/HPV_HNSC_Revision.R) and High/Low ZFR2 median split
cl = pd.read_csv(f"{REPO}/data_raw/data_clinical_patient_full.txt", sep="	", skiprows=4)
d = pd.DataFrame({"barcode": N.columns, "ZFR2_normalised_count": N.loc[ZFR2].values})
d["PATIENT_ID"] = d.barcode.str[:12]
d = d.merge(cl[["PATIENT_ID", "OS_STATUS", "OS_MONTHS"]], on="PATIENT_ID")
d["OS_event"] = d.OS_STATUS.astype(str).str.contains("DECEASED|DEAD|1").astype(int)
d["OS_months"] = pd.to_numeric(d.OS_MONTHS, errors="coerce")
d = d.dropna(subset=["OS_months"])
d["group"] = np.where(d.ZFR2_normalised_count > d.ZFR2_normalised_count.median(), "High ZFR2", "Low ZFR2")
os.makedirs(f"{REPO}/results/review_sensitivity", exist_ok=True)
d[["barcode", "ZFR2_normalised_count", "OS_months", "OS_event", "group"]].to_csv(f"{REPO}/results/review_sensitivity/ZFR2_KM_input.csv", index=False)
print("ZFR2 KM input", d.shape, d.group.value_counts().to_dict())

# ---- CIBERSORTx CD8+ T-cell fraction against CD8A / CD8B
job = pd.read_csv(f"{REPO}/data_processed/CIBERSORTx_Job14_Results.csv")
job["s"] = job["Mixture"].str[:15]
c = pd.DataFrame({"barcode": N.columns, "s": [x[:15] for x in N.columns],
                  "CD8A_normalised_count": N.loc[CD8A].values, "CD8B_normalised_count": N.loc[CD8B].values})
c = c.merge(job[["s", "T cells CD8"]], on="s").rename(columns={"T cells CD8": "CIBERSORTx_CD8_T_cells"}).drop(columns="s")
c.to_csv(f"{REPO}/results/review_sensitivity/CD8_validation_input.csv", index=False)
print("CD8 validation input", c.shape)
