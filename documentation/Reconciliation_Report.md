# Reconciliation of the three manuscript versions (2026-10-27)

Versions: **DOCX** (`manuscript/FINAL_INTEGRATED_MANUSCRIPT.docx`), **Doc 1** = Google Doc "HPV Manuscript" (id 1nH7A1JK…, owner naisargbpatel14, tabs Revised Manuscript / Revised Supplementary File), **Doc 2** = Google Doc "HPV_Manuscript_revised" (id 1G5xpNNJ…, owner Suganth). Backups of both Google Docs before any edit are in `gdoc_backups_2026-10-27/`.

## Canonical version: Doc 1
Doc 1 is the authors' working text: full author block and affiliations, seven-person contributions, its own Abstract and Conclusions, and the numbering the reviewer used. Doc 2 is an older state (no author block, six figures, old declarations). The DOCX is a build of the repository's own text and is now aligned to Doc 1.

## Figure numbering and structure (updated 2026-10-27, second pass)
- **Evidence:** the reviewer's email calls the graphical overview "Figure 1" and asks that "Figure 2 and Supplementary Table S2" share the top-gene ranking. In Doc 1, Figure 1 is the authors' overview image and Figure 2 is the volcano/top-gene figure, so the reviewer's numbering is Doc 1's. Doc 2 numbers the volcano as Figure 1.
- **Original Figure 1 recovered:** the authors' BioRender-style overview was recovered from Doc 1 (the image embedded in the document, 2046 x 1432 px) and saved as `figures/integrated/Figure1_overview_original.png`. The older backup zip does not contain it (its "Figure 1" files are the volcano figure). It is not a 600 dpi export.
- **DOCX structure now:** Abstract, Keywords, unnumbered redrawn graphical abstract, Introduction (ending "summarised in Fig. 1"), **Figure 1 = authors' overview** (their caption, unchanged), **Figure 2 = volcano/top-gene**, Figures 3-7 follow; supplementary numbering is unchanged. Exported files: `Figure1`-`Figure7` and `Graphical_Abstract` in `manuscript/submission_figures/`.
- **Earlier mistake corrected:** in the previous pass the redraw had been put in as numbered Figure 1. That substitution had no authors' approval and has been reversed. Backups: `../FINAL_INTEGRATED_MANUSCRIPT.pre_figure1_restore.docx`.
- **Still needed from the authors:** a 600 dpi export of the original overview (see `Author_Confirmation_Checklist.md`).

## Abstract and Conclusions
| Version | Wording | Assessment |
|---|---|---|
| Doc 1 (before my edits) | Conclusions: "strongly distinguished...", "findings supported across independent cohorts", "meiotic gene reactivation represents a distinct molecular feature... rather than nonspecific germ-cell gene derepression" | "strongly", "supported" and "represents" are stronger than correlative cohort data allow; softened in Doc 1 |
| Doc 1 (now) | associated with...; "differs from"; "consistent findings"; "These associations are correlative...; causality was not tested" | Most defensible: states association only, names the comparator, flags causality. Kept as canonical |
| DOCX (before) | Structured Abstract with CIs; Conclusions with "directed epigenetic programme", "specific, internally coordinated", "dependent on viral transcriptional activity" | Stronger than the data; replaced |
| DOCX (now) | Abstract and Conclusions match Doc 1, including the proliferation sentence below. The Abstract carries no confidence intervals (they remain in Results) | Aligned |
| Doc 2 | My earlier softened text (structured Abstract, hedged Conclusions) | **Not aligned to Doc 1.** The write that would have aligned it was refused by the permission system. Still open: replace its four Abstract paragraphs and Conclusions with Doc 1's text |

**Proliferation wording (checked against the data and applied to Doc 1 and the DOCX):** the old Abstract said the association "persisted" after proliferation adjustment. The statistics: in the pooled single-cell per-tumour model the four-gene HPV coefficient fell from 0.141 to 0.109 (about 22%; P 4.5 x 10^-6 to 2.7 x 10^-5), with larger attenuation in GSE182227 (35%) than GSE181919 (6%). In the bulk analyses proliferation adjustment did not attenuate the effect (GSE65858 logistic beta 4.45 to 4.52; TCGA beta 2.29 to 2.25). So "attenuated but persisted" is accurate only for the single-cell tumour-level model, and the new sentence says exactly that: "The meiotic association persisted after accounting for anatomical site and tumour purity; adjustment for proliferation attenuated the single-cell tumour-level association, which nevertheless remained significant in the pooled analysis (Supplementary Table S10)." (The 22% figure was later dropped from the Abstract because the stored GSE182227 outputs do not reproduce it; see `Reproducibility_Audit.md`.) No causal language was added and no quantitative result was removed from Results.

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

## Google Docs status
- **Doc 1:** edited (the Abstract proliferation sentence, on top of the earlier edits); a revision check confirmed nobody else had edited it in between.
- **Doc 2:** not updated; see `Doc2_Alignment_Checklist.md`.
- **Images:** nothing was uploaded or published. Doc 1 already holds the authors' Figure 1.
