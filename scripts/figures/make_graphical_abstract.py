"""Graphical abstract for the integrated manuscript (600 dpi PNG; TIFF via export_submission_figures.py).
All numbers shown are those reported in the manuscript."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ORANGE, BLUE, INK, MUTED, LINE = "#eb6834", "#2a78d6", "#1f1f1f", "#5f5f5f", "#b9b9b9"
FILL_HPV, FILL_TME, FILL_COH = "#fdf1ec", "#eef4fc", "#f4f4f2"

fig = plt.figure(figsize=(7.2, 4.6))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 100); ax.set_ylim(0, 66); ax.axis("off")

def box(x, y, w, h, fc, ec=LINE, lw=0.8):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.2", fc=fc, ec=ec, lw=lw))

def arrow(x1, y1, x2, y2, c=MUTED):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=9, lw=1.1, color=c))

def t(x, y, s, size=6.6, c=INK, w="normal", ha="left", va="center", style="normal"):
    ax.text(x, y, s, fontsize=size, color=c, fontweight=w, ha=ha, va=va, fontstyle=style, family="DejaVu Sans")

# title
t(50, 62.5, "Transcriptionally active HPV+ HNSCC is associated with\na coordinated meiotic programme", size=10.5, w="bold", ha="center")

# cohorts
box(1.5, 7.5, 22, 46, FILL_COH)
t(12.5, 51, "Five cohorts", size=8.8, w="bold", ha="center")
rows = [("TCGA-HNSC", "RNA-seq n = 279\nHM450 n = 125"), ("GSE65858", "HPV DNA vs RNA\nn = 256"),
        ("GSE38266", "HM450 replication\nn = 42"), ("GSE181919 +\nGSE182227", "scRNA-seq\n36 tumours")]
for i, (a, b) in enumerate(rows):
    y = 46.5 - i * 9.6
    t(3, y, a, size=7.6, w="bold", va="top"); t(3, y - (4.8 if "\n" in a else 2.8), b, size=7.0, c=MUTED, va="top")

arrow(24, 30.5, 27.4, 30.5)

# malignant cell
box(28.5, 7.5, 40, 46, FILL_HPV, ec=ORANGE, lw=1.1)
t(48.5, 51, "HPV+ malignant cell", size=8.8, w="bold", ha="center")
t(30.5, 46.0, "Active viral transcription", size=8.0, w="bold")
t(30.5, 42.4, "Core score AUC 0.959; HPV DNA+/RNA−\nnot different from HPV− (P = 0.56)", size=6.8, c=MUTED, va="top")
t(30.5, 34.6, "Associated promoter hypomethylation", size=8.0, w="bold")
t(30.5, 31.0, "18/49 panel promoters; methylation\nvs expression ρ = −0.755", size=6.8, c=MUTED, va="top")
t(30.5, 23.4, "Coordinated meiotic module  ↑", size=8.0, w="bold", c=ORANGE)
t(30.5, 19.8, "SYCP2  SYCE2  MAJIN  SMC1B  STAG3  MEI1", size=7.2, style="italic")
t(30.5, 16.6, "Co-expression ρ = 0.556 (HPV+) vs 0.149 (HPV−)", size=6.8, c=MUTED)
t(30.5, 11.0, "MAGE/CTAG antigens: no change (AUC 0.411)", size=6.8, c=MUTED, style="italic")

# microenvironment
box(72.5, 7.5, 26, 46, FILL_TME, ec=BLUE, lw=1.1)
t(85.5, 51, "Tumour\nmicroenvironment", size=8.8, w="bold", ha="center", va="center")
t(74.5, 43.6, "CIBERSORTx (TCGA)", size=7.0, c=MUTED, w="bold")
t(74.5, 39.8, "Plasma cells  ↑", size=8.0, c=BLUE, w="bold")
t(74.5, 36.0, "CD8+ T cells  ↑", size=8.0, c=BLUE, w="bold")
t(74.5, 32.2, "M0 macrophages  ↓", size=8.0, c=BLUE, w="bold")
t(74.5, 26.0, "scRNA-seq (two cohorts)", size=7.0, c=MUTED, w="bold")
t(74.5, 22.8, "Meiotic signal in\nmalignant cells only\n(Δ = 0.100); ≤ 0.011 in\nnon-malignant cells", size=6.8, va="top")
arrow(72.0, 30.5, 69.0, 30.5, BLUE)

# take-home
t(50, 3.0, "Associations consistent with a coordinated meiotic programme rather than\nstochastic cancer–testis antigen de-repression",
  size=7.6, c=INK, ha="center", style="italic")

fig.savefig("figures/integrated/Graphical_Abstract.png", dpi=600, facecolor="white")

fig.savefig("figures/integrated/Graphical_Abstract.pdf", facecolor="white")  # vector copy for submission
print("ok")
