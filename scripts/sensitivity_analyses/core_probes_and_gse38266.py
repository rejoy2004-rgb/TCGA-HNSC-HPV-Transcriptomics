"""Core-gene HM450 probe list (all annotated probes and promoter probes: 1,500 bp upstream to 500 bp downstream
of an annotated TSS; SeSAMe HM450 GENCODE v36 manifest) and the GSE38266 β values for those probes.
Inputs in <data_dir>/geo: HM450.hg38.manifest.gencode.v36.tsv.gz
  (https://github.com/zhou-lab/InfiniumAnnotationV1/raw/main/Anno/HM450/HM450.hg38.manifest.gencode.v36.tsv.gz)
  and GSE38266_series_matrix.txt.gz (GEO).
Usage: python core_probes_and_gse38266.py <data_dir>"""
import gzip, io, sys
import pandas as pd

D = sys.argv[1] + "/geo"
CORE = ["MEI1", "SMC1B", "STAG3", "SYCP2", "SYCE2", "MAJIN"]
a = pd.read_csv(f"{D}/HM450.hg38.manifest.gencode.v36.tsv.gz", sep="\t", usecols=["probeID", "geneNames", "transcriptTypes", "distToTSS"]).dropna(subset=["geneNames"])
rows = []
for r in a.itertuples():
    for g, dist in zip(r.geneNames.split(";"), str(r.distToTSS).split(";")):
        if g in CORE:
            rows.append((r.probeID, g, int(dist)))
df = pd.DataFrame(rows, columns=["ID", "gene", "dist"])
per = df.groupby(["ID", "gene"]).agg(mindist=("dist", lambda x: min(x, key=abs)), prom=("dist", lambda x: any(-1500 <= v <= 500 for v in x))).reset_index()
per.to_csv(f"{D}/gpl13534_core.tsv", sep="\t", index=False)
print(per.groupby("gene").agg(all=("ID", "size"), promoter=("prom", "sum")))

ids, titles, header, lines, intab = set(per.ID), None, None, [], False
for l in gzip.open(f"{D}/GSE38266_series_matrix.txt.gz", "rt"):
    if l.startswith("!Sample_title"):
        titles = [x.strip('"\n') for x in l.split("\t")[1:]]
    elif l.startswith('"ID_REF"'):
        header = [x.strip('"\n') for x in l.split("\t")]; intab = True
    elif l.startswith("!series_matrix_table_end"):
        break
    elif intab and l.split("\t", 1)[0].strip('"') in ids:
        lines.append(l)
b = pd.read_csv(io.StringIO("".join(lines)), sep="\t", header=None, index_col=0)
b.index = b.index.str.strip('"'); b.columns = header[1:]
grp = pd.Series(["HPV+" if t.startswith("HPV+") else ("HPV-" if t.startswith("HPV-") else "other") for t in titles], index=header[1:])
b.to_csv(f"{D}/gse38266_core_probes.csv"); grp.to_csv(f"{D}/gse38266_groups.csv")
print(grp.value_counts().to_dict(), b.shape)
