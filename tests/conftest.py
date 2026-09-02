"""
Shared pytest fixtures for the last-mile delivery test suite.
"""

import pandas as pd
import pytest


@pytest.fixture
def raw_sample_df() -> pd.DataFrame:
    """
    A small, hand-built sample mirroring the real dataset's schema and
    known quirks: malformed time columns, a duplicated delivery_id, and
    both delayed/failed/delivered statuses represented.
    """
    return pd.DataFrame({
        "delivery_id": [100.11, 100.11, 200.22, 300.33, 400.44],
        "delivery_partner": ["Delhivery", "Blue Dart", "Delhivery", "Xpressbees", "Blue Dart"],
        "package_type": ["electronics", "groceries", "pharmacy", "furniture", "electronics"],
        "vehicle_type": ["bike", "van", "truck", "van", "bike"],
        "delivery_mode": ["express", "standard", "same day", "two day", "express"],
        "region": ["North", "South", "East", "West", "North"],
        "weather_condition": ["clear", "rainy", "stormy", "clear", "foggy"],
        "distance_km": [50.0, 120.5, 200.0, 30.0, 80.0],
        "package_weight_kg": [2.5, 10.0, 5.5, 20.0, 1.2],
        "delivery_time_hours": [
            "1970-01-01 00:00:00.000000005",
            "1970-01-01 00:00:00.000000008",
            "1970-01-01 00:00:00.000000012",
            "1970-01-01 00:00:00.000000003",
            "1970-01-01 00:00:00.000000006",
        ],
        "expected_time_hours": [
            "1970-01-01 00:00:00.000000004",
            "1970-01-01 00:00:00.000000006",
            "1970-01-01 00:00:00.000000006",
            "1970-01-01 00:00:00.000000004",
            "1970-01-01 00:00:00.000000005",
        ],
        "delayed": ["no", "yes", "yes", "no", "yes"],
        "delivery_status": ["delivered", "delayed", "failed", "delivered", "delayed"],
        "delivery_rating": [5, 3, 1, 5, 2],
        "delivery_cost": [300.0, 650.0, 950.0, 180.0, 420.0],
    })
