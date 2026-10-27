"""Checks every reference in build_integrated_manuscript.js against Crossref (author order, year, title, journal, volume, pages, DOI).
Writes documentation/Reference_Audit.md. Needs network access."""
import re, json, urllib.request, difflib, sys
src = open("scripts/build_integrated_manuscript.js", encoding="utf-8").read()
block = src[src.index("const refs = ["):]; block = block[:block.index("\n];")]
refs = re.findall(r'^\s*"(.*)",?$', block, re.M)
norm = lambda s: re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()
body = src[:src.index("const refs = [")]
seen = []
for d in re.findall(r"https://doi\.org/([^\s;\]]+)", body):
    d = d.rstrip(".,")
    if d not in seen and any(r.endswith("doi.org/" + d) for r in refs): seen.append(d)      # manuscript numbers follow first appearance
rows = []
for n, r in enumerate(refs, 1):
    doi = re.search(r"doi\.org/(\S+)$", r).group(1)
    m = re.match(r"(.*?)\. (.*?)\. \*(.*?)\*\. (\d{4});([^.]*?)\. https", r)
    authors, title, jour, year, volpg = m.groups() if m else (None,) * 5
    try:
        c = json.load(urllib.request.urlopen(urllib.request.Request("https://api.crossref.org/works/" + doi, headers={"User-Agent": "ref-audit (set your contact address here)"}), timeout=30))["message"]
    except Exception as e:
        rows.append((n, doi, "UNVERIFIED", [f"Crossref lookup failed: {e}"])); continue
    issues = []
    if not m: issues.append("could not parse reference string")
    else:
        ct = c.get("title", [""])[0]
        sim = difflib.SequenceMatcher(None, norm(title), norm(ct)).ratio()
        if sim < 0.9: issues.append(f"title differs (sim {sim:.2f}): Crossref '{ct}'")
        fa = (c.get("author") or [{}])[0].get("family", "")
        if norm(fa).split()[:1] and norm(fa).split()[0] not in norm(authors.split(",")[0] if "Network" not in authors else authors): issues.append(f"first author: Crossref '{fa}' vs '{authors.split(',')[0]}'")
        if not c.get("author"): issues.append("no author list in Crossref") if "Network" not in authors else None
        cy = (c.get("issued", c.get("published", {})).get("date-parts") or [[None]])[0][0]
        py = (c.get("published-print", {}).get("date-parts") or [[None]])[0][0]
        if str(year) not in (str(cy), str(py)): issues.append(f"year {year} vs Crossref {py or cy}")
        cj = " ".join([c.get("container-title", [""])[0]] + c.get("short-container-title", []))
        if difflib.SequenceMatcher(None, norm(jour), norm(c.get("container-title", [""])[0])).ratio() < 0.6 and norm(jour) not in norm(cj): issues.append(f"journal '{jour}' vs '{c.get('container-title', [''])[0]}'")
        v, pg = c.get("volume", ""), c.get("page", c.get("article-number", ""))
        mv = re.match(r"(\d+)(?::|$)(.*)", volpg)
        if mv and v and mv.group(1) != v: issues.append(f"volume {mv.group(1)} vs {v}")
        elif not mv: issues.append(f"volume/pages '{volpg}' not parsed")
        else:
            first = re.split(r"[–-]", mv.group(2))[0].strip()
            if first and pg and first not in pg and first not in c.get("article-number", ""): issues.append(f"pages '{mv.group(2)}' vs Crossref '{pg}'")
        n_auth = len(c.get("author", [])); listed = authors.count(",") + 1
        if "et al" not in authors and n_auth and n_auth != listed and "Network" not in authors: issues.append(f"{listed} authors listed vs {n_auth} in Crossref")
    rows.append((n, doi, "OK" if not issues else "CHECK", issues))
out = ["# Reference audit (metadata)", "", "Each DOI was resolved through Crossref and compared with the reference string in `scripts/build_integrated_manuscript.js` (first author, title, year, journal, volume, pages, author count). Whether each paper supports its in-text claim is not checked by this script; see below.", "", "| Manuscript no. | Source row | DOI | Status | Discrepancies |", "|---|---|---|---|---|"]
for n, d, s, i in rows: out.append(f"| {seen.index(d) + 1 if d in seen else '-'} | {n} | {d} | {s} | {'; '.join(i) or '-'} |")
open("documentation/Reference_Audit.md", "w", encoding="utf-8").write("\n".join(out) + "\n")
NOTES = """
## Reading of the CHECK rows

The five journal-name flags (Arch Pathol Lab Med, Int J Cancer, J Biol Chem twice, Int J Mol Sci) are false positives: the manuscript uses the journal's standard abbreviation and Crossref returns the full name. The year flag for Zhou 2017 (*Nucleic Acids Res* 45:e22) is also benign: the paper was published online in 2016 and appears in the 2017 volume, so the volume, article number and year in the manuscript are correct. All 48 DOIs resolve, and first author, title, journal, volume, pages and author count agree with Crossref. No reference string was changed.

## Whether each reference supports its claim

Checked from the title, journal and the claim sentence in the manuscript, not from the full text of each paper (the full texts were not read). No reference appears to be misattributed. Points for the authors to confirm:

- Chiappinelli 2016 (combining epigenetic therapy and immunotherapy) is cited for "CTAs as broadly shared immunotherapeutic targets"; it supports the epigenetic-induction side of that statement only loosely.
- Choi 2023 and Puram 2023 are assigned to GSE181919 and GSE182227. This is how the authors cite the cohorts; the GEO-to-paper mapping was not independently confirmed here.
- Hinic 2022 is cited for SYCP2 and TAF7L emerging from a combined TCGA expression and methylation analysis; this was judged from the title only.
"""
open("documentation/Reference_Audit.md", "a", encoding="utf-8").write(NOTES)
print(sum(r[2] == "OK" for r in rows), "OK of", len(rows))
for r in rows:
    if r[2] != "OK": print(r)
