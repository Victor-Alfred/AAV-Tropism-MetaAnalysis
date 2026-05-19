import pandas as pd
import numpy as np
import re

# -------------------------
# Constants / assumptions (Mouse-only dataset)
# -------------------------
MOUSE_DIPLOID_GENOME_MASS_PG = 6.5   # pg per diploid genome (approx.)
EPS_FOR_LOG = 0.0                   # set e.g. 1e-12 if you have zeros

INPUT_XLSX = "data/metadata/tropism_extraction_template_enhanced_working.xlsx"
INPUT_SHEET = "Data"

OUT_HARMONISED_XLSX = "tropism_harmonised.xlsx"
OUT_UNIT_SCAN_XLSX = "unit_scan_report.xlsx"
OUT_CONVERSION_REPORT_XLSX = "conversion_report.xlsx"


def _clean(x):
    if pd.isna(x):
        return np.nan
    s = str(x).strip()
    s = s.replace("µ", "u").replace("μ", "u")
    s = re.sub(r"\s+", " ", s)
    return s

def canon_method(m):
    m = _clean(m)
    if pd.isna(m):
        return np.nan
    ml = m.lower().replace("-", "_").replace(" ", "_")
    if ml in {"luciferase_ex_vivo", "luciferase_exvivo"}:
        return "Luciferase_ex_vivo"
    if ml in {"luciferase_in_vivo", "luciferase_invivo"}:
        return "Luciferase_in_vivo"
    if ml in {"qpcr", "q_pcr"}:
        return "qPCR"
    return m

def canon_units(u):
    u = _clean(u)
    if pd.isna(u):
        return np.nan

    ul = u.lower()
    ul = ul.replace("per", "/").replace("sec", "s").replace("seconds", "s")
    ul = ul.replace(" ", "")
    ul = ul.replace("cm2", "cm^2")
    ul = re.sub(r"cm\^?2", "cm^2", ul)

    if ul == "rlu/ugprotein":
        return "RLU/ug protein"
    if ul == "rlu/mgprotein":
        return "RLU/mg protein"

    if "photons" in ul and "/s/" in ul and "cm^2" in ul and "/sr" in ul:
        return "photons/s/cm^2/sr"

    if ul == "vg/ugdna":
        return "vg/ug DNA"
    if ul == "vcn/dg":
        return "VCN/dg"

    return _clean(u)

def convert_row(raw_value, method_c, units_canon):
    if pd.isna(raw_value) or pd.isna(units_canon):
        return np.nan, np.nan, np.nan, "missing"

    v = float(raw_value)

    # Luciferase ex vivo lysate (convert mg -> ug)
    if method_c == "Luciferase_ex_vivo":
        if units_canon == "RLU/ug protein":
            return v, "RLU/ug protein", "luciferase_ex_vivo_RLU_per_ug_protein", "ok"
        if units_canon == "RLU/mg protein":
            return v / 1000.0, "RLU/ug protein", "luciferase_ex_vivo_RLU_per_ug_protein", "ok"
        return np.nan, np.nan, "luciferase_ex_vivo_RLU_per_ug_protein", "fail_unexpected_unit_for_method"

    # Luciferase in vivo imaging (radiance)
    if method_c == "Luciferase_in_vivo":
        if units_canon == "photons/s/cm^2/sr":
            return v, "photons/s/cm^2/sr", "luciferase_in_vivo_radiance", "ok"
        return np.nan, np.nan, "luciferase_in_vivo_radiance", "fail_unexpected_unit_for_method"

    # qPCR genome delivery (vg/ug DNA) with VCN/dg conversion
    if method_c == "qPCR":
        if units_canon == "vg/ug DNA":
            return v, "vg/ug DNA", "qPCR_vg_per_ug_DNA", "ok"
        if units_canon == "VCN/dg":
            dg_per_ug = 1e6 / MOUSE_DIPLOID_GENOME_MASS_PG
            return v * dg_per_ug, "vg/ug DNA", "qPCR_vg_per_ug_DNA", "ok_assumption_vcn_to_vg"
        return np.nan, np.nan, "qPCR_vg_per_ug_DNA", "fail_unexpected_unit_for_method"

    return np.nan, np.nan, np.nan, "fail_unknown_method"

def scan_units(df):
    tmp = df.copy()
    tmp["measurement_method_c"] = tmp["measurement_method"].map(canon_method)
    tmp["units_canon"] = tmp["units"].map(canon_units)
    return (
        tmp.groupby(["measurement_method_c", "measurement_type"])["units_canon"]
           .apply(lambda x: sorted(set([u for u in x.dropna().tolist()])))
           .reset_index(name="units_found")
    )

def harmonise_units(df):
    out = df.copy()
    out["measurement_method_c"] = out["measurement_method"].map(canon_method)
    out["units_canon"] = out["units"].map(canon_units)
    out["raw_value_num"] = pd.to_numeric(out["raw_value"], errors="coerce")

    conv = out.apply(
        lambda r: convert_row(r["raw_value_num"], r["measurement_method_c"], r["units_canon"]),
        axis=1,
        result_type="expand"
    )
    conv.columns = ["raw_value_std", "units_std", "endpoint_std", "conversion_status"]
    out = pd.concat([out, conv], axis=1)

    out["normalized_score"] = np.log10(out["raw_value_std"] + EPS_FOR_LOG)
    return out

def conversion_report(df_h):
    return (
        df_h.groupby(["measurement_method_c", "endpoint_std", "units_canon", "units_std", "conversion_status"])
            .size()
            .reset_index(name="n_rows")
            .sort_values(["conversion_status", "n_rows"], ascending=[True, False])
    )

def main():
    df = pd.read_excel(INPUT_XLSX, sheet_name=INPUT_SHEET, engine="openpyxl")

    unit_rep = scan_units(df)
    df_h = harmonise_units(df)
    conv_rep = conversion_report(df_h)

    df_h.to_excel(OUT_HARMONISED_XLSX, index=False)
    unit_rep.to_excel(OUT_UNIT_SCAN_XLSX, index=False)
    conv_rep.to_excel(OUT_CONVERSION_REPORT_XLSX, index=False)

    print("Wrote:")
    print(f"  {OUT_HARMONISED_XLSX}")
    print(f"  {OUT_UNIT_SCAN_XLSX}")
    print(f"  {OUT_CONVERSION_REPORT_XLSX}")

if __name__ == "__main__":
    main()