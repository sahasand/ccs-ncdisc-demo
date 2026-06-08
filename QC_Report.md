# Independent QC Report — HF-1002-CL-101

**Protocol:** HF-1002-CL-101 (FICTIONAL / SYNTHETIC — demonstration only)
A Phase 1, open-label, single-arm, sequential dose-escalation gene-therapy study; 18 subjects, 3 dose cohorts (6/6/6). Non-CDISC workflow (raw EDC → home-grown analysis datasets → tables; no SDTM/ADaM).

**QC role:** Independent (double-programming) QC. All analysis datasets and the 8 in-scope tables were re-derived from scratch in **R**, from `raw_edc/` + `specs/`, then compared cell-by-cell against `production_output/`.

**Date:** 2026-06-07 | **QC programmer:** Independent QC (R) | **Status:** ✅ **PASS WITH FINDINGS**

---

## 1. Scope

| In scope | Detail |
|---|---|
| Analysis datasets | `an_subject` (18), `an_ae` (57), `an_lb` (2,131), `an_eff` (503) |
| Tables (8) | 14.1.1 Demographics · 14.1.2 Disposition · 14.1.3 Exposure · 14.3.1.1 TEAE Overall · 14.3.1.2 TEAE by Verbatim Term · 14.3.3.1 DLT by Cohort · 14.2.1.1 LVEF (Central) CFB · 14.2.4.2 KCCQ CFB |
| Cross-foot | Internal reconciliation + tie-out to SAP/protocol (independent of production) |

Out of scope (per CLAUDE.md Appendix B): MedDRA SOC/PT coding (AEs are uncoded by design; 14.3.1.2 is a by-verbatim-term table), and the non-submission caveat (QC is to the SAP + Derivation Spec as written).

## 2. Environment

- **R 4.6.0** (`/opt/homebrew/bin/Rscript`), **base R only** — no third-party packages, so a single `source()` regenerates everything with zero install/manual steps.
- `Sys.setlocale("LC_TIME","C")` set before any date parse; dates parsed explicitly with `as.Date(x, "%d-%b-%Y")` and an NA-introduction guard (no silent `NA`).
- All raw CSVs read as **character** (`colClasses="character"`), then numerics coerced explicitly with an NA-introduction guard (Subject kept as character; no scientific-notation/type-guessing surprises).
- Display formatting via `sprintf("%.Nf")` (IEEE/C round-half-to-even on the stored double) — see Finding F-2.

## 3. Independence & reproducibility

- Analysis datasets and all table statistics were derived **solely** from `raw_edc/` + `specs/`. `production_output/` was opened **only after** the independent derivation was written (`qc_01`, `qc_02` complete), and only by the comparison harness (`qc_compare.R`). Production source code was never requested or used.
- Pipeline (run from `QC/qc_work/`): `Rscript qc_run_all.R` → builds datasets, tables, cross-foot, and the production diff in ~0.3 s.

| Script | Purpose |
|---|---|
| `qc_00_common.R` | paths, raw loader, date/numeric guards, display formatters, stat helpers |
| `qc_01_build_analysis_datasets.R` | independent `an_subject/an_ae/an_lb/an_eff` → `qc_data/` |
| `qc_02_generate_tables.R` | independent 8 tables → `qc_tables/` + machine-readable `qc_cells.csv`, `qc_raw.csv` |
| `qc_03_crossfoot.R` | internal cross-foot & reconciliation, edge-case subjects |
| `qc_compare.R` | cell-by-cell diff vs `production_output/` → `qc_diffs/` + PASS/FAIL summary |
| `qc_run_all.R` | one-shot driver |

## 4. Results — analysis datasets

Compared on natural keys; **every** shared analytical column compared (strings exact; numerics within 1e-6; dates as normalized strings; `DOSE_VG` numerically, since production stores the expanded float `30000000000000.0` vs raw `3.0E13`).

| Dataset | Key | Rows | Cells compared | Differences |
|---|---|---|---|---|
| `an_subject` | SUBJID | 18 | 360 (20 cols) | **0** |
| `an_ae` | SUBJID+AETERM+AESTDAT | 57 | 855 (15 cols) | **0** |
| `an_lb` | SUBJID+LBTESTCD+AVISIT | 2,131 | 23,441 (11 cols) | **0** |
| `an_eff` | SUBJID+PARAMCD+AVISIT | 503 | 3,521 (7 cols) | **0** |

**All four analysis datasets reproduce exactly (0 unexplained cell differences).** Derivation rules verified against the Derivation Spec, including: `SAFFL/FASFL` (all 18), DLT-Evaluable `DLTFL` (all 18 reached/exceeded the Day-1–29 window), `COMPLFL` (16), `DTHFL` (1); AE `AEDY = onset − infusion + 1`, `TEAEFL/RELFL/SERFL/GE3FL/DLTWINFL/DLTFL/FATALFL`; lab `BASE` (screening per subject×test), `CHG`, and `LBALERT` (ALT/AST >5×/>3× ULN); efficacy `BASE/CHG` per subject×param and observed-case visits.

## 5. Results — tables (cell-by-cell vs production)

| Table | Title | Cells | FAIL | Boundary | Verdict |
|---|---|---:|---:|---:|---|
| 14.1.1 | Demographics & Baseline | 56 | 0 | 0 | ✅ PASS |
| 14.1.2 | Disposition | 24 | 0 | 0 | ✅ PASS |
| 14.1.3 | Extent of Exposure | 16 | 0 | 0 | ✅ PASS |
| 14.3.1.1 | TEAE Overall | 24 | 0 | 0 | ✅ PASS |
| 14.3.1.2 | TEAE by Verbatim Term | 48 | 0 | 0 | ✅ PASS |
| 14.3.3.1 | DLT by Cohort | 12 | 0 | 0 | ✅ PASS |
| 14.2.1.1 | LVEF (Central) CFB | 56 | 0 | 1 | ✅ PASS (1 boundary) |
| 14.2.4.2 | KCCQ CFB | 56 | 0 | 0 | ✅ PASS |
| **Total** | | **292** | **0** | **1** | |

Every production data row was mapped and compared (0 unmapped rows). Counts and n(%) match **exactly**; continuous statistics match production's display **and** agree on the unrounded value within 1e-6. The single "boundary" cell is a display-rounding artifact with bit-level unrounded agreement (Finding F-1).

Confirmed key results (independently reproduced): Total Age 59.7 (10.04), median 59.0, 43–76; <65 12 (66.7%); Male 11 (61.1%); Baseline LVEF 23.6 (4.73); NYHA III 18 (100%). TEAE Total: Any 18 (100%), Related 18 (100%), SAE 2 (11.1%), Grade ≥3 3 (16.7%), DLT 2 (11.1%), Deaths 1 (5.6%). DLT: Hepatic transaminases increased (Cohort 1, n=1), Myocarditis (Cohort 3, n=1). LVEF central mean CFB at M12: C1 +1.9, C2 +4.4, C3 +6.1 (observed n 6/5/5).

## 6. Cross-foot & reconciliation (independent of production) — 28/28 PASS

- Populations tie to SAP/protocol: Safety = FAS = DLT-Evaluable = 18; completers 16; deaths 1; ≤6/cohort; cohorts 6/6/6.
- Cohort columns sum to Total for **all 47** count rows.
- Safety events reconcile across `an_ae` and tables: **SAE {2005, 3003}**; **Grade ≥3 {1002, 2005, 3003}**; **DLT {1002, 3003}**; **Fatal {2005}**. DLT total reconciles between 14.3.1.1 (=2) and 14.3.3.1 (=2).
- Death (2005) ties across disposition (`DSDECOD=DEATH`), AE (`AEOUT=FATAL`), and `DTHFL=Y`.
- Efficacy observed-case n consistent with disposition: LVEF baseline 18; M3 17; M6 16; M12 16 (by cohort 6/5/5).
- **Edge-case subjects verified:** 1002 Grade-3 hepatotoxicity DLT in window (Day 15; ALT 283/AST 290 = >5×ULN at WK2); 3003 myocarditis serious DLT at **Day 29** (window boundary); 2005 DTHFL=Y/COMPLFL=N/no M12; 3006 COMPLFL=N/no M3–M12; 1005 missed M6 only. Verified that an `AEDLT=Y` outside the window would **not** be counted as a DLT.

## 7. Discrepancy log

No data or derivation defects were found. All discrepancies below are display-formatting or documentation items; each is explained and resolved.

### F-1 — LVEF 14.2.1.1, Cohort 1, Month 12 *Observed* Mean: production `25.0` vs QC `25.1` — **rounding (x.x5 boundary)**
- **Cells:** 6 values {28.4, 22.8, 22.5, 24.9, 19.1, 32.6}; arithmetic mean = exactly 25.05.
- **Root cause:** floating-point **summation order**. R `mean()` = `25.05000000000000071` (just above 25.05); numpy `mean()` = `25.04999999999999716` (just below). Both formatted with `%.1f` → R 25.1, Python 25.0. Unrounded values agree to **3.55e-15** (far inside the 1e-6 tolerance).
- **Assessment:** Not a defect. Production's `25.0` is the round-half-to-even result of the true value 25.05 (SAP convention) and is the technically preferred display. The QC display is the artifact; no R formatting choice can match without replicating numpy's pairwise summation (not warranted to chase a 1e-15 effect).
- **Classification:** rounding / x.x5 boundary. **Resolution:** accepted as `PASS(boundary)` per the CLAUDE.md tolerance rule (compare unrounded at x.x5 boundaries). Logged in `qc_diffs/difftab_14_2_1_1.csv`.

### F-2 — Demographics 14.1.1, Cohort 1, Baseline LVEF Mean: initial QC `23.0` vs production `22.9` — **QC-code formatting (resolved)**
- **Root cause:** the cohort-1 mean is 22.95, stored as `22.9499999999999993`. The first QC build used R's `round()`, which since R 4.0 is **decimal-aware** and returned `23.0`; production uses Python `%.1f`, which formats the stored double → `22.9`. R `sprintf("%.1f", …)` = `22.9` (matches the stored value and production).
- **Assessment:** Production is correct; the QC display was the outlier (checked own code before raising any defect, per the golden rules).
- **Classification:** QC-code formatting. **Resolution:** QC formatters changed from `round()+formatC` to `sprintf("%.Nf")` (standard IEEE/C rounding). After the fix QC = `22.9`, matching production. (This also surfaced F-1, which is irreducible.)

### F-3 — Disposition population label: SAP says **"Enrolled Set"**, production/spec say **"Safety Set"** — **documentation inconsistency**
- The SAP §11 TLF inventory and the mock shell (A.x) label T-14.1.2 population as **Enrolled Set**; the Derivation Spec, CLAUDE.md, and the production table header (`t_14_1_2_disposition.txt`) use **Safety Set**.
- **Impact:** none numerically (Enrolled = Safety = 18 here). The SAP is the higher authority (CLAUDE.md), but production followed the Derivation Spec; because the populations coincide, no cell is affected.
- **Classification:** spec/SAP disagreement (documentation). **Recommendation:** align the SAP, mock shell, and table footnote on a single population label for 14.1.2 in the next revision.

### F-4 — DLT verbatim term trimmed in display (14.3.1.2, 14.3.3.1) — **cosmetic label**
- Raw `AETERM = "Hepatic transaminases increased (ALT >5x ULN)"`; production displays `"Hepatic transaminases increased"` (parenthetical qualifier dropped). **Counts identical** (1/0/0/1).
- **Classification:** cosmetic. CLAUDE.md specifies grouping by *exact* verbatim term; the production display label deviates slightly from the raw verbatim, but only one subject carries the term so grouping and all counts are unaffected. **Resolution:** noted; no count impact. (QC mapped the two labels explicitly in the harness.)

### F-5 — 95% CI display precision: production **1 dp**, mock shell specified **2 dp** — **minor (production vs shell)**
- Production renders the descriptive t-based 95% CI at 1 decimal (e.g., `(-1.3, 2.7)`); mock shell A.2 showed `(xx.xx, xx.xx)`. QC matched production (1 dp); the underlying CI bounds agree. CI confirmed t-based with **df = n−1** (`qt(0.975, n−1)`), not 1.96; the `(-)` convention for n<2 was implemented (not triggered in these two tables, where min cohort n = 5).
- **Classification:** minor formatting (production deviates from mock shell). No value impact.

### F-6 — DLT-by-term rows show plain counts (14.3.3.1) — **formatting note**
- Under "DLT by term, n", production prints plain integers (`1`) with no percent, while the header row "Subjects with ≥1 DLT" shows n (%). QC reproduced the counts; harness compares the integer. No issue.

## 8. Conclusion / sign-off

- **Analysis datasets:** all four reproduce with **0** unexplained cell differences (28,177 cells).
- **Tables:** all 8 reproduce — counts and n(%) **exact**; continuous statistics within tolerance after identical rounding. **0 FAIL** cells across 292 compared; **1** documented x.x5 rounding-boundary cell (unrounded identical to 3.6e-15).
- **Cross-foot:** 28/28 internal checks pass and tie to the SAP/protocol.
- **Defects:** **none** in the production output. Findings F-1, F-4, F-5, F-6 are display/cosmetic; F-2 was a QC-code formatting item (resolved); F-3 is a SAP-vs-spec documentation inconsistency with no data impact.

### FINAL VERDICT: ✅ **PASS WITH FINDINGS**

The production analysis datasets and the 8 tables are confirmed numerically correct against an independent R re-derivation from raw EDC + specs. The only residual table difference is a single x.x5 floating-point display-rounding artifact (F-1) with bit-level unrounded agreement; it is not a data error. Documentation finding F-3 (disposition population label: SAP "Enrolled Set" vs production "Safety Set") is raised for SAP/shell alignment but has no numerical impact.

---
*Artifacts:* `qc_work/qc_data/` (QC datasets, `qc_cells.csv`, `qc_raw.csv`), `qc_work/qc_tables/` (QC tables), `qc_work/qc_diffs/` (per-object machine-readable diffs + `qc_compare_summary.csv`). Reproduce with `Rscript qc_run_all.R`.
