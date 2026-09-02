# Last-Mile Delivery Operations Analysis

A complete, portfolio-ready Data Analyst project investigating delivery
performance, delays, failures, and customer satisfaction for a
last-mile delivery operation — built entirely in Python, following a
professional end-to-end analytics workflow from business understanding
through statistical business analysis, visualization, and an
interactive dashboard.

---

## Business Problem

A last-mile delivery company lacked a consolidated, evidence-based view
of where and why deliveries fail, and which operational factors (region,
partner, vehicle, weather, delivery mode) actually drive performance.
This project investigates 25,000 real delivery records to separate real
operational levers from noise, and delivers prioritized, statistically
validated recommendations.

## Key Findings

- **73.3%** of deliveries arrive on time, **21.4%** are delayed, **5.3%** fail.
- Chi-square testing confirms only **delivery mode** (p < 0.0001) and
  **weather condition** (p < 0.0001) are statistically significant
  drivers of delivery outcome — region, vehicle type, and package type
  showed **no significant effect**.
- **Express delivery is unreliable even in clear weather** (48.4%
  on-time) and **collapses in storms** (0.2% on-time).
- A single segment — **express deliveries in rainy/stormy weather** —
  is 8.3% of volume but only **1.3%** delivered.
- Customer rating tracks outcome closely: **4.21/5** (delivered) →
  **2.40/5** (delayed) → **1.31/5** (failed).
- Cost is driven almost entirely by distance (r ≈ 0.99), not by
  partner or vehicle choice.

Full detail in [`reports/03_full_analytical_report.md`](reports/03_full_analytical_report.md)
and [`reports/02_insights_and_recommendations.md`](reports/02_insights_and_recommendations.md).

## Objectives

- Quantify on-time, delayed, and failed delivery rates overall and by segment.
- Identify statistically valid (not just visually apparent) drivers of delivery outcome.
- Identify root causes behind poor performance through interaction analysis.
- Quantify the customer satisfaction and cost impact of operational problems.
- Deliver management-ready, evidence-backed recommendations.

## Dataset

- 25,000 delivery records, 15 raw columns.
- Fields: delivery partner, package type, vehicle type, delivery mode,
  region, weather condition, distance, package weight, delivery time,
  expected time, delayed flag, delivery status, customer rating, delivery cost.
- **Limitation:** no date/timestamp field — trend and seasonality
  analysis were out of scope for this project (documented in
  `reports/01_business_understanding.md`).

## Technologies

- Python 3.9+
- pandas, numpy — data manipulation
- matplotlib, seaborn, plotly — visualization
- scipy, statsmodels — statistical testing
- Jupyter — exploratory notebooks
- Streamlit — interactive dashboard
- pytest — automated testing

No SQL, Excel, Power BI, or Tableau were used — this project
demonstrates a complete analytics workflow in pure Python.

## Project Structure

```text
last-mile-delivery-analysis/
│
├── data/
│   ├── raw/                 # Original, untouched dataset
│   ├── processed/           # Cleaned + feature-engineered dataset
│   └── external/
│
├── notebooks/
│   ├── 01_initial_inspection.ipynb
│   ├── 02_data_understanding.ipynb
│   ├── 03_data_cleaning.ipynb
│   ├── 04_eda.ipynb
│   ├── 05_feature_engineering.ipynb
│   ├── 06_business_analysis.ipynb
│   └── 07_visualization.ipynb
│
├── src/
│   ├── data/loader.py
│   ├── cleaning/cleaner.py
│   ├── analysis/
│   │   ├── features.py
│   │   └── business_analysis.py
│   └── visualization/charts.py
│
├── config/config.py           # Centralized paths, no hardcoding
├── dashboard/app.py           # Streamlit dashboard
├── reports/
│   ├── 01_business_understanding.md
│   ├── 02_insights_and_recommendations.md
│   └── 03_full_analytical_report.md
├── figures/                   # Saved chart images
├── tests/                     # 31 pytest tests
├── requirements.txt
├── main.py                    # Reproducible pipeline entry point
└── .gitignore
```

## Workflow

1. **Business Understanding** — problem, objectives, 9 answerable business questions, KPIs
2. **Data Understanding** — structure, quality issues, cardinality, distributions
3. **Data Cleaning** — evidence-based fixes (malformed time columns, unreliable ID)
4. **EDA** — segment-by-segment breakdown of delivery outcome
5. **Feature Engineering** — 8 derived variables, each with a stated purpose
6. **Business Analysis** — chi-square significance testing, interaction/root-cause analysis
7. **Visualization** — 7 figures mapped directly to business questions
8. **Dashboard** — interactive Streamlit app for management use
9. **Testing** — 31 automated tests validating cleaning, features, and analysis logic

## KPIs

| KPI | Value |
|---|---|
| On-time delivery rate | 73.3% |
| Delayed rate | 21.4% |
| Failed delivery rate | 5.3% |
| Average delivery time | ~6.2 hours |
| Average delivery cost | ~864.9 |
| Average customer rating | 3.67 / 5 (overall) |

## Dashboard

Run the interactive management dashboard:

```bash
streamlit run dashboard/app.py
```

4 sections: Executive Overview, Operations, Root Cause (weather × mode
interaction), and Customer — with live filters across region, partner,
vehicle, weather, and mode.

## Recommendations

1. Redesign express-mode SLA with realistic time buffers.
2. Build a weather-contingent handling rule for express orders.
3. Use standard-mode routing/buffer logic as the benchmark for the redesign.
4. Deprioritize region/partner/vehicle-focused initiatives — not supported by the data.
5. Monitor the high-risk segment's volume as a customer-satisfaction early-warning signal.

Full Finding → Evidence → Business Impact → Recommendation detail in
[`reports/02_insights_and_recommendations.md`](reports/02_insights_and_recommendations.md).

## How to Run This Project

**1. Clone and set up the environment**

```powershell
git clone <your-repo-url>
cd last-mile-delivery-analysis
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**2. Place the dataset**

Put the source CSV at `data/raw/Delivery_Logistics.csv`.

**3. Run the reproducible pipeline**

```powershell
python main.py
```

This loads, validates, cleans, and feature-engineers the data, saving
the final dataset to `data/processed/delivery_logistics_features.csv`
and printing a KPI summary.

**4. Explore the analysis**

Open the notebooks in `notebooks/` in order (01 → 07) for the full
exploratory, statistical, and visual analysis.

**5. Launch the dashboard**

```powershell
streamlit run dashboard/app.py
```

**6. Run the tests**

```powershell
pytest tests/ -v
```

## Limitations

- No cost-of-failure data (redelivery, refunds, support volume) —
  business impact of the high-risk segment is inferred, not directly measured.
- No date/timestamp field — no trend, seasonality, or time-of-day analysis.
- Currency unit for delivery cost is unspecified in the source data.
- Findings are correlational/associational, not from a controlled
  experiment — recommendations should be validated with a pilot before
  full rollout.