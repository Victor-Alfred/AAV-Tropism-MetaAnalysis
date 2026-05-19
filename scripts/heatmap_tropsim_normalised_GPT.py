import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from scipy.cluster.hierarchy import linkage
from scipy.spatial.distance import squareform
from sklearn.metrics.pairwise import nan_euclidean_distances

# -------------------------
# Inputs / outputs
# -------------------------
INFILE = "tropism_harmonised.xlsx"
SHEET = 0  # change if needed

OUT_PREFIX = "heatmap_systemic"
MIN_EXPERIMENTS_PER_CELL = 2   # mask serotype×tissue cells seen in fewer experiments than this

ENDPOINTS = {
    "expression_luc_ex_vivo": "luciferase_ex_vivo_RLU_per_ug_protein",
    "expression_luc_in_vivo": "luciferase_in_vivo_radiance",
    "genome_qpcr": "qPCR_vg_per_ug_DNA",
}

# -------------------------
# Helpers
# -------------------------
def clean_text(x):
    if pd.isna(x):
        return ""
    return str(x).strip()

def is_systemic_admin_route(route: str) -> bool:
    r = clean_text(route).lower()
    return ("intravenous" in r) or ("retro-orbital" in r) or ("retro orbital" in r) or ("retroorbital" in r)

def build_experiment_id(df):
    """
    Proxy experiment_id: tweak if you later see panels being merged/split incorrectly.
    """
    cols = [
        "paper_id", "figure_reference",
        "species", "strain", "sex",
        "administration_route", "injection_site",
        "dose_vg_kg", "dose_vg_total",
        "timepoint_days", "timepoint_weeks",
        "promoter", "transgene",
        "endpoint_std"
    ]
    for c in cols:
        if c not in df.columns:
            df[c] = np.nan
    df["experiment_id"] = df[cols].astype(str).agg("|".join, axis=1)
    return df

def two_way_center_within_experiment(g):
    """
    r_{s,t} = x_{s,t} - mean_s - mean_t + grand_mean
    where x is normalized_score_std (log10 of standardised raw_value).
    """
    g = g.copy()
    x = g["normalized_score_std"]
    mean_s = g.groupby("serotype")["normalized_score_std"].transform("mean")
    mean_t = g.groupby("tissue")["normalized_score_std"].transform("mean")
    grand = x.mean()
    g["tropism_pref"] = x - mean_s - mean_t + grand
    return g

def make_matrix(d, min_experiments=2):
    agg = (
        d.groupby(["serotype", "tissue"])
         .agg(
             tropism_pref_mean=("tropism_pref", "mean"),
             n_experiments=("experiment_id", "nunique"),
         )
         .reset_index()
    )

    mat = agg.pivot(index="serotype", columns="tissue", values="tropism_pref_mean")
    mat_n = agg.pivot(index="serotype", columns="tissue", values="n_experiments")

    # Mask low-evidence cells as NaN
    mat_masked = mat.where(mat_n >= min_experiments)

    # Drop rows/cols that are entirely missing (helps plotting)
    mat_masked = mat_masked.dropna(axis=0, how="all").dropna(axis=1, how="all")
    return mat_masked, mat_n

def plot_heatmap_no_clustering(mat_masked, title, outfile):
    cmap = sns.color_palette("vlag", as_cmap=True)
    cmap.set_bad(color="lightgrey")

    mask = mat_masked.isna()

    plt.figure(figsize=(1 + 0.6 * mat_masked.shape[1], 1 + 0.4 * mat_masked.shape[0]))
    sns.heatmap(
        mat_masked,
        mask=mask,
        cmap=cmap,
        center=0.0,
        linewidths=0.3,
        linecolor="lightgrey",
        cbar_kws={"label": "Tropism preference (two-way centered; mean across experiments)"}
    )
    plt.title(title)
    plt.xlabel("Tissue")
    plt.ylabel("Serotype")
    plt.tight_layout()
    plt.savefig(outfile, dpi=300)
    plt.close()

def nan_aware_linkage(mat_values_2d, axis="rows", method="average"):
    """
    Computes hierarchical linkage using NaN-aware Euclidean distances.
    - axis="rows": cluster serotypes
    - axis="cols": cluster tissues
    """
    X = mat_values_2d if axis == "rows" else mat_values_2d.T
    D = nan_euclidean_distances(X)          # square distance matrix
    Dc = squareform(D, checks=False)        # condensed form for scipy.linkage
    return linkage(Dc, method=method)

def plot_heatmap_with_clustering(mat_masked, title, outfile):
    """
    Uses NaN-aware distances for clustering so you can keep masked cells as NaN.
    """
    cmap = sns.color_palette("vlag", as_cmap=True)
    cmap.set_bad(color="lightgrey")

    # Compute linkages from NaN-aware distances
    row_link = nan_aware_linkage(mat_masked.values, axis="rows", method="average")
    col_link = nan_aware_linkage(mat_masked.values, axis="cols", method="average")

    g = sns.clustermap(
        mat_masked,
        row_linkage=row_link,
        col_linkage=col_link,
        cmap=cmap,
        center=0.0,
        linewidths=0.2,
        linecolor="lightgrey",
        figsize=(1 + 0.6 * mat_masked.shape[1], 1 + 0.4 * mat_masked.shape[0]),
        cbar_kws={"label": "Tropism preference (two-way centered; mean across experiments)"}
    )
    g.fig.suptitle(title, y=1.02)
    g.ax_heatmap.set_xlabel("Tissue")
    g.ax_heatmap.set_ylabel("Serotype")
    plt.savefig(outfile, dpi=300, bbox_inches="tight")
    plt.close()

# -------------------------
# Main
# -------------------------
df = pd.read_excel(INFILE, sheet_name=SHEET, engine="openpyxl")

# Keep extracted normalised score, compute standardised log score separately
df["normalized_score_extracted"] = df.get("normalized_score", np.nan)
df["raw_value_std"] = pd.to_numeric(df["raw_value_std"], errors="coerce")
df["normalized_score_std"] = np.log10(df["raw_value_std"])

# Systemic filter (Intravenous, Retro-orbital)
df["is_systemic"] = df["administration_route"].apply(is_systemic_admin_route)

# Build experiment_id for within-experiment centering
df = build_experiment_id(df)

for label, endpoint in ENDPOINTS.items():
    d = df.loc[
        (df["is_systemic"]) &
        (df["endpoint_std"] == endpoint) &
        (~df["normalized_score_std"].isna()) &
        (~df["serotype"].isna()) &
        (~df["tissue"].isna())
    ].copy()

    if d.empty:
        print(f"[WARN] No rows found for endpoint_std='{endpoint}' after filtering. Skipping.")
        continue

    # Within-experiment two-way centering
    d = d.groupby("experiment_id", group_keys=False).apply(two_way_center_within_experiment)

    mat_masked, _mat_n = make_matrix(d, min_experiments=MIN_EXPERIMENTS_PER_CELL)

    if mat_masked.empty:
        print(f"[WARN] Matrix empty after masking for endpoint='{endpoint}'. Skipping.")
        continue

    title_base = (
        f"Systemic (Intravenous/Retro-orbital) — {endpoint}\n"
        f"Cell masked if < {MIN_EXPERIMENTS_PER_CELL} experiments"
    )

    # No clustering
    out_png_plain = f"{OUT_PREFIX}_{label}_plain.png"
    plot_heatmap_no_clustering(mat_masked, title_base + " (no clustering)", out_png_plain)
    print(f"Wrote {out_png_plain}")

    # With hierarchical clustering
    out_png_cluster = f"{OUT_PREFIX}_{label}_clustered.png"
    plot_heatmap_with_clustering(mat_masked, title_base + " (hierarchical clustering)", out_png_cluster)
    print(f"Wrote {out_png_cluster}")