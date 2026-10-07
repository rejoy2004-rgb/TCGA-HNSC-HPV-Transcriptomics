"""Side-by-side supplementary composites from the R pipeline's plots (native resolution, no resampling):
Supplementary Fig. S3 (downregulated GO and KEGG) and Supplementary Fig. S5 (CD8A/CD8B validation)."""
from PIL import Image

def side_by_side(left, right, out, dpi, gap=120):
    a, b = Image.open(left).convert("RGB"), Image.open(right).convert("RGB")
    assert a.height == b.height, "panels must share a height"
    c = Image.new("RGB", (a.width + gap + b.width, a.height), "white")
    c.paste(a, (0, 0)); c.paste(b, (a.width + gap, 0))
    c.save(out, dpi=(dpi, dpi))
    print(out, c.size)

side_by_side("figures/HNSC_HPV_GO_Downregulated.png", "figures/HNSC_HPV_KEGG_Downregulated.png",
             "figures/integrated/SuppFig_Down_GO_KEGG.png", 600)
side_by_side("figures/Figure_CD8A_Validation.png", "figures/Figure_CD8B_Validation.png",
             "figures/integrated/SuppFig_CD8_Validation.png", 300, gap=0)
