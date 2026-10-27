"""Structural and layout checks on manuscript/FINAL_INTEGRATED_MANUSCRIPT.docx.
Usage: python scripts/validate_manuscript_docx.py [rendered.pdf]   (the PDF, e.g. exported by Word, enables page checks)"""
import re, sys, zipfile, csv, glob
import xml.etree.ElementTree as ET
DOCX = "manuscript/FINAL_INTEGRATED_MANUSCRIPT.docx"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
z = zipfile.ZipFile(DOCX); assert z.testzip() is None
root = ET.fromstring(z.read("word/document.xml"))
paras = ["".join(t.text or "" for t in p.iter(W + "t")) for p in root.iter(W + "p")]
text = "\n".join(paras); fails = []
def check(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg); (None if ok else fails.append(msg))
ia = next(i for i, p in enumerate(paras) if p.startswith("Keywords:"))
check(not any(p.startswith("Graphical abstract.") for p in paras), "no separate unnumbered graphical abstract (the overview is Figure 1)")
check(any(p.startswith("Figure 1. Overview of the study design") for p in paras), "Figure 1 is the overview")
check(paras.index(next(p for p in paras if p.startswith("Figure 1. Overview"))) < paras.index("2. Materials and Methods"), "Figure 1 sits before Methods")
check(len(root.findall(f".//{W}drawing")) >= 1, "drawing present")
figs = sorted(set(int(n) for n in re.findall(r"^Figure (\d+)\. ", text, re.M)))
check(figs == [1, 2, 3, 4, 5, 6, 7], f"main figure captions {figs}")
check(sorted(set(re.findall(r"^Table (\d)\. ", text, re.M))) == list("123456"), "main table captions 1-6")
check(sorted(set(int(n) for n in re.findall(r"^Supplementary Table S(\d+)\. ", text, re.M))) == list(range(1, 12)), "Supplementary Tables S1-S11")
check(sorted(set(int(n) for n in re.findall(r"^Supplementary Fig\. S(\d+)\. ", text, re.M))) == list(range(1, 8)), "Supplementary Figs S1-S7")
for s in ("scripts/download_data.py", "DATA/meiotic", "1.2 GB", "CIBERSORTx output (Job 14)", "Canonical_Outputs.md", "TCGAbiolinks"):
    check(s in text, f"availability text contains '{s}'")
rows = [len(t.findall(W + "tr")) - 1 for t in root.iter(W + "tbl")]
csvs = sorted(glob.glob("supplementary/tables/*.csv")) + sorted(glob.glob("manuscript/tables/*.csv"))
csvrows = sorted(sum(1 for _ in csv.reader(open(f, encoding="utf-8-sig"))) - 1 for f in csvs)
check(sorted(rows) == csvrows, f"{len(rows)} docx tables match {len(csvs)} CSV exports in row counts")
if len(sys.argv) > 1:
    import fitz
    d = fitz.open(sys.argv[1]); n = len(d)
    short = [i + 1 for i, p in enumerate(d) if len(p.get_text().strip()) < 250]
    check(not short, f"{n} pages, no near-empty pages (found {short})")
    for i, p in enumerate(d):
        if "Figure 1. Overview" in p.get_text(): check(i <= 4, f"Figure 1 on page {i + 1}")
print("FAILED:" if fails else "ALL CHECKS PASSED", *fails)
sys.exit(bool(fails))
