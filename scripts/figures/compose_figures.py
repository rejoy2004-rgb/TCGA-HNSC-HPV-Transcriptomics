"""Assemble the 600 dpi panels in figures/source_panels_600dpi into full figures.

* The sentence-style title printed above each panel is cropped off (the figure legends
  describe each panel), and a uniform bold panel letter is drawn instead.
* Panels in a row are scaled to a common height and rows to a common width, always
  downscaling to the smallest natural size so that nothing is upsampled.
Output numbering follows the integrated manuscript."""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import matplotlib

SRC = "figures/source_panels_600dpi"
OUT = "figures/integrated/composed"
GAP = 60          # px between panels and between rows
STRIP = 130       # px strip above each row for panel letters
LETTER_PX = 100   # letter cap height ~4 mm at 600 dpi
FONT = ImageFont.truetype(os.path.join(matplotlib.get_data_path(), "fonts/ttf/DejaVuSans-Bold.ttf"), LETTER_PX)
os.makedirs(OUT, exist_ok=True)

def ink_blocks(a):
    rows = (a < 200).sum(1) > 0
    out, inb = [], False
    for i, r in enumerate(rows):
        if r and not inb: s, inb = i, True
        if not r and inb: out.append((s, i)); inb = False
    if inb: out.append((s, len(rows)))
    return out

def strip_title(im):
    """Remove the leading title text lines (blocks separated by < 25 px) and the gap below them."""
    b = ink_blocks(np.asarray(im.convert("L"), float))
    title = [b[0]]
    for nb in b[1:]:
        if nb[0] - title[-1][1] < 25 and nb[1] - nb[0] < 120: title.append(nb)
        else: break
    nxt = b[len(title)][0]
    cut = title[-1][1] + (nxt - title[-1][1]) // 2
    return im.crop((0, cut, im.width, im.height))

def load(fig, p):
    im = Image.open(f"{SRC}/Figure {fig}/Figure {fig}{p}.png")
    if im.mode in ("RGBA", "LA"):
        bg = Image.new("RGB", im.size, "white"); bg.paste(im, mask=im.split()[-1]); im = bg
    return strip_title(im.convert("RGB"))

def compose(rows, name):
    letters = iter("abcdefghij")
    built = []                                   # (row image, [panel x offsets])
    for panels in rows:
        h = min(p.height for p in panels)
        ps = [p.resize((round(p.width * h / p.height), h), Image.LANCZOS) if p.height != h else p for p in panels]
        xs, x = [], 0
        for p in ps: xs.append(x); x += p.width + GAP
        r = Image.new("RGB", (x - GAP, h), "white")
        for p, px in zip(ps, xs): r.paste(p, (px, 0))
        built.append((r, xs))
    w = min(r.width for r, _ in built)
    scaled = []
    for r, xs in built:
        f = w / r.width
        if f != 1: r = r.resize((w, round(r.height * f)), Image.LANCZOS)
        scaled.append((r, [round(x * f) for x in xs]))
    H = sum(STRIP + r.height for r, _ in scaled) + GAP * (len(scaled) - 1)
    out = Image.new("RGB", (w, H), "white"); d = ImageDraw.Draw(out); y = 0
    for r, xs in scaled:
        for x in xs: d.text((x + 10, y + 5), next(letters), font=FONT, fill=(0, 0, 0))
        out.paste(r, (0, y + STRIP)); y += STRIP + r.height + GAP
    out.save(f"{OUT}/{name}.png", dpi=(600, 600))
    print(f"{name}: {out.size[0]}x{out.size[1]} px = {out.size[0] / 600 * 25.4:.0f} mm wide at 600 dpi")

L = lambda f, s: [load(f, c) for c in s]
compose([L(1, "a"), L(1, "b"), L(1, "c")], "Figure1")           # draft Fig 1
compose([L(3, "abc")], "Figure2")                                # draft Fig 3 (methylation)
compose([L(4, "abc")], "Figure3")                                # draft Fig 4 (GSE65858)
compose([L(6, "abc"), L(6, "de")], "Figure5")                    # draft Fig 6 (GSE181919)
compose([L(7, "abc"), L(7, "def")], "Figure6")                   # draft Fig 7 (GSE182227)
compose([L(2, "abc")], "SuppFig_S2")                             # draft Fig 2 (enrichment origin)
compose([L(5, "abc")], "SuppFig_S4")                             # draft Fig 5 (module coherence)
