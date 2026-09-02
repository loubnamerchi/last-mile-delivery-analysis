"""
Tests for src.analysis.features
"""

import pandas as pd
import pytest

from src.cleaning.cleaner import clean_dataset
from src.analysis.features import (
    add_delay_duration,
    add_delay_category,
    add_on_time_flag,
    add_delivery_success_flag,
    add_distance_category,
    add_cost_per_km,
    add_satisfaction_category,
    add_performance_score,
    engineer_features,
)


@pytest.fixture
def cleaned_sample_df(raw_sample_df):
    """The sample fixture run through the cleaning pipeline, ready for features."""
    return clean_dataset(raw_sample_df)


def test_add_delay_duration_computes_correct_difference(cleaned_sample_df):
    result = add_delay_duration(cleaned_sample_df)
    # Row 0: delivery=5, expected=4 -> delay_duration = 1
    assert result.loc[0, "delay_duration_hours"] == 1
    # Row 3: delivery=3, expected=4 -> delay_duration = -1 (early)
    assert result.loc[3, "delay_duration_hours"] == -1


def test_add_delay_category_assigns_correct_bins(cleaned_sample_df):
    result = add_delay_duration(cleaned_sample_df)
    result = add_delay_category(result)
    # Row 3: delay_duration = -1 -> on_time_or_early
    assert result.loc[3, "delay_category"] == "on_time_or_early"
    # Row 0: delay_duration = 1 -> mild_delay
    assert result.loc[0, "delay_category"] == "mild_delay"


def test_add_on_time_flag_matches_delayed_column(cleaned_sample_df):
    result = add_on_time_flag(cleaned_sample_df)
    expected = (cleaned_sample_df["delayed"] == "no").astype(int)
    assert result["on_time_flag"].tolist() == expected.tolist()


def test_add_delivery_success_flag_excludes_only_failed(cleaned_sample_df):
    result = add_delivery_success_flag(cleaned_sample_df)
    # Row 2 has delivery_status == 'failed' -> success flag should be 0
    assert result.loc[2, "delivery_success_flag"] == 0
    # Row 0 has delivery_status == 'delivered' -> success flag should be 1
    assert result.loc[0, "delivery_success_flag"] == 1
    # Row 1 has delivery_status == 'delayed' (not failed) -> success flag should be 1
    assert result.loc[1, "delivery_success_flag"] == 1


def test_add_distance_category_covers_all_rows_with_valid_labels(cleaned_sample_df):
    result = add_distance_category(cleaned_sample_df)
    valid_labels = {"short", "medium", "long", "very_long"}
    assert set(result["distance_category"].unique()).issubset(valid_labels)
    assert result["distance_category"].isnull().sum() == 0


def test_add_cost_per_km_computes_correctly(cleaned_sample_df):
    result = add_cost_per_km(cleaned_sample_df)
    # Row 0: cost=300, distance=50 -> cost_per_km = 6.0
    assert result.loc[0, "cost_per_km"] == pytest.approx(6.0)


def test_add_satisfaction_category_assigns_correct_tiers(cleaned_sample_df):
    result = add_satisfaction_category(cleaned_sample_df)
    # Row 0: rating=5 -> excellent
    assert result.loc[0, "satisfaction_category"] == "excellent"
    # Row 2: rating=1 -> poor
    assert result.loc[2, "satisfaction_category"] == "poor"


def test_add_performance_score_requires_flags_and_stays_in_range(cleaned_sample_df):
    result = add_on_time_flag(cleaned_sample_df)
    result = add_delivery_success_flag(result)
    result = add_performance_score(result)
    assert result["performance_score"].between(0, 100).all()
    # Row 0: on_time=1, success=1, rating=5 -> 40 + 30 + 30 = 100
    assert result.loc[0, "performance_score"] == pytest.approx(100.0)
    # Row 2: on_time=0 (delayed=='yes'), success=0 (failed), rating=1 -> 0 + 0 + 6 = 6
    assert result.loc[2, "performance_score"] == pytest.approx(6.0)


def test_engineer_features_full_pipeline_runs_without_error(cleaned_sample_df):
    result = engineer_features(cleaned_sample_df)
    expected_new_columns = {
        "delay_duration_hours", "delay_category", "on_time_flag",
        "delivery_success_flag", "distance_category", "cost_per_km",
        "satisfaction_category", "performance_score",
    }
    assert expected_new_columns.issubset(set(result.columns))
    assert len(result) == len(cleaned_sample_df)


def test_engineer_features_preserves_row_count(cleaned_sample_df):
    result = engineer_features(cleaned_sample_df)
    assert len(result) == len(cleaned_sample_df)
