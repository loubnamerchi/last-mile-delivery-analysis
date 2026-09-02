"""
Tests for src.cleaning.cleaner
"""

import pandas as pd
import numpy as np
import pytest

from src.cleaning.cleaner import (
    decode_malformed_time_column,
    add_surrogate_key,
    validate_logical_consistency,
    clean_dataset,
)


def test_decode_malformed_time_column_extracts_correct_values():
    series = pd.Series([
        "1970-01-01 00:00:00.000000005",
        "1970-01-01 00:00:00.000000012",
    ])
    result = decode_malformed_time_column(series)
    assert result.tolist() == [5.0, 12.0]


def test_decode_malformed_time_column_handles_bad_input_gracefully():
    series = pd.Series(["not_a_valid_value", "1970-01-01 00:00:00.000000007"])
    result = decode_malformed_time_column(series)
    assert np.isnan(result.iloc[0])
    assert result.iloc[1] == 7.0


def test_add_surrogate_key_is_always_unique(raw_sample_df):
    result = add_surrogate_key(raw_sample_df)
    assert result["row_id"].is_unique
    assert result["row_id"].tolist() == list(range(1, len(raw_sample_df) + 1))
    assert "row_id" in result.columns


def test_add_surrogate_key_does_not_mutate_original(raw_sample_df):
    original_columns = raw_sample_df.columns.tolist()
    add_surrogate_key(raw_sample_df)
    assert raw_sample_df.columns.tolist() == original_columns


def test_validate_logical_consistency_finds_no_issues_in_clean_data(raw_sample_df):
    # raw_sample_df is internally consistent: delayed == 'no' -> delivered,
    # delayed == 'yes' -> delayed or failed
    inconsistent = validate_logical_consistency(raw_sample_df)
    assert len(inconsistent) == 0


def test_validate_logical_consistency_flags_real_inconsistency(raw_sample_df):
    broken = raw_sample_df.copy()
    # Introduce an inconsistency: delayed == 'no' but status == 'failed'
    broken.loc[0, "delivery_status"] = "failed"
    inconsistent = validate_logical_consistency(broken)
    assert len(inconsistent) == 1


def test_clean_dataset_preserves_row_count(raw_sample_df):
    cleaned = clean_dataset(raw_sample_df)
    assert len(cleaned) == len(raw_sample_df)


def test_clean_dataset_drops_malformed_columns_and_adds_clean_ones(raw_sample_df):
    cleaned = clean_dataset(raw_sample_df)
    assert "delivery_time_hours" not in cleaned.columns
    assert "expected_time_hours" not in cleaned.columns
    assert "delivery_time_hours_clean" in cleaned.columns
    assert "expected_time_hours_clean" in cleaned.columns
    assert "row_id" in cleaned.columns


def test_clean_dataset_decoded_values_are_numeric(raw_sample_df):
    cleaned = clean_dataset(raw_sample_df)
    assert pd.api.types.is_numeric_dtype(cleaned["delivery_time_hours_clean"])
    assert pd.api.types.is_numeric_dtype(cleaned["expected_time_hours_clean"])
    # Known value from the fixture: first row decodes to 5.0
    assert cleaned.loc[0, "delivery_time_hours_clean"] == 5.0
