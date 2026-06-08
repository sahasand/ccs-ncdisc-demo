# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A **demonstration** of a clinical-trial analysis workflow run end-to-end on a *fictional*
Phase 1 study (protocol HF-1002-CL-101). All data is synthetic; nothing here is for clinical,
operational, or regulatory-submission use. The published deliverable is the single-page site
(`index.html` + `styles.css` + `app.js`, with self-hosted fonts in `fonts/`); the Python programs,
documents, EDC workbook, and QC report are the supporting artifacts it describes. See `README.md`
for the file-by-file inventory.

GitHub: `sahasand/ccs-ncdisc-demo` (currently **private**; default branch `main`). There is no
CI, build, lint, or test setup.

## The two layers are decoupled — this is the most important thing to know

1. **The static site is the product.** A small set of plain static files — `index.html`
   (structure), `styles.css` (the design system), `app.js` (hash router + accessible tabs),
   self-hosted IBM Plex woff2 in `fonts/`, and `.nojekyll` so GitHub Pages serves the assets
   verbatim. No framework, bundler, package manager, or build step — edit the files directly.
   Tab navigation is hash-routed (`#overview`, `#docs`, `#data`, `#tables`, `#qc`) so individual
   tabs are deep-linkable; `show()`/`showTbl()` in `app.js` drive it. **Viewing:** serve over
   HTTP (`python3 -m http.server`, then `http://127.0.0.1:8000/`) or use GitHub Pages — opening
   `index.html` straight off `file://` works but falls back to system fonts (browsers block
   `file://` font loads).

2. **The Python pipeline does NOT feed the site.** The tables and figures shown in `index.html`
   (the Tables tab, the data tables) are **hand-transcribed mirrors** of the pipeline's output,
   not generated at view time. If a pipeline number changes, you must update `index.html` by
   hand to match — there is no regeneration step linking them.

## Front-end design system

The site uses a *"clinical instrument"* visual system defined in `styles.css`: a refined
**navy/red** identity (navy = institutional/structure; red = signal only — DLT/death/HIGH, the
QC step, critical accents), self-hosted **IBM Plex Sans/Mono**, and a token set of `:root` custom
properties (color, type scale, spacing, shadows). Tone is **formal and serious — no decorative
figures or charts.** When changing the look, *elevate this identity rather than reinventing it*:
a prior editorial redesign (the "Transactions" fascicle, commit `b1bcecc`) was reverted for going
too far off-brand. Keep all text at **WCAG AA** contrast, and make sure `@media print` keeps every
TFL table visible. Note for CSS: `calc()`/`clamp()` require whitespace around `+`/`-`.

## The pipeline (programs 01 → 02 → 03)

Each program writes files the next one reads. **Critical gotcha:** the input/output directories
they expect are *not* checked into this repo, so the pipeline is mostly not runnable from a fresh
clone:

| Program | Reads | Writes | Runnable from a clone? |
|---|---|---|---|
| `01_build_analysis_datasets.py` | `./raw_edc/*.csv` | `./analysis_data/*.csv` | **No** — `raw_edc/` is absent everywhere (not even in the zip). |
| `02_generate_tables.py` | `./analysis_data/*.csv` | `./tables_output/*.txt` + `HF-1002-CL-101_Populated_Tables.docx` | **Yes**, after extracting `analysis_data/` from `HF-1002-CL-101_NonCDISC_Pipeline.zip` into this dir. |
| `03_ae_meddra_soc_pt.py` | `./analysis_data/*.csv` + `./analysis_data/meddra_coding_map.csv` | `tables_output/t_14_3_1_2_teae_by_soc_pt.txt` + `HF-1002-CL-101_Final_TFL_Package.docx` | **No** — `meddra_coding_map.csv` is absent from the repo and the zip. |

Dependencies (not declared anywhere — there is no requirements file): `pip install pandas numpy python-docx`.

The pipeline is deliberately **non-CDISC**: home-grown analysis datasets (`an_subject`, `an_ae`,
`an_lb`, `an_eff`), no SDTM/ADaM, no define.xml. The derivations 01 performs (baseline, change-from-
baseline, TEAE/related/serious/DLT flags, population flags) are computed once and reused by every
table — that is the role ADaM would otherwise play.

## QC model

QC is **independent double-programming**: the whole pipeline was re-derived from scratch in **R**
and compared cell-by-cell against the Python output. Verdict: **PASS WITH FINDINGS**. The R QC
scripts (`qc_*.R`) live in a separate QC workspace and are **not** in this repo — only the
write-ups (`QC_Report.md`, `HF-1002-CL-101_QC_Closure_Memo.docx`) are. Reproducing QC would be
`Rscript qc_run_all.R` in that original workspace.

## Invariants to preserve when editing the site

These are domain facts the narrative depends on; breaking them makes the site internally
inconsistent with the QC:

- **Table 14.3.1.2 has two versions.** A *by-verbatim-term* version (one of the 8 tables the R
  QC double-programmed) and a *MedDRA SOC/PT* version (produced by `03`, **supportive, outside
  the QC scope**). The site displays the SOC/PT version — keep its framing as supportive and
  outside the double-programming QC. The "9 tables" figure = 8 QC'd tables + 1 supportive MedDRA table.
- **The one substantive QC finding is F-3:** the disposition population label (SAP says "Enrolled
  Set", production/spec say "Safety Set"). It has **zero numerical impact** because Enrolled =
  Safety = DLT-Evaluable = 18 in this study. The remaining findings (F-1, F-4, F-5, F-6) are
  display/cosmetic. Don't write copy that claims a single all-encompassing issue in a way that
  contradicts the findings table, and don't overstate QC coverage.
- Keep the **FICTIONAL / synthetic** disclaimers and the fictional sponsor name ("Corvexa
  Therapeutics, Inc.").
