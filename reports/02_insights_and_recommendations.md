# Insights & Recommendations
## Last-Mile Delivery Operations Analysis

---

## Executive Summary

Across 25,000 deliveries, **73.3% arrive on time, 21.4% are delayed, and
5.3% fail outright**. Statistical testing (chi-square, Step 9) confirms
that only two factors meaningfully explain this variation:
**delivery mode** and **weather condition** — region, vehicle type, and
package type show no statistically significant effect, and delivery
partner shows a statistically detectable but practically negligible
one. The two significant drivers interact: weather's damage is
concentrated almost entirely inside **express-mode** deliveries, which
are unreliable even in clear weather (48.4% on-time) and collapse
almost completely in storms (0.2% on-time). This report translates
those findings into five prioritized, evidence-backed recommendations.

---

## Finding 1 — Express Delivery Is Structurally Unreliable, Not Just Weather-Sensitive

**Evidence:** Even in clear weather, express-mode deliveries only
arrive on time **48.4%** of the time, versus 83.5% for same-day and
near-100% for two-day/standard modes. Under stormy conditions, express
collapses to **0.2%** delivered, 79.4% delayed, and 20.4% failed
(Business Analysis, Step 9, Section 2). This gap exists before weather
is even factored in.

**Business Impact:** Customers choosing and paying for the fastest,
presumably premium delivery tier are receiving the least reliable
service in the company's portfolio — the opposite of what an express
promise should deliver. This directly damages trust in the express
product specifically, and by extension the brand.

**Recommendation:** Redesign the express-mode SLA with a realistic time
buffer, benchmarked against how two-day and standard modes achieve
their near-perfect reliability (see Finding 4). This is an operational
design problem, not a weather problem or a partner/vehicle problem —
fixing it will require revisiting how express routes and buffers are
planned, not reallocating vehicles or partners.

---

## Finding 2 — A Single, Well-Defined Segment Drives a Disproportionate Share of Failures

**Evidence:** Express deliveries during rainy or stormy weather make up
just **8.3%** of total volume (2,077 of 25,000 deliveries) but have a
delivered rate of only **1.3%**, against a 73.3% company-wide baseline
— a 72-point gap (Business Analysis, Step 9, Section 3).

**Business Impact:** This is a small, specific population responsible
for an outsized share of failed deliveries, and very likely an outsized
share of redelivery cost, refund cost, and customer support volume
(these costs aren't directly in the dataset, but the failure
concentration strongly implies it).

**Recommendation:** Build a weather-contingent rule that automatically
adjusts the express promise ahead of time — e.g. flagging express
orders for downgrade to same-day or adding an explicit delay warning
at checkout when the forecast shows rain or storms in the delivery
area. This targets the exact segment causing the most harm rather than
a blanket policy change across all deliveries.

---

## Finding 3 — Region, Vehicle Type, and Package Type Are Not Meaningful Levers

**Evidence:** Chi-square tests found no statistically significant
association between delivery outcome and region (p = 0.40), vehicle
type (p = 0.87), or package type (p = 0.56). Delivery partner is
technically significant (p = 0.044) but with a small effect size —
partner performance scores range only 78.6–80.7 out of 100, and
cost-per-km is flat (₹5.79–5.84) across all partners and vehicle types
once short-distance skew is removed (Business Analysis, Step 9,
Sections 5–6).

**Business Impact:** Any initiative framed around "which region needs
help" or "which partner/vehicle should we drop" would be optimizing
against noise, not signal. Resources spent there won't move the
company-wide numbers.

**Recommendation:** Deprioritize regional, partner, and vehicle-level
interventions as primary levers. If operational review of specific
partners or vehicles is still desired (e.g. for contract or compliance
reasons unrelated to this dataset), treat it as a separate initiative —
not one this analysis supports as a performance fix.

---

## Finding 4 — The Company Already Has Proof That Reliable Delivery Is Achievable

**Evidence:** Standard-mode deliveries show a **100% delivered rate**
with zero delays or failures across all 25,000 records, and this is not
explained by shorter distances — standard mode's average distance
(148.6km) is nearly identical to express mode's (151.0km) (Business
Analysis, Step 9, Section 4).

**Business Impact:** This rules out "the network can't reliably cover
these distances" as an excuse for express-mode failures. The same
delivery network reliably completes similar-distance trips under
standard mode — the difference is in how much time buffer and planning
margin each mode is allowed.

**Recommendation:** Use standard/two-day mode's operational design
(routing, time allocation, driver assignment logic) as the internal
benchmark when redesigning express-mode SLAs in Finding 1, rather than
starting from scratch.

---

## Finding 5 — Delay and Failure Directly and Severely Damage Customer Satisfaction

**Evidence:** Average customer rating drops from **4.21/5** for
delivered orders to **2.40/5** for delayed orders and just **1.31/5**
for failed orders (EDA, Step 7, Section 7). Cost, meanwhile, is almost
entirely explained by distance (r ≈ 0.99) — not by which partner or
vehicle handles the delivery.

**Business Impact:** The ratings data quantifies exactly why fixing
Findings 1–2 matters commercially: failed deliveries aren't just an
operational cost, they're the single strongest predictor of a bad
customer rating in this dataset.

**Recommendation:** Track the high-risk segment from Finding 2 as a
leading indicator for customer satisfaction risk, not just a delivery
KPI — a spike in express+bad-weather volume should be treated as an
early warning for a coming dip in average rating, not just a delay
statistic.

---

## Priority Summary

| Priority | Recommendation | Addresses |
|---|---|---|
| 1 | Redesign express-mode SLA with realistic buffers | Finding 1 |
| 2 | Weather-contingent express downgrade/warning rule | Finding 2 |
| 3 | Use standard-mode routing logic as the benchmark for the redesign | Finding 4 |
| 4 | Deprioritize region/partner/vehicle-focused initiatives | Finding 3 |
| 5 | Monitor high-risk segment volume as a satisfaction early-warning signal | Finding 5 |

---

## Limitations

- **No cost-of-failure data.** Redelivery cost, refund cost, and support
  ticket volume are not in this dataset — the business impact of
  Finding 2 is inferred from failure concentration, not directly
  measured.
- **No date/timestamp field.** Trend, seasonality, and time-of-day
  analysis were out of scope for this entire project (documented in
  Step 4) — it's possible weather-driven risk is seasonal in ways this
  dataset cannot show.
- **Currency unit for `delivery_cost` is unspecified** in the source
  data.
- **Correlational, not experimental, evidence.** The weather × mode
  interaction is a strong, consistent statistical pattern, but this
  analysis cannot run a controlled experiment (e.g. randomly assigning
  extra buffer time to express orders) to prove causation directly —
  the recommendation to redesign express SLAs should be validated with
  a pilot before full rollout.

---

## Conclusion

This analysis replaces a broad, unfocused list of possible delivery
problems with two confirmed, statistically validated drivers —
delivery mode and weather — and one precisely defined high-risk segment
responsible for a disproportionate share of failures. The clearest,
highest-leverage action available to management is a redesign of the
express-mode delivery promise, informed by the company's own
already-successful standard-mode operations, paired with a
weather-contingent handling rule for the specific express + rainy/stormy
segment identified above.
