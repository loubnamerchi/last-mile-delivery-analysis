"""
Tests for src.analysis.business_analysis
"""

import pandas as pd
import pytest

from src.cleaning.cleaner import clean_dataset
from src.analysis.features import engineer_features
from src.analysis.business_analysis import (
    chi_square_association,
    run_significance_scan,
    rank_segments_by_score,
    weather_mode_interaction,
    identify_high_risk_segment,
    cost_efficiency_by_segment,
)


@pytest.fixture
def engineered_sample_df(raw_sample_df):
    """Sample fixture run through cleaning + feature engineering."""
    cleaned = clean_dataset(raw_sample_df)
    return engineer_features(cleaned)


def test_chi_square_association_returns_expected_keys(engineered_sample_df):
    result = chi_square_association(engineered_sample_df, "weather_condition")
    assert set(result.keys()) == {"column", "chi2", "p_value", "dof", "significant_at_0.05"}
    assert result["column"] == "weather_condition"
    # numpy bool_ is returned by the p_value < 0.05 comparison; accept both
    # Python bool and numpy bool_ since both behave correctly as booleans.
    assert result["significant_at_0.05"] in (True, False)


def test_chi_square_association_p_value_in_valid_range(engineered_sample_df):
    result = chi_square_association(engineered_sample_df, "region")
    assert 0.0 <= result["p_value"] <= 1.0


def test_run_significance_scan_returns_one_row_per_column(engineered_sample_df):
    columns = ["region", "weather_condition", "vehicle_type"]
    result = run_significance_scan(engineered_sample_df, columns)
    assert len(result) == len(columns)
    assert set(result["column"]) == set(columns)


def test_run_significance_scan_sorted_by_chi2_descending(engineered_sample_df):
    columns = ["region", "weather_condition", "vehicle_type"]
    result = run_significance_scan(engineered_sample_df, columns)
    chi2_values = result["chi2"].tolist()
    assert chi2_values == sorted(chi2_values, reverse=True)


def test_rank_segments_by_score_includes_volume_and_score(engineered_sample_df):
    result = rank_segments_by_score(engineered_sample_df, "delivery_partner")
    assert "avg_performance_score" in result.columns
    assert "delivery_count" in result.columns
    # Should be sorted best score first
    scores = result["avg_performance_score"].tolist()
    assert scores == sorted(scores, reverse=True)


def test_rank_segments_by_score_volume_sums_to_total(engineered_sample_df):
    result = rank_segments_by_score(engineered_sample_df, "region")
    assert result["delivery_count"].sum() == len(engineered_sample_df)


def test_weather_mode_interaction_returns_percentages(engineered_sample_df):
    result = weather_mode_interaction(engineered_sample_df)
    # Each row (mode, weather) should sum to ~100%
    row_sums = result.sum(axis=1)
    for total in row_sums:
        assert total == pytest.approx(100.0, abs=0.1)


def test_weather_mode_interaction_respects_mode_filter(engineered_sample_df):
    result = weather_mode_interaction(engineered_sample_df, modes=["express"])
    modes_in_result = result.index.get_level_values("delivery_mode").unique().tolist()
    assert modes_in_result == ["express"]


def test_identify_high_risk_segment_returns_expected_structure(engineered_sample_df):
    result = identify_high_risk_segment(
        engineered_sample_df, weather_values=["rainy", "stormy"], mode_value="express"
    )
    expected_keys = {
        "segment_size", "pct_of_total_volume",
        "segment_status_distribution", "overall_baseline_distribution",
    }
    assert set(result.keys()) == expected_keys
    assert result["segment_size"] >= 0


def test_identify_high_risk_segment_pct_is_valid_range(engineered_sample_df):
    result = identify_high_risk_segment(
        engineered_sample_df, weather_values=["clear"], mode_value="express"
    )
    assert 0.0 <= result["pct_of_total_volume"] <= 100.0


def test_cost_efficiency_by_segment_returns_positive_values(engineered_sample_df):
    # Lower min_distance_km so the small sample fixture isn't filtered to empty
    result = cost_efficiency_by_segment(engineered_sample_df, "vehicle_type", min_distance_km=0)
    assert (result["avg_cost_per_km"] > 0).all()


def test_cost_efficiency_by_segment_sorted_descending(engineered_sample_df):
    result = cost_efficiency_by_segment(engineered_sample_df, "delivery_partner", min_distance_km=0)
    values = result["avg_cost_per_km"].tolist()
    assert values == sorted(values, reverse=True)
