
import pandas as pd
import numpy as np


def add_delay_duration(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()
    df["delay_duration_hours"] = (
        df["delivery_time_hours_clean"] - df["expected_time_hours_clean"]
    )
    return df


def add_delay_category(df: pd.DataFrame) -> pd.DataFrame:

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

    df = df.copy()
    df["on_time_flag"] = (df["delayed"] == "no").astype(int)
    return df


def add_delivery_success_flag(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()
    df["delivery_success_flag"] = (df["delivery_status"] != "failed").astype(int)
    return df


def add_distance_category(df: pd.DataFrame) -> pd.DataFrame:

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

    df = df.copy()
    df["cost_per_km"] = df["delivery_cost"] / df["distance_km"]
    return df


def add_satisfaction_category(df: pd.DataFrame) -> pd.DataFrame:

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

    df = df.copy()
    df["performance_score"] = (
        df["on_time_flag"] * 40
        + df["delivery_success_flag"] * 30
        + (df["delivery_rating"] / 5) * 30
    ).round(1)
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:

    df = add_delay_duration(df)
    df = add_delay_category(df)
    df = add_on_time_flag(df)
    df = add_delivery_success_flag(df)
    df = add_distance_category(df)
    df = add_cost_per_km(df)
    df = add_satisfaction_category(df)
    df = add_performance_score(df)  # must run after on_time_flag & success_flag
    return df
