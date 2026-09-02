"""
Main entry point for the Last-Mile Delivery Operations Analysis.

Runs the full reproducible pipeline: load raw data -> clean -> engineer
features -> save the final processed dataset -> print a summary of key
KPIs. This is the same logic developed interactively across
notebooks 03-05, consolidated here so the whole project can be
reproduced with a single command:

    python main.py

Exploratory analysis, business analysis, and visualization remain in
their respective notebooks (04-07) since those are exploration and
interpretation steps, not part of the repeatable data pipeline.
"""

import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from config.config import RAW_DATA_FILE, PROCESSED_DATA_DIR
from src.data.loader import load_raw_data
from src.cleaning.cleaner import clean_dataset, validate_logical_consistency
from src.analysis.features import engineer_features

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def run_pipeline() -> None:
    """Execute the full data pipeline and print a KPI summary."""
    logger.info("Starting Last-Mile Delivery Operations pipeline")

    # 1. Load
    logger.info("Loading raw data from %s", RAW_DATA_FILE)
    try:
        df_raw = load_raw_data(RAW_DATA_FILE)
    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)
    logger.info("Loaded %d rows, %d columns", *df_raw.shape)

    # 2. Validate before cleaning
    inconsistent = validate_logical_consistency(df_raw)
    if len(inconsistent) > 0:
        logger.warning(
            "%d rows have inconsistent delayed/delivery_status values "
            "-- review before trusting downstream KPIs",
            len(inconsistent),
        )
    else:
        logger.info("Logical consistency check passed: 0 inconsistent rows")

    # 3. Clean
    logger.info("Cleaning dataset")
    df_clean = clean_dataset(df_raw)
    assert len(df_clean) == len(df_raw), "Row count changed during cleaning!"
    logger.info("Cleaning complete: %d rows, %d columns", *df_clean.shape)

    # 4. Engineer features
    logger.info("Engineering features")
    df_final = engineer_features(df_clean)
    logger.info("Feature engineering complete: %d rows, %d columns", *df_final.shape)

    # 5. Save
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_path = PROCESSED_DATA_DIR / "delivery_logistics_features.csv"
    df_final.to_csv(output_path, index=False)
    logger.info("Saved final dataset to %s", output_path)

    # 6. KPI summary
    print_kpi_summary(df_final)

    logger.info("Pipeline complete. Run the notebooks in notebooks/ for full "
                "EDA, business analysis, and visualization, or launch the "
                "dashboard with: streamlit run dashboard/app.py")


def print_kpi_summary(df) -> None:
    """Print the headline KPIs to the console."""
    total = len(df)
    on_time_rate = (df["delivery_status"] == "delivered").mean() * 100
    delayed_rate = (df["delivery_status"] == "delayed").mean() * 100
    failed_rate = (df["delivery_status"] == "failed").mean() * 100
    avg_time = df["delivery_time_hours_clean"].mean()
    avg_cost = df["delivery_cost"].mean()
    avg_rating = df["delivery_rating"].mean()

    print("\n" + "=" * 50)
    print("KPI SUMMARY")
    print("=" * 50)
    print(f"Total deliveries:        {total:,}")
    print(f"On-time delivery rate:   {on_time_rate:.1f}%")
    print(f"Delayed rate:            {delayed_rate:.1f}%")
    print(f"Failed delivery rate:    {failed_rate:.1f}%")
    print(f"Average delivery time:   {avg_time:.2f} hours")
    print(f"Average delivery cost:   {avg_cost:,.2f}")
    print(f"Average customer rating: {avg_rating:.2f} / 5")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    run_pipeline()