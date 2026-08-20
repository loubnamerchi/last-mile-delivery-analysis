"""
Project-wide configuration: paths used across notebooks and src modules.
Using a config file avoids hardcoded absolute paths scattered through the codebase.
"""

from pathlib import Path

# Project root = parent of the config/ folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Data paths
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
EXTERNAL_DATA_DIR = PROJECT_ROOT / "data" / "external"

RAW_DATA_FILE = RAW_DATA_DIR / "Delivery_Logistics.csv"
PROCESSED_DATA_FILE = PROCESSED_DATA_DIR / "delivery_logistics_clean.csv"

# Output paths
FIGURES_DIR = PROJECT_ROOT / "figures"
REPORTS_DIR = PROJECT_ROOT / "reports"