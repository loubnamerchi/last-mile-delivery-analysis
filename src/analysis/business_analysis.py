"""
Business analysis functions for the last-mile delivery dataset.

Goes beyond descriptive EDA: statistical significance testing,
segment ranking, and interaction/root-cause analysis. Every function
is built to answer a specific business question from
reports/01_business_understanding.md.
"""

import pandas as pd
import numpy as np
from scipy import stats


def chi_square_association(df: pd.DataFrame, category_col: str,
                            status_col: str = "delivery_status") -> dict:
    """
    Test whether a categorical column is statistically associated with
    delivery_status using a chi-square test of independence.

    This answers "is the difference we see in a bar chart real, or
    could it plausibly be random noise?" -- a step EDA alone cannot
    answer.

    Parameters
    ----------
    df : pd.DataFrame
    category_col : str
        The categorical column to test (e.g. 'region', 'weather_condition').
    status_col : str
        The outcome column, default 'delivery_status'.

    Returns
    -------
    dict
        chi2 statistic, p-value, degrees of freedom, and a plain-language
        verdict at alpha = 0.05.
    """
    contingency = pd.crosstab(df[category_col], df[status_col])
    chi2, p_value, dof, _ = stats.chi2_contingency(contingency)

    return {
        "column": category_col,
        "chi2": round(chi2, 2),
        "p_value": round(p_value, 6),
        "dof": dof,
        "significant_at_0.05": p_value < 0.05,
    }


def run_significance_scan(df: pd.DataFrame, columns: list,
                           status_col: str = "delivery_status") -> pd.DataFrame:
    """
    Run chi_square_association across multiple categorical columns and
    return a single ranked summary table, sorted by chi2 (largest
    effect first).

    Parameters
    ----------
    df : pd.DataFrame
    columns : list of str
        Categorical columns to test.
    status_col : str

    Returns
    -------
    pd.DataFrame
        One row per tested column, sorted by chi2 descending.
    """
    results = [chi_square_association(df, col, status_col) for col in columns]
    return pd.DataFrame(results).sort_values("chi2", ascending=False).reset_index(drop=True)


def rank_segments_by_score(df: pd.DataFrame, segment_col: str,
                            score_col: str = "performance_score") -> pd.DataFrame:
    """
    Rank a categorical segment (partner, vehicle, region, etc.) by
    average performance_score, alongside volume so small segments
    aren't over-interpreted.

    Parameters
    ----------
    df : pd.DataFrame
    segment_col : str
    score_col : str

    Returns
    -------
    pd.DataFrame
        Segment, average score, delivery count, sorted best to worst.
    """
    result = (
        df.groupby(segment_col)
        .agg(avg_performance_score=(score_col, "mean"), delivery_count=(score_col, "count"))
        .round(2)
        .sort_values("avg_performance_score", ascending=False)
    )
    return result


def weather_mode_interaction(df: pd.DataFrame,
                              modes: list = None,
                              status_col: str = "delivery_status") -> pd.DataFrame:
    """
    Break down delivery status by weather_condition WITHIN each
    delivery_mode, to check whether weather's effect differs depending
    on delivery mode (root-cause / interaction analysis, not just two
    separate main effects).

    Parameters
    ----------
    df : pd.DataFrame
    modes : list of str, optional
        Restrict to specific delivery_mode values. Defaults to all.
    status_col : str

    Returns
    -------
    pd.DataFrame
        Multi-index (delivery_mode, weather_condition) x status_col (%).
    """
    subset = df[df["delivery_mode"].isin(modes)] if modes else df
    result = (
        pd.crosstab(
            [subset["delivery_mode"], subset["weather_condition"]],
            subset[status_col],
            normalize="index",
        )
        .mul(100)
        .round(1)
    )
    return result


def identify_high_risk_segment(df: pd.DataFrame, weather_values: list,
                                mode_value: str,
                                status_col: str = "delivery_status") -> dict:
    """
    Quantify a specific high-risk operational segment (e.g. express
    deliveries during rainy/stormy weather) against the overall
    baseline, to support a Finding -> Evidence -> Impact narrative.

    Parameters
    ----------
    df : pd.DataFrame
    weather_values : list of str
        Weather conditions defining the risk segment.
    mode_value : str
        Delivery mode defining the risk segment.
    status_col : str

    Returns
    -------
    dict
        Segment size, % of total volume, status distribution within
        the segment, and the overall baseline for comparison.
    """
    segment = df[
        (df["weather_condition"].isin(weather_values)) & (df["delivery_mode"] == mode_value)
    ]
    segment_dist = segment[status_col].value_counts(normalize=True).mul(100).round(1)
    baseline_dist = df[status_col].value_counts(normalize=True).mul(100).round(1)

    return {
        "segment_size": len(segment),
        "pct_of_total_volume": round(len(segment) / len(df) * 100, 1),
        "segment_status_distribution": segment_dist.to_dict(),
        "overall_baseline_distribution": baseline_dist.to_dict(),
    }


def cost_efficiency_by_segment(df: pd.DataFrame, segment_col: str,
                                min_distance_km: float = 50) -> pd.DataFrame:
    """
    Compare cost_per_km across a segment, restricted to deliveries
    above a minimum distance to avoid the fixed-cost skew seen in very
    short trips (see Step 8 feature engineering notes).

    Parameters
    ----------
    df : pd.DataFrame
        Must contain cost_per_km (see src.analysis.features).
    segment_col : str
    min_distance_km : float
        Minimum distance to include, default 50km.

    Returns
    -------
    pd.DataFrame
        Segment, average cost_per_km, sorted highest to lowest.
    """
    subset = df[df["distance_km"] > min_distance_km]
    result = (
        subset.groupby(segment_col)["cost_per_km"]
        .mean()
        .round(2)
        .sort_values(ascending=False)
        .to_frame(name="avg_cost_per_km")
    )
    return result
