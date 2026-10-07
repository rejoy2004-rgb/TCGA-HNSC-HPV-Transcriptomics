"""Graphical abstract for the integrated manuscript (600 dpi PNG; TIFF via export_submission_figures.py).
All numbers shown are those reported in the manuscript."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ORANGE, BLUE, INK, MUTED, LINE = "#eb6834", "#2a78d6", "#1f1f1f", "#5f5f5f", "#b9b9b9"
FILL_HPV, FILL_TME, FILL_COH = "#fdf1ec", "#eef4fc", "#f4f4f2"

fig = plt.figure(figsize=(7.2, 3.9))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 100); ax.set_ylim(0, 54); ax.axis("off")

def box(x, y, w, h, fc, ec=LINE, lw=0.8):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.2", fc=fc, ec=ec, lw=lw))

def arrow(x1, y1, x2, y2, c=MUTED):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=9, lw=1.1, color=c))

def t(x, y, s, size=6.6, c=INK, w="normal", ha="left", va="center", style="normal"):
    ax.text(x, y, s, fontsize=size, color=c, fontweight=w, ha=ha, va=va, fontstyle=style, family="DejaVu Sans")

# title
t(50, 51.2, "Transcriptionally active HPV+ HNSCC is associated with a coordinated meiotic programme",
  size=8.4, w="bold", ha="center")

# cohorts
box(1.5, 6.5, 19, 38, FILL_COH)
t(11, 42, "Five cohorts", size=7.2, w="bold", ha="center")
rows = [("TCGA-HNSC", "RNA-seq, n = 279\nHM450, n = 125"), ("GSE65858", "HPV DNA vs RNA,\nn = 256"),
        ("GSE38266", "HM450 replication,\nn = 42"), ("GSE181919 +\nGSE182227", "scRNA-seq,\n35 tumours")]
for i, (a, b) in enumerate(rows):
    y = 37.5 - i * 7.6
    t(3, y, a, size=6.3, w="bold", va="top"); t(3, y - (4.2 if "\n" in a else 2.4), b, size=5.9, c=MUTED, va="top")

arrow(21.2, 25.5, 24.6, 25.5)

# malignant cell
box(25.5, 6.5, 40, 38, FILL_HPV, ec=ORANGE, lw=1.1)
t(45.5, 42, "HPV+ malignant cell", size=7.2, w="bold", ha="center")
t(28, 37.2, "Active viral transcription (E6/E7)", size=6.6, w="bold")
t(28, 34.2, "Core score AUC 0.959; HPV DNA+/RNA− ≈ HPV− (P = 0.56)", size=5.6, c=MUTED)
t(28, 28.0, "Associated promoter hypomethylation", size=6.6, w="bold")
t(28, 25.2, "18/49 panel promoters; methylation vs expression ρ = −0.755", size=5.6, c=MUTED)
t(28, 19.0, "Coordinated meiotic module  ↑", size=6.6, w="bold", c=ORANGE)
t(28, 15.9, "SYCP2   SYCE2   MAJIN   SMC1B   STAG3   MEI1", size=6.3, style="italic")
t(28, 12.6, "Co-expression ρ = 0.556 (HPV+) vs 0.149 (HPV−)", size=5.6, c=MUTED)
t(28, 9.3, "MAGE/CTAG antigens: no change (AUC 0.411)", size=6.0, c=MUTED, style="italic")

# microenvironment
box(69.5, 6.5, 29, 38, FILL_TME, ec=BLUE, lw=1.1)
t(84, 42, "Tumour microenvironment", size=7.2, w="bold", ha="center")
t(72, 36.6, "CIBERSORTx (TCGA)", size=6.0, c=MUTED, w="bold")
t(72, 32.8, "Plasma cells  ↑", size=6.6, c=BLUE, w="bold")
t(72, 29.4, "CD8+ T cells  ↑", size=6.6, c=BLUE, w="bold")
t(72, 26.0, "M0 macrophages  ↓", size=6.6, c=BLUE, w="bold")
t(72, 20.4, "scRNA-seq (two cohorts)", size=6.0, c=MUTED, w="bold")
t(72, 16.6, "Meiotic signal in malignant\ncells only (Δ = 0.103);\n≤ 0.011 in immune and\nstromal cells", size=5.9, va="top")
arrow(68.8, 25.5, 66.2, 25.5, BLUE)

# take-home
t(50, 2.6, "Consistent with a directed meiotic programme rather than stochastic cancer–testis antigen de-repression",
  size=6.4, c=INK, ha="center", style="italic")

fig.savefig("figures/integrated/Graphical_Abstract.png", dpi=600, facecolor="white")
print("ok")
