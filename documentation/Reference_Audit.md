# Reference audit (metadata)

Each DOI was resolved through Crossref and compared with the reference string in `scripts/build_integrated_manuscript.js` (first author, title, year, journal, volume, pages, author count). Whether each paper supports its in-text claim is not checked by this script; see below.

| Manuscript no. | Source row | DOI | Status | Discrepancies |
|---|---|---|---|---|
| 3 | 1 | 10.1038/nature14129 | OK | - |
| 4 | 2 | 10.1056/NEJMoa0912217 | OK | - |
| 10 | 3 | 10.1186/gm419 | OK | - |
| 8 | 4 | 10.1186/s13073-017-0419-z | OK | - |
| 11 | 5 | 10.5858/arpa.2014-0554-RA | CHECK | journal 'Arch Pathol Lab Med' vs 'Archives of Pathology &amp; Laboratory Medicine' |
| 15 | 6 | 10.1002/gcc.20160 | OK | - |
| 16 | 7 | 10.1093/nar/gkn673 | OK | - |
| 30 | 8 | 10.1158/2159-8290.CD-12-0095 | OK | - |
| 31 | 9 | 10.1126/scisignal.2004088 | OK | - |
| 14 | 10 | 10.1002/ijc.29649 | CHECK | journal 'Int J Cancer' vs 'International Journal of Cancer' |
| 32 | 11 | 10.1038/s41467-023-36691-x | OK | - |
| 33 | 12 | 10.1038/s41588-023-01357-3 | OK | - |
| 1 | 13 | 10.3322/caac.21660 | OK | - |
| 2 | 14 | 10.1200/JCO.2011.36.4596 | OK | - |
| 5 | 15 | 10.1038/nrc.2018.11 | OK | - |
| 6 | 16 | 10.1038/s41571-022-00603-7 | OK | - |
| 7 | 17 | 10.1038/nrc2886 | OK | - |
| 9 | 18 | 10.1111/cas.12761 | OK | - |
| 12 | 19 | 10.1016/j.omtn.2022.11.012 | OK | - |
| 13 | 20 | 10.1073/pnas.1416074111 | OK | - |
| 23 | 21 | 10.1158/2159-8290.CD-14-1092 | OK | - |
| 17 | 22 | 10.1038/301089a0 | OK | - |
| 18 | 23 | 10.1371/journal.pone.0058743 | OK | - |
| 19 | 24 | 10.1016/j.tranon.2019.02.008 | OK | - |
| 20 | 25 | 10.1158/0008-5472.CAN-15-2125 | OK | - |
| 21 | 26 | 10.1056/NEJMoa1602252 | OK | - |
| 22 | 27 | 10.1073/pnas.2204071119 | OK | - |
| 24 | 28 | 10.3390/cells12121627 | OK | - |
| 25 | 29 | 10.1016/j.jbc.2023.105348 | CHECK | journal 'J Biol Chem' vs 'Journal of Biological Chemistry' |
| 26 | 30 | 10.1080/15384101.2020.1743902 | OK | - |
| 43 | 31 | 10.1126/science.aad0501 | OK | - |
| 34 | 32 | 10.1186/s13059-014-0550-8 | OK | - |
| 35 | 33 | 10.1089/omi.2011.0118 | OK | - |
| 36 | 34 | 10.1073/pnas.0506580102 | OK | - |
| 41 | 35 | 10.1038/s41587-019-0114-2 | OK | - |
| 27 | 36 | 10.1158/0008-5472.CAN-06-3619 | OK | - |
| 28 | 37 | 10.1111/cas.12809 | OK | - |
| 29 | 38 | 10.3390/ijms231810967 | CHECK | journal 'Int J Mol Sci' vs 'International Journal of Molecular Sciences' |
| 44 | 39 | 10.1095/biolreprod.108.067645 | OK | - |
| 45 | 40 | 10.1074/jbc.M506797200 | CHECK | journal 'J Biol Chem' vs 'Journal of Biological Chemistry' |
| 46 | 41 | 10.1073/pnas.1000473107 | OK | - |
| 42 | 42 | 10.1038/nbt.2203 | OK | - |
| 40 | 43 | 10.1148/radiology.143.1.7063747 | OK | - |
| 39 | 44 | 10.2307/2531595 | OK | - |
| 37 | 45 | 10.1093/nar/gky691 | OK | - |
| 38 | 46 | 10.1093/nar/gkw967 | CHECK | year 2017 vs Crossref 2016; pages 'e22' vs Crossref 'gkw967' |
| 47 | 47 | 10.1038/s41586-019-1914-8 | OK | - |
| 48 | 48 | 10.1038/s41586-019-1906-8 | OK | - |

## Reading of the CHECK rows

The five journal-name flags (Arch Pathol Lab Med, Int J Cancer, J Biol Chem twice, Int J Mol Sci) are false positives: the manuscript uses the journal's standard abbreviation and Crossref returns the full name. The year flag for Zhou 2017 (*Nucleic Acids Res* 45:e22) is also benign: the paper was published online in 2016 and appears in the 2017 volume, so the volume, article number and year in the manuscript are correct. All 48 DOIs resolve, and first author, title, journal, volume, pages and author count agree with Crossref. No reference string was changed.

## Whether each reference supports its claim

Checked from the title, journal and the claim sentence in the manuscript, not from the full text of each paper (the full texts were not read). No reference appears to be misattributed. Points for the authors to confirm:

- Chiappinelli 2016 (combining epigenetic therapy and immunotherapy) is cited for "CTAs as broadly shared immunotherapeutic targets"; it supports the epigenetic-induction side of that statement only loosely.
- Choi 2023 and Puram 2023 are assigned to GSE181919 and GSE182227. This is how the authors cite the cohorts; the GEO-to-paper mapping was not independently confirmed here.
- Hinic 2022 is cited for SYCP2 and TAF7L emerging from a combined TCGA expression and methylation analysis; this was judged from the title only.
