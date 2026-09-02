"""
Streamlit dashboard for the Last-Mile Delivery Operations Analysis.

Run from the project root with:
    streamlit run dashboard/app.py

Sections:
- Executive Overview: headline KPIs
- Operations: region / partner / vehicle / weather / mode breakdowns
- Root Cause: the weather x delivery_mode interaction and high-risk segment
- Customer: satisfaction and rating analysis

Design note: region, delivery_partner, vehicle_type, and package_type
were found NOT to be statistically significant drivers of delivery
outcome (see notebooks/06_business_analysis.ipynb). They remain
available here as filters for operational monitoring, but the dashboard
does not claim these differences are meaningful -- only weather_condition
and delivery_mode are flagged as confirmed drivers.
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# --- Path setup so this app can import config/ and src/ regardless of
# --- the working directory Streamlit was launched from.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from config.config import PROCESSED_DATA_DIR  # noqa: E402

PALETTE = {"delivered": "#2E7D32", "delayed": "#F9A825", "failed": "#C62828"}

st.set_page_config(
    page_title="Last-Mile Delivery Operations Dashboard",
    page_icon="🚚",
    layout="wide",
)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

@st.cache_data
def load_data() -> pd.DataFrame:
    """Load the final feature-engineered dataset produced in Step 8."""
    path = PROCESSED_DATA_DIR / "delivery_logistics_features.csv"
    if not path.exists():
        st.error(
            f"Could not find {path}. Run notebooks 03-05 first to "
            "produce the cleaned, feature-engineered dataset."
        )
        st.stop()
    return pd.read_csv(path)


df = load_data()


# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------

st.sidebar.title("Filters")
st.sidebar.caption(
    "Region, partner, and vehicle filters are provided for operational "
    "drill-down, but Business Analysis found no statistically significant "
    "difference between their categories."
)

def multiselect_filter(label: str, column: str) -> list:
    options = sorted(df[column].dropna().unique().tolist())
    return st.sidebar.multiselect(label, options, default=options)

selected_regions = multiselect_filter("Region", "region")
selected_partners = multiselect_filter("Delivery Partner", "delivery_partner")
selected_vehicles = multiselect_filter("Vehicle Type", "vehicle_type")
selected_weather = multiselect_filter("Weather Condition", "weather_condition")
selected_modes = multiselect_filter("Delivery Mode", "delivery_mode")

filtered_df = df[
    df["region"].isin(selected_regions)
    & df["delivery_partner"].isin(selected_partners)
    & df["vehicle_type"].isin(selected_vehicles)
    & df["weather_condition"].isin(selected_weather)
    & df["delivery_mode"].isin(selected_modes)
]

if filtered_df.empty:
    st.warning("No deliveries match the current filter selection. Adjust filters in the sidebar.")
    st.stop()


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.title("🚚 Last-Mile Delivery Operations Dashboard")
st.caption(
    f"Showing {len(filtered_df):,} of {len(df):,} deliveries based on current filters."
)

tab_overview, tab_operations, tab_root_cause, tab_customer = st.tabs(
    ["📊 Executive Overview", "🚛 Operations", "🔍 Root Cause", "😊 Customer"]
)


# ---------------------------------------------------------------------------
# Tab 1 -- Executive Overview
# ---------------------------------------------------------------------------

with tab_overview:
    st.subheader("Headline KPIs")

    total = len(filtered_df)
    on_time_rate = (filtered_df["delivery_status"] == "delivered").mean() * 100
    delayed_rate = (filtered_df["delivery_status"] == "delayed").mean() * 100
    failed_rate = (filtered_df["delivery_status"] == "failed").mean() * 100
    avg_time = filtered_df["delivery_time_hours_clean"].mean()
    avg_cost = filtered_df["delivery_cost"].mean()
    avg_rating = filtered_df["delivery_rating"].mean()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Deliveries", f"{total:,}")
    c2.metric("On-Time Rate", f"{on_time_rate:.1f}%")
    c3.metric("Delayed Rate", f"{delayed_rate:.1f}%")
    c4.metric("Failed Rate", f"{failed_rate:.1f}%")

    c5, c6, c7 = st.columns(3)
    c5.metric("Avg. Delivery Time", f"{avg_time:.1f} hrs")
    c6.metric("Avg. Delivery Cost", f"₹{avg_cost:,.2f}")
    c7.metric("Avg. Customer Rating", f"{avg_rating:.2f} / 5")

    st.divider()
    st.subheader("Overall Delivery Status Distribution")

    status_counts = (
        filtered_df["delivery_status"].value_counts(normalize=True).mul(100).round(1).reset_index()
    )
    status_counts.columns = ["delivery_status", "percentage"]

    fig = px.bar(
        status_counts, x="delivery_status", y="percentage", color="delivery_status",
        color_discrete_map=PALETTE, text="percentage",
        labels={"percentage": "% of Deliveries", "delivery_status": "Status"},
    )
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------------------
# Tab 2 -- Operations
# ---------------------------------------------------------------------------

with tab_operations:
    st.subheader("Performance by Delivery Mode")
    st.caption("Confirmed statistically significant driver (p < 0.0001).")

    mode_ct = pd.crosstab(filtered_df["delivery_mode"], filtered_df["delivery_status"], normalize="index").mul(100).round(1)
    mode_ct = mode_ct.reset_index().melt(id_vars="delivery_mode", var_name="status", value_name="pct")
    fig_mode = px.bar(
        mode_ct, x="delivery_mode", y="pct", color="status", barmode="group",
        color_discrete_map=PALETTE,
        labels={"pct": "% of Deliveries", "delivery_mode": "Delivery Mode", "status": "Outcome"},
    )
    st.plotly_chart(fig_mode, use_container_width=True)

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Performance Score by Region")
        st.caption("Not statistically significant (p = 0.40) -- shown for completeness.")
        region_score = filtered_df.groupby("region")["performance_score"].mean().round(1).sort_values(ascending=False)
        fig_region = px.bar(
            region_score, orientation="h",
            labels={"value": "Avg. Performance Score", "region": "Region"},
        )
        fig_region.update_layout(showlegend=False)
        st.plotly_chart(fig_region, use_container_width=True)

    with col_b:
        st.subheader("Performance Score by Vehicle Type")
        st.caption("Not statistically significant (p = 0.87) -- shown for completeness.")
        vehicle_score = filtered_df.groupby("vehicle_type")["performance_score"].mean().round(1).sort_values(ascending=False)
        fig_vehicle = px.bar(
            vehicle_score, orientation="h",
            labels={"value": "Avg. Performance Score", "vehicle_type": "Vehicle Type"},
        )
        fig_vehicle.update_layout(showlegend=False)
        st.plotly_chart(fig_vehicle, use_container_width=True)

    st.subheader("Delivery Partner Ranking")
    st.caption("Statistically significant (p = 0.044) but small effect size -- differences are minor.")
    partner_score = (
        filtered_df.groupby("delivery_partner")
        .agg(avg_performance_score=("performance_score", "mean"), deliveries=("performance_score", "count"))
        .round(1)
        .sort_values("avg_performance_score", ascending=False)
    )
    st.dataframe(partner_score, use_container_width=True)


# ---------------------------------------------------------------------------
# Tab 3 -- Root Cause (Weather x Mode)
# ---------------------------------------------------------------------------

with tab_root_cause:
    st.subheader("Weather x Delivery Mode: Where Failures Concentrate")
    st.caption(
        "The two confirmed statistically significant drivers interact: weather's "
        "damage is concentrated almost entirely in express-mode deliveries."
    )

    interaction = (
        pd.crosstab(
            [filtered_df["delivery_mode"], filtered_df["weather_condition"]],
            filtered_df["delivery_status"],
            normalize="index",
        )
        .mul(100)
        .round(1)
        .reset_index()
        .melt(id_vars=["delivery_mode", "weather_condition"], var_name="status", value_name="pct")
    )

    fig_interaction = px.bar(
        interaction, x="weather_condition", y="pct", color="status",
        facet_col="delivery_mode", facet_col_wrap=2,
        color_discrete_map=PALETTE,
        labels={"pct": "% of Deliveries", "weather_condition": "Weather", "status": "Outcome"},
    )
    st.plotly_chart(fig_interaction, use_container_width=True)

    st.divider()
    st.subheader("High-Risk Segment: Express + Rainy/Stormy Weather")

    high_risk_mask = (
        filtered_df["delivery_mode"].eq("express")
        & filtered_df["weather_condition"].isin(["rainy", "stormy"])
    )
    high_risk_df = filtered_df[high_risk_mask]

    if len(high_risk_df) == 0:
        st.info("No deliveries in the express + rainy/stormy segment under the current filters.")
    else:
        pct_volume = len(high_risk_df) / len(filtered_df) * 100
        segment_delivered = (high_risk_df["delivery_status"] == "delivered").mean() * 100
        baseline_delivered = (filtered_df["delivery_status"] == "delivered").mean() * 100

        c1, c2, c3 = st.columns(3)
        c1.metric("Segment Size", f"{len(high_risk_df):,} deliveries", f"{pct_volume:.1f}% of filtered volume")
        c2.metric("Segment On-Time Rate", f"{segment_delivered:.1f}%")
        c3.metric("Overall On-Time Rate", f"{baseline_delivered:.1f}%", delta=f"{segment_delivered - baseline_delivered:.1f} pts")


# ---------------------------------------------------------------------------
# Tab 4 -- Customer
# ---------------------------------------------------------------------------

with tab_customer:
    st.subheader("Customer Rating by Delivery Outcome")
    st.caption("Rating tracks outcome closely -- the clearest downstream consequence of delays/failures.")

    fig_rating = px.box(
        filtered_df, x="delivery_status", y="delivery_rating", color="delivery_status",
        color_discrete_map=PALETTE,
        labels={"delivery_rating": "Customer Rating (1-5)", "delivery_status": "Delivery Status"},
    )
    fig_rating.update_layout(showlegend=False)
    st.plotly_chart(fig_rating, use_container_width=True)

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Satisfaction Category Breakdown")
        sat_counts = filtered_df["satisfaction_category"].value_counts(normalize=True).mul(100).round(1)
        fig_sat = px.pie(
            values=sat_counts.values, names=sat_counts.index,
            title="Poor / Average / Good / Excellent",
        )
        st.plotly_chart(fig_sat, use_container_width=True)

    with col_b:
        st.subheader("Avg. Rating by Weather Condition")
        weather_rating = filtered_df.groupby("weather_condition")["delivery_rating"].mean().round(2).sort_values()
        fig_wr = px.bar(
            weather_rating, orientation="h",
            labels={"value": "Avg. Rating", "weather_condition": "Weather"},
        )
        fig_wr.update_layout(showlegend=False)
        st.plotly_chart(fig_wr, use_container_width=True)


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.divider()
st.caption(
    "Data source: internal delivery logistics dataset (25,000 records). "
    "No date/timestamp field is present, so calendar-based trend analysis "
    "is out of scope for this dashboard -- see reports/01_business_understanding.md."
)
