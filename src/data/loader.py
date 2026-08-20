"""
Data loading utilities for the last-mile delivery analysis project.
"""

import pandas as pd
from pathlib import Path


def load_raw_data(filepath: Path) -> pd.DataFrame:
    """
    Load the raw delivery logistics dataset from CSV.

    Parameters
    ----------
    filepath : Path
        Path to the raw CSV file.

    Returns
    -------
    pd.DataFrame
        The dataset, loaded as-is (no cleaning applied here).

    Raises
    ------
    FileNotFoundError
        If the file does not exist at the given path.
    """
    if not filepath.exists():
        raise FileNotFoundError(
            f"Raw data file not found at: {filepath}\n"
            "Make sure the dataset is placed in data/raw/."
        )

    df = pd.read_csv(filepath)
    return df


def get_basic_info(df: pd.DataFrame) -> dict:
    """
    Return a small dictionary of basic dataset facts, useful for quick
    sanity checks after loading (not a substitute for full EDA).

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    dict
        Row count, column count, and column names.
    """
    return {
        "n_rows": df.shape[0],
        "n_columns": df.shape[1],
        "columns": list(df.columns),
    }