# Non-CDISC Workflow Demo — HF-1002-CL-101

A worked example of a clinical-trial analysis workflow run end to end on a **fictional**
Phase 1 study, from source documents to QC'd tables. Open `index.html` in a browser to
view the single-page site.

> **Demonstration only.** Protocol HF-1002-CL-101 is fictional and all data is synthetic.
> Not for clinical, operational, or regulatory-submission use.

## What's here

| File | Description |
|------|-------------|
| `index.html` | Single-page site summarizing the workflow (open in a browser) |
| `01_build_analysis_datasets.py` | Derives non-CDISC analysis datasets from raw EDC |
| `02_generate_tables.py` | Generates the populated TFL tables |
| `03_ae_meddra_soc_pt.py` | Applies the MedDRA coding map and assembles the final package |
| `QC_Report.md` | Independent double-programming QC (re-derived from scratch in R) |
| `*.docx` | Protocol, SAP, DMP, ICF, mock shells, final TFL package, QC closure memo |
| `HF-1002-CL-101_RawEDC_Rave.xlsx` | Synthetic Rave-style raw EDC workbook |
| `HF-1002-CL-101_NonCDISC_Pipeline.zip` | Packaged non-CDISC pipeline (programs 01–02 + outputs) |

## Workflow

Protocol → SAP / DMP / ICF → mock shells → simulated EDC → analysis datasets →
populated tables → independent QC (R) → coded package.

The pipeline is written in Python; the QC was written separately in R and compared
cell-by-cell against the production output (PASS with findings — see `QC_Report.md`).
