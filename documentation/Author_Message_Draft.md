# Draft message to the corresponding authors (not sent)

**To:** Vijayachitra Modhukur, Andres Salumets (corresponding authors); cc Suganth Gopinath Sangeetha, Naisarg Patel
**Subject:** HPV meiotic-programme manuscript: points to confirm before submission

Dear Dr Modhukur and Prof. Salumets,

We have finished the technical corrections the reviewer asked for. Before the manuscript can be submitted, a few points need the authors' decision. None of them is a criticism of anyone's work; they are places where two parts of the manuscript, or the manuscript and the repository, say slightly different things, and only you can say which is right.

**1. GSE182227 results (most important).** The manuscript, Doc 1 and Supplementary Table S10 report, for GSE182227, a four-gene HPV difference of 0.176 and an AUC of 0.945, and a pooled proliferation-adjusted attenuation of 22%. The output files in `results/meiotic_programme/gse182227/` (dated 25 October) give 0.141, an AUC of 0.836 and 28.5%, and in GSE182227 alone the effect is no longer significant after proliferation adjustment (P = 0.11). The manuscript values match an earlier (8 October) analysis. Could you tell us which analysis is final? We have not changed any result. As a precaution the Abstract no longer quotes the 22% figure; the Results still do.

**2. Figure 1 at 600 dpi.** The reviewer asked for the original overview at 600 dpi. The only copy we can recover is the one embedded in the Google Doc, 2046 x 1432 pixels (about 300 dpi at print width), because Google Docs stores images at no more than 2048 px. Could you export the original BioRender figure as PNG or TIFF at 600 dpi (about 4100 x 2900 px) and send it? We have not enlarged the image artificially.

**3. Funding.** The manuscript says "No external funding was received for this work.", and the contributions list gives Vijayachitra Modhukur the role "Funding acquisition". These can both be true (for example, if the funds were internal), so this may need no change; we would like you to confirm the wording.

**4. Competing interests.** The declaration reads "The authors declare no competing interests." Some authors are affiliated with Celvia CC AS and Nalam Biosciences OÜ. An affiliation does not by itself imply a competing interest; we just need each author to confirm that the statement is accurate for them.

**5. Consent declarations.** The study uses public, de-identified data. Does the target journal require "Consent to participate / Consent for publication: not applicable" statements? If so we will add them.

**6. Author name.** Is it "Sajitha Lulu. S" (byline in Doc 1) or "Sajitha Lulu S." (contributions)? We would like to use one form throughout.

**7. Graphical abstract.** We prepared a separate redrawn graphical abstract (unnumbered, after the Keywords) in addition to your Figure 1. Is it approved for inclusion, or should it be left out?

**8. The second Google Doc.** `HPV_Manuscript_revised` is out of date (no author block, old figure numbering). We have not changed it. If it is still in use, its owner can follow `documentation/Doc2_Alignment_Checklist.md`.

Everything else (references, abstract and conclusions wording, the figure order Figure 1 overview, Figure 2 volcano, supplementary tables) is consistent with Doc 1 and the reviewer's numbering. The R analysis stages, the single-cell stages and the CIBERSORTx run have not been re-executed by us, so we cannot yet say the whole analysis is reproducible end to end.

Thank you,
[sender]
