
import pandas as pd
from pathlib import Path


def load_raw_data(filepath: Path) -> pd.DataFrame:

    if not filepath.exists():
        raise FileNotFoundError(
            f"Raw data file not found at: {filepath}\n"
            "Make sure the dataset is placed in data/raw/."
        )

    df = pd.read_csv(filepath)
    return df


def get_basic_info(df: pd.DataFrame) -> dict:
    
    return {
        "n_rows": df.shape[0],
        "n_columns": df.shape[1],
        "columns": list(df.columns),
    }