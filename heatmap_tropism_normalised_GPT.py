import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

INFILE = "tropism_harmonised.xlsx"
SHEET = 0  # change if needed

ENDPOINTS = {
    "expression_luc_ex_vivo": "luciferase_ex_vivo_RLU_per_ug_protein",
    "expression_luc_in_vivo": "luciferase_in_vivo_radiance",
    "genome_qpcr": "qPCR_vg_per_ug_DNA",
}

ROUTES_KEEP = {"Intravenous", "Retro-orbital"}

# show/hide sparse cells
MIN_PAPERS_BUBBLE = 1
MIN_PAPERS_HEATMAP = 1   # set to 2+ to reduce missingness

OUT_PREFIX = "tropism_by_route_no_experimentid"

sns.set_theme(context="paper", style="white", font_scale=0.75)

def route_std(route):
    r = "" if pd.isna(route) else str(route).strip()
    rl = r.lower()
    if "retro" in rl:
        return "Retro-orbital"
    if "intravenous" in rl or rl in {"iv", "i.v.", "i.v"}:
        return "Intravenous"
    return r if r else "Unknown"

def safe_log10(x: pd.Series) -> pd.Series:
    s = pd.to_numeric(x, errors="coerce")
    pos = s[s > 0]
    if pos.empty:
        return pd.Series(np.nan, index=s.index)
    eps = 0.5 * pos.min()   # avoids log10(0) -> -inf
    return np.log10(s + eps)

def aggregate_by_paper(df_sub):
    """
    2-stage aggregation to avoid overweighting papers:
      (1) within each paper: mean over rows for same (route, endpoint, serotype, tissue)
      (2) across papers: median of paper means + n_papers evidence
    """
    step1 = (
        df_sub.groupby(["paper_id", "administration_route_std", "endpoint_std", "serotype", "tissue"], dropna=False)
              .agg(value_paper_mean=("log_value", "mean"))
              .reset_index()
    )

    step2 = (
        step1.groupby(["administration_route_std", "endpoint_std", "serotype", "tissue"], dropna=False)
             .agg(
                 value_median=("value_paper_mean", "median"),
                 value_mean=("value_paper_mean", "mean"),
                 n_papers=("paper_id", "nunique")
             )
             .reset_index()
    )
    return step2

def bubble_plot(agg, endpoint_label, outfile):
    plot_df = agg.loc[agg["n_papers"] >= MIN_PAPERS_BUBBLE].copy()
    if plot_df.empty:
        print(f"[WARN] No data for {endpoint_label}")
        return

    # order by evidence (no clustering)
    tissue_order = plot_df.groupby("tissue")["n_papers"].sum().sort_values(ascending=False).index.tolist()
    serotype_order = plot_df.groupby("serotype")["n_papers"].sum().sort_values(ascending=False).index.tolist()
    plot_df["tissue"] = pd.Categorical(plot_df["tissue"], categories=tissue_order, ordered=True)
    plot_df["serotype"] = pd.Categorical(plot_df["serotype"], categories=serotype_order, ordered=True)

    # diverging scale centered at 0
    absmax = np.nanmax(np.abs(plot_df["value_median"].values))
    absmax = absmax if np.isfinite(absmax) and absmax > 0 else 1.0
    norm = TwoSlopeNorm(vmin=-absmax, vcenter=0.0, vmax=absmax)

    g = sns.relplot(
        data=plot_df,
        x="tissue", y="serotype",
        col="administration_route_std",
        col_order=[r for r in ["Intravenous", "Retro-orbital"] if r in plot_df["administration_route_std"].unique()],
        kind="scatter",
        hue="value_median",
        hue_norm=norm,
        palette="vlag",
        size="n_papers",
        sizes=(25, 260),
        height=6, aspect=1.35
    )
    g.set_titles("{col_name}")
    g.set_axis_labels("Tissue", "Serotype")
    for ax in g.axes.flatten():
        ax.tick_params(axis="x", labelrotation=60, labelsize=7)
        ax.tick_params(axis="y", labelsize=7)

    g.fig.suptitle(
        f"{endpoint_label} — log10(standardised units)\nColor = median across papers; size = # papers",
        y=1.02
    )
    plt.tight_layout()
    plt.savefig(outfile, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Wrote {outfile}")

def heatmap_per_route(agg, endpoint_label, outfile_prefix):
    routes = [r for r in ["Intravenous", "Retro-orbital"] if r in agg["administration_route_std"].unique()]
    for r in routes:
        sub = agg.loc[(agg["administration_route_std"] == r) & (agg["n_papers"] >= MIN_PAPERS_HEATMAP)].copy()
        if sub.empty:
            continue

        mat = sub.pivot(index="serotype", columns="tissue", values="value_median")
        mat = mat.dropna(axis=0, how="all").dropna(axis=1, how="all")
        if mat.empty:
            continue

        absmax = np.nanmax(np.abs(mat.values))
        absmax = absmax if np.isfinite(absmax) and absmax > 0 else 1.0

        cmap = sns.color_palette("vlag", as_cmap=True)
        cmap.set_bad("white")

        fig_w = max(10, 0.45 * mat.shape[1])
        fig_h = max(6, 0.28 * mat.shape[0])

        plt.figure(figsize=(fig_w, fig_h))
        sns.heatmap(
            mat,
            cmap=cmap,
            vmin=-absmax, vmax=absmax, center=0.0,
            linewidths=0.2, linecolor="lightgrey",
            cbar_kws={"label": "Median log10(standardised units) across papers"}
        )
        plt.title(f"{endpoint_label} — {r} (cells shown if ≥ {MIN_PAPERS_HEATMAP} papers)")
        plt.xlabel("Tissue")
        plt.ylabel("Serotype")
        plt.xticks(rotation=60, ha="right", fontsize=7)
        plt.yticks(fontsize=7)
        plt.tight_layout()

        out = f"{outfile_prefix}_{endpoint_label}_{r}.png".replace(" ", "_")
        plt.savefig(out, dpi=300)
        plt.close()
        print(f"Wrote {out}")

# ---- run ----
df = pd.read_excel(INFILE, sheet_name=SHEET, engine="openpyxl")
df["administration_route_std"] = df["administration_route"].apply(route_std)
df = df[df["administration_route_std"].isin(ROUTES_KEEP)].copy()

df["raw_value_std"] = pd.to_numeric(df["raw_value_std"], errors="coerce")
df["log_value"] = safe_log10(df["raw_value_std"])

df = df.loc[
    (df["endpoint_std"].notna()) &
    (df["serotype"].notna()) &
    (df["tissue"].notna()) &
    (~df["log_value"].isna())
].copy()

for label, endpoint in ENDPOINTS.items():
    sub = df[df["endpoint_std"] == endpoint].copy()
    if sub.empty:
        print(f"[WARN] No rows for endpoint '{endpoint}'")
        continue

    agg = aggregate_by_paper(sub)

    bubble_plot(
        agg,
        endpoint_label=label,
        outfile=f"{OUT_PREFIX}_{label}_BUBBLE.png"
    )

    heatmap_per_route(
        agg,
        endpoint_label=label,
        outfile_prefix=f"{OUT_PREFIX}_{label}_HEATMAP"
    )