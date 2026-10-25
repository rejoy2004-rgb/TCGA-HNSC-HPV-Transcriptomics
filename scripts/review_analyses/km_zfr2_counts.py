"""Fetch GDC STAR unstranded counts for the 279 TCGA-HNSC tumours of the final cohort and write the normalised
ZFR2 expression (DESeq2 median-of-ratios) with overall-survival time/status, for the exploratory ZFR2 Kaplan-Meier plot.
Because DESeq2's variance-stabilising transformation is monotone in normalised counts, a median split on normalised
counts gives the same High/Low ZFR2 groups as a median split on VST values.
Usage: python km_zfr2_counts.py <repo> <work_dir>   (writes <work_dir>/zfr2_km_input.csv)"""
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
with cf.ThreadPoolExecutor(8) as ex:
    for i, (b, d) in enumerate(ex.map(get, list(fmap.items()))):
        if d is None: print("FAILED", b, flush=True)
        else: cols[b] = d
        if i % 25 == 0: print(i, flush=True)
M = pd.DataFrame(cols)
M.to_pickle(f"{W}/counts.pkl")
print(M.shape)
