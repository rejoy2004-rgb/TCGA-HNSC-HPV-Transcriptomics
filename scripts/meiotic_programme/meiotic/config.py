"""Shared imports, constants, the 95-gene panel and analysis settings.

Every analysis module does ``from .config import *`` so the function bodies are
exactly those of the verified analysis notebook."""
from __future__ import annotations

import os
os.environ.setdefault("KMP_AFFINITY", "disabled")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
import argparse
import gzip
import io
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp_sparse
from scipy import stats
from statsmodels.stats.multitest import multipletests

RANDOM_SEED = 0
CBIO = "https://www.cbioportal.org/api"
GEO = "https://ftp.ncbi.nlm.nih.gov/geo"


# ----------------------------------------------------------------------------
# Gene set. 95 germline / meiotic / cancer-testis-antigen genes, grouped by
# the biological machine each belongs to. The category split is the paper's
# central analytical device: it separates the meiotic machinery (which tracks
# HPV) from the classic MAGE/CTAG cancer-testis antigens (which do not).
# ----------------------------------------------------------------------------
GENE_SET: dict[str, list[str]] = {
    "Synaptonemal complex": [
        "MAJIN", "SIX6OS1", "SYCE1", "SYCE2", "SYCE3", "SYCP1", "SYCP2", "SYCP2L",
        "SYCP3", "TEX12"
    ],
    "Meiotic cohesin": [
        "RAD21L1", "REC8", "SMC1B", "STAG3"
    ],
    "Meiotic recombination/DSB": [
        "ANKRD31", "BRME1", "CCDC36", "CNTD1", "DMC1", "HFM1", "HORMAD1", "HORMAD2",
        "MCMDC2", "MEI1", "MEI4", "MEIOB", "MLH3", "MND1", "MSH4", "MSH5",
        "PSMC3IP", "RAD9B", "REC114", "RNF212", "SHCBP1L", "SPATA22", "SPO11"
    ],
    "piRNA/Tudor germline": [
        "DDX4", "HENMT1", "MAEL", "MOV10L1", "PIWIL1", "PIWIL2", "TDRD1", "TDRD10",
        "TDRD12", "TDRD5", "TDRD6", "TDRD9"
    ],
    "Cell-cycle meiosis": [
        "AURKC", "CCNB3", "CDC20B", "OIP5", "TDRKH"
    ],
    "Cancer-testis antigen (MAGE/CTAG)": [
        "ACRBP", "CT45A1", "CTAG1B", "CTAG2", "CTCFL", "DPPA2", "FMR1NB", "GAGE1",
        "GAGE2A", "LUZP4", "MAGEA1", "MAGEA10", "MAGEA11", "MAGEA12", "MAGEA2",
        "MAGEA3", "MAGEA4", "MAGEA6", "MAGEB1", "MAGEB2", "MAGEC1", "MAGEC2",
        "PASD1", "PRAME", "PRSS55", "SPANXB1", "SSX1", "SSX2", "SSX4", "TAF7L",
        "XAGE1B", "ZNF165", "ZPBP2"
    ],
    "Other germ-cell": [
        "GBX1", "GRIN2C", "GTSF1", "RBMXL2", "STRA8", "TEX14", "TEX15", "ZFR2"
    ],
}

# The six genes carrying the coordinated module (Fig 3). Chosen in discovery
# as the meiotic-machinery genes with both FDR-significant hypomethylation and
# top-decile HPV discrimination; used unchanged in validation.
CORE6 = ["MEI1", "SMC1B", "STAG3", "SYCP2", "SYCE2", "MAJIN"]

# Immune / proliferation reference sets. Proliferation is the key confounder:
# meiotic genes are cell-cycle-adjacent, so any HPV association must survive
# adjustment for how fast the tumour is dividing.
PROLIFERATION = ["MKI67", "CCNB1", "TOP2A", "BUB1", "CDK1", "AURKA", "PLK1", "TYMS"]
CD8_MARKERS = ["CD8A", "CD8B", "GZMB", "PRF1", "IFNG", "CXCL9", "CXCL10"]
BPLASMA_MARKERS = ["CD79A", "CD79B", "MS4A1", "MZB1"]

ALL_GENES = sorted({g for v in GENE_SET.values() for g in v})

MEIOTIC_CATS = ["Meiotic recombination/DSB", "Synaptonemal complex",
                "Meiotic cohesin", "Cell-cycle meiosis"]
CTA_CAT = "Cancer-testis antigen (MAGE/CTAG)"
GERMLINE_CATS = ["piRNA/Tudor germline", "Other germ-cell"]


def panel_frame() -> pd.DataFrame:
    """The gene panel as a tidy gene/category frame."""
    return pd.DataFrame([dict(gene=g, category=k)
                         for k, v in GENE_SET.items() for g in v])
GENE2CAT = {g: c for c, gs in GENE_SET.items() for g in gs}


# ============================================================================
# utilities


# ============================================================================
# ANALYSES
# ============================================================================

# Where the meiotic hypothesis came from: the panel was NOT picked a priori.
# It was motivated by an unbiased GO/GSEA analysis of an HPV+ vs HPV- DESeq2
# comparison in TCGA-HNSC run before this study. These artefacts are that
# analysis's own output, re-tested here against the final 95-gene panel.
import re as _re
from scipy.stats import hypergeom, fisher_exact

MEIO_RE = _re.compile(r"meio|synapton|synapsis|homologous recombination|chiasma|"
                      r"reciprocal recombination|germ cell|spermato|oogen|piRNA|"
                      r"chromosome pairing|DNA recombination", _re.I)

PROV_FILES = {
    "gsea":  "HNSC_HPV_GSEA_full.csv",     # GSEA on the full log2FC ranking
    "go_up": "GO_BP_upregulated_ORA.csv"   # GO BP over-representation, up genes (78 terms; Fig. 1c)
    , "deg": "DEGs_reannotated.csv",       # DESeq2 table, symbols re-mapped
}

# Values as reported by the original (pre-existing) differential-expression
# walkthrough, for side-by-side comparison. These are published constants, not
# recomputed: symbol annotation in that analysis was incomplete, so it could
# test fewer panel genes (82) than the re-annotated table supports.
ORIG_PROV = {
    "Loose (padj<0.05, log2FC>0)":      dict(wt_selected=7971, wt_hits=36,
                                             wt_testable=82, wt_fold=1.7),
    "Stringent (padj<1e-10, log2FC>1)": dict(wt_selected=454, wt_hits=21,
                                             wt_testable=82, wt_fold=17.4),
}


# ============================================================================
# STAGE 5 - single-cell validation (GSE181919): which cells carry the programme
# ============================================================================

GSE181919_FILES = {
    "counts": "GSE181919_UMI_counts.txt.gz",
    "meta": "GSE181919_Barcode_metadata.txt.gz",
}
SC_MIN_CELLS = 20        # minimum malignant cells for a patient-level pseudobulk
SC_CTRL_SIZE = 50        # control genes per scored gene (Tirosh binned scoring)
SC_N_BINS = 25

# Canonical lineage markers used to re-verify the depositors' cell-type labels.
SC_MARKERS = {
    "Malignant.cells": ["EPCAM", "KRT5", "KRT14", "KRT17", "SFN"],
    "T.cells": ["CD3E", "CD2", "CD3D"],
    "B_Plasma.cells": ["MS4A1", "MZB1", "CD79A"],
    "Macrophages": ["CD68", "CD14", "AIF1"],
    "Dendritic.cells": ["LILRA4", "CLEC9A", "CD1C"],
    "Mast.cells": ["TPSAB1", "CPA3", "MS4A2"],
    "Fibroblasts": ["COL1A1", "DCN", "LUM"],
    "Endothelial.cells": ["PECAM1", "VWF", "CLDN5"],
    "Myocytes": ["ACTA1", "DES", "MYH11"],
}
