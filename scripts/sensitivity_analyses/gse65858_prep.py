"""Build the GSE65858 gene-level matrix (probes collapsed by maximum mean intensity, GPL10558) and group labels:
active = HPV16 DNA+RNA+ (35), silent = HPV16 DNA+ without detected RNA (25), HPV- = DNA- (196).
Inputs in <data_dir>/geo: GSE65858_series_matrix.txt.gz and GPL10558.annot.gz (GEO).
Usage: python gse65858_prep.py <data_dir>/geo"""
import gzip, io, sys
import numpy as np, pandas as pd

D = sys.argv[1]
meta, lines, in_tab = {}, [], False
for l in gzip.open(f"{D}/GSE65858_series_matrix.txt.gz", "rt"):
    if l.startswith("!Sample_characteristics_ch1"):
        f = [x.strip('"\n') for x in l.split("\t")[1:]]
        meta[f[0].split(":")[0]] = [x.split(": ", 1)[1] if ": " in x else x for x in f]
    elif l.startswith("!Sample_geo_accession"):
        meta["gsm"] = [x.strip('"\n') for x in l.split("\t")[1:]]
    elif l.startswith("!series_matrix_table_begin"):
        in_tab = True
    elif l.startswith("!series_matrix_table_end"):
        break
    elif in_tab:
        lines.append(l)
expr = pd.read_csv(io.StringIO("".join(lines)), sep="\t", index_col=0)
meta = pd.DataFrame(meta).set_index("gsm")

ann_lines = [l for l in gzip.open(f"{D}/GPL10558.annot.gz", "rt") if not l.startswith(("!", "#", "^"))]
ann = pd.read_csv(io.StringIO("".join(ann_lines)), sep="\t", usecols=["ID", "Gene symbol"]).dropna()
ann = ann[~ann["Gene symbol"].str.contains("///")].set_index("ID")["Gene symbol"]
expr = expr.loc[expr.index.intersection(ann.index)]
expr["sym"] = ann.loc[expr.index].values
expr["mean"] = expr.drop(columns="sym").mean(axis=1)
gene = expr.sort_values("mean", ascending=False).drop_duplicates("sym").set_index("sym").drop(columns="mean")

def grp(r):
    if r["hpv_dna"] == "Negative" and r["hpv16_dna_rna"] == "DNA-": return "neg"
    if r["hpv_dna"] == "HPV16" and r["hpv16_dna_rna"] == "DNA+RNA+": return "active"
    if r["hpv_dna"] == "HPV16" and r["hpv16_dna_rna"] in ("DNA+RNA-", "NA"): return "silent"
    return None
meta["group"] = meta.apply(grp, axis=1)
meta = meta[meta.group.notna()]
gene = gene[meta.index]
print("range", float(gene.values.min()), float(gene.values.max()), gene.shape, meta.group.value_counts().to_dict())
gene.to_parquet(f"{D}/gse65858_gene.parquet"); meta.to_csv(f"{D}/gse65858_meta.csv")
