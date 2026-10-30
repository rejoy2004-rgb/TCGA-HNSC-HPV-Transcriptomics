"""Fetch TCGA-HNSC (hnsc_tcga) gene-level data from cBioPortal: RSEM all-sample Z-scores for the core,
proliferation and B/plasma marker genes, and gene-level HM450 methylation for the core genes.
Usage: python tcga_fetch.py <data_dir>   (writes <data_dir>/tcga/*.csv)"""
import json, os, sys, urllib.request
import pandas as pd

OUT = os.path.join(sys.argv[1], "tcga"); os.makedirs(OUT, exist_ok=True)
API = "https://www.cbioportal.org/api"
CORE = ["MEI1", "SMC1B", "STAG3", "SYCP2", "SYCE2", "MAJIN", "MKI67", "PCNA", "TOP2A", "CCNB1", "BUB1", "AURKA"]
BMARK = ["CD19", "CD79A", "JCHAIN", "MS4A1", "MZB1"]


def post(url, body):
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "Accept": "application/json", "User-Agent": "Mozilla/5.0"})
    return json.load(urllib.request.urlopen(req, timeout=300))


def fetch(profile, symbols, path):
    ent = {g["entrezGeneId"]: g["hugoGeneSymbol"] for g in post(f"{API}/genes/fetch?geneIdType=HUGO_GENE_SYMBOL", symbols)}
    rows = post(f"{API}/molecular-profiles/{profile}/molecular-data/fetch?projection=SUMMARY",
                {"entrezGeneIds": list(ent), "sampleListId": "hnsc_tcga_all"})
    df = pd.DataFrame([(r["sampleId"], ent[r["entrezGeneId"]], r["value"]) for r in rows], columns=["sample", "gene", "value"])
    wide = df.pivot_table(index="sample", columns="gene", values="value", aggfunc="first")
    wide.to_csv(path); print(path, wide.shape)


Z = "hnsc_tcga_rna_seq_v2_mrna_median_all_sample_Zscores"
fetch(Z, CORE, f"{OUT}/{Z}.csv")
fetch(Z, BMARK, f"{OUT}/{Z}_bmarkers.csv")
fetch("hnsc_tcga_methylation_hm450", CORE, f"{OUT}/hnsc_tcga_methylation_hm450.csv")
