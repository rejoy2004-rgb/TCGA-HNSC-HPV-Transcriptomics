"""Vector (PDF) versions of the composed figures.

Uses exactly the layout of compose_figures.py (title strip cropped, panels in a row scaled to a common height, rows to a common
width, uniform bold panel letters) but places the vector panel PDFs from figures/source_panels_600dpi instead of resampling the
PNGs, so text and lines stay vector. Output: figures/integrated/composed/<name>.pdf (same name as the PNG).
Run after the panel folders are current:  python scripts/figures/compose_figures_vector.py"""
import os
import fitz
import numpy as np
from PIL import Image
import matplotlib

SRC = "figures/source_panels_600dpi"
OUT = "figures/integrated/composed"
GAP, STRIP, LETTER_PX = 60, 130, 100          # same constants as compose_figures.py (pixels at 600 dpi)
PT = 72 / 600                                  # points per pixel
FONTFILE = os.path.join(matplotlib.get_data_path(), "fonts/ttf/DejaVuSans-Bold.ttf")


def ink_blocks(a):
    rows = (a < 200).sum(1) > 0
    out, inb = [], False
    for i, r in enumerate(rows):
        if r and not inb: s, inb = i, True
        if not r and inb: out.append((s, i)); inb = False
    if inb: out.append((s, len(rows)))
    return out


def title_cut(im):
    """Pixel row below which the panel starts (same rule as compose_figures.strip_title)."""
    b = ink_blocks(np.asarray(im.convert("L"), float))
    title = [b[0]]
    for nb in b[1:]:
        if nb[0] - title[-1][1] < 25 and nb[1] - nb[0] < 120: title.append(nb)
        else: break
    nxt = b[len(title)][0]
    return title[-1][1] + (nxt - title[-1][1]) // 2


def load(fig, p):
    base = f"{SRC}/Figure {fig}/Figure {fig}{p}"
    im = Image.open(base + ".png")
    if im.mode in ("RGBA", "LA"):
        bg = Image.new("RGB", im.size, "white"); bg.paste(im, mask=im.split()[-1]); im = bg
    cut = title_cut(im.convert("RGB"))
    return dict(pdf=base + ".pdf", w=im.width, h=im.height - cut, cut=cut, full_h=im.height)


def compose(rows, name):
    letters = iter("abcdefghij")
    built = []                                    # per row: (row height, row width, [(panel, x, w)])
    for panels in rows:
        h = min(p["h"] for p in panels)
        x, items = 0, []
        for p in panels:
            w = round(p["w"] * h / p["h"]) if p["h"] != h else p["w"]
            items.append((p, x, w)); x += w + GAP
        built.append((h, x - GAP, items))
    W = min(r[1] for r in built)
    scaled = []
    for h, rw, items in built:
        f = W / rw
        scaled.append((round(h * f), [(p, round(x * f), w * f) for p, x, w in items]))
    H = sum(STRIP + rh for rh, _ in scaled) + GAP * (len(scaled) - 1)
    doc = fitz.open()
    page = doc.new_page(width=W * PT, height=H * PT)
    page.insert_font(fontname="dvb", fontfile=FONTFILE)
    y = 0
    for rh, items in scaled:
        for p, x, w in items:
            src = fitz.open(p["pdf"])
            sh = src[0].rect.height
            clip = fitz.Rect(0, p["cut"] * sh / p["full_h"], src[0].rect.width, sh)
            page.show_pdf_page(fitz.Rect(x * PT, (y + STRIP) * PT, (x + w) * PT, (y + STRIP + rh) * PT), src, 0, clip=clip)
            page.insert_text(fitz.Point((x + 10) * PT, (y + 5 + 0.93 * LETTER_PX) * PT), next(letters), fontname="dvb",
                             fontsize=LETTER_PX * PT * 1.0, color=(0, 0, 0))
        y += STRIP + rh + GAP
    doc.save(f"{OUT}/{name}.pdf", garbage=3, deflate=True)
    print(f"{name}.pdf: {W * PT / 72 * 25.4:.0f} x {H * PT / 72 * 25.4:.0f} mm")


L = lambda f, s: [load(f, c) for c in s]
compose([L(1, "a"), L(1, "b"), L(1, "c")], "Figure1")
compose([L(3, "abc")], "Figure2")
compose([L(4, "abc")], "Figure3")
compose([L(6, "abc"), L(6, "de")], "Figure5")
# Figure 6 (GSE182227): the deposited panels in "Figure 7" exist only as 600 dpi PNG/TIFF (no vector source), so the PDF
# holds the composed 600 dpi raster at its natural size.
im = Image.open(f"{OUT}/Figure6.png")
doc = fitz.open(); pg = doc.new_page(width=im.width * PT, height=im.height * PT)
pg.insert_image(pg.rect, filename=f"{OUT}/Figure6.png")
doc.save(f"{OUT}/Figure6.pdf", garbage=3, deflate=True)
print("Figure6.pdf: raster-in-PDF (no vector panels available)")
compose([L(2, "abc")], "SuppFig_S2")
compose([L(5, "abc")], "SuppFig_S4")
