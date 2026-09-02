# Last-Mile Delivery Operations Analysis
## Full Analytical Report

---

## 1. Executive Summary

This project analyzed 25,000 individual delivery records from a
last-mile delivery operation spanning 5 regions, 9 delivery partners,
6 vehicle types, and 4 delivery modes. The goal was to identify what
actually drives delivery delays, failures, and customer dissatisfaction,
and to separate real operational levers from noise.

**Headline result:** company-wide, **73.3%** of deliveries arrive on
time, **21.4%** are delayed, and **5.3%** fail. Statistical testing
found that only **delivery mode** and **weather condition** are
meaningfully associated with delivery outcome — region, vehicle type,
and package type showed no statistically significant effect at all.
The two confirmed drivers interact sharply: **express-mode deliveries
are unreliable even in clear weather (48.4% on-time)** and **collapse
almost entirely during storms (0.2% on-time)**. A single, well-defined
segment — express deliveries in rainy or stormy weather — makes up
8.3% of volume but has a delivered rate of just 1.3%. Five prioritized
recommendations are detailed in Section 10.

---

## 2. Business Problem

A last-mile delivery company lacked a consolidated, evidence-based view
of where and why deliveries fail, which factors actually drive delays,
and how these problems affect cost and customer satisfaction. Prior
assumptions (that region or specific partners might be underperforming)
had not been formally tested against the data. This analysis was
commissioned to identify true root causes and provide management with
prioritized, defensible recommendations rather than intuition-driven
guesses.

---

## 3. Dataset

| Attribute | Value |
|---|---|
| Source | Internal delivery logistics export |
| File format | CSV |
| Records | 25,000 |
| Variables | 15 (raw) |
| Data period | Not available — no date/timestamp field |
| Categorical fields | delivery_partner (9), package_type (9), vehicle_type (6), delivery_mode (4), region (5), weather_condition (6), delayed (2), delivery_status (3) |
| Numerical fields | distance_km, package_weight_kg, delivery_rating, delivery_cost |

**Key limitation:** the dataset contains no date or timestamp field —
only duration values (`delivery_time_hours`, `expected_time_hours`).
Calendar-based trend, seasonality, and time-of-day analysis were
therefore out of scope for this entire project (documented at project
start, Step 4).

---

## 4. Data Quality

Two real data quality issues were identified and corrected (Steps 5–6):

1. **`delivery_id` is not a reliable unique key.** Stored as a float
   rounded to 2 decimals, causing 500 of 25,000 rows to share a
   `delivery_id` with another row despite representing distinct
   deliveries. A guaranteed-unique `row_id` was added; `delivery_id`
   was retained but never used as a key.

2. **`delivery_time_hours` and `expected_time_hours` were malformed.**
   Both were stored as broken timestamp strings
   (`1970-01-01 00:00:00.000000008`) instead of numeric hours. The
   digits after the decimal point were confirmed (via correlation with
   distance and cost, ~0.69 and ~0.68 respectively) to represent real
   duration values, and were decoded into
   `delivery_time_hours_clean` / `expected_time_hours_clean`.

No missing values and no fully duplicated rows were found. Categorical
fields required no standardization — all category labels were already
clean and consistent. `delayed` and `delivery_status` were verified as
logically consistent with each other. Outliers in distance, weight, and
cost were reviewed and retained, as all fell within physically
plausible ranges for a real delivery business.

---

## 5. Methodology

The analysis followed a structured workflow, entirely in Python
(pandas, numpy, matplotlib, seaborn, plotly, scipy):

1. Business & requirements understanding (defining 9 answerable
   business questions, tied explicitly to available columns)
2. Data understanding (structural diagnosis)
3. Data cleaning (evidence-based fixes only, no blind removal)
4. Exploratory data analysis (segment-by-segment breakdowns)
5. Feature engineering (8 derived variables, each with a stated purpose)
6. Business analysis (chi-square significance testing, interaction/root-
   cause analysis, segment ranking)
7. Visualization (7 figures, each mapped to a business question or
   confirmed finding)
8. Dashboard (Streamlit, 4 sections, live filters)
9. Testing (31 automated pytest tests against real cleaning, feature,
   and analysis functions)

No machine learning was used — every finding in this report is
descriptive/inferential statistics (correlation, chi-square testing),
appropriate for the analytical questions asked.

---

## 6. Exploratory Data Analysis — Summary

Full detail in `notebooks/04_eda.ipynb`. Key patterns found:

| Segment | Effect on delivery outcome |
|---|---|
| Region | Flat (~1 pt spread) |
| Delivery partner | Small (~2 pt spread) |
| Vehicle type | Flat (~1 pt spread) |
| **Weather condition** | **Large** — stormy failure rate (8.9%) nearly 3x clear (3.2%) |
| **Delivery mode** | **Very large** — express delivered rate (26.2%) vs. standard (100%) |
| Package type | Flat (~1 pt spread) |
| Distance | Strongly drives cost (r≈0.99), moderately drives time (r≈0.69) |
| Customer rating | Tracks outcome closely: 4.21 (delivered) → 2.40 (delayed) → 1.31 (failed) |

---

## 7. Business Analysis — Summary

Full detail in `notebooks/06_business_analysis.ipynb`. Chi-square
testing of each categorical segment against `delivery_status`:

| Segment | Chi² | p-value | Significant? |
|---|---|---|---|
| Delivery mode | 11,654.5 | <0.0001 | **Yes — very strong** |
| Weather condition | 1,360.0 | <0.0001 | **Yes — strong** |
| Delivery partner | 26.8 | 0.044 | Technically yes, negligible effect |
| Package type | — | 0.56 | No |
| Region | — | 0.40 | No |
| Vehicle type | — | 0.87 | No |

**Root cause analysis** (weather × mode interaction) found weather's
damage is concentrated almost entirely in express mode:

| Mode | Weather | Delivered % |
|---|---|---|
| Express | Clear | 48.4% |
| Express | Stormy | 0.2% |
| Same day | Clear | 83.5% |
| Same day | Stormy | 34.4% |

**Highest-risk segment:** express + rainy/stormy weather — 8.3% of
volume, 1.3% delivered rate vs. 73.3% baseline.

**Cross-check:** `standard` mode's 100% delivered rate is not a
distance artifact — its average distance (148.6km) is nearly identical
to express mode's (151.0km), confirming the network can reliably
handle these distances under the right operational design.

---

## 8. Key Findings

1. Express delivery is structurally unreliable, independent of weather.
2. Weather sharply amplifies express-mode failure specifically, not
   delivery outcomes broadly.
3. Region, vehicle type, and package type are not meaningful
   performance levers.
4. The company's own standard-mode operations prove reliable delivery
   is achievable at comparable distances.
5. Customer rating is a direct, severe casualty of delay and failure.
6. Cost is driven almost entirely by distance, not by partner or
   vehicle choice.

---

## 9. KPIs

| KPI | Value |
|---|---|
| Total deliveries analyzed | 25,000 |
| On-time delivery rate | 73.3% |
| Delay rate | 21.4% |
| Failed delivery rate | 5.3% |
| Average delivery time | ~6.2–6.3 hours (flat across vehicle types) |
| Average delivery cost | ~₹858–869 (flat across vehicle types) |
| Average customer rating | Ranges 4.21 (delivered) to 1.31 (failed) |
| Express-mode on-time rate | 26.2% |
| Express-mode on-time rate (clear weather only) | 48.4% |
| High-risk segment (express + rainy/stormy) delivered rate | 1.3% |

---

## 10. Recommendations

Full Finding → Evidence → Business Impact → Recommendation detail in
`reports/02_insights_and_recommendations.md`. Summary, in priority
order:

1. **Redesign express-mode SLA** with realistic time buffers.
2. **Build a weather-contingent handling rule** for express orders
   (downgrade or warn when forecast shows rain/storms).
3. **Use standard-mode routing/buffer logic as the benchmark** for the
   express redesign.
4. **Deprioritize region/partner/vehicle-focused initiatives** — the
   data does not support them as meaningful levers.
5. **Monitor the high-risk segment's volume as an early-warning
   indicator** for customer satisfaction risk.

---

## 11. Limitations

- No cost-of-failure data (redelivery, refunds, support tickets) — the
  business impact of the high-risk segment is inferred, not directly
  measured.
- No date/timestamp field — trend, seasonality, and time-of-day
  analysis were out of scope for the entire project.
- Currency unit for `delivery_cost` is unspecified in the source data.
- Findings are correlational/associational (chi-square, correlation),
  not from a controlled experiment — the recommendation to redesign
  express SLAs should be validated with a pilot before full rollout.

---

## 12. Conclusion

This analysis replaced a broad, unfocused set of possible delivery
problems with two statistically confirmed drivers — delivery mode and
weather — and one precisely quantified high-risk segment. The clearest
path to improving company-wide delivery performance is a redesign of
the express-mode delivery promise, informed by the company's own
successful standard-mode operations, combined with a weather-contingent
handling rule targeted at the specific segment identified in this
report. Region, partner, and vehicle-level initiatives are not
supported by the data as meaningful next steps.
