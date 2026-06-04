import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter
from pathlib import Path
from scipy.stats import fisher_exact, false_discovery_control, ttest_ind


def clean_marketing_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the marketing campaign dataset and create analysis-ready metrics.

    The source file is already at a campaign-row level, so no extra
    aggregation is needed unless a later analysis asks for it.
    """
    df = df.copy()

    # Standardize column names first so downstream logic is predictable.
    df.columns = df.columns.str.strip()

    # Remove duplicate rows and duplicate campaign IDs if present.
    df = df.drop_duplicates()
    if "Campaign_ID" in df.columns:
        df = df.drop_duplicates(subset=["Campaign_ID"], keep="first")

    # Fix data types.
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    if "Duration" in df.columns:
        df["Duration"] = (
            df["Duration"]
            .astype(str)
            .str.extract(r"(\d+)", expand=False)
        )
        df["Duration"] = pd.to_numeric(df["Duration"], errors="coerce").astype("Int64")

    if "Acquisition_Cost" in df.columns:
        df["Acquisition_Cost"] = (
            df["Acquisition_Cost"]
            .astype(str)
            .str.replace(r"[\$,]", "", regex=True)
        )
        df["Acquisition_Cost"] = pd.to_numeric(df["Acquisition_Cost"], errors="coerce")

    numeric_cols = [
        "Conversion_Rate",
        "ROI",
        "Clicks",
        "Impressions",
        "Engagement_Score",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Some datasets store conversion rate as 0-100 instead of 0-1.
    if "Conversion_Rate" in df.columns:
        max_rate = df["Conversion_Rate"].dropna().max()
        if pd.notna(max_rate) and max_rate > 1:
            df["Conversion_Rate"] = df["Conversion_Rate"] / 100.0

    # Remove obvious errors / impossible values.
    for col in ["Acquisition_Cost", "Conversion_Rate", "ROI", "Clicks", "Impressions", "Engagement_Score"]:
        if col in df.columns:
            df.loc[df[col] < 0, col] = np.nan

    if "Engagement_Score" in df.columns:
        df.loc[~df["Engagement_Score"].between(1, 10), "Engagement_Score"] = np.nan

    if "Clicks" in df.columns and "Impressions" in df.columns:
        df.loc[df["Clicks"] > df["Impressions"], ["Clicks", "Impressions"]] = np.nan

    # Drop rows missing key fields after cleaning.
    key_columns = [
        c
        for c in [
            "Date",
            "Campaign_ID",
            "Company",
            "Campaign_Type",
            "Target_Audience",
            "Channel_Used",
            "Conversion_Rate",
            "Acquisition_Cost",
            "ROI",
            "Location",
            "Language",
            "Clicks",
            "Impressions",
            "Engagement_Score",
            "Customer_Segment",
            "Duration",
        ]
        if c in df.columns
    ]
    df = df.dropna(subset=key_columns)

    # Create missing metrics for analysis.
    if "Clicks" in df.columns and "Impressions" in df.columns:
        df["CTR"] = np.where(df["Impressions"] > 0, df["Clicks"] / df["Impressions"], np.nan)
    else:
        df["CTR"] = np.nan

    if "Clicks" in df.columns and "Conversion_Rate" in df.columns:
        df["Estimated_Conversions"] = df["Clicks"] * df["Conversion_Rate"]
    else:
        df["Estimated_Conversions"] = np.nan

    if "Acquisition_Cost" in df.columns:
        df["CPA"] = np.where(
            df["Estimated_Conversions"] > 0,
            df["Acquisition_Cost"] / df["Estimated_Conversions"],
            np.nan,
        )
    else:
        df["CPA"] = np.nan

    return df


def build_preparation_report(raw_data: pd.DataFrame, cleaned_data: pd.DataFrame) -> str:
    """Create a markdown summary of the cleaning steps and basic statistics."""
    categorical_cols = [
        "Company",
        "Campaign_Type",
        "Target_Audience",
        "Channel_Used",
        "Location",
        "Language",
        "Customer_Segment",
    ]
    numeric_cols = [
        "Campaign_ID",
        "Duration",
        "Conversion_Rate",
        "Acquisition_Cost",
        "ROI",
        "Clicks",
        "Impressions",
        "Engagement_Score",
        "CTR",
        "Estimated_Conversions",
        "CPA",
    ]
    discrete_numeric_cols = {"Campaign_ID", "Duration", "Clicks", "Impressions", "Engagement_Score"}

    def format_range(series: pd.Series, is_discrete: bool) -> str:
        if is_discrete:
            return f"{int(series.min()):,} to {int(series.max()):,}"
        return f"{series.min():,.4f} to {series.max():,.4f}"

    lines = []
    lines.append("# Data Preparation Report")
    lines.append("")
    lines.append("## Transformations Applied")
    lines.append("- Standardized column names by stripping leading and trailing spaces.")
    lines.append("- Removed duplicate rows and duplicate `Campaign_ID` values.")
    lines.append("- Converted `Date` to datetime and kept the original row order.")
    lines.append("- Extracted numeric values from `Duration` and stored them as days.")
    lines.append("- Cleaned `Acquisition_Cost` by removing currency symbols and commas.")
    lines.append("- Coerced numeric fields to numeric types: `Conversion_Rate`, `ROI`, `Clicks`, `Impressions`, and `Engagement_Score`.")
    lines.append("- Removed negative values, invalid engagement scores, invalid dates, and rows where `Clicks > Impressions`.")
    lines.append("- Created derived metrics: `CTR`, `Estimated_Conversions`, and `CPA`.")
    lines.append("")
    lines.append("## Row Counts")
    lines.append(f"- Raw rows: {len(raw_data):,}")
    lines.append(f"- Cleaned rows: {len(cleaned_data):,}")
    lines.append("")
    lines.append("## Column Summary Statistics")

    for col in categorical_cols:
        if col in cleaned_data.columns:
            counts = cleaned_data[col].value_counts(dropna=False)
            lines.append(f"### {col}")
            lines.append(f"- Number of groups: {counts.shape[0]:,}")
            lines.append("")
            lines.append("| Group | Sample Size |")
            lines.append("| --- | ---: |")
            for group, count in counts.items():
                lines.append(f"| {group} | {count:,} |")
            lines.append("")

    if "Date" in cleaned_data.columns:
        date_min = cleaned_data["Date"].min()
        date_max = cleaned_data["Date"].max()
        lines.append("### Date")
        lines.append(f"- Number of groups: {cleaned_data['Date'].nunique():,} unique days")
        lines.append(f"- Data range: {date_min:%Y-%m-%d} to {date_max:%Y-%m-%d}")
        lines.append("")

    for col in numeric_cols:
        if col in cleaned_data.columns:
            series = cleaned_data[col].dropna()
            lines.append(f"### {col}")
            if pd.api.types.is_integer_dtype(series) or pd.api.types.is_float_dtype(series):
                if col in discrete_numeric_cols:
                    lines.append("- Number of groups: discrete numeric values")
                else:
                    lines.append("- Number of groups: continuous numeric values")
                lines.append(f"- Data range: {format_range(series, col in discrete_numeric_cols)}")
            else:
                lines.append("- Data range: N/A")
            lines.append("")

    return "\n".join(lines)


def calculate_group_metrics(cleaned_data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Calculate channel-level summary metrics and daily channel metrics.

    Revenue is estimated as Acquisition_Cost * ROI because the source dataset
    does not contain a separate revenue column.
    """
    df = cleaned_data.copy()

    if "ROI" in df.columns and "Acquisition_Cost" in df.columns:
        df["Revenue"] = df["Acquisition_Cost"] * df["ROI"]
    else:
        df["Revenue"] = np.nan

    if "Estimated_Conversions" not in df.columns and {"Clicks", "Conversion_Rate"}.issubset(df.columns):
        df["Estimated_Conversions"] = df["Clicks"] * df["Conversion_Rate"]

    channel_summary = (
        df.groupby("Channel_Used", as_index=False)
        .agg(
            Impressions=("Impressions", "sum"),
            Clicks=("Clicks", "sum"),
            Conversions=("Estimated_Conversions", "sum"),
            Cost=("Acquisition_Cost", "sum"),
            Revenue=("Revenue", "sum"),
        )
    )

    channel_summary["CTR"] = np.where(channel_summary["Impressions"] > 0, channel_summary["Clicks"] / channel_summary["Impressions"], np.nan)
    channel_summary["Conversion_Rate"] = np.where(channel_summary["Clicks"] > 0, channel_summary["Conversions"] / channel_summary["Clicks"], np.nan)
    channel_summary["CPA"] = np.where(channel_summary["Conversions"] > 0, channel_summary["Cost"] / channel_summary["Conversions"], np.nan)
    channel_summary["ROAS"] = np.where(channel_summary["Cost"] > 0, channel_summary["Revenue"] / channel_summary["Cost"], np.nan)
    channel_summary["Profit"] = channel_summary["Revenue"] - channel_summary["Cost"]
    channel_summary["Profit_Margin"] = np.where(channel_summary["Revenue"] > 0, channel_summary["Profit"] / channel_summary["Revenue"], np.nan)
    channel_summary = channel_summary.replace([np.inf, -np.inf], np.nan)

    daily_summary = pd.DataFrame()
    if "Date" in df.columns:
        daily_summary = (
            df.groupby(["Date", "Channel_Used"], as_index=False)
            .agg(
                Impressions=("Impressions", "sum"),
                Clicks=("Clicks", "sum"),
                Conversions=("Estimated_Conversions", "sum"),
                Cost=("Acquisition_Cost", "sum"),
                Revenue=("Revenue", "sum"),
            )
        )
        daily_summary["CTR"] = np.where(daily_summary["Impressions"] > 0, daily_summary["Clicks"] / daily_summary["Impressions"], np.nan)
        daily_summary["Conversion_Rate"] = np.where(daily_summary["Clicks"] > 0, daily_summary["Conversions"] / daily_summary["Clicks"], np.nan)
        daily_summary["CPA"] = np.where(daily_summary["Conversions"] > 0, daily_summary["Cost"] / daily_summary["Conversions"], np.nan)
        daily_summary["ROAS"] = np.where(daily_summary["Cost"] > 0, daily_summary["Revenue"] / daily_summary["Cost"], np.nan)
        daily_summary["Profit"] = daily_summary["Revenue"] - daily_summary["Cost"]
        daily_summary["Profit_Margin"] = np.where(daily_summary["Revenue"] > 0, daily_summary["Profit"] / daily_summary["Revenue"], np.nan)
        daily_summary = daily_summary.replace([np.inf, -np.inf], np.nan)

    return channel_summary, daily_summary


def save_group_metrics_overview(channel_summary: pd.DataFrame, output_path: Path) -> None:
    """Save a horizontal bar overview of the key channel metrics."""
    metrics = [
        ("CPA", "CPA by Channel"),
        ("ROAS", "ROAS by Channel"),
        ("Conversion_Rate", "Conversion Rate by Channel"),
        ("Conversions", "Total Conversions by Channel"),
        ("Cost", "Total Cost by Channel"),
        ("Profit", "Profit by Channel"),
    ]
    available_metrics = [(col, title) for col, title in metrics if col in channel_summary.columns]
    if not available_metrics:
        return

    sns.set_theme(style="whitegrid")
    n_metrics = len(available_metrics)
    n_cols = 2
    n_rows = int(np.ceil(n_metrics / n_cols))
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 5 * n_rows), constrained_layout=True)
    axes = np.atleast_1d(axes).ravel()

    for ax, (metric, title) in zip(axes, available_metrics):
        plot_df = channel_summary[["Channel_Used", metric]].dropna().sort_values(metric, ascending=True)
        ax.barh(plot_df["Channel_Used"], plot_df[metric], color="#2E86AB")
        ax.set_title(title)
        ax.set_xlabel(metric.replace("_", " "))
        ax.set_ylabel("")
        ax.grid(axis="x", alpha=0.25)
        if metric == "Profit":
            ax.axvline(0, color="black", linewidth=1)

    for ax in axes[len(available_metrics):]:
        ax.axis("off")

    fig.suptitle("Channel Performance Overview", fontsize=16, fontweight="bold")
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def save_group_distributions(daily_summary: pd.DataFrame, output_path: Path) -> None:
    """Save histograms and box plots showing daily metric variability by channel."""
    if daily_summary.empty:
        return

    sns.set_theme(style="whitegrid")
    metrics = [
        ("CTR", "CTR"),
        ("CPA", "CPA"),
        ("ROAS", "ROAS"),
    ]
    metrics = [(col, title) for col, title in metrics if col in daily_summary.columns]
    if not metrics:
        return

    channels = daily_summary["Channel_Used"].dropna().unique().tolist()
    palette = sns.color_palette("tab10", n_colors=len(channels))
    color_map = dict(zip(channels, palette))

    fig, axes = plt.subplots(2, len(metrics), figsize=(6 * len(metrics), 10), constrained_layout=True)
    if len(metrics) == 1:
        axes = np.array([[axes[0]], [axes[1]]])

    for idx, (metric, title) in enumerate(metrics):
        ax_hist = axes[0, idx]
        ax_box = axes[1, idx]

        for channel in channels:
            series = daily_summary.loc[daily_summary["Channel_Used"] == channel, metric].dropna()
            if series.empty:
                continue
            ax_hist.hist(
                series,
                bins=30,
                alpha=0.35,
                label=channel,
                color=color_map[channel],
                edgecolor="white",
            )

        ax_hist.set_title(f"Daily {title} Distribution")
        ax_hist.set_xlabel(title)
        ax_hist.set_ylabel("Frequency")
        ax_hist.legend(title="Channel", fontsize=8)

        box_data = [daily_summary.loc[daily_summary["Channel_Used"] == channel, metric].dropna() for channel in channels]
        ax_box.boxplot(box_data, labels=channels, patch_artist=True)
        for patch, channel in zip(ax_box.artists, channels):
            patch.set_facecolor(color_map[channel])
        ax_box.set_title(f"Daily {title} by Channel")
        ax_box.set_xlabel("Channel")
        ax_box.set_ylabel(title)
        ax_box.tick_params(axis="x", rotation=30)

    fig.suptitle("Daily Metric Distributions by Channel", fontsize=16, fontweight="bold")
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def format_group_summary(channel_summary: pd.DataFrame) -> pd.DataFrame:
    """Return a rounded summary table for display."""
    display_cols = [
        "Channel_Used",
        "Impressions",
        "Clicks",
        "Conversions",
        "Cost",
        "Revenue",
        "CTR",
        "Conversion_Rate",
        "CPA",
        "ROAS",
        "Profit",
        "Profit_Margin",
    ]
    existing_cols = [col for col in display_cols if col in channel_summary.columns]
    summary = channel_summary[existing_cols].copy()
    numeric_cols = summary.select_dtypes(include=[np.number]).columns
    summary[numeric_cols] = summary[numeric_cols].round(2)
    return summary.sort_values("Channel_Used").reset_index(drop=True)


def dataframe_to_markdown(df: pd.DataFrame, float_precision: int = 4) -> str:
    """Render a DataFrame as a markdown table without extra dependencies."""
    if df.empty:
        return "No data available."

    def format_value(value):
        if pd.isna(value):
            return ""
        if isinstance(value, (np.floating, float)):
            return f"{value:.{float_precision}f}"
        if isinstance(value, (np.integer, int)):
            return f"{int(value)}"
        if isinstance(value, (bool, np.bool_)):
            return "True" if value else "False"
        return str(value)

    columns = list(df.columns)
    lines = []
    lines.append("| " + " | ".join(columns) + " |")
    lines.append("| " + " | ".join(["---"] * len(columns)) + " |")
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(format_value(row[col]) for col in columns) + " |")
    return "\n".join(lines)


def interpret_effect_size(cohens_d: float) -> str:
    """Map Cohen's d to a simple effect-size label."""
    if pd.isna(cohens_d):
        return "undefined"
    abs_d = abs(cohens_d)
    if abs_d < 0.2:
        return "negligible"
    if abs_d < 0.5:
        return "small"
    if abs_d < 0.8:
        return "medium"
    return "large"


def compare_groups_with_ttests(
    comparison_data: pd.DataFrame,
    group_col: str,
    metric_cols: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    """
    Compare groups for each metric using pairwise independent t-tests.

    The comparisons are based on daily channel metrics so each group has a
    repeated sample over time rather than a single aggregated value.
    """
    results: list[dict] = []
    primary_metric = metric_cols[0] if metric_cols else ""

    groups = sorted(comparison_data[group_col].dropna().unique().tolist())
    for metric in metric_cols:
        if metric not in comparison_data.columns:
            continue
        metric_data = comparison_data[[group_col, metric]].replace([np.inf, -np.inf], np.nan).dropna()
        metric_groups = {group: metric_data.loc[metric_data[group_col] == group, metric].astype(float) for group in groups}

        for i, group_a in enumerate(groups):
            values_a = metric_groups.get(group_a, pd.Series(dtype=float)).dropna()
            if len(values_a) < 2:
                continue
            for group_b in groups[i + 1 :]:
                values_b = metric_groups.get(group_b, pd.Series(dtype=float)).dropna()
                if len(values_b) < 2:
                    continue

                t_stat, p_value = ttest_ind(values_a, values_b, equal_var=False, nan_policy="omit")
                mean_a = values_a.mean()
                mean_b = values_b.mean()
                difference = mean_b - mean_a
                percentage_difference = (difference / mean_a * 100) if pd.notna(mean_a) and mean_a != 0 else np.nan
                var_a = values_a.var(ddof=1)
                var_b = values_b.var(ddof=1)
                pooled_std = np.sqrt((var_a + var_b) / 2) if pd.notna(var_a) and pd.notna(var_b) else np.nan
                cohens_d = difference / pooled_std if pooled_std and pd.notna(pooled_std) and pooled_std != 0 else np.nan
                significant = bool(pd.notna(p_value) and p_value < 0.05)

                results.append(
                    {
                        "Metric": metric,
                        "Group_A": group_a,
                        "Group_B": group_b,
                        "Mean_A": mean_a,
                        "Mean_B": mean_b,
                        "Difference_B_minus_A": difference,
                        "Percent_Difference": percentage_difference,
                        "t_statistic": t_stat,
                        "p_value": p_value,
                        "Cohens_d": cohens_d,
                        "Effect_Size": interpret_effect_size(cohens_d),
                        "Significant": significant,
                        "N_A": len(values_a),
                        "N_B": len(values_b),
                    }
                )

    results_df = pd.DataFrame(results)
    primary_df = results_df[results_df["Metric"] == primary_metric].copy() if not results_df.empty else pd.DataFrame()
    return results_df, primary_df, primary_metric


def apply_multiple_comparisons_correction(
    comparison_results: pd.DataFrame,
    alpha: float = 0.05,
    metrics: tuple[str, ...] = ("CPA", "Conversion_Rate"),
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Apply Bonferroni and Benjamini-Hochberg corrections to selected metrics.

    The correction is applied separately to each metric family.
    """
    corrected = comparison_results.copy()
    if corrected.empty:
        return corrected, pd.DataFrame()

    corrected["significant_bonferroni"] = pd.NA
    corrected["bonferroni_alpha"] = pd.NA
    corrected["p_value_fdr"] = pd.NA
    corrected["significant_fdr"] = pd.NA

    summary_rows: list[dict] = []
    for metric in metrics:
        metric_mask = corrected["Metric"] == metric
        metric_df = corrected.loc[metric_mask].copy()
        if metric_df.empty:
            continue

        p_values = metric_df["p_value"].to_numpy(dtype=float)
        total_comparisons = len(metric_df)
        expected_false_positives = total_comparisons * alpha
        bonferroni_alpha = alpha / total_comparisons if total_comparisons else np.nan
        bonferroni_sig = metric_df["p_value"] < bonferroni_alpha
        fdr_adjusted = false_discovery_control(p_values, method="bh")
        fdr_sig = fdr_adjusted < alpha

        corrected.loc[metric_mask, "significant_bonferroni"] = bonferroni_sig.values
        corrected.loc[metric_mask, "bonferroni_alpha"] = bonferroni_alpha
        corrected.loc[metric_mask, "p_value_fdr"] = fdr_adjusted
        corrected.loc[metric_mask, "significant_fdr"] = fdr_sig

        summary_rows.append(
            {
                "Metric": metric,
                "Total_Comparisons": total_comparisons,
                "Expected_False_Positives": expected_false_positives,
                "Uncorrected_Significant": int(metric_df["Significant"].sum()),
                "Bonferroni_Alpha": bonferroni_alpha,
                "Bonferroni_Significant": int(bonferroni_sig.sum()),
                "FDR_Significant": int(fdr_sig.sum()),
            }
        )

    summary_df = pd.DataFrame(summary_rows)
    return corrected, summary_df


def build_pvalue_matrix(comparison_df: pd.DataFrame, primary_metric: str, groups: list[str]) -> pd.DataFrame:
    """Build a symmetric matrix of p-values for the selected primary metric."""
    matrix = pd.DataFrame(np.ones((len(groups), len(groups))), index=groups, columns=groups)
    if comparison_df.empty:
        return matrix

    metric_df = comparison_df[comparison_df["Metric"] == primary_metric]
    for _, row in metric_df.iterrows():
        a = row["Group_A"]
        b = row["Group_B"]
        p_value = row["p_value"]
        matrix.loc[a, b] = p_value
        matrix.loc[b, a] = p_value
    np.fill_diagonal(matrix.values, 1.0)
    return matrix


def save_correction_comparison_plot(correction_summary: pd.DataFrame, output_path: Path) -> None:
    """Save a bar chart comparing uncorrected, Bonferroni, and FDR results."""
    if correction_summary.empty:
        return

    sns.set_theme(style="whitegrid")
    display_names = {"CPA": "CPA", "Conversion_Rate": "Conversion Rate"}
    method_cols = [
        ("Uncorrected_Significant", "Uncorrected"),
        ("Bonferroni_Significant", "Bonferroni"),
        ("FDR_Significant", "FDR (BH)"),
    ]
    metric_order = ["CPA", "Conversion_Rate"]
    plot_df = correction_summary.copy()
    plot_df["Metric_Display"] = plot_df["Metric"].map(display_names).fillna(plot_df["Metric"])
    plot_df["Metric"] = pd.Categorical(plot_df["Metric"], categories=metric_order, ordered=True)

    counts_matrix = plot_df.set_index("Metric")[ [col for col, _ in method_cols] ].fillna(0).astype(float)
    max_count = float(np.nanmax(counts_matrix.to_numpy())) if not counts_matrix.empty else 0.0
    display_height = 0.5 if max_count == 0 else max(0.1, max_count * 0.03)

    fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)
    x_positions = np.arange(len(plot_df))
    width = 0.22
    colors = ["#5B8FF9", "#F6BD16", "#61DDAA"]

    for idx, ((col, label), color) in enumerate(zip(method_cols, colors)):
        heights = plot_df[col].fillna(0).astype(float).to_numpy()
        visible_heights = np.where(heights > 0, heights, display_height)
        bars = ax.bar(x_positions + (idx - 1) * width, visible_heights, width=width, label=label, color=color)
        for bar, actual_height in zip(bars, heights):
            label_y = actual_height if actual_height > 0 else display_height
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                label_y + display_height * 0.15,
                f"{int(actual_height)}",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    ax.set_xticks(x_positions)
    ax.set_xticklabels(plot_df["Metric_Display"].tolist())
    ax.set_title("Effect of Multiple Comparisons Correction")
    ax.set_xlabel("Metric")
    ax.set_ylabel("Significant Comparisons")
    ax.set_ylim(0, max(display_height * 2.5, max_count * 1.25 + display_height))
    ax.legend(title="Method")
    ax.grid(axis="y", alpha=0.25)

    if max_count == 0:
        ax.text(
            0.5,
            0.92,
            "No comparisons remained significant after correction.",
            transform=ax.transAxes,
            ha="center",
            va="top",
            fontsize=11,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor="#999999"),
        )

    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def save_pvalue_heatmap(pvalue_matrix: pd.DataFrame, metric_name: str, output_path: Path) -> None:
    """Save a heatmap of pairwise p-values for the primary metric."""
    sns.set_theme(style="white")
    fig, ax = plt.subplots(figsize=(8, 6), constrained_layout=True)
    sns.heatmap(
        pvalue_matrix,
        annot=True,
        fmt=".3f",
        cmap="RdYlGn_r",
        vmin=0,
        vmax=1,
        square=True,
        cbar_kws={"label": "p-value"},
        ax=ax,
    )
    ax.set_title(f"Pairwise p-values for {metric_name}")
    ax.set_xlabel("Channel")
    ax.set_ylabel("Channel")
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def calculate_fisher_exact_results(channel_summary: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Compare channels using Fisher's exact test on binary conversion outcomes.

    Conversions are estimated from the available campaign data because the
    source dataset does not include a row-level binary conversion flag.
    """
    summary = channel_summary.copy()
    summary["Conversions"] = np.rint(summary["Conversions"]).astype(int)
    summary["Total_Attempts"] = summary["Clicks"].round().astype(int)
    summary["Non_Conversions"] = (summary["Total_Attempts"] - summary["Conversions"]).clip(lower=0)
    summary["Conversion_Rate"] = np.where(
        summary["Total_Attempts"] > 0,
        summary["Conversions"] / summary["Total_Attempts"],
        np.nan,
    )

    groups = summary["Channel_Used"].dropna().tolist()
    results: list[dict] = []

    for i, group_a in enumerate(groups):
        row_a = summary.loc[summary["Channel_Used"] == group_a].iloc[0]
        conversions_a = int(row_a["Conversions"])
        attempts_a = int(row_a["Total_Attempts"])
        non_conversions_a = int(row_a["Non_Conversions"])
        rate_a = row_a["Conversion_Rate"]

        for group_b in groups[i + 1 :]:
            row_b = summary.loc[summary["Channel_Used"] == group_b].iloc[0]
            conversions_b = int(row_b["Conversions"])
            attempts_b = int(row_b["Total_Attempts"])
            non_conversions_b = int(row_b["Non_Conversions"])
            rate_b = row_b["Conversion_Rate"]

            contingency = np.array(
                [
                    [conversions_a, non_conversions_a],
                    [conversions_b, non_conversions_b],
                ]
            )
            odds_ratio, p_value = fisher_exact(contingency, alternative="two-sided")
            difference = rate_b - rate_a
            percentage_difference = (difference / rate_a * 100) if pd.notna(rate_a) and rate_a != 0 else np.nan

            results.append(
                {
                    "Group_A": group_a,
                    "Group_B": group_b,
                    "Conversions_A": conversions_a,
                    "Total_Attempts_A": attempts_a,
                    "Non_Conversions_A": non_conversions_a,
                    "Rate_A": rate_a,
                    "Conversions_B": conversions_b,
                    "Total_Attempts_B": attempts_b,
                    "Non_Conversions_B": non_conversions_b,
                    "Rate_B": rate_b,
                    "Difference_B_minus_A": difference,
                    "Percent_Difference": percentage_difference,
                    "Odds_Ratio": odds_ratio,
                    "p_value": p_value,
                    "Significant": bool(pd.notna(p_value) and p_value < 0.05),
                }
            )

    results_df = pd.DataFrame(results)
    return summary, results_df


def save_rate_comparison_plot(group_summary: pd.DataFrame, output_path: Path) -> None:
    """Save a horizontal bar chart of conversion rates by channel."""
    if group_summary.empty:
        return

    plot_df = group_summary.sort_values(["Conversion_Rate", "Total_Attempts"], ascending=[True, True]).copy()
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)
    bars = ax.barh(plot_df["Channel_Used"], plot_df["Conversion_Rate"], color="#5B8FF9")
    ax.set_xlabel("Conversion Rate")
    ax.set_ylabel("Channel")
    ax.set_title("Conversion Rate by Channel")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:.0%}"))

    for bar, rate in zip(bars, plot_df["Conversion_Rate"]):
        ax.text(
            bar.get_width() + 0.002,
            bar.get_y() + bar.get_height() / 2,
            f"{rate:.1%}",
            va="center",
            fontsize=9,
        )

    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def build_metrics_report(
    group_summary: pd.DataFrame,
    comparison_results: pd.DataFrame,
    correction_summary: pd.DataFrame,
    corrected_comparison_results: pd.DataFrame,
    fisher_group_summary: pd.DataFrame,
    fisher_results: pd.DataFrame,
) -> str:
    """Create one combined markdown report for the comparison steps."""
    lines = []
    lines.append("# Metrics Report")
    lines.append("")
    lines.append("## Channel Performance")
    if not group_summary.empty:
        lines.append(dataframe_to_markdown(group_summary, float_precision=2))
    else:
        lines.append("No channel summary available.")
    lines.append("")

    lines.append("## T-test Results")
    if comparison_results.empty:
        lines.append("No pairwise t-test comparisons were generated.")
    else:
        for metric_name, metric_df in comparison_results.groupby("Metric"):
            lines.append(f"### {metric_name}")
            lines.append(dataframe_to_markdown(metric_df))
            lines.append("")
            total_count = len(metric_df)
            significant_count = int(metric_df["Significant"].sum())
            lines.append(f"**Summary:** {total_count} comparisons, {significant_count} significant at alpha=0.05")
            lines.append("")

    lines.append("## Multiple Comparisons Correction")
    if correction_summary.empty:
        lines.append("No correction summary available.")
    else:
        display_summary = correction_summary.copy()
        display_summary["Metric"] = display_summary["Metric"].replace(
            {"Conversion_Rate": "Conversion Rate"}
        )
        lines.append(
            "With alpha = 0.05, the expected number of false positives by chance alone is "
            "total_comparisons × 0.05."
        )
        lines.append("")
        lines.append(dataframe_to_markdown(display_summary, float_precision=2))
        lines.append("")
        for metric_name, metric_df in corrected_comparison_results.groupby("Metric"):
            if metric_name not in correction_summary["Metric"].values:
                continue
            pretty_metric_name = "Conversion Rate" if metric_name == "Conversion_Rate" else metric_name
            lines.append(f"### Corrected Results — {pretty_metric_name}")
            display_df = metric_df[
                [
                    "Group_A",
                    "Group_B",
                    "p_value",
                    "significant_bonferroni",
                    "p_value_fdr",
                    "significant_fdr",
                ]
            ].copy()
            lines.append(dataframe_to_markdown(display_df))
            lines.append("")

    lines.append("## Fisher Exact Test Results")
    lines.append("### Group Summary")
    lines.append("| Channel | Conversions | Total Attempts | Non-Conversions | Rate |")
    lines.append("| --- | ---: | ---: | ---: | ---: |")
    for _, row in fisher_group_summary.iterrows():
        lines.append(
            f"| {row['Channel_Used']} | {int(row['Conversions']):,} | {int(row['Total_Attempts']):,} | "
            f"{int(row['Non_Conversions']):,} | {row['Conversion_Rate']:.2%} |"
        )
    lines.append("")
    lines.append("### Pairwise Comparisons")
    if fisher_results.empty:
        lines.append("No pairwise comparisons were generated.")
        return "\n".join(lines)

    display_cols = [
        "Group_A",
        "Group_B",
        "Rate_A",
        "Rate_B",
        "Difference_B_minus_A",
        "Percent_Difference",
        "Odds_Ratio",
        "p_value",
        "Significant",
    ]
    lines.append("| " + " | ".join(display_cols) + " |")
    lines.append("| " + " | ".join(["---"] * len(display_cols)) + " |")
    for _, row in fisher_results[display_cols].iterrows():
        lines.append(
            f"| {row['Group_A']} | {row['Group_B']} | {row['Rate_A']:.4f} | {row['Rate_B']:.4f} | "
            f"{row['Difference_B_minus_A']:.4f} | {row['Percent_Difference']:.2f} | "
            f"{row['Odds_Ratio']:.4f} | {row['p_value']:.4g} | {bool(row['Significant'])} |"
        )
    lines.append("")
    total = len(fisher_results)
    significant = int(fisher_results["Significant"].sum())
    lines.append("### Summary")
    lines.append(f"- Total comparisons: {total:,}")
    lines.append(f"- Significant at alpha=0.05: {significant:,}")
    return "\n".join(lines)


def bootstrap_ci(
    data: pd.Series,
    n_bootstrap: int = 1000,
    ci_level: float = 0.95,
    rng: np.random.Generator | None = None,
) -> tuple[float, float]:
    """Return bootstrap confidence interval bounds for the mean."""
    values = pd.Series(data).dropna().to_numpy(dtype=float)
    if len(values) == 0:
        return np.nan, np.nan

    rng = np.random.default_rng(42) if rng is None else rng
    boot_means = np.empty(n_bootstrap, dtype=float)
    for i in range(n_bootstrap):
        sample = rng.choice(values, size=len(values), replace=True)
        boot_means[i] = float(np.mean(sample))

    alpha = 1 - ci_level
    lower = float(np.quantile(boot_means, alpha / 2))
    upper = float(np.quantile(boot_means, 1 - alpha / 2))
    return lower, upper


def empirical_power_ttest(
    true_diff_pct: float,
    base_value: float,
    n_days: int,
    n_sim: int = 1000,
    alpha: float = 0.05,
    rng: np.random.Generator | None = None,
) -> float:
    """Estimate power for a two-sample t-test under a relative mean difference."""
    if not np.isfinite(base_value) or base_value <= 0 or n_days < 2:
        return np.nan

    rng = np.random.default_rng(42) if rng is None else rng
    std = base_value * 0.15
    lower_bound = base_value * 0.5
    rejections = 0

    for _ in range(n_sim):
        sample_a = np.clip(rng.normal(base_value, std, n_days), lower_bound, None)
        sample_b = np.clip(
            rng.normal(base_value * (1 + true_diff_pct), std, n_days),
            lower_bound,
            None,
        )
        _, p_value = ttest_ind(sample_a, sample_b, equal_var=False, nan_policy="omit")
        if pd.notna(p_value) and p_value < alpha:
            rejections += 1

    return rejections / n_sim


def empirical_power_cpa(
    true_diff_pct: float,
    base_cpa: float,
    n_days: int,
    n_sim: int = 1000,
    alpha: float = 0.05,
    rng: np.random.Generator | None = None,
) -> float:
    """Estimate empirical power for CPA differences."""
    return empirical_power_ttest(true_diff_pct, base_cpa, n_days, n_sim=n_sim, alpha=alpha, rng=rng)


def build_power_curve_table(
    base_cpa: float,
    effect_sizes_pct: tuple[float, ...] = (0.05, 0.10, 0.15, 0.20),
    sample_sizes: tuple[int, ...] = (30, 60, 90, 120, 180),
    n_sim: int = 1000,
    alpha: float = 0.05,
) -> pd.DataFrame:
    """Compute empirical power across the requested effect sizes and sample sizes."""
    rows = []
    for effect_size_pct in effect_sizes_pct:
        for n_days in sample_sizes:
            power = empirical_power_cpa(
                effect_size_pct,
                base_cpa,
                n_days,
                n_sim=n_sim,
                alpha=alpha,
            )
            rows.append(
                {
                    "effect_size_pct": effect_size_pct,
                    "n_days": n_days,
                    "power": power,
                }
            )
    return pd.DataFrame(rows)


def find_min_days_for_power(
    base_cpa: float,
    true_diff_pct: float,
    target_power: float = 0.80,
    max_days: int = 365,
    n_sim: int = 300,
    alpha: float = 0.05,
) -> tuple[float, float]:
    """Find the minimum days needed to reach the target power."""
    for n_days in range(10, max_days + 1):
        power = empirical_power_cpa(
            true_diff_pct,
            base_cpa,
            n_days,
            n_sim=n_sim,
            alpha=alpha,
        )
        if power >= target_power:
            return float(n_days), float(power)
    return np.nan, np.nan


def save_power_analysis_plot(power_curve_df: pd.DataFrame, output_path: Path) -> None:
    """Save power curves for the CPA simulation."""
    if power_curve_df.empty:
        return

    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)

    for effect_size_pct, effect_df in power_curve_df.groupby("effect_size_pct"):
        effect_df = effect_df.sort_values("n_days")
        ax.plot(
            effect_df["n_days"],
            effect_df["power"],
            marker="o",
            linewidth=2,
            label=f"{int(effect_size_pct * 100)}% difference",
        )

    ax.axhline(0.80, color="black", linestyle="--", linewidth=1.5, label="80% power")
    ax.set_xlabel("Sample Size (days)")
    ax.set_ylabel("Empirical Power")
    ax.set_title("Power Analysis for CPA Differences")
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.25)
    ax.legend(title="Effect Size")
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def build_cpa_ci_table(
    daily_summary: pd.DataFrame,
    n_bootstrap: int = 1000,
    ci_level: float = 0.95,
) -> pd.DataFrame:
    """Calculate bootstrap CPA confidence intervals for each channel."""
    rows = []
    if daily_summary.empty or "CPA" not in daily_summary.columns:
        return pd.DataFrame()

    rng = np.random.default_rng(42)
    for channel, group_df in daily_summary.groupby("Channel_Used"):
        cpa_series = group_df["CPA"].dropna()
        if cpa_series.empty:
            continue
        ci_lower, ci_upper = bootstrap_ci(cpa_series, n_bootstrap=n_bootstrap, ci_level=ci_level, rng=rng)
        rows.append(
            {
                "Channel_Used": channel,
                "Mean_CPA": float(cpa_series.mean()),
                "CI_Lower": ci_lower,
                "CI_Upper": ci_upper,
            }
        )

    return pd.DataFrame(rows).sort_values("Mean_CPA").reset_index(drop=True)


def summarize_fdr_significant_findings(corrected_comparison_results: pd.DataFrame) -> pd.DataFrame:
    """Summarize pairwise findings that remain significant after FDR correction."""
    if corrected_comparison_results.empty:
        return pd.DataFrame()

    rows = []
    significant = corrected_comparison_results[corrected_comparison_results["significant_fdr"] == True]
    for _, row in significant.iterrows():
        metric = row["Metric"]
        mean_a = float(row["Mean_A"])
        mean_b = float(row["Mean_B"])
        if metric == "CPA":
            better_group = row["Group_A"] if mean_a < mean_b else row["Group_B"]
            worse_group = row["Group_B"] if mean_a < mean_b else row["Group_A"]
        else:
            better_group = row["Group_A"] if mean_a > mean_b else row["Group_B"]
            worse_group = row["Group_B"] if mean_a > mean_b else row["Group_A"]

        abs_diff = abs(mean_b - mean_a)
        smaller_mean = min(mean_a, mean_b)
        pct_diff = abs_diff / smaller_mean if smaller_mean else np.nan
        rows.append(
            {
                "Metric": metric.replace("_", " "),
                "Better_Group": better_group,
                "Worse_Group": worse_group,
                "Absolute_Difference": abs_diff,
                "Percent_Difference": pct_diff,
                "Adjusted_p_value": float(row["p_value_fdr"]),
                "Cohens_d": float(row["Cohens_d"]),
            }
        )

    return pd.DataFrame(rows)


def build_allocation_recommendations(channel_summary: pd.DataFrame) -> pd.DataFrame:
    """Create a simple composite-score allocation recommendation table."""
    if channel_summary.empty:
        return pd.DataFrame()

    df = channel_summary[["Channel_Used", "CPA", "ROAS"]].copy()
    n_groups = len(df)
    scale_denom = max(n_groups - 1, 1)

    cpa_rank = df["CPA"].rank(ascending=True, method="min")
    roas_rank = df["ROAS"].rank(ascending=False, method="min")
    df["CPA_Score"] = 1 - (cpa_rank - 1) / scale_denom
    df["ROAS_Score"] = 1 - (roas_rank - 1) / scale_denom
    df["Composite_Score"] = 0.5 * df["CPA_Score"] + 0.5 * df["ROAS_Score"]
    df["Allocation_Percentage"] = df["Composite_Score"] / df["Composite_Score"].sum() * 100
    df["Allocation_Units"] = df["Allocation_Percentage"]
    df = df.sort_values("Composite_Score", ascending=False).reset_index(drop=True)

    df["Priority"] = "Maintain"
    if len(df) >= 2:
        df.loc[: max(1, len(df) // 3) - 1, "Priority"] = "Increase investment"
        df.loc[len(df) - max(1, len(df) // 3) :, "Priority"] = "Deprioritize"

    return df


def assess_power_adequacy(
    corrected_comparison_results: pd.DataFrame,
    benchmark_days: int = 90,
    target_power: float = 0.80,
) -> pd.DataFrame:
    """Assess whether the benchmark number of days is adequate for significant pairs."""
    if corrected_comparison_results.empty:
        return pd.DataFrame()

    rows = []
    significant = corrected_comparison_results[corrected_comparison_results["significant_fdr"] == True]
    for _, row in significant.iterrows():
        mean_a = float(row["Mean_A"])
        mean_b = float(row["Mean_B"])
        baseline = min(mean_a, mean_b)
        observed_diff_pct = abs(mean_b - mean_a) / baseline if baseline else np.nan
        power_at_benchmark = empirical_power_ttest(observed_diff_pct, baseline, benchmark_days, n_sim=1000)
        min_days, power_at_min_days = find_min_days_for_power(
            baseline,
            observed_diff_pct,
            target_power=target_power,
            max_days=max(benchmark_days, 730),
            n_sim=300,
        )
        rows.append(
            {
                "Metric": row["Metric"].replace("_", " "),
                "Group_A": row["Group_A"],
                "Group_B": row["Group_B"],
                "Observed_Difference_Pct": observed_diff_pct * 100,
                "Power_At_90_Days": power_at_benchmark,
                "Minimum_Days_For_80Pct": min_days,
                "Power_At_Min_Days": power_at_min_days,
                "Status_At_90_Days": "sufficient" if power_at_benchmark >= target_power else "insufficient",
                "Additional_Days_Needed": max(min_days - benchmark_days, 0) if pd.notna(min_days) else np.nan,
            }
        )

    return pd.DataFrame(rows)


def build_min_power_table(
    base_cpa: float,
    effect_sizes_pct: tuple[float, ...] = (0.05, 0.10, 0.15, 0.20),
    benchmark_days: int = 90,
    target_power: float = 0.80,
) -> pd.DataFrame:
    """Summarize the minimum sample size needed to reach target power."""
    rows = []
    for effect_size_pct in effect_sizes_pct:
        min_days, power_at_min = find_min_days_for_power(
            base_cpa,
            effect_size_pct,
            target_power=target_power,
            max_days=max(benchmark_days, 730),
            n_sim=300,
        )
        if pd.isna(min_days):
            status = "insufficient"
            extra_days = np.nan
        else:
            status = "sufficient" if min_days <= benchmark_days else "insufficient"
            extra_days = max(min_days - benchmark_days, 0)

        rows.append(
            {
                "Effect_Size_Pct": effect_size_pct * 100,
                "Minimum_Days_For_80Pct": min_days,
                "Power_At_Min_Days": power_at_min,
                "Status_At_90_Days": status,
                "Additional_Days_Needed": extra_days,
            }
        )

    return pd.DataFrame(rows)


def build_executive_memo(
    cleaned_data: pd.DataFrame,
    cpa_ci_table: pd.DataFrame,
    significant_findings: pd.DataFrame,
    power_curve_df: pd.DataFrame,
    min_power_table: pd.DataFrame,
    adequacy_table: pd.DataFrame,
    allocation_table: pd.DataFrame,
    current_days_available: int,
) -> str:
    """Create the executive memo markdown."""
    date_value = pd.Timestamp.today().strftime("%Y-%m-%d")
    period_start = cleaned_data["Date"].min().strftime("%Y-%m-%d") if "Date" in cleaned_data.columns else "N/A"
    period_end = cleaned_data["Date"].max().strftime("%Y-%m-%d") if "Date" in cleaned_data.columns else "N/A"

    lines = []
    lines.append("# Executive Memo")
    lines.append("")
    lines.append(f"- Date: {date_value}")
    lines.append("- Analyst: Codex")
    lines.append("- Dataset used: marketing_campaign_dataset_original.csv")
    lines.append(f"- Period analyzed: {period_start} to {period_end}")
    lines.append("")

    lines.append("## Executive Summary")
    if significant_findings.empty:
        lines.append(
            "No CPA or conversion-rate channel pairs remained statistically significant after FDR correction. "
            "The channels are broadly similar on the metrics tested, so the main decision lever is relative efficiency "
            "rather than a single clearly dominant channel."
        )
    else:
        lines.append(
            "Several channel pairs remained significant after FDR correction. The strongest differences favor the "
            "channels listed below in the key findings section."
        )
    lines.append("")

    lines.append("## Key Findings")
    if not allocation_table.empty:
        top_channels = allocation_table.head(3)[["Channel_Used", "Composite_Score", "Allocation_Percentage", "Priority"]]
        lines.append("### Top Performing Channels")
        lines.append(dataframe_to_markdown(top_channels, float_precision=2))
        lines.append("")

    lines.append("### Statistically Significant Differences")
    if significant_findings.empty:
        lines.append("No CPA or conversion-rate differences survived FDR correction.")
    else:
        lines.append(dataframe_to_markdown(significant_findings, float_precision=4))
    lines.append("")

    lines.append("### Confidence Intervals for CPA")
    if cpa_ci_table.empty:
        lines.append("No CPA confidence intervals available.")
    else:
        lines.append(dataframe_to_markdown(cpa_ci_table, float_precision=2))
    lines.append("")

    lines.append("### Data Adequacy and Power")
    if not power_curve_df.empty:
        lines.append("#### Power Curves")
        lines.append(dataframe_to_markdown(power_curve_df.assign(effect_size_pct=power_curve_df["effect_size_pct"] * 100), float_precision=3))
        lines.append("")
    if not min_power_table.empty:
        lines.append("#### Minimum Sample Size for 80% Power")
        lines.append(dataframe_to_markdown(min_power_table, float_precision=2))
        lines.append("")
    if not adequacy_table.empty:
        lines.append("#### Current Data Adequacy")
        lines.append(dataframe_to_markdown(adequacy_table, float_precision=2))
    else:
        lines.append(
            f"The current benchmark uses 90 days of data, while the dataset contains {current_days_available} daily observations per channel."
        )
    lines.append("")

    lines.append("## Recommendations")
    if not allocation_table.empty:
        lines.append(
            "Prioritize channels with the highest composite score, and reduce emphasis on channels in the bottom tier."
        )
        lines.append("Allocate resources proportionally to the composite score below.")
        lines.append("")
        lines.append(dataframe_to_markdown(allocation_table[["Channel_Used", "Composite_Score", "Allocation_Percentage", "Priority"]], float_precision=2))
    else:
        lines.append("Use the channel-level CPA and ROAS rankings to prioritize investment.")
    lines.append("")

    lines.append("## Statistical Caveats")
    lines.append("- Conversions were estimated from clicks and conversion rate because the source file did not include a raw binary conversion flag.")
    lines.append("- Multiple comparisons correction was applied to CPA and conversion-rate pairwise tests.")
    lines.append("- Bootstrap confidence intervals capture sampling variability, but they do not remove model or measurement bias.")
    lines.append("- Statistical significance does not necessarily imply practical significance.")
    lines.append("- Power estimates are simulation-based and depend on the assumed variance structure.")
    lines.append("")

    lines.append("## Next Steps")
    lines.append("- Re-run the analysis after new campaign data arrives to see whether the composite ranking changes.")
    lines.append("- Test whether channel-specific creative or audience segments explain the small differences observed here.")
    lines.append("- If budget changes are possible, bias incremental spend toward the top-ranked channels and monitor CPA and ROAS weekly.")

    return "\n".join(lines)


if __name__ == "__main__":
    data_source = "Lab22_Statistics/marketing_campaign_dataset_original.csv"
    output_data = Path("Lab22_Statistics/marketing_data.csv")
    output_report = Path("Lab22_Statistics/data_preparation.md")
    overview_png = Path("Lab22_Statistics/group_metrics_overview.png")
    distributions_png = Path("Lab22_Statistics/group_distributions.png")
    comparison_png = Path("Lab22_Statistics/metric_comparison_heatmap.png")
    rate_png = Path("Lab22_Statistics/rate_comparison.png")
    correction_png = Path("Lab22_Statistics/correction_comparison.png")
    power_png = Path("Lab22_Statistics/power_analysis_cpa.png")
    metrics_report_path = Path("Lab22_Statistics/metrics.md")
    memo_path = Path("Lab22_Statistics/executive_memo.md")
    data = pd.read_csv(data_source)
    cleaned_data = clean_marketing_data(data)
    report = build_preparation_report(data, cleaned_data)
    channel_summary, daily_summary = calculate_group_metrics(cleaned_data)
    group_summary_table = format_group_summary(channel_summary)
    comparison_metrics = [metric for metric in ["ROAS", "CPA", "Conversion_Rate"] if metric in daily_summary.columns]
    comparison_results, primary_results, primary_metric = compare_groups_with_ttests(
        daily_summary,
        "Channel_Used",
        comparison_metrics,
    )
    corrected_comparison_results, correction_summary = apply_multiple_comparisons_correction(comparison_results)
    pvalue_matrix = build_pvalue_matrix(
        corrected_comparison_results,
        primary_metric,
        sorted(daily_summary["Channel_Used"].dropna().unique().tolist()),
    )
    fisher_group_summary, fisher_results = calculate_fisher_exact_results(channel_summary)
    base_cpa = float(daily_summary["CPA"].dropna().mean()) if "CPA" in daily_summary.columns and not daily_summary["CPA"].dropna().empty else float(channel_summary["CPA"].dropna().mean())
    power_curve_df = build_power_curve_table(base_cpa)
    save_power_analysis_plot(power_curve_df, power_png)
    min_power_table = build_min_power_table(base_cpa, benchmark_days=90)
    cpa_ci_table = build_cpa_ci_table(daily_summary)
    significant_findings = summarize_fdr_significant_findings(corrected_comparison_results)
    allocation_table = build_allocation_recommendations(channel_summary)
    adequacy_table = assess_power_adequacy(corrected_comparison_results, benchmark_days=90)
    metrics_report = build_metrics_report(
        group_summary_table,
        comparison_results,
        correction_summary,
        corrected_comparison_results,
        fisher_group_summary,
        fisher_results,
    )
    memo = build_executive_memo(
        cleaned_data,
        cpa_ci_table,
        significant_findings,
        power_curve_df,
        min_power_table,
        adequacy_table,
        allocation_table,
        current_days_available=int(daily_summary["Date"].nunique()) if "Date" in daily_summary.columns else 0,
    )

    cleaned_data.to_csv(output_data, index=False)
    output_report.write_text(report, encoding="utf-8")
    metrics_report_path.write_text(metrics_report, encoding="utf-8")
    memo_path.write_text(memo, encoding="utf-8")
    save_group_metrics_overview(channel_summary, overview_png)
    save_group_distributions(daily_summary, distributions_png)
    save_pvalue_heatmap(pvalue_matrix, primary_metric, comparison_png)
    save_rate_comparison_plot(fisher_group_summary, rate_png)
    save_correction_comparison_plot(correction_summary, correction_png)

    print("Raw shape:", data.shape)
    print("Cleaned shape:", cleaned_data.shape)
    print(f"Saved cleaned data to: {output_data}")
    print(f"Saved report to: {output_report}")
    print(f"Saved metrics report to: {metrics_report_path}")
    print("\nChannel Summary:")
    print(group_summary_table.to_string(index=False))
    print("\nT-test Results:")
    if comparison_results.empty:
        print("No pairwise comparisons were generated.")
    else:
        for metric_name, metric_df in comparison_results.groupby("Metric"):
            significant_count = int(metric_df["Significant"].sum())
            total_count = len(metric_df)
            print(f"\nMetric: {metric_name}")
            print(metric_df.to_string(index=False))
            print(f"Summary: {total_count} comparisons, {significant_count} significant at alpha=0.05")
    print(f"\nSaved overview chart to: {overview_png}")
    print(f"Saved distributions chart to: {distributions_png}")
    print(f"Saved p-value heatmap to: {comparison_png}")
    print(f"Saved rate comparison chart to: {rate_png}")
    print(f"Saved correction comparison chart to: {correction_png}")
    print(f"Saved power analysis chart to: {power_png}")
    print(f"Saved executive memo to: {memo_path}")
    print("\nMultiple Comparisons Correction:")
    if correction_summary.empty:
        print("No correction summary was generated.")
    else:
        printable_summary = correction_summary.copy()
        printable_summary["Metric"] = printable_summary["Metric"].replace(
            {"Conversion_Rate": "Conversion Rate"}
        )
        print(printable_summary.to_string(index=False))
    print("\nPower Analysis:")
    if power_curve_df.empty:
        print("No power analysis results were generated.")
    else:
        display_power = power_curve_df.copy()
        display_power["effect_size_pct"] = (display_power["effect_size_pct"] * 100).round(0)
        print(display_power.to_string(index=False))
    print("\nMinimum Sample Size Recommendations:")
    if min_power_table.empty:
        print("No minimum sample size recommendations were generated.")
    else:
        print(min_power_table.to_string(index=False))
    print("\nCPA Confidence Intervals:")
    if cpa_ci_table.empty:
        print("No CPA confidence intervals were generated.")
    else:
        print(cpa_ci_table.to_string(index=False))
    print("\nAllocation Recommendations:")
    if allocation_table.empty:
        print("No allocation recommendations were generated.")
    else:
        print(allocation_table.to_string(index=False))
    print("\nFisher Exact Results:")
    if fisher_results.empty:
        print("No pairwise comparisons were generated.")
    else:
        print(fisher_results.to_string(index=False))
        print(
            f"Summary: {len(fisher_results)} comparisons, "
            f"{int(fisher_results['Significant'].sum())} significant at alpha=0.05"
        )
    print(cleaned_data.head())
