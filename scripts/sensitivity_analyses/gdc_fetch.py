"""Download TCGA-HNSC HM450 beta files (GDC, SeSAMe level-3 betas) for primary tumours with a p16/ISH call and keep
only the core-gene probes listed in <data_dir>/geo/gpl13534_core.tsv (from core_probes_and_gse38266.py).
Usage: python gdc_fetch.py <data_dir> <repo>/data_raw   (writes <data_dir>/gdc/tcga_core_probe_betas.csv)"""
import json, os, sys, urllib.parse, urllib.request, concurrent.futures as cf
import numpy as np, pandas as pd

S, RAW = sys.argv[1], sys.argv[2]
os.makedirs(f"{S}/gdc", exist_ok=True)
if not os.path.exists(f"{S}/gdc/hm450_files.json"):
    flt = {"op": "and", "content": [
        {"op": "=", "content": {"field": "cases.project.project_id", "value": "TCGA-HNSC"}},
        {"op": "=", "content": {"field": "data_type", "value": "Methylation Beta Value"}},
        {"op": "=", "content": {"field": "platform", "value": "Illumina Human Methylation 450"}}]}
    q = {"filters": json.dumps(flt), "size": "2000", "format": "JSON",
         "fields": "file_id,file_name,file_size,cases.submitter_id,cases.samples.submitter_id,cases.samples.sample_type"}
    url = "https://api.gdc.cancer.gov/files?" + urllib.parse.urlencode(q)
    hits = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})))["data"]["hits"]
    json.dump(hits, open(f"{S}/gdc/hm450_files.json", "w"))
probes = set(pd.read_csv(f"{S}/geo/gpl13534_core.tsv", sep="\t", usecols=["ID"]).ID)
cl = pd.read_csv(f"{RAW}/data_clinical_patient_full.txt", sep="\t", comment="#", dtype=str)
called = set(cl.PATIENT_ID[(cl.HPV_STATUS_P16.isin(["Positive", "Negative"])) | (cl.HPV_STATUS_ISH.isin(["Positive", "Negative"]))])
hits = json.load(open(f"{S}/gdc/hm450_files.json"))
todo = []
for h in hits:
    smp = h["cases"][0]["samples"][0]
    if smp["sample_type"] == "Primary Tumor" and h["cases"][0]["submitter_id"] in called:
        todo.append((h["file_id"], smp["submitter_id"]))
print("files", len(todo), flush=True)


def get(item):
    fid, sid = item
    for _ in range(3):
        try:
            txt = urllib.request.urlopen(urllib.request.Request(f"https://api.gdc.cancer.gov/data/{fid}", headers={"User-Agent": "Mozilla/5.0"}), timeout=600).read().decode()
            vals = {}
            for line in txt.splitlines():
                p, _, v = line.partition("\t")
                if p in probes:
                    vals[p] = float(v) if v not in ("", "NA") else np.nan
            return sid, vals
        except Exception as e:
            err = e
    return sid, None


out = {}
with cf.ThreadPoolExecutor(8) as ex:
    for i, (sid, vals) in enumerate(ex.map(get, todo)):
        if vals is None:
            print("FAILED", sid, flush=True)
        else:
            out[sid] = vals
        if i % 20 == 0:
            print(i, flush=True)
pd.DataFrame(out).to_csv(f"{S}/gdc/tcga_core_probe_betas.csv")
print("done", len(out))
