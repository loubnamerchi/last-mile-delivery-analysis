
import pandas as pd
import numpy as np


def decode_malformed_time_column(series: pd.Series) -> pd.Series:

    def _extract(value):
        try:
            return float(str(value).split(".")[1])
        except (IndexError, ValueError):
            return np.nan

    return series.apply(_extract)


def add_surrogate_key(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()
    df.insert(0, "row_id", range(1, len(df) + 1))
    return df


def validate_logical_consistency(df: pd.DataFrame) -> pd.DataFrame:

    inconsistent = df[
        ((df["delayed"] == "no") & (df["delivery_status"] != "delivered")) |
        ((df["delayed"] == "yes") & (df["delivery_status"] == "delivered"))
    ]
    return inconsistent


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:

    df = add_surrogate_key(df)

    df["delivery_time_hours_clean"] = decode_malformed_time_column(
        df["delivery_time_hours"]
    )
    df["expected_time_hours_clean"] = decode_malformed_time_column(
        df["expected_time_hours"]
    )

    df = df.drop(columns=["delivery_time_hours", "expected_time_hours"])

    return df
