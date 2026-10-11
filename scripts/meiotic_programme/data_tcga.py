"""TCGA-HNSC expression, HM450 methylation and HPV status from cBioPortal."""
from __future__ import annotations

from .config import *  # noqa: F401,F403
from .helpers import *  # noqa: F401,F403

# ============================================================================
# STEP 1 - TCGA-HNSC discovery cohort
# ============================================================================

def fetch_tcga_expression(cache: Path) -> tuple[pd.DataFrame, dict[str, int]]:
    """RSEM expression for the gene panel, TCGA-HNSC, via the cBioPortal API."""
    out = cache / "tcga_expression.csv"
    ids_file = cache / "tcga_gene_ids.json"
    if out.exists() and ids_file.exists():
        log("  cached: TCGA expression")
        return pd.read_csv(out, index_col=0), json.load(open(ids_file))

    log("  resolving gene symbols to Entrez IDs")
    genes = post_json("/genes/fetch?geneIdType=HUGO_GENE_SYMBOL",
                      ALL_GENES + PROLIFERATION + CD8_MARKERS + BPLASMA_MARKERS + ["CDKN2A"])
    resolved = {g["hugoGeneSymbol"]: g["entrezGeneId"] for g in genes}
    missing = sorted(set(ALL_GENES) - set(resolved))
    log(f"  resolved {len(resolved)} symbols; {len(missing)} unresolved: {missing}")

    log("  fetching RSEM expression (this is the slow call)")
    data = post_json(
        "/molecular-profiles/hnsc_tcga_rna_seq_v2_mrna/molecular-data/fetch"
        "?projection=SUMMARY",
        {"entrezGeneIds": sorted(set(resolved.values())), "sampleListId": "hnsc_tcga_all"},
    )
    log(f"  {len(data):,} data points returned")
    e2s = {v: k for k, v in resolved.items()}
    df = pd.DataFrame(
        [(d["sampleId"], e2s[d["entrezGeneId"]], d["value"]) for d in data],
        columns=["sample", "gene", "value"],
    )
    mat = df.pivot_table(index="sample", columns="gene", values="value", aggfunc="mean")
    mat.to_csv(out)
    json.dump(resolved, open(ids_file, "w"))
    return mat, resolved


def fetch_tcga_methylation(cache: Path, resolved: dict[str, int]) -> pd.DataFrame:
    """HM450 gene-level methylation (beta) for the panel, TCGA-HNSC."""
    out = cache / "tcga_methylation.csv"
    if out.exists():
        log("  cached: TCGA methylation")
        return pd.read_csv(out, index_col=0)
    log("  fetching HM450 methylation")
    data = post_json(
        "/molecular-profiles/hnsc_tcga_methylation_hm450/molecular-data/fetch"
        "?projection=SUMMARY",
        {"entrezGeneIds": sorted(set(resolved.values())), "sampleListId": "hnsc_tcga_all"},
    )
    e2s = {v: k for k, v in resolved.items()}
    df = pd.DataFrame(
        [(d["sampleId"], e2s[d["entrezGeneId"]], d["value"]) for d in data],
        columns=["sample", "gene", "value"],
    )
    mat = df.pivot_table(index="sample", columns="gene", values="value", aggfunc="mean")
    mat.to_csv(out)
    log(f"  {mat.shape[0]} samples x {mat.shape[1]} genes")
    return mat


def fetch_tcga_hpv_status(cache: Path) -> pd.DataFrame:
    """HPV status per TCGA-HNSC sample.

    HPV_STATUS_P16 and HPV_STATUS_ISH are PATIENT-level attributes in
    cBioPortal (a SAMPLE-level fetch returns an empty list). We therefore
    fetch per patient and map to the primary-tumour sample id (-01), which is
    how the expression and methylation matrices are keyed. A tumour is called
    HPV+ if either assay is positive.
    """
    out = cache / "tcga_hpv_status.csv"
    if out.exists():
        log("  cached: TCGA HPV status")
        return pd.read_csv(out)
    log("  fetching clinical HPV status (patient-level)")
    rows = []
    for attr in ("HPV_STATUS_P16", "HPV_STATUS_ISH"):
        try:
            rows += post_json(
                "/studies/hnsc_tcga/clinical-data/fetch"
                "?clinicalDataType=PATIENT&projection=SUMMARY",
                {"attributeIds": [attr]})
        except Exception as exc:  # noqa: BLE001
            log(f"  warning: {attr} fetch failed ({type(exc).__name__})")
    if not rows:
        raise RuntimeError("no clinical HPV data returned from cBioPortal")
    cd = pd.DataFrame(rows)
    wide = cd.pivot_table(index="patientId", columns="clinicalAttributeId",
                          values="value", aggfunc="first")

    def call(r) -> str:
        vals = [str(v).strip().lower() for v in r.values if pd.notna(v)]
        if any(v.startswith("positive") for v in vals):
            return "positive"
        if any(v.startswith("negative") for v in vals):
            return "negative"
        return "unknown"

    res = pd.DataFrame({"patient": wide.index,
                        "HPV_status": wide.apply(call, axis=1).values})
    res = res[res.HPV_status != "unknown"].copy()
    res["sample"] = res.patient + "-01"          # primary tumour
    res = res[["sample", "patient", "HPV_status"]].reset_index(drop=True)
    res.to_csv(out, index=False)
    log(f"  {(res.HPV_status == 'positive').sum()} HPV+ / "
        f"{(res.HPV_status == 'negative').sum()} HPV- with a usable call")
    return res
