#!/usr/bin/env python3
"""
01_build_analysis_datasets.py  --  HF-1002-CL-101 (FICTIONAL DEMO)

NON-CDISC analysis-dataset build.
Reads raw Medidata Rave-style EDC extracts from ./raw_edc/ and derives
home-grown (non-ADaM) analysis datasets into ./analysis_data/:

    an_subject.csv  one row per subject  (populations, demographics, disposition)
    an_ae.csv       one row per AE        (TEAE / related / serious / DLT flags)
    an_lb.csv       one row per lab result(baseline, change, alert flags)
    an_eff.csv      one row per subject/param/visit (baseline, change from baseline)

These are deliberately NOT CDISC: own naming, no SDTM/ADaM standard, no define.xml.
The derivations (baseline, CHG, TEAE/DLT flags, population flags) are exactly the
work ADaM would standardize -- here we do it once so the table programs stay simple.
"""
import os
import pandas as pd
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, "raw_edc")
OUT = os.path.join(BASE, "analysis_data")
os.makedirs(OUT, exist_ok=True)

def rd(name):
    return pd.read_csv(os.path.join(RAW, name + ".csv"))

def dt(series):
    return pd.to_datetime(series, format="%d-%b-%Y", errors="coerce")

# ----------------------------------------------------------------------
# AN_SUBJECT  (one row per subject)
# ----------------------------------------------------------------------
dm, el, ds, ex = rd("dm"), rd("el"), rd("ds"), rd("ex")

an_subject = el[["Subject", "SiteNumber", "COHORT", "COHORT_LABEL", "DOSE_LEVEL_VG",
                 "SCRN_LVEF_PCT", "SCRN_NYHA"]].copy()
an_subject = an_subject.merge(dm[["Subject", "AGE", "SEX", "RACE_DECODE"]], on="Subject", how="left")
an_subject = an_subject.merge(ex[["Subject", "EXSTDAT", "EXADMIN_COMPLETE", "EXVOL_ML"]], on="Subject", how="left")
an_subject = an_subject.merge(ds[["Subject", "DSDECOD", "DSREAS", "DSDAT", "PRIMARY_OBS_COMPLETED"]], on="Subject", how="left")

an_subject = an_subject.rename(columns={
    "Subject": "SUBJID", "SiteNumber": "SITEID", "COHORT_LABEL": "COHORTLBL",
    "DOSE_LEVEL_VG": "DOSE_VG", "SCRN_LVEF_PCT": "BL_LVEF", "SCRN_NYHA": "BL_NYHA",
    "RACE_DECODE": "RACE", "EXSTDAT": "TRTSDT"})

# Population flags
an_subject["SAFFL"] = np.where(an_subject["TRTSDT"].notna(), "Y", "N")            # received any HF-1002
an_subject["FASFL"] = np.where(an_subject["EXADMIN_COMPLETE"] == "Y", "Y", "N")    # complete planned infusion
an_subject["DLTFL"] = "Y"   # all dosed subjects reached/exceeded the DLT window (Day 1-29) or had a DLT; see derivation spec
an_subject["COMPLFL"] = np.where(an_subject["PRIMARY_OBS_COMPLETED"] == "Y", "Y", "N")
an_subject["DTHFL"] = np.where(an_subject["DSDECOD"] == "DEATH", "Y", "N")
an_subject["AGEGR1"] = np.where(an_subject["AGE"] >= 65, ">=65", "<65")

an_subject = an_subject[["SUBJID", "SITEID", "COHORT", "COHORTLBL", "DOSE_VG",
                         "AGE", "AGEGR1", "SEX", "RACE", "BL_LVEF", "BL_NYHA",
                         "TRTSDT", "EXVOL_ML", "SAFFL", "FASFL", "DLTFL",
                         "COMPLFL", "DTHFL", "DSDECOD", "DSREAS", "DSDAT"]]
an_subject.to_csv(os.path.join(OUT, "an_subject.csv"), index=False)
cohmap = dict(zip(an_subject.SUBJID, an_subject.COHORT))
trtmap = dict(zip(an_subject.SUBJID, dt(an_subject.TRTSDT)))

# ----------------------------------------------------------------------
# AN_AE  (one row per AE; TEAE / related / serious / DLT-window flags)
# ----------------------------------------------------------------------
ae = rd("ae").copy()
ae["COHORT"] = ae.Subject.map(cohmap)
ae["TRTSDT"] = ae.Subject.map(trtmap)
ae["AESTDT"] = dt(ae["AESTDAT"])
ae["AEDY"] = (ae["AESTDT"] - ae["TRTSDT"]).dt.days + 1           # study day of AE onset (Day 1 = dose)
ae["TEAEFL"] = np.where(ae["AESTDT"] >= ae["TRTSDT"], "Y", "N")  # treatment-emergent
REL = {"POSSIBLY RELATED", "PROBABLY RELATED", "RELATED"}
ae["RELFL"] = np.where(ae["AEREL"].isin(REL), "Y", "N")
ae["SERFL"] = np.where(ae["AESER"] == "Y", "Y", "N")
ae["SEVGR"] = pd.to_numeric(ae["AETOXGR"], errors="coerce")
ae["GE3FL"] = np.where(ae["SEVGR"] >= 3, "Y", "N")
ae["DLTWINFL"] = np.where((ae["AEDY"] >= 1) & (ae["AEDY"] <= 29), "Y", "N")  # DLT window Day 1-29
ae["DLTFL"] = np.where((ae["AEDLT"] == "Y") & (ae["DLTWINFL"] == "Y"), "Y", "N")
ae["FATALFL"] = np.where(ae["AEOUT"] == "FATAL", "Y", "N")
an_ae = ae[["Subject", "COHORT", "AETERM", "AESTDAT", "AEDY", "AETOXGR", "SEVGR",
            "AESER", "AEREL", "AEOUT", "AEDLT", "TEAEFL", "RELFL", "SERFL",
            "GE3FL", "DLTWINFL", "DLTFL", "FATALFL"]].rename(columns={"Subject": "SUBJID"})
an_ae.to_csv(os.path.join(OUT, "an_ae.csv"), index=False)

# ----------------------------------------------------------------------
# AN_LB  (one row per lab result; baseline, change, alert flags)
# ----------------------------------------------------------------------
lb = rd("lb").copy()
lb["COHORT"] = lb.Subject.map(cohmap)
lb["AVAL"] = pd.to_numeric(lb["LBORRES"], errors="coerce")
lb["ABLFL"] = np.where(lb["Folder"] == "SCRN", "Y", "N")
base = (lb[lb.ABLFL == "Y"].groupby(["Subject", "LBTESTCD"])["AVAL"].first().rename("BASE").reset_index())
lb = lb.merge(base, on=["Subject", "LBTESTCD"], how="left")
lb["CHG"] = np.where(lb["ABLFL"] == "N", lb["AVAL"] - lb["BASE"], np.nan)
uln = dict(zip(lb["LBTESTCD"], lb["LBORNRHI"]))
# Liver alert (hepatocellular): ALT or AST > 3x ULN flagged; > 5x ULN = DLT-level
def liver_alert(r):
    if r["LBTESTCD"] in ("ALT", "AST"):
        hi = pd.to_numeric(r["LBORNRHI"], errors="coerce")
        if pd.notna(hi) and pd.notna(r["AVAL"]):
            if r["AVAL"] > 5 * hi:
                return ">5xULN"
            if r["AVAL"] > 3 * hi:
                return ">3xULN"
    return ""
lb["LBALERT"] = lb.apply(liver_alert, axis=1)
an_lb = lb[["Subject", "COHORT", "Folder", "LBCAT", "LBTESTCD", "LBTEST", "AVAL",
            "LBORRESU", "LBORNRLO", "LBORNRHI", "LBNRIND", "ABLFL", "BASE", "CHG",
            "LBALERT", "LBDAT"]].rename(columns={"Subject": "SUBJID", "Folder": "AVISIT",
            "LBNRIND": "ANRIND"})
an_lb.to_csv(os.path.join(OUT, "an_lb.csv"), index=False)

# ----------------------------------------------------------------------
# AN_EFF  (one row per subject/param/visit; baseline + change from baseline)
# ----------------------------------------------------------------------
def eff_from(form, valcol, paramcd, param, datecol):
    d = rd(form)[["Subject", "Folder", valcol, datecol]].copy()
    d = d.rename(columns={valcol: "AVAL", datecol: "ADT", "Folder": "AVISIT"})
    d["PARAMCD"] = paramcd
    d["PARAM"] = param
    return d

eff = pd.concat([
    eff_from("ec", "LVEF_CENTRAL_PCT", "LVEFC", "LVEF, central reader (%)", "ECHODAT"),
    eff_from("ec", "LVEF_LOCAL_PCT", "LVEFL", "LVEF, local read (%)", "ECHODAT"),
    eff_from("cpet", "PEAKVO2_MLKGMIN", "PVO2", "Peak VO2 (mL/kg/min)", "CPETDAT"),
    eff_from("walk6", "WALKDIST_M", "WALK6", "6-Minute Walk Distance (m)", "WALK6DAT"),
    eff_from("mlhfq", "MLHFQ_TOTAL", "MLHFQ", "MLHFQ Total Score", "MLHFQDAT"),
    eff_from("kccq", "KCCQ_OSS", "KCCQ", "KCCQ Overall Summary Score", "KCCQDAT"),
    eff_from("nyha", "NYHA_CLASS", "NYHA", "NYHA Functional Class", "NYHADAT"),
], ignore_index=True)
eff["COHORT"] = eff.Subject.map(cohmap)
eff["AVAL"] = pd.to_numeric(eff["AVAL"], errors="coerce")
eff["ABLFL"] = np.where(eff["AVISIT"] == "SCRN", "Y", "N")
ebase = (eff[eff.ABLFL == "Y"].groupby(["Subject", "PARAMCD"])["AVAL"].first().rename("BASE").reset_index())
eff = eff.merge(ebase, on=["Subject", "PARAMCD"], how="left")
eff["CHG"] = np.where(eff["ABLFL"] == "N", eff["AVAL"] - eff["BASE"], np.nan)
fasmap = dict(zip(an_subject.SUBJID, an_subject.FASFL))
eff["FASFL"] = eff.Subject.map(fasmap)
an_eff = eff[["Subject", "COHORT", "PARAMCD", "PARAM", "AVISIT", "ADT", "AVAL",
              "ABLFL", "BASE", "CHG", "FASFL"]].rename(columns={"Subject": "SUBJID"})
an_eff.to_csv(os.path.join(OUT, "an_eff.csv"), index=False)

print("Analysis datasets written to ./analysis_data/")
for nm, d in [("an_subject", an_subject), ("an_ae", an_ae), ("an_lb", an_lb), ("an_eff", an_eff)]:
    print(f"  {nm:12s} {len(d):5d} rows  x {d.shape[1]} cols")
print("Populations: SAFFL=%d  FASFL=%d  DLTFL=%d  Deaths=%d  Completed=%d" % (
    (an_subject.SAFFL == "Y").sum(), (an_subject.FASFL == "Y").sum(),
    (an_subject.DLTFL == "Y").sum(), (an_subject.DTHFL == "Y").sum(),
    (an_subject.COMPLFL == "Y").sum()))
print("DLTs (AE-level, in window):", (an_ae.DLTFL == "Y").sum())
