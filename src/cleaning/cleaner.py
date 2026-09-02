"""
Cleaning functions for the last-mile delivery dataset.
Every function here fixes a specific, documented issue found during
Data Understanding (see notebooks/02_data_understanding.ipynb).
"""

import pandas as pd
import numpy as np


def decode_malformed_time_column(series: pd.Series) -> pd.Series:
    """
    Decode the malformed timestamp strings in `delivery_time_hours` and
    `expected_time_hours` into real numeric hour values.

    The raw values look like '1970-01-01 00:00:00.000000008'. The digits
    after the decimal point represent the actual hour value. This was
    validated in Data Understanding by checking correlation with
    distance_km (~0.69) and delivery_cost (~0.68), which confirmed the
    decoded values behave like genuine delivery durations rather than
    noise.

    Parameters
    ----------
    series : pd.Series
        Raw string column (e.g. df['delivery_time_hours']).

    Returns
    -------
    pd.Series
        Numeric hour values (float).
    """
    def _extract(value):
        try:
            return float(str(value).split(".")[1])
        except (IndexError, ValueError):
            return np.nan

    return series.apply(_extract)


def add_surrogate_key(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a reliable unique row identifier.

    `delivery_id` is unreliable: it is stored as a float rounded to 2
    decimals, causing 500 rows to collide onto a shared value despite
    representing distinct deliveries (confirmed in Data Understanding).
    Rather than dropping `delivery_id` (it may still carry business
    meaning), we add a guaranteed-unique `row_id` for internal use in
    joins, tests, and traceability.

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
        Copy of df with a new leading `row_id` column.
    """
    df = df.copy()
    df.insert(0, "row_id", range(1, len(df) + 1))
    return df


def validate_logical_consistency(df: pd.DataFrame) -> pd.DataFrame:
    """
    Flag rows where `delayed` and `delivery_status` are logically
    inconsistent (e.g. delayed == 'no' but delivery_status == 'failed').

    This does not remove rows -- it returns only the inconsistent subset
    so it can be inspected before deciding what to do with it.

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
        Subset of rows with inconsistent delayed/delivery_status values.
    """
    inconsistent = df[
        ((df["delayed"] == "no") & (df["delivery_status"] != "delivered")) |
        ((df["delayed"] == "yes") & (df["delivery_status"] == "delivered"))
    ]
    return inconsistent


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run the full cleaning pipeline on the raw dataset.

    Steps:
    1. Add a reliable surrogate key (row_id).
    2. Decode delivery_time_hours and expected_time_hours into numeric hours.
    3. Drop the original malformed time columns, keep decoded versions.

    Parameters
    ----------
    df : pd.DataFrame
        Raw dataset as loaded by src.data.loader.load_raw_data.

    Returns
    -------
    pd.DataFrame
        Cleaned, analysis-ready dataset.
    """
    df = add_surrogate_key(df)

    df["delivery_time_hours_clean"] = decode_malformed_time_column(
        df["delivery_time_hours"]
    )
    df["expected_time_hours_clean"] = decode_malformed_time_column(
        df["expected_time_hours"]
    )

    df = df.drop(columns=["delivery_time_hours", "expected_time_hours"])

    return df
