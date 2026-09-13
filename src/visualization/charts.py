"""
Reusable visualization functions for the last-mile delivery analysis.
Each function returns a matplotlib Figure (or a Plotly Figure, clearly
named) so callers can further customize, save, or embed it (e.g. in the
Streamlit dashboard).
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

sns.set_style("whitegrid")
PALETTE = {"delivered": "#2E7D32", "delayed": "#F9A825", "failed": "#C62828"}


def plot_status_distribution(df: pd.DataFrame, status_col: str = "delivery_status") -> plt.Figure:
    """Bar chart of overall delivery status distribution (%)."""
    fig, ax = plt.subplots(figsize=(6, 4))
    pct = df[status_col].value_counts(normalize=True).mul(100).sort_values(ascending=False)
    sns.barplot(x=pct.index, y=pct.values, ax=ax, palette="viridis")
    ax.set_title("Overall Delivery Status Distribution")
    ax.set_xlabel("Delivery Status")
    ax.set_ylabel("Percentage of Deliveries (%)")
    for i, v in enumerate(pct.values):
        ax.text(i, v + 0.5, f"{v:.1f}%", ha="center")
    fig.tight_layout()
    return fig


def plot_segment_status(df: pd.DataFrame, segment_col: str, status_col: str = "delivery_status") -> plt.Figure:
    """Stacked bar chart of delivery status (%) broken down by a categorical segment."""
    ct = pd.crosstab(df[segment_col], df[status_col], normalize="index").mul(100)
    fig, ax = plt.subplots(figsize=(9, 5))
    ct.plot(kind="bar", stacked=True, ax=ax, colormap="viridis")
    ax.set_title(f"Delivery Status by {segment_col.replace('_', ' ').title()}")
    ax.set_xlabel(segment_col.replace("_", " ").title())
    ax.set_ylabel("Percentage of Deliveries (%)")
    ax.legend(title="Status", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.xticks(rotation=45, ha="right")
    fig.tight_layout()
    return fig

def plot_numeric_status(df: pd.DataFrame, numeric_col: str, status_col: str = "delivery_status") -> plt.Figure:
    """Stacked bar chart of delivery status (%) by numerical value ranges."""
    df = df.copy()
    df["range"] = pd.cut(df[numeric_col], bins=5)

    ct = pd.crosstab(df["range"], df[status_col], normalize="index").mul(100)

    fig, ax = plt.subplots(figsize=(9, 5))
    ct.plot(kind="bar", stacked=True, ax=ax, colormap="viridis")

    ax.set_title(f"Delivery Status by {numeric_col.replace('_', ' ').title()} Range")
    ax.set_xlabel(f"{numeric_col.replace('_', ' ').title()} Range")
    ax.set_ylabel("Percentage of Deliveries (%)")

    ax.legend(title="Status", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.xticks(rotation=45, ha="right")
    fig.tight_layout()

    return fig


def plot_distance_vs_metric(df: pd.DataFrame, metric_col: str, metric_label: str) -> plt.Figure:
    """Scatter plot of distance_km vs a numeric metric (e.g. delivery time or cost)."""
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.scatterplot(data=df, x="distance_km", y=metric_col, alpha=0.15, ax=ax)
    ax.set_title(f"Distance vs {metric_label}")
    ax.set_xlabel("Distance (km)")
    ax.set_ylabel(metric_label)
    fig.tight_layout()
    return fig


def plot_rating_by_status(df: pd.DataFrame, rating_col: str = "delivery_rating",
                           status_col: str = "delivery_status") -> plt.Figure:
    """Boxplot of customer rating grouped by delivery status."""
    fig, ax = plt.subplots(figsize=(6, 5))
    order = df.groupby(status_col)[rating_col].mean().sort_values().index
    sns.boxplot(data=df, x=status_col, y=rating_col, order=order, ax=ax, palette="viridis")
    ax.set_title("Customer Rating by Delivery Status")
    ax.set_xlabel("Delivery Status")
    ax.set_ylabel("Customer Rating (1-5)")
    fig.tight_layout()
    return fig


def plot_correlation_heatmap(df: pd.DataFrame, numeric_cols: list) -> plt.Figure:
    """Correlation heatmap for a list of numeric columns."""
    fig, ax = plt.subplots(figsize=(6, 5))
    corr = df[numeric_cols].corr()
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax)
    ax.set_title("Correlation Heatmap: Numeric Variables")
    fig.tight_layout()
    return fig


def plot_weather_mode_heatmap(df: pd.DataFrame, status_value: str = "failed",
                               status_col: str = "delivery_status") -> plt.Figure:
    """
    Heatmap of a chosen delivery_status outcome rate (%) across
    delivery_mode (rows) x weather_condition (columns). Built to
    visualize the interaction effect found in Business Analysis
    (weather's damage concentrates in express mode).
    """
    ct = pd.crosstab(
        [df["delivery_mode"]], [df["weather_condition"]],
        values=(df[status_col] == status_value), aggfunc="mean"
    ).mul(100).round(1)

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(ct, annot=True, fmt=".1f", cmap="Reds", ax=ax,
                cbar_kws={"label": f"{status_value.title()} Rate (%)"})
    ax.set_title(f"{status_value.title()} Rate (%) by Delivery Mode x Weather")
    ax.set_xlabel("Weather Condition")
    ax.set_ylabel("Delivery Mode")
    fig.tight_layout()
    return fig


def plot_mode_reliability_comparison(df: pd.DataFrame,
                                      status_col: str = "delivery_status") -> plt.Figure:
    """
    Grouped bar chart comparing on-time (delivered), delayed, and failed
    rates across delivery_mode, using a consistent traffic-light color
    scheme (green/amber/red) for immediate readability.
    """
    ct = pd.crosstab(df["delivery_mode"], df[status_col], normalize="index").mul(100)
    ct = ct[["delivered", "delayed", "failed"]]  # consistent column order
    order = ct["delivered"].sort_values(ascending=False).index
    ct = ct.loc[order]

    fig, ax = plt.subplots(figsize=(8, 5))
    ct.plot(kind="bar", ax=ax, color=[PALETTE[c] for c in ct.columns], width=0.7)
    ax.set_title("Delivery Outcome Rate by Delivery Mode")
    ax.set_xlabel("Delivery Mode")
    ax.set_ylabel("Percentage of Deliveries (%)")
    ax.legend(title="Outcome")
    plt.xticks(rotation=0)
    fig.tight_layout()
    return fig


def plot_high_risk_segment_comparison(segment_dist: dict, baseline_dist: dict,
                                       segment_label: str = "High-Risk Segment") -> plt.Figure:
    """
    Side-by-side bar comparison of a specific segment's outcome
    distribution vs. the overall baseline. Built for the
    express + rainy/stormy high-risk segment identified in Business
    Analysis, but works for any two comparable distributions.

    Parameters
    ----------
    segment_dist : dict
        e.g. {'delivered': 1.3, 'delayed': 79.0, 'failed': 19.8}
    baseline_dist : dict
        e.g. {'delivered': 73.3, 'delayed': 21.4, 'failed': 5.3}
    segment_label : str
    """
    statuses = ["delivered", "delayed", "failed"]
    seg_vals = [segment_dist.get(s, 0) for s in statuses]
    base_vals = [baseline_dist.get(s, 0) for s in statuses]

    x = range(len(statuses))
    width = 0.35

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar([i - width / 2 for i in x], base_vals, width, label="Overall Baseline", color="#90A4AE")
    ax.bar([i + width / 2 for i in x], seg_vals, width, label=segment_label,
           color=[PALETTE[s] for s in statuses], alpha=0.9)
    ax.set_xticks(list(x))
    ax.set_xticklabels([s.title() for s in statuses])
    ax.set_ylabel("Percentage of Deliveries (%)")
    ax.set_title(f"{segment_label} vs. Overall Baseline")
    ax.legend()
    fig.tight_layout()
    return fig


def plotly_weather_mode_interactive(df: pd.DataFrame,
                                     status_col: str = "delivery_status") -> go.Figure:
    """
    Interactive Plotly grouped bar: delivered/delayed/failed rate (%)
    by weather_condition, faceted by delivery_mode. Intended for use in
    the Streamlit dashboard (Step 11) where hover interactivity adds
    real value for a manager exploring the data live.
    """
    ct = (
        pd.crosstab([df["delivery_mode"], df["weather_condition"]], df[status_col], normalize="index")
        .mul(100)
        .round(1)
        .reset_index()
        .melt(id_vars=["delivery_mode", "weather_condition"], var_name="status", value_name="pct")
    )

    fig = px.bar(
        ct, x="weather_condition", y="pct", color="status",
        facet_col="delivery_mode", facet_col_wrap=2,
        color_discrete_map=PALETTE,
        labels={"pct": "% of Deliveries", "weather_condition": "Weather", "status": "Outcome"},
        title="Delivery Outcome by Weather Condition, per Delivery Mode",
    )
    fig.update_layout(legend_title_text="Outcome")
    return fig
