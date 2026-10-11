#!/usr/bin/env python3
"""Meiotic gene programme in HPV+ HNSCC - bulk analyses and GSE181919 single-cell stage.

Runs, in order:
  1. Origin of the hypothesis  GSEA ranking, panel-category enrichment, panel/DEG overlap
                               (frozen DESeq2/GSEA/GO outputs in data_processed/meiotic_programme)
  2. TCGA-HNSC discovery       promoter hypomethylation and methylation-expression coupling (cBioPortal)
  3. GSE65858 validation       viral activity, per-gene/per-category specificity, coherence, confounders
  4. GSE38266 replication      promoter hypomethylation in an independent oropharyngeal cohort
  5. GSE181919 single cell     malignant-cell localisation (optional; ~1.2 GB download)

Usage (from the repository root):
    python scripts/meiotic_programme/run_meiotic_analysis.py --data DATA/meiotic
    python scripts/meiotic_programme/run_meiotic_analysis.py --data DATA/meiotic --skip-singlecell
    python scripts/meiotic_programme/run_meiotic_analysis.py --data DATA/meiotic --panels

Public inputs are downloaded into --data on first use and re-used afterwards.
Outputs go to results/meiotic_programme/ (tables, JSON, 600 dpi PNG + PDF figures).
With --panels, every figure is also split into 600 dpi per-panel files in
figures/source_panels_600dpi/ (the folders compose_figures.py reads).
"""
import argparse, json, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
REPO = HERE.parents[1]

from meiotic.config import *            # noqa: F401,F403  (constants, gene panel)
from meiotic.helpers import log
from meiotic.data_tcga import fetch_tcga_expression, fetch_tcga_methylation, fetch_tcga_hpv_status
from meiotic.data_geo import load_gse65858, load_gse38266, fetch_gse181919
from meiotic.enrichment_provenance import analysis_provenance
from meiotic.tcga_discovery import analysis_discovery
from meiotic.gse65858_validation import analysis_validation
from meiotic.gse38266_replication import analysis_methylation_replication
from meiotic.gse181919_singlecell import analysis_singlecell
from meiotic.figures import make_provenance_figure, make_figures
from meiotic.panel_export import install_export_hook

# figure file stem -> folder in figures/source_panels_600dpi (folder numbering as in the repository)
PANEL_FOLDERS = {"fig0_provenance": "Figure 2", "fig2_methylation": "Figure 3",
                 "fig1_activation": "Figure 4", "fig3_coordination": "Figure 5",
                 "fig4_singlecell": "Figure 6"}


def scalars(d):
    """Keep only JSON-friendly scalars; tables are already written as CSV."""
    out = {}
    for k, v in d.items():
        if isinstance(v, (int, float, str, bool)) or v is None:
            out[k] = v
        elif isinstance(v, (list, tuple)) and all(isinstance(x, (int, float, str)) for x in v):
            out[k] = list(v)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", default="DATA/meiotic", help="download/cache folder (outside the repository)")
    ap.add_argument("--processed", default=str(REPO / "data_processed" / "meiotic_programme"),
                    help="frozen enrichment inputs and gene panel")
    ap.add_argument("--out", default=str(REPO / "results" / "meiotic_programme"))
    ap.add_argument("--skip-singlecell", action="store_true", help="skip GSE181919 (1.2 GB download)")
    ap.add_argument("--panels", action="store_true", help="also write per-panel 600 dpi files")
    a = ap.parse_args()

    CACHE, RESULTS, PROCESSED = Path(a.data), Path(a.out), Path(a.processed)
    CACHE.mkdir(parents=True, exist_ok=True); RESULTS.mkdir(parents=True, exist_ok=True)
    install_export_hook(RESULTS, str(REPO / "figures" / "source_panels_600dpi") if a.panels else None,
                        PANEL_FOLDERS, dpi=600)
    np.random.seed(RANDOM_SEED)
    T0 = time.time()

    # ---------------------------------------------------------------- 1-2. TCGA-HNSC
    log("gene panel: %d genes in %d categories" % (len(ALL_GENES), len(GENE_SET)))
    log("STEP 1/5 - TCGA-HNSC discovery cohort")
    expr, resolved = fetch_tcga_expression(CACHE)
    meth = fetch_tcga_methylation(CACHE, resolved)
    hpv = fetch_tcga_hpv_status(CACHE)

    prov, prov_percat, prov_top20, prov_overlap = analysis_provenance(PROCESSED, ALL_GENES)
    if prov is not None:
        prov_overlap.to_csv(RESULTS / "table0a_deg_provenance.csv", index=False)
        prov_percat.to_csv(RESULTS / "table0b_deg_percategory.csv", index=False)
        prov_top20.to_csv(RESULTS / "table0c_gsea_top20.csv", index=False)
        with open(RESULTS / "provenance_values.json", "w") as fh:
            json.dump(prov, fh, indent=1, default=str)
        log("  provenance: %d/5 top GSEA terms meiotic; mei-vs-CTA OR=%.1f"
            % (prov["gsea_meio_top5"], prov["mei_vs_cta_or"]))
    disc = analysis_discovery(expr, meth, hpv, RESULTS)

    # ---------------------------------------------------------------- 3. GSE65858
    log("STEP 2/5 - GSE65858 validation cohort")
    gexpr, gclin = load_gse65858(CACHE)
    val = analysis_validation(gexpr, gclin, RESULTS)

    # ---------------------------------------------------------------- 4. GSE38266
    log("STEP 3/5 - GSE38266 methylation replication")
    beta, bclin, pmap = load_gse38266(CACHE)
    rep = analysis_methylation_replication(beta, bclin, pmap, disc, RESULTS)

    # ---------------------------------------------------------------- 5. GSE181919
    scv = None
    if a.skip_singlecell:
        log("STEP 4/5 - GSE181919 skipped (--skip-singlecell)")
    else:
        log("STEP 4/5 - GSE181919 single-cell validation")
        if not all((CACHE / f).exists() for f in ("sc_CA_counts.npz", "sc_CA_genes.npy", "sc_CA_meta.csv")):
            fetch_gse181919(CACHE)
        scv = analysis_singlecell(CACHE, RESULTS)
        log("  malignant cells: delta=%.4f AUC=%.3f; largest non-malignant |delta|=%.4f"
            % (scv["mal_delta"], scv["mal_auc"], scv["nonmal_delta_max"]))
        log("  pseudobulk: %.1fx core meiotic CPM in HPV+ (P=%.2e, %dv%d tumours)"
            % (scv["pb_core_fold"], scv["pb_core_p"], scv["n_pb_pos"], scv["n_pb_neg"]))

    # ---------------------------------------------------------------- tables, figures, values
    log("STEP 5/5 - figures and tables")
    pd.DataFrame([
        dict(cohort="TCGA-HNSC (discovery)", platform="Illumina RNA-seq (RSEM)",
             n_HPVpos=disc["n_pos"], n_HPVneg=disc["n_neg"], role="expression discovery"),
        dict(cohort="TCGA-HNSC (discovery)", platform="Illumina HM450",
             n_HPVpos=disc["n_mpos"], n_HPVneg=disc["n_mneg"], role="methylation discovery"),
        dict(cohort="GSE65858 (validation)", platform="Illumina HT-12 v4 microarray",
             n_HPVpos=val["n_active"] + val["n_silent"], n_HPVneg=val["n_neg"],
             role="independent expression validation"),
        dict(cohort="GSE38266 (replication)", platform="Illumina HM450",
             n_HPVpos=rep["n_pos"], n_HPVneg=rep["n_neg"], role="independent methylation replication"),
    ]).to_csv(RESULTS / "table1_cohorts.csv", index=False)
    if prov is not None:
        make_provenance_figure(prov, prov_percat, prov_top20, prov_overlap, RESULTS)
    make_figures(val, disc, rep, RESULTS)

    import platform, matplotlib, sklearn, statsmodels, scipy
    with open(RESULTS / "session_info.txt", "w") as fh:
        fh.write("python        %s (%s)\n" % (sys.version.split()[0], platform.platform()))
        for m in (np, pd, matplotlib, sklearn, statsmodels, scipy):
            fh.write("%-13s %s\n" % (m.__name__, m.__version__))
        fh.write("random seed   %d\nruntime       %.0f s\n" % (RANDOM_SEED, time.time() - T0))

    values = {"panel": {"n_genes": len(ALL_GENES), "n_categories": len(GENE_SET), "core": list(CORE6),
                        "per_category": {k: len(v) for k, v in GENE_SET.items()}},
              "discovery": scalars(disc), "validation": scalars(val), "replication": scalars(rep)}
    if scv is not None:
        values["singlecell"] = scalars(scv)
    with open(RESULTS / "headline_values.json", "w") as fh:
        json.dump(values, fh, indent=1, default=str)

    log("=" * 72); log("HEADLINE RESULTS")
    log("  discovery : %d/%d genes hypomethylated in HPV+ (FDR<0.05); %d/%d with rho<0"
        % (disc["n_hypo"], disc["n_tested"], disc["n_neg_rho"], disc["n_hypo"]))
    log("  discovery : hypomethylation vs expression rho=%.3f, p=%.2e" % (disc["coupling_rho"], disc["coupling_p"]))
    log("  validation: virus-active vs HPV- AUC=%.3f, p=%.2e" % (val["auc_active_vs_neg"], val["p_active_vs_neg"]))
    log("  validation: virus-SILENT vs HPV- p=%.3f (not significant)" % val["p_silent_vs_neg"])
    log("  validation: coherence %.3f vs HPV- null %.3f-%.3f, permutation p=%.4f"
        % (val["perm_obs"], val["perm_ci"][0], val["perm_ci"][1], val["perm_p"]))
    log("  replication: cross-cohort rho=%.3f (p=%.1e); set-level p=%.2e" % (rep["cross_rho"], rep["cross_p"], rep["set_p"]))
    log("=" * 72)
    log("done in %.0f s; outputs in %s/" % (time.time() - T0, RESULTS))


if __name__ == "__main__":
    main()
