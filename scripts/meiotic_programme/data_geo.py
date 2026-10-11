"""GEO loaders: series-matrix parsing, HM450 probe map, GSE65858, GSE38266 and GSE181919."""
from __future__ import annotations

from .config import *  # noqa: F401,F403
from .helpers import *  # noqa: F401,F403

# ============================================================================
# STEP 2 - GSE65858 validation cohort (Illumina HT-12 microarray)
# ============================================================================

def parse_series_matrix(path: Path) -> tuple[list[str], pd.DataFrame]:
    """Split a GEO series-matrix file into its !-metadata and its data block."""
    meta: list[str] = []
    with gzip.open(path, "rt", errors="replace") as fh:
        for line in fh:
            if line.startswith("!series_matrix_table_begin"):
                break
            meta.append(line.rstrip("\n"))
        buf = io.StringIO()
        for line in fh:
            if line.startswith("!series_matrix_table_end"):
                break
            buf.write(line)
    buf.seek(0)
    data = pd.read_csv(buf, sep="\t", index_col=0, low_memory=False)
    data.index = data.index.astype(str).str.strip('"')
    data.columns = [c.strip('"') for c in data.columns]
    return meta, data


def meta_field(meta: list[str], key: str) -> list[str]:
    for line in meta:
        if line.startswith(key):
            return re.findall(r'"([^"]*)"', line)
    return []


def build_probe_map(annot_gz: Path, id_col: str, sym_col: str) -> pd.Series:
    """probe -> gene symbol from a GEO platform .annot file."""
    with gzip.open(annot_gz, "rt", errors="replace") as fh:
        lines = fh.readlines()
    hdr_i = next(i for i, l in enumerate(lines) if l.startswith(f"{id_col}\t"))
    hdr = lines[hdr_i].rstrip("\n").split("\t")
    ai, si = hdr.index(id_col), hdr.index(sym_col)
    pairs = []
    for line in lines[hdr_i + 1:]:
        if line.startswith("!") or not line.strip():
            continue
        p = line.rstrip("\n").split("\t")
        if len(p) > si and p[si]:
            pairs.append((p[ai], p[si].split("///")[0].strip()))
    return pd.Series(dict(pairs))



def load_gse65858(cache: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (gene x sample expression, clinical) for GSE65858."""
    expr_out, clin_out = cache / "gse65858_expr.csv", cache / "gse65858_clinical.csv"
    if expr_out.exists() and clin_out.exists():
        log("  cached: GSE65858")
        return pd.read_csv(expr_out, index_col=0), pd.read_csv(clin_out)

    mx = download(f"{GEO}/series/GSE65nnn/GSE65858/matrix/GSE65858_series_matrix.txt.gz",
                  cache / "GSE65858_series_matrix.txt.gz")
    an = download(f"{GEO}/platforms/GPL10nnn/GPL10558/annot/GPL10558.annot.gz",
                  cache / "GPL10558.annot.gz")
    meta, data = parse_series_matrix(mx)

    gsms = meta_field(meta, "!Sample_geo_accession")
    chars = [l for l in meta if l.startswith("!Sample_characteristics_ch1")]
    fields: dict[str, list[str]] = {}
    for line in chars:
        vals = re.findall(r'"([^"]*)"', line)
        if not vals:
            continue
        key = vals[0].split(":")[0].strip().lower().replace(" ", "_")
        fields[key] = [v.split(":", 1)[1].strip() if ":" in v else "" for v in vals]

    clin = pd.DataFrame({"gsm": gsms})
    for k, v in fields.items():
        if len(v) == len(gsms):
            clin[k] = v

    def pick(*cands: str) -> pd.Series:
        for c in cands:
            for col in clin.columns:
                if c in col:
                    return clin[col]
        return pd.Series([""] * len(clin))

    clin["tumor_site"] = pick("tumor_site", "site", "localisation").astype(str)
    clin["hpv_dna"] = pick("hpv_dna").astype(str).str.lower()
    clin["hpv_rna"] = pick("hpv16_dna_rna", "rna").astype(str).str.lower()
    clin["os"] = pd.to_numeric(pick("os_month", "os"), errors="coerce")
    clin["os_event"] = pd.to_numeric(pick("os_event", "death"), errors="coerce")

    dna_pos = clin.hpv_dna.str.contains("pos|1|yes", na=False)
    active = clin.hpv_rna.str.contains("pos|dna\\+rna\\+|1", na=False)
    clin["hpv_dna_pos"] = dna_pos
    clin["hpv_active"] = dna_pos & active
    clin["hpv_group"] = np.where(
        clin.hpv_active, "HPV+ active",
        np.where(dna_pos, "HPV+ silent",
                 np.where(clin.hpv_dna.str.contains("neg|0|no", na=False), "HPV-", "unknown")))

    # probes -> symbols, keeping the highest-variance probe per gene
    pmap = build_probe_map(an, "ID", "Gene symbol")
    data = data.apply(pd.to_numeric, errors="coerce")
    keep = data.index.intersection(pmap.index)
    data = data.loc[keep]
    sym = pmap.loc[keep]
    var = data.var(axis=1)
    best = var.groupby(sym.values).idxmax()
    expr = data.loc[best.values]
    expr.index = best.index

    expr.to_csv(expr_out)
    clin.to_csv(clin_out, index=False)
    log(f"  GSE65858: {expr.shape[0]:,} genes x {expr.shape[1]} samples; "
        f"groups = {clin.hpv_group.value_counts().to_dict()}")
    return expr, clin


# ============================================================================
# STEP 3 - GSE38266 methylation replication (HM450, all oropharyngeal)
# ============================================================================

def load_gse38266(cache: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return (beta matrix, clinical, promoter probe->gene map) for GSE38266.

    NOTE (added for the shareable package; not part of the original analysis):
    this loader originally had no cache check, so every run re-downloaded
    ~151 MB of raw archives (87.6 MB series matrix + 64.0 MB HM450 manifest)
    to produce ~390 KB of derived output. The three derived frames are now
    cached on first run and reused thereafter, following the same pattern as
    load_gse65858(). The download path below is unchanged and is still used
    whenever the cache is absent, so behaviour from raw is identical. The
    cached beta matrix is subset to the promoter probes the analysis uses
    (823 of 485,577 rows); nothing downstream reads the other rows.
    """
    beta_out = cache / "gse38266_beta_panel.csv"
    clin_out = cache / "gse38266_clinical.csv"
    pm_out = cache / "probe_gene_map_450k.csv"
    if beta_out.exists() and clin_out.exists() and pm_out.exists():
        log("  cached: GSE38266 (derived; raw archives not required)")
        return (pd.read_csv(beta_out, index_col=0), pd.read_csv(clin_out),
                pd.read_csv(pm_out))

    mx = download(f"{GEO}/series/GSE38nnn/GSE38266/matrix/GSE38266_series_matrix.txt.gz",
                  cache / "GSE38266_series_matrix.txt.gz")
    # The HM450 *manifest* (~60 MB). Do NOT use GPL13534_family.soft.gz: that
    # bundles every sample ever run on the platform and is tens of GB.
    man = download(
        f"{GEO}/platforms/GPL13nnn/GPL13534/suppl/"
        "GPL13534_HumanMethylation450_15017482_v.1.1.csv.gz",
        cache / "GPL13534_manifest.csv.gz")

    meta, beta = parse_series_matrix(mx)
    beta = beta.apply(pd.to_numeric, errors="coerce")

    gsms = meta_field(meta, "!Sample_geo_accession")
    titles = meta_field(meta, "!Sample_title")
    clin = pd.DataFrame({"gsm": gsms, "title": titles})
    t = clin.title.str.lower()
    clin["hpv"] = np.where(t.str.contains(r"hpv[\s_+-]*pos|hpv\+"), "positive",
                           np.where(t.str.contains(r"hpv[\s_+-]*neg|hpv-"), "negative", "unknown"))
    clin = clin[clin.hpv != "unknown"]

    # probe -> gene, restricted to promoter-proximal regions
    rows = []
    with gzip.open(man, "rt", errors="replace") as fh:
        import csv as _csv
        hdr = None
        for i, line in enumerate(fh):
            if hdr is None:
                if line.startswith("IlmnID,"):
                    hdr = next(_csv.reader([line]))
                    iN = hdr.index("Name")
                    iG = hdr.index("UCSC_RefGene_Name")
                    iR = hdr.index("UCSC_RefGene_Group")
                continue
            if line.startswith("[Controls]"):
                break
            p = line.split(",")
            if len(p) <= max(iG, iR) or not p[iG]:
                continue
            hit = set(p[iG].split(";")) & set(ALL_GENES)
            if hit:
                rows.append((p[iN], sorted(hit)[0], p[iR]))
    pm = pd.DataFrame(rows, columns=["probe", "gene", "region"])
    pm = pm[pm.region.str.contains("TSS1500|TSS200|5'UTR|1stExon", na=False)]
    log(f"  GSE38266: {beta.shape[1]} samples; {len(clin)} with an HPV call; "
        f"{len(pm)} promoter probes over {pm.gene.nunique()} panel genes")

    # cache the derived frames (see the note in this function's docstring)
    beta.loc[beta.index.intersection(sorted(set(pm.probe)))].to_csv(beta_out)
    clin.to_csv(clin_out, index=False)
    pm.to_csv(pm_out, index=False)

    return beta, clin, pm



def build_sc_matrix(cache: Path) -> tuple:
    """Stream the dense published matrix into a sparse primary-tumour subset.

    GSE181919 ships genes x 54,239 cells as tab-delimited text (~1.5 GB
    uncompressed). Only primary-tumour ("CA") cells are analysed, so the file
    is parsed in row chunks and the retained columns stacked as CSR. The
    result is cached; re-runs load the checkpoint.
    """
    npz = cache / "sc_CA_counts.npz"
    gnp = cache / "sc_CA_genes.npy"
    mcsv = cache / "sc_CA_meta.csv"
    if npz.exists() and gnp.exists() and mcsv.exists():
        return (sp_sparse.load_npz(npz), np.load(gnp, allow_pickle=True),
                pd.read_csv(mcsv))

    meta = (pd.read_csv(cache / GSE181919_FILES["meta"], sep="\t")
            .reset_index().rename(columns={"index": "barcode"}))
    meta["barcode"] = meta["barcode"].str.replace("-", ".", regex=False)
    ca = meta[meta["tissue.type"] == "CA"].copy()

    with gzip.open(cache / GSE181919_FILES["counts"], "rt") as fh:
        barcodes = fh.readline().rstrip("\n").split("\t")
    pos = {b: i for i, b in enumerate(barcodes)}
    missing = [b for b in ca.barcode if b not in pos]
    assert not missing, f"{len(missing)} CA barcodes absent from counts header"

    keep = np.array([pos[b] for b in ca.barcode])
    order = np.argsort(keep)
    keep_sorted = keep[order]
    ca = ca.iloc[order].reset_index(drop=True)

    # The header names only the cell columns; data rows carry an extra leading
    # gene-name field that pandas treats as an implicit index. Typing must be
    # declared per barcode column or the gene names are coerced to int.
    dtypes = {b: np.int32 for b in barcodes}
    genes, blocks = [], []
    reader = pd.read_csv(cache / GSE181919_FILES["counts"], sep="\t", index_col=0,
                         header=0, chunksize=1000, dtype=dtypes)
    for chunk in reader:
        genes.extend(chunk.index.tolist())
        blocks.append(sp_sparse.csr_matrix(chunk.to_numpy()[:, keep_sorted]))

    X = sp_sparse.vstack(blocks, format="csr")
    genes = np.array(genes, dtype=object)
    sp_sparse.save_npz(npz, X)
    np.save(gnp, genes)
    ca.to_csv(mcsv, index=False)
    return X, genes, ca


def fetch_gse181919(cache: Path) -> None:
    """Download the deposited UMI matrix and barcode metadata (~1.2 GB)."""
    base = f"{GEO}/series/GSE181nnn/GSE181919/suppl"
    for fn in GSE181919_FILES.values():
        download(f"{base}/{fn}", cache / fn)
