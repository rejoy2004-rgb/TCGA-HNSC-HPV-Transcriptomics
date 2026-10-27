# Reconciliation of the three manuscript versions (2026-10-27)

Versions: **DOCX** (`manuscript/FINAL_INTEGRATED_MANUSCRIPT.docx`), **Doc 1** = Google Doc "HPV Manuscript" (id 1nH7A1JK…, owner naisargbpatel14, tabs Revised Manuscript / Revised Supplementary File), **Doc 2** = Google Doc "HPV_Manuscript_revised" (id 1G5xpNNJ…, owner Suganth). Backups of both Google Docs before any edit are in `gdoc_backups_2026-10-27/`.

## Canonical version: Doc 1
Doc 1 is the authors' working text: full author block and affiliations, seven-person contributions, its own Abstract and Conclusions, and the numbering the reviewer used. Doc 2 is an older state (no author block, six figures, old declarations). The DOCX is a build of the repository's own text and is now aligned to Doc 1.

## Figure numbering
- **Evidence:** the reviewer's email calls the graphical overview "Figure 1" and asks that "Figure 2 and Supplementary Table S2" share the top-gene ranking. In Doc 1, Figure 1 is the overview and Figure 2 is the volcano/top-gene figure, so the reviewer's numbering is Doc 1's. Doc 2 numbers the volcano as Figure 1.
- **Decision applied to the DOCX:** Doc 1 numbering, seven main figures: Figure 1 overview (placed after the Introduction, as in Doc 1; the Introduction ends with "summarised in Fig. 1"), Figure 2 volcano, Figures 3-7 as before plus one. All in-text "Fig. N" references and captions were renumbered in a single pass; supplementary numbering is unchanged. A pre-change copy is `../FINAL_INTEGRATED_MANUSCRIPT.pre_renumber.docx`.
- **Consequence:** the earlier request that the graphical abstract stay unnumbered no longer holds. Because the reviewer treats the overview as Figure 1, the approved redraw is now Figure 1 and there is no separate unnumbered copy.
- **Needs author confirmation:** Doc 1's Figure 1 is a different, BioRender-style image (cohort, methylation, class-specificity and single-cell panels). The reviewer's request to make it readable at 600 dpi refers to that image. The DOCX Figure 1 uses the approved redraw (`manuscript/submission_figures/Figure1.png`) with a caption written from numbers already in the manuscript. The authors must choose which image is Figure 1: (a) the redraw, or (b) their original exported at 600 dpi (the original file is not in this project and could not be downloaded from the Google Doc).

## Abstract and Conclusions
| Version | Wording | Assessment |
|---|---|---|
| Doc 1 (before my edits) | Conclusions: "strongly distinguished...", "findings supported across independent cohorts", "meiotic gene reactivation represents a distinct molecular feature... rather than nonspecific germ-cell gene derepression" | "strongly", "supported" and "represents" are stronger than correlative cohort data allow; softened in Doc 1 |
| Doc 1 (now) | associated with...; "differs from"; "consistent findings"; "These associations are correlative...; causality was not tested" | Most defensible: states association only, names the comparator, flags causality. Kept as canonical |
| DOCX (before) | Structured Abstract with CIs; Conclusions with "directed epigenetic programme", "specific, internally coordinated", "dependent on viral transcriptional activity" | Stronger than the data; replaced |
| DOCX (now) | Abstract and Conclusions copied from Doc 1 (now). The Abstract no longer carries the confidence intervals or the 22% proliferation attenuation (both remain in Results) | Aligned; the authors may want the CIs back |
| Doc 2 | My earlier softened text (structured Abstract, hedged Conclusions) | **Not aligned to Doc 1.** The write that would have aligned it was refused by the permission system. Still open: replace its four Abstract paragraphs and Conclusions with Doc 1's text |

One scientific point in Doc 1's Abstract: "The meiotic association persisted after accounting for ... proliferation" while Results report a 22% attenuation of the four-gene effect after proliferation adjustment. "Persisted" is accurate but incomplete; consider "was attenuated but persisted".

## Author information
| Item | DOCX | Doc 1 | Doc 2 |
|---|---|---|---|
| Author list (8), affiliations (8), joint first authors, two corresponding authors with e-mails | present (copied from Doc 1) | present | **absent** |
| Seven-person contribution statement | present | present | present |
| Funding | "No external funding was received for this work." | same | same |
| Ethics, competing interests, acknowledgements | identical text | identical | identical |
| Consent to participate / publication | absent | absent | absent |

**Authors must confirm (not guessed):**
1. Funding: the text says "No external funding was received for this work.", while the contribution statement gives V. Modhukur the role "Funding acquisition". Either the role or the funding statement needs to change, or the funding statement should name the source.
2. Competing interests ("The authors declare no competing interests.") given affiliations with Celvia CC AS and Nalam Biosciences OÜ.
3. Whether the target journal needs "Consent to participate / for publication: not applicable" lines.
4. Author name form: Doc 1 uses "Sajitha Lulu. S" in the byline and "Sajitha Lulu S." in the contributions; the DOCX byline uses "Sajitha Lulu S".

## Overview figure in the Google Docs
Inserting an image through the Docs API needs a publicly reachable URL. Publishing the manuscript figure to a public address was not authorised, so nothing was inserted in either Google Doc. Doc 1 already has an overview as Figure 1, so a second insertion would duplicate it. Manual steps if the authors choose option (a): in Doc 1, right-click the Figure 1 image, choose Replace image, then Upload from computer, and select `manuscript/submission_figures/Figure1.png`; then replace the Figure 1 caption with the DOCX caption (the old caption describes the BioRender panels). Doc 2 has no overview figure; add it after the Introduction only if Doc 2 is to be kept, and renumber its figures as in Doc 1.
