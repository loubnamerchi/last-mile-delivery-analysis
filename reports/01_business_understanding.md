# Business Understanding & Requirements
## Last-Mile Delivery Operations Analysis

---

## 1. Business Problem

A last-mile delivery company operates across 5 regions using 9 delivery
partners, 6 vehicle types, and 4 delivery modes. Management does not have
a consolidated view of where deliveries fail, what drives delays, which
partners/vehicles underperform, and how these factors relate to cost and
customer satisfaction. This lack of visibility makes it difficult to
prioritize operational fixes.

## 2. Business Context

The dataset represents 25,000 individual delivery records, each capturing
the partner, vehicle, region, weather, package characteristics, timing,
outcome, cost, and customer rating for that delivery. This is
representative of a mid-to-large delivery operation handling mixed
package types (electronics, groceries, pharmacy, furniture, etc.) via
multiple delivery speeds (same day, express, two day, standard).

## 3. Stakeholders

- **Operations Manager** — needs to know which regions/partners/vehicles
  need intervention.
- **Customer Experience team** — needs to understand what drives low
  ratings and failed deliveries.
- **Finance** — needs visibility into cost drivers (distance, vehicle,
  partner) to control delivery cost per order.
- **Delivery Partner Management** — needs partner-level performance
  data to inform contract/volume decisions.

## 4. Business Objectives

- Reduce delivery delays and failures.
- Improve customer satisfaction (delivery_rating).
- Control and optimize delivery cost.
- Identify which partners, vehicles, and regions to invest in or fix.

## 5. Analytical Objectives

- Quantify on-time, delayed, and failed delivery rates overall and by
  segment (region, partner, vehicle, weather, mode).
- Identify statistically meaningful relationships between distance,
  weather, vehicle type, and delivery outcomes.
- Identify drivers of customer rating.
- Identify cost drivers and cost inefficiencies by segment.
- Rank delivery partners and vehicle types by a defined performance
  score.

## 6. Key Business Questions

Each question below is confirmed answerable with existing columns.

| # | Business Question | Supporting Columns |
|---|---|---|
| 1 | What is the overall on-time, delayed, and failed delivery rate? | `delivery_status`, `delayed` |
| 2 | Which regions have the highest delay/failure rates? | `region`, `delivery_status` |
| 3 | Which delivery partners perform best/worst? | `delivery_partner`, `delivery_status`, `delivery_rating`, `delivery_cost` |
| 4 | Which vehicle types are fastest, cheapest, most reliable? | `vehicle_type`, `delivery_time_hours`, `delivery_cost`, `delivery_status` |
| 5 | Does weather affect delays/failures? | `weather_condition`, `delayed`, `delivery_status` |
| 6 | How does distance relate to delivery time and cost? | `distance_km`, `delivery_time_hours`, `delivery_cost` |
| 7 | What drives customer satisfaction (rating)? | `delivery_rating` vs. all operational variables |
| 8 | Which delivery mode (same day/express/two day/standard) has the best performance-to-cost ratio? | `delivery_mode`, `delivery_status`, `delivery_cost` |
| 9 | Does package type/weight affect delay or failure risk? | `package_type`, `package_weight_kg`, `delivery_status` |

**Explicitly out of scope:** daily/weekly/monthly trend analysis and
seasonality — the dataset has no order date or timestamp field, only
duration fields (`delivery_time_hours`, `expected_time_hours`).

**Proposed alternative** for the "Trends" angle: since we cannot analyze
trends over calendar time, we will instead analyze **volume and
performance distribution across delivery_mode and package_type as
operational segments** — this gives management a comparable "which
segment of our business behaves differently" view without inventing
time data that doesn't exist.

## 7. KPIs / Metrics

| KPI | Definition | Source Columns |
|---|---|---|
| On-Time Delivery Rate | % where `delayed == 'no'` and `delivery_status == 'delivered'` | `delayed`, `delivery_status` |
| Delay Rate | % where `delayed == 'yes'` | `delayed` |
| Failed Delivery Rate | % where `delivery_status == 'failed'` | `delivery_status` |
| Average Delivery Time | mean of `delivery_time_hours` (post-cleaning) | `delivery_time_hours` |
| Average Delivery Cost | mean of `delivery_cost` | `delivery_cost` |
| Average Customer Rating | mean of `delivery_rating` | `delivery_rating` |
| Cost per Kilometer | `delivery_cost / distance_km` | `delivery_cost`, `distance_km` |
| Delay Duration | `delivery_time_hours - expected_time_hours` (post-cleaning) | both time columns |

## 8. Expected Deliverables

- Cleaned dataset (`data/processed/`)
- EDA notebook(s) with structured findings
- Engineered feature set supporting the KPIs above
- Business analysis identifying best/worst performers by segment
- Visualizations answering each of the 9 business questions
- Streamlit dashboard for management use
- Findings & recommendations report
- Automated tests for cleaning/KPI logic
- README summarizing the full project

---

## Requirements Gathering

### Business Requirements
- Analysis must produce actionable, segment-level findings (not just
  overall averages).
- Recommendations must be traceable to specific evidence in the data.

### Analytical Requirements
- Use only Python (pandas, numpy, matplotlib, seaborn, plotly,
  scipy/statsmodels where justified).
- No machine learning unless a specific analytical question requires it.
- Statistical claims (e.g. "Region X has more delays") should be
  supported by comparison against the overall baseline, not asserted
  from a single chart alone.

### Data Requirements
- `delivery_time_hours` / `expected_time_hours` must be corrected from
  their malformed timestamp format before any time-based analysis.
- `delivery_id` uniqueness must be verified before using it as a key.

### Success Criteria
- All 9 business questions above are answered with evidence.
- Dashboard allows a manager to filter by region/partner/vehicle and see
  KPI impact.
- Every recommendation follows Finding → Evidence → Business Impact →
  Recommendation structure.

### Constraints
- No external/enrichment data beyond the provided CSV.
- No date/time-based trend analysis (data limitation, see above).

### Assumptions
- `delayed == 'yes'` is the authoritative delay flag; `delivery_status`
  breaks this down further into `delayed` (still completed) vs.
  `failed` (not completed).
- All monetary values in `delivery_cost` are in a single, consistent
  currency (currency unit not specified in the dataset — will be noted
  as a limitation in the final report). 