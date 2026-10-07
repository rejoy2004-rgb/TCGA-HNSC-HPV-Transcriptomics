"""Export every manuscript figure as LZW TIFF + PNG, numbered as in the integrated manuscript.
Main figures and the graphical abstract go to manuscript/submission_figures/; supplementary figures go to
supplementary/figures/. dpi metadata is 600 for 600 dpi sources; legacy 300 dpi
supplementary plots keep their true resolution."""
import os
import shutil
from PIL import Image

I = "figures/integrated"
MAIN = [("Figure1", f"{I}/composed/Figure1.png"), ("Figure2", f"{I}/composed/Figure2.png"),
        ("Figure3", f"{I}/composed/Figure3.png"), ("Figure4", f"{I}/Figure4_TME_CIBERSORTx_Job14.png"),
        ("Figure5", f"{I}/composed/Figure5.png"), ("Figure6", f"{I}/composed/Figure6.png"),
        ("Graphical_Abstract", f"{I}/Graphical_Abstract.png")]
SUPP = [("Supplementary_Figure_S1_PCA", "figures/HNSC_HPV_PCA.png", 300),
        ("Supplementary_Figure_S2_enrichment_origin", f"{I}/composed/SuppFig_S2.png", 600),
        ("Supplementary_Figure_S3_downregulated_GO_KEGG", f"{I}/SuppFig_Down_GO_KEGG.png", 600),
        ("Supplementary_Figure_S4_module_coherence", f"{I}/composed/SuppFig_S4.png", 600),
        ("Supplementary_Figure_S5_CD8_validation", f"{I}/SuppFig_CD8_Validation.png", 300),
        ("Supplementary_Figure_S6_Cox_forest", f"{I}/SuppFig_Cox_forest_600dpi.png", 600),
        ("Supplementary_Figure_S7_ZFR2_Kaplan_Meier", "figures/HNSC_BestGene_KM.png", 300)]

out = "manuscript/submission_figures"
if os.path.isdir(out):
    shutil.rmtree(out)
os.makedirs(out); os.makedirs("supplementary/figures", exist_ok=True)

def save(name, src, dpi, dests):
    im = Image.open(src).convert("RGB")
    for d in dests:
        im.save(f"{d}/{name}.tif", compression="tiff_lzw", dpi=(dpi, dpi))
        im.save(f"{d}/{name}.png", dpi=(dpi, dpi))
    print(f"{name:48s} {im.width:>5d}x{im.height:<5d} {dpi} dpi, {im.width / dpi * 25.4:.0f} mm wide")

for n, s in MAIN:
    save(n, s, 600, [out])
for n, s, dpi in SUPP:
    save(n, s, dpi, ["supplementary/figures"])
