"""Export every panel of a matplotlib figure as its own image.

Panels are found from their bold single-letter labels (a, b, c ...). Each axes is
assigned to a panel: the axes that owns the letter, plus any helper axes (colour
bars, twin axes) whose centre lies nearest to that panel. When a panel is saved,
every other panel's axes and letter are hidden, so a crop can never pick up a
neighbour's tick labels, and the crop box is the panel's own tight bounding box.
The figure is restored afterwards, so the full-figure export is unaffected.
"""
import os
import numpy as np
from matplotlib.transforms import Bbox

LETTERS = set("abcdefghij")


def _is_letter(t):
    s = t.get_text().strip()
    w = t.get_fontweight()
    return t.get_visible() and s in LETTERS and (w == "bold" or (isinstance(w, (int, float)) and w >= 600))


def _letters(fig):
    out = [t for t in fig.texts if _is_letter(t)]
    for ax in fig.axes:
        out += [t for t in ax.texts if _is_letter(t)]
    return out


def panels(fig):
    r = fig.canvas.get_renderer()
    lets = _letters(fig)
    groups = {}
    owner = {}
    for t in lets:
        ax = t.axes
        if ax is None:          # figure-level letter: owner is the axes nearest below-right
            p = t.get_window_extent(r)
            cand = [a for a in fig.axes if a.get_visible() and a not in owner.values()]
            ax = min(cand, key=lambda a: np.hypot(a.get_window_extent(r).x0 - p.x0,
                                                  a.get_window_extent(r).y1 - p.y1))
        owner[t.get_text().strip()] = ax
        groups[t.get_text().strip()] = {"letter": t, "axes": [ax]}
    mains = set(owner.values())
    for ax in fig.axes:
        if ax in mains or not ax.get_visible():
            continue
        c = ax.get_window_extent(r)
        cx, cy = (c.x0 + c.x1) / 2, (c.y0 + c.y1) / 2
        best = min(groups, key=lambda k: _dist(owner[k].get_window_extent(r), cx, cy))
        groups[best]["axes"].append(ax)
    return dict(sorted(groups.items()))


def _dist(b, x, y):
    dx = max(b.x0 - x, 0, x - b.x1)
    dy = max(b.y0 - y, 0, y - b.y1)
    return np.hypot(dx, dy)


def export_panels(fig, outdir, stem, dpi=600, fmts=("tif", "png", "pdf"), pad=0.05, save=None):
    """Write <outdir>/<stem><letter>.<fmt> for every panel. `save` is the raw
    Figure.savefig to call (so a patched savefig does not recurse)."""
    save = save or fig.__class__.savefig
    os.makedirs(outdir, exist_ok=True)
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    G = panels(fig)
    all_letters = [g["letter"] for g in G.values()]
    other_figtexts = [t for t in fig.texts if t not in all_letters and t.get_visible()]
    vis = {ax: ax.get_visible() for ax in fig.axes}
    legs = [l for l in fig.legends if l.get_visible()]
    written = []
    try:
        for t in other_figtexts: t.set_visible(False)
        for l in legs: l.set_visible(False)
        for k, g in G.items():
            for ax in fig.axes: ax.set_visible(ax in g["axes"] and vis[ax])
            for t in all_letters: t.set_visible(t is g["letter"])
            fig.canvas.draw()
            boxes = [ax.get_tightbbox(r) for ax in g["axes"] if vis[ax]]
            boxes.append(g["letter"].get_window_extent(r))
            bb = Bbox.union([b for b in boxes if b is not None and b.width > 0])
            bb = bb.transformed(fig.dpi_scale_trans.inverted()).padded(pad)
            for f in fmts:
                p = os.path.join(outdir, f"{stem}{k}.{f}")
                kw = dict(dpi=dpi, bbox_inches=bb)
                if f == "tif":
                    kw["pil_kwargs"] = {"compression": "tiff_lzw"}
                save(fig, p, **kw)
                written.append(p)
    finally:
        for ax, v in vis.items(): ax.set_visible(v)
        for t in all_letters + other_figtexts: t.set_visible(True)
        for l in legs: l.set_visible(True)
        fig.canvas.draw()
    return G, written


# ---------------------------------------------------------------------------
# 600 dpi export hook used by the run scripts
# ---------------------------------------------------------------------------
def install_export_hook(results_dir, panels_root=None, stem_to_folder=None, dpi=600):
    """Wrap Figure.savefig so every figure the analysis code saves is written at
    `dpi` (PNG + vector PDF), and - when `panels_root` is given - each figure named
    in `stem_to_folder` is also split into one file per panel
    (<panels_root>/<folder>/<folder><letter>.tif/.png/.pdf).

    The analysis code itself is not edited; only the export resolution changes."""
    import matplotlib.figure as _mf
    stem_to_folder = stem_to_folder or {}
    orig = getattr(_mf.Figure, "_meiotic_orig_savefig", _mf.Figure.savefig)
    _mf.Figure._meiotic_orig_savefig = orig

    def _savefig(self, fname, *a, **kw):
        kw["dpi"] = dpi
        orig(self, fname, *a, **kw)
        fn = str(fname)
        if fn.lower().endswith(".png"):
            kw2 = {k: v for k, v in kw.items() if k not in ("dpi", "format")}
            orig(self, fn[:-4] + ".pdf", *a, dpi=dpi, **kw2)
            stem = os.path.splitext(os.path.basename(fn))[0]
            if panels_root and stem in stem_to_folder:
                folder = stem_to_folder[stem]
                export_panels(self, os.path.join(panels_root, folder), folder, dpi=dpi, save=orig)
    _mf.Figure.savefig = _savefig
