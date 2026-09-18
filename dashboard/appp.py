import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# --- Path setup ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from config.config import PROCESSED_DATA_DIR  # noqa: E402


# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Last-Mile Delivery Intelligence",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Theme / CSS
# ---------------------------------------------------------------------------

PALETTE = {
    "delivered": "#22C55E",
    "delayed": "#F59E0B",
    "failed": "#EF4444",
}

STATUS_ORDER = ["delivered", "delayed", "failed"]

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 15% 5%, rgba(99,102,241,.14), transparent 28%),
            radial-gradient(circle at 90% 10%, rgba(6,182,212,.10), transparent 25%),
            #0B1120;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111827 0%, #0F172A 100%);
        border-right: 1px solid rgba(148,163,184,.12);
    }

    [data-testid="stSidebar"] * {
        color: #E5E7EB;
    }

    .hero {
        padding: 24px 28px;
        border-radius: 22px;
        background: linear-gradient(135deg, rgba(30,41,59,.96), rgba(17,24,39,.90));
        border: 1px solid rgba(129,140,248,.22);
        box-shadow: 0 18px 50px rgba(0,0,0,.22);
        margin-bottom: 22px;
    }

    .hero-title {
        font-size: 31px;
        font-weight: 800;
        color: #F8FAFC;
        margin: 0;
    }

    .hero-subtitle {
        color: #94A3B8;
        margin-top: 7px;
        font-size: 14px;
    }

    .hero-badge {
        display: inline-block;
        margin-top: 15px;
        padding: 6px 11px;
        border-radius: 999px;
        background: rgba(99,102,241,.13);
        border: 1px solid rgba(129,140,248,.25);
        color: #C7D2FE;
        font-size: 12px;
        font-weight: 600;
    }

    .kpi {
        min-height: 135px;
        padding: 19px 20px;
        border-radius: 18px;
        background: rgba(17,24,39,.86);
        border: 1px solid rgba(148,163,184,.13);
        box-shadow: 0 10px 30px rgba(0,0,0,.16);
    }

    .kpi-label {
        color: #94A3B8;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: .06em;
    }

    .kpi-value {
        color: #F8FAFC;
        font-size: 29px;
        font-weight: 800;
        margin-top: 8px;
    }

    .kpi-sub {
        color: #64748B;
        font-size: 11px;
        margin-top: 5px;
    }

    .section-title {
        color: #F8FAFC;
        font-size: 20px;
        font-weight: 750;
        margin-top: 12px;
        margin-bottom: 2px;
    }

    .section-caption {
        color: #64748B;
        font-size: 12px;
        margin-bottom: 12px;
    }

    .insight {
        padding: 17px 18px;
        border-radius: 16px;
        background: linear-gradient(135deg, rgba(30,41,59,.9), rgba(15,23,42,.85));
        border: 1px solid rgba(148,163,184,.13);
        min-height: 122px;
    }

    .insight-title {
        color: #E2E8F0;
        font-size: 13px;
        font-weight: 750;
        margin-bottom: 8px;
    }

    .insight-text {
        color: #94A3B8;
        font-size: 12px;
        line-height: 1.55;
    }

    .risk {
        border-left: 4px solid #F59E0B;
    }

    .success {
        border-left: 4px solid #22C55E;
    }

    .info {
        border-left: 4px solid #6366F1;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        background: rgba(30,41,59,.65);
        border-radius: 12px;
        padding: 10px 17px;
        color: #94A3B8;
        border: 1px solid rgba(148,163,184,.10);
    }

    .stTabs [aria-selected="true"] {
        background: rgba(99,102,241,.18) !important;
        color: #E0E7FF !important;
        border-color: rgba(129,140,248,.35) !important;
    }

    div[data-testid="stMetric"] {
        background: transparent;
    }

    .filter-summary {
        padding: 9px 13px;
        border-radius: 12px;
        background: rgba(99,102,241,.10);
        border: 1px solid rgba(129,140,248,.18);
        color: #C7D2FE;
        font-size: 11px;
        margin-top: 10px;
    }

    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

@st.cache_data
def load_data() -> pd.DataFrame:
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
# Plotly theme
# ---------------------------------------------------------------------------

def style_fig(fig, height=380):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=dict(l=15, r=15, t=45, b=20),
        font=dict(family="Inter", color="#CBD5E1", size=12),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            orientation="h",
            yanchor="bottom",
            y=1.02,
            x=0,
        ),
        hoverlabel=dict(
            bgcolor="#111827",
            font_size=12,
            font_family="Inter",
        ),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            linecolor="rgba(148,163,184,.12)",
        ),
        yaxis=dict(
            gridcolor="rgba(148,163,184,.08)",
            zeroline=False,
        ),
    )
    return fig


# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------

st.sidebar.markdown("## 🎛️ Dashboard Filters")
st.sidebar.caption("Use filters to drill into operational segments.")

def multiselect_filter(label: str, column: str) -> list:
    options = sorted(df[column].dropna().unique().tolist())
    return st.sidebar.multiselect(label, options, default=options, key=f"filter_{column}")


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

st.sidebar.markdown(
    f"""
    <div class="filter-summary">
    <b>{len(filtered_df):,}</b> deliveries selected<br>
    from <b>{len(df):,}</b> total records
    </div>
    """,
    unsafe_allow_html=True,
)

if filtered_df.empty:
    st.warning("No deliveries match the current filters. Adjust the sidebar selections.")
    st.stop()


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown(
    f"""
    <div class="hero">
        <div class="hero-title">🚚 Last-Mile Delivery Intelligence</div>
        <div class="hero-subtitle">
            Interactive operations dashboard for delivery performance,
            risk analysis, and customer outcomes.
        </div>
        <div class="hero-badge">
            LIVE FILTERED VIEW · {len(filtered_df):,} / {len(df):,} DELIVERIES
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# KPI calculations
# ---------------------------------------------------------------------------

total = len(filtered_df)
delivered_rate = (filtered_df["delivery_status"] == "delivered").mean() * 100
delayed_rate = (filtered_df["delivery_status"] == "delayed").mean() * 100
failed_rate = (filtered_df["delivery_status"] == "failed").mean() * 100
avg_time = filtered_df["delivery_time_hours_clean"].mean()
avg_cost = filtered_df["delivery_cost"].mean()
avg_rating = filtered_df["delivery_rating"].mean()


def kpi_card(label, value, subtitle):
    st.markdown(
        f"""
        <div class="kpi">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab_overview, tab_operations, tab_root_cause, tab_customer = st.tabs(
    ["📊 Executive Overview", "🚛 Operations", "🔍 Root Cause", "😊 Customer"]
)


# ---------------------------------------------------------------------------
# Executive Overview
# ---------------------------------------------------------------------------

with tab_overview:

    st.markdown('<div class="section-title">Performance at a Glance</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Key operational indicators for the currently selected population.</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Total Deliveries", f"{total:,}", "Selected volume")
    with c2:
        kpi_card("Delivered", f"{delivered_rate:.1f}%", "Successful deliveries")
    with c3:
        kpi_card("Delayed", f"{delayed_rate:.1f}%", "Delayed deliveries")
    with c4:
        kpi_card("Failed", f"{failed_rate:.1f}%", "Failed deliveries")

    st.write("")

    c5, c6, c7 = st.columns(3)
    with c5:
        kpi_card("Avg. Delivery Time", f"{avg_time:.1f} hrs", "Average delivery duration")
    with c6:
        kpi_card("Avg. Delivery Cost", f"₹{avg_cost:,.2f}", "Average cost per delivery")
    with c7:
        kpi_card("Customer Rating", f"{avg_rating:.2f} / 5", "Average rating")

    st.write("")

    col1, col2 = st.columns([1.05, 1.45])

    with col1:
        st.markdown("#### Delivery Outcome Mix")
        status_counts = (
            filtered_df["delivery_status"]
            .value_counts()
            .reindex(STATUS_ORDER, fill_value=0)
            .reset_index()
        )
        status_counts.columns = ["delivery_status", "count"]

        fig = px.pie(
            status_counts,
            names="delivery_status",
            values="count",
            hole=.68,
            color="delivery_status",
            color_discrete_map=PALETTE,
        )
        fig.update_traces(
            textinfo="percent",
            hovertemplate="<b>%{label}</b><br>%{value:,} deliveries<br>%{percent}<extra></extra>",
        )
        fig.update_layout(showlegend=True)
        style_fig(fig, 380)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Delivery Status Distribution")
        status_counts["percentage"] = status_counts["count"] / total * 100

        fig = px.bar(
            status_counts,
            x="delivery_status",
            y="percentage",
            color="delivery_status",
            color_discrete_map=PALETTE,
            text="percentage",
        )
        fig.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>%{y:.1f}% of deliveries<extra></extra>",
        )
        fig.update_yaxes(title="% of Deliveries", range=[0, max(status_counts["percentage"]) * 1.18])
        fig.update_xaxes(title="")
        fig.update_layout(showlegend=False)
        style_fig(fig, 380)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### 💡 Business Signals")

    i1, i2, i3 = st.columns(3)

    with i1:
        st.markdown(
            """
            <div class="insight risk">
                <div class="insight-title">⚠️ Operational Risk</div>
                <div class="insight-text">
                    Delivery mode is a confirmed statistically significant
                    driver of delivery outcome.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with i2:
        st.markdown(
            """
            <div class="insight info">
                <div class="insight-title">🌦️ Root-Cause Signal</div>
                <div class="insight-text">
                    Weather effects are concentrated particularly in
                    express-mode deliveries.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with i3:
        st.markdown(
            """
            <div class="insight success">
                <div class="insight-title">😊 Customer Impact</div>
                <div class="insight-text">
                    Customer ratings vary with delivery outcome, linking
                    operational performance to customer experience.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# Operations
# ---------------------------------------------------------------------------

with tab_operations:

    st.markdown('<div class="section-title">Operational Performance</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Compare delivery outcomes across operational dimensions.</div>',
        unsafe_allow_html=True,
    )

    st.markdown("#### Delivery Mode Performance")
    st.caption("Confirmed statistically significant driver (p < 0.0001).")

    mode_ct = (
        pd.crosstab(
            filtered_df["delivery_mode"],
            filtered_df["delivery_status"],
            normalize="index",
        )
        .mul(100)
        .reset_index()
        .melt(id_vars="delivery_mode", var_name="status", value_name="pct")
    )

    fig_mode = px.bar(
        mode_ct,
        x="delivery_mode",
        y="pct",
        color="status",
        barmode="stack",
        color_discrete_map=PALETTE,
        category_orders={"status": STATUS_ORDER},
        text_auto=".1f",
    )
    fig_mode.update_traces(
        hovertemplate="<b>%{x}</b><br>%{fullData.name}: %{y:.1f}%<extra></extra>"
    )
    fig_mode.update_yaxes(title="% of Deliveries", range=[0, 100])
    fig_mode.update_xaxes(title="")
    style_fig(fig_mode, 420)
    st.plotly_chart(fig_mode, use_container_width=True)

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### Performance by Region")
        st.caption("Not statistically significant (p = 0.40).")

        region_score = (
            filtered_df.groupby("region")["performance_score"]
            .mean()
            .round(1)
            .sort_values()
            .reset_index()
        )

        fig_region = px.bar(
            region_score,
            x="performance_score",
            y="region",
            orientation="h",
            text="performance_score",
        )
        fig_region.update_traces(
            texttemplate="%{x:.1f}",
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Avg. score: %{x:.1f}<extra></extra>",
        )
        fig_region.update_xaxes(title="Average Performance Score")
        fig_region.update_yaxes(title="")
        style_fig(fig_region, 350)
        st.plotly_chart(fig_region, use_container_width=True)

    with col_b:
        st.markdown("#### Performance by Vehicle Type")
        st.caption("Not statistically significant (p = 0.87).")

        vehicle_score = (
            filtered_df.groupby("vehicle_type")["performance_score"]
            .mean()
            .round(1)
            .sort_values()
            .reset_index()
        )

        fig_vehicle = px.bar(
            vehicle_score,
            x="performance_score",
            y="vehicle_type",
            orientation="h",
            text="performance_score",
        )
        fig_vehicle.update_traces(
            texttemplate="%{x:.1f}",
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Avg. score: %{x:.1f}<extra></extra>",
        )
        fig_vehicle.update_xaxes(title="Average Performance Score")
        fig_vehicle.update_yaxes(title="")
        style_fig(fig_vehicle, 350)
        st.plotly_chart(fig_vehicle, use_container_width=True)

    st.markdown("#### Delivery Partner Performance")
    st.caption("Statistically significant (p = 0.044), but effect size is small.")

    partner_score = (
        filtered_df.groupby("delivery_partner")
        .agg(
            avg_performance_score=("performance_score", "mean"),
            deliveries=("performance_score", "count"),
        )
        .round(1)
        .sort_values("avg_performance_score", ascending=False)
        .reset_index()
    )

    fig_partner = px.bar(
        partner_score,
        x="avg_performance_score",
        y="delivery_partner",
        orientation="h",
        text="avg_performance_score",
        hover_data=["deliveries"],
    )
    fig_partner.update_traces(
        texttemplate="%{x:.1f}",
        textposition="outside",
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Avg. score: %{x:.1f}<br>"
            "Deliveries: %{customdata[0]:,}<extra></extra>"
        ),
    )
    fig_partner.update_xaxes(title="Average Performance Score")
    fig_partner.update_yaxes(title="")
    style_fig(fig_partner, 430)
    st.plotly_chart(fig_partner, use_container_width=True)


# ---------------------------------------------------------------------------
# Root Cause
# ---------------------------------------------------------------------------

with tab_root_cause:

    st.markdown('<div class="section-title">Root-Cause & Risk Analysis</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Explore the interaction between weather and delivery mode.</div>',
        unsafe_allow_html=True,
    )

    st.markdown("#### 🌦️ Weather × Delivery Mode")
    st.caption(
        "The confirmed interaction shows weather-related performance differences "
        "concentrated particularly in express deliveries."
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
        .melt(
            id_vars=["delivery_mode", "weather_condition"],
            var_name="status",
            value_name="pct",
        )
    )

    fig_interaction = px.bar(
        interaction,
        x="weather_condition",
        y="pct",
        color="status",
        facet_col="delivery_mode",
        facet_col_wrap=2,
        barmode="stack",
        color_discrete_map=PALETTE,
        category_orders={"status": STATUS_ORDER},
        text_auto=".1f",
    )
    fig_interaction.update_yaxes(title="% of Deliveries", range=[0, 100])
    fig_interaction.update_xaxes(title="")
    fig_interaction.for_each_annotation(lambda a: a.update(text=a.text.replace("delivery_mode=", "").title()))
    style_fig(fig_interaction, 520)
    st.plotly_chart(fig_interaction, use_container_width=True)

    st.markdown("#### ⚠️ High-Risk Segment")

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
        gap = segment_delivered - baseline_delivered

        r1, r2, r3, r4 = st.columns(4)

        with r1:
            kpi_card("Segment Volume", f"{len(high_risk_df):,}", f"{pct_volume:.1f}% of filtered volume")
        with r2:
            kpi_card("Segment Delivered", f"{segment_delivered:.1f}%", "Express + rainy/stormy")
        with r3:
            kpi_card("Overall Delivered", f"{baseline_delivered:.1f}%", "Current filtered baseline")
        with r4:
            kpi_card("Gap", f"{gap:+.1f} pts", "Segment vs. baseline")


# ---------------------------------------------------------------------------
# Customer
# ---------------------------------------------------------------------------

with tab_customer:

    st.markdown('<div class="section-title">Customer Experience</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Understand how delivery outcomes relate to customer satisfaction.</div>',
        unsafe_allow_html=True,
    )

    col_a, col_b = st.columns([1.35, 1])

    with col_a:
        st.markdown("#### Customer Rating by Delivery Outcome")

        fig_rating = px.box(
            filtered_df,
            x="delivery_status",
            y="delivery_rating",
            color="delivery_status",
            color_discrete_map=PALETTE,
            category_orders={"delivery_status": STATUS_ORDER},
            points="outliers",
        )
        fig_rating.update_yaxes(title="Customer Rating (1–5)", range=[0.8, 5.2])
        fig_rating.update_xaxes(title="")
        fig_rating.update_layout(showlegend=False)
        style_fig(fig_rating, 430)
        st.plotly_chart(fig_rating, use_container_width=True)

    with col_b:
        st.markdown("#### Satisfaction Breakdown")

        sat_counts = (
            filtered_df["satisfaction_category"]
            .value_counts()
            .reset_index()
        )
        sat_counts.columns = ["category", "count"]

        fig_sat = px.pie(
            sat_counts,
            names="category",
            values="count",
            hole=.55,
        )
        fig_sat.update_traces(
            textinfo="percent",
            hovertemplate="<b>%{label}</b><br>%{value:,} customers<br>%{percent}<extra></extra>",
        )
        style_fig(fig_sat, 430)
        st.plotly_chart(fig_sat, use_container_width=True)

    st.markdown("#### ⭐ Average Rating by Weather")

    weather_rating = (
        filtered_df.groupby("weather_condition")["delivery_rating"]
        .mean()
        .round(2)
        .sort_values()
        .reset_index()
    )

    fig_wr = px.bar(
        weather_rating,
        x="delivery_rating",
        y="weather_condition",
        orientation="h",
        text="delivery_rating",
    )
    fig_wr.update_traces(
        texttemplate="%{x:.2f}",
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Avg. rating: %{x:.2f}<extra></extra>",
    )
    fig_wr.update_xaxes(title="Average Customer Rating", range=[0, 5.2])
    fig_wr.update_yaxes(title="")
    style_fig(fig_wr, 380)
    st.plotly_chart(fig_wr, use_container_width=True)


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.divider()
st.caption(
    "Data source: internal delivery logistics dataset (25,000 records). "
    "No date/timestamp field is present, so calendar-based trend analysis "
    "is out of scope for this dashboard."
)
