"""
Feature engineering for the last-mile delivery dataset.

Every feature below is tied to a specific analytical or business purpose
defined in reports/01_business_understanding.md. Thresholds used for
categorization (distance, delay severity, rating) are derived from the
actual distribution of the cleaned dataset (see
notebooks/05_feature_engineering.ipynb), not arbitrary guesses.

Note: a peak/off-peak indicator was intentionally NOT created. The
dataset has no time-of-day or timestamp field (only duration values),
so there is no basis to classify a delivery as "peak" or "off-peak" --
doing so would require inventing data that doesn't exist.
"""

import pandas as pd
import numpy as np


def add_delay_duration(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add delay_duration_hours = actual delivery time - expected delivery time.

    Positive values mean the delivery took longer than expected (late).
    Negative or zero values mean the delivery arrived at or before the
    expected time.

    Requires df to already contain delivery_time_hours_clean and
    expected_time_hours_clean (see src/cleaning/cleaner.py).
    """
    df = df.copy()
    df["delay_duration_hours"] = (
        df["delivery_time_hours_clean"] - df["expected_time_hours_clean"]
    )
    return df


def add_delay_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Categorize delay_duration_hours into business-relevant severity bands.

    Bands were chosen based on the observed distribution: delayed/failed
    deliveries range from 0 to 12 hours late, so bins split that range
    into roughly even, interpretable severity tiers.
    """
    df = df.copy()

    def _categorize(hours):
        if hours <= 0:
            return "on_time_or_early"
        elif hours <= 2:
            return "mild_delay"
        elif hours <= 6:
            return "moderate_delay"
        else:
            return "severe_delay"

    df["delay_category"] = df["delay_duration_hours"].apply(_categorize)
    return df


def add_on_time_flag(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a binary on_time_flag (1 = not delayed, 0 = delayed).
    Directly derived from the `delayed` column for convenience in
    numeric aggregations (mean of this column = on-time rate).
    """
    df = df.copy()
    df["on_time_flag"] = (df["delayed"] == "no").astype(int)
    return df


def add_delivery_success_flag(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a binary delivery_success_flag (1 = delivered or delayed but
    completed, 0 = failed). This is distinct from on_time_flag: a
    delayed delivery still counts as "successful" here because the
    package did arrive, just late.
    """
    df = df.copy()
    df["delivery_success_flag"] = (df["delivery_status"] != "failed").astype(int)
    return df


def add_distance_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Bin distance_km into quartile-based categories (Short/Medium/Long/
    Very Long). Using the dataset's own quartiles (~76km, ~151km,
    ~225km) rather than arbitrary round numbers keeps each category
    populated with a comparable number of deliveries.
    """
    df = df.copy()
    q1, q2, q3 = df["distance_km"].quantile([0.25, 0.5, 0.75])

    def _categorize(km):
        if km <= q1:
            return "short"
        elif km <= q2:
            return "medium"
        elif km <= q3:
            return "long"
        else:
            return "very_long"

    df["distance_category"] = df["distance_km"].apply(_categorize)
    return df


def add_cost_per_km(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add cost_per_km = delivery_cost / distance_km.

    A direct operational efficiency metric: how much each kilometer of
    delivery costs, useful for comparing partners/vehicles/modes on a
    distance-normalized basis rather than raw cost.
    """
    df = df.copy()
    df["cost_per_km"] = df["delivery_cost"] / df["distance_km"]
    return df


def add_satisfaction_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Bin delivery_rating (1-5) into interpretable satisfaction tiers.
    """
    df = df.copy()

    def _categorize(rating):
        if rating <= 2:
            return "poor"
        elif rating == 3:
            return "average"
        elif rating == 4:
            return "good"
        else:
            return "excellent"

    df["satisfaction_category"] = df["delivery_rating"].apply(_categorize)
    return df


def add_performance_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a composite performance_score (0-100) combining three signals:

    - on_time_flag (40 points): did it arrive on time?
    - delivery_success_flag (30 points): did it arrive at all?
    - normalized rating (30 points): how satisfied was the customer?

    Weights reflect that failure (0 points if failed) is the most
    severe outcome, followed by lateness, with customer rating as a
    confirming signal rather than the primary driver -- this avoids
    double-counting, since rating is already strongly correlated with
    on-time/success status (see EDA Section 7).

    Requires on_time_flag and delivery_success_flag to already exist
    (run add_on_time_flag and add_delivery_success_flag first).
    """
    df = df.copy()
    df["performance_score"] = (
        df["on_time_flag"] * 40
        + df["delivery_success_flag"] * 30
        + (df["delivery_rating"] / 5) * 30
    ).round(1)
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run the full feature engineering pipeline in the correct order
    (some features depend on others being present first).

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned dataset (output of src.cleaning.cleaner.clean_dataset).

    Returns
    -------
    pd.DataFrame
        Dataset with all engineered features added.
    """
    df = add_delay_duration(df)
    df = add_delay_category(df)
    df = add_on_time_flag(df)
    df = add_delivery_success_flag(df)
    df = add_distance_category(df)
    df = add_cost_per_km(df)
    df = add_satisfaction_category(df)
    df = add_performance_score(df)  # must run after on_time_flag & success_flag
    return df
