# Data Governance and Quality Boundaries

## Purpose
This page documents the data governance tiers, privacy constraints, obfuscation artifacts, and data finality rules required to query the Merch Store Clickstream dataset (`MSC-417`) correctly [1, 2]. Analysts and automated agents must apply these rules to avoid compliance violations, unfinalized metrics reporting, and distorted revenue or attribution calculations [1].

## Definitions
- **Tier C1 (Internal)**: Fields including `device.*`, `traffic_source.*`, and all other unclassified columns that carry no additional export or join restrictions [1].
- **Tier C2 (Pseudonymous)**: Device cookie identifiers (`user_pseudo_id`) restricted strictly to the analytics project; they must never be exported externally or joined with CRM or email identity tables [1, 3].
- **Tier C3 (Restricted)**: Granular location attributes (`geo.city` and `geo.metro`) that must never be displayed at city level in dashboards and may only be published aggregated to region or country [1].
- **Finality Lag**: The 72-hour window following day-end during which daily partition data is refreshed and considered provisional [1].

## How to Query
- **Apply Date Partition Filters**: Every query against `kc-okf-poc-261122.ga4_sample.events` or wildcard tables (`events_*`) must include a filter on the partition column `event_date_dt` (or `_TABLE_SUFFIX`) to prevent full table scans and control compute costs [1, 4, 5].
- **Enforce Date Coverage Limits**: The dataset spans exactly 92 daily tables from `2020-11-01` to `2021-01-31`; no newer records will arrive, and queries outside this interval return no data [1, 2].
- **Observe Finality Windows**: Because data refreshes once per day and requires 72 hours to achieve finality, queries reporting final metrics must exclude the trailing 3 days [1].
- **Filter Deleted Attribution Sources**: Exclude records where `traffic_source.source = '(data deleted)'` across all marketing attribution reports [1].
- **Enforce Currency Normalization**: Calculate net merchandise revenue exclusively using USD columns as `SUM(ecommerce.purchase_revenue_in_usd) - SUM(ecommerce.refund_value_in_usd)`, never aggregating local currency fields [1].
- **Aggregate Tier C3 Geographies**: When reporting geography, aggregate `geo.city` and `geo.metro` up to `geo.region` or `geo.country` before exposing results in dashboards [1].
- **Unnest Nested Structures**: Extract attributes from nested arrays and structs (`event_params`, `user_properties`, `items`) via `UNNEST()` rather than attempting direct column references [6, 7, 8].

```sql
SELECT
  PARSE_DATE('%Y%m%d', event_date) AS event_date,
  geo.country AS country,
  geo.region AS region,
  COUNT(DISTINCT user_pseudo_id) AS active_users,
  COUNTIF(event_name = 'purchase') AS total_purchases,
  SUM(ecommerce.purchase_revenue_in_usd) - SUM(IFNULL(ecommerce.refund_value_in_usd, 0)) AS net_merch_revenue_usd
FROM
  `kc-okf-poc-261122.ga4_sample.events`
WHERE
  event_date_dt BETWEEN '2020-11-01' AND '2021-01-31'
  AND traffic_source.source != '(data deleted)'
GROUP BY
  1, 2, 3;
```


## Method
To calculate standard business metrics within governance boundaries, proceed in the following order:

1. **Partition and Finality Boundary**: Restrict the scan using `event_date_dt` between `2020-11-01` and `2021-01-31`, ensuring that if running on live pipelines, the most recent 72 hours (3 days) are omitted from finalized outputs [1, 2].
2. **Attribution Cleansing**: Apply a `WHERE` predicate filtering out `traffic_source.source = '(data deleted)'` for any acquisition or campaign attribution reporting [1].
3. **Session Identification**: Identify distinct sessions using `user_pseudo_id` combined with the unnested `event_params` integer value where `key = 'ga_session_id'` [1, 7].
4. **Metric Computation**:
   - **Engaged Sessions**: Count sessions identified by `user_pseudo_id` and `ga_session_id` that had a duration greater than 10 seconds, accumulated 2 or more `page_view` events, or logged a `purchase` event [1, 4].
   - **Active Buyers (28d)**: Identify unique `user_pseudo_id` counts that contain at least one `purchase` event within the trailing 28-day window [1, 4].
   - **Cart Conversion Rate**: Calculate total sessions containing at least one `purchase` event divided by total sessions containing at least one `add_to_cart` event [1, 4, 8].
   - **Net Merch Revenue**: Compute `SUM(ecommerce.purchase_revenue_in_usd) - SUM(ecommerce.refund_value_in_usd)` [1].
5. **Privacy and Compliance Export Gate**: Ensure `user_pseudo_id` is not joined with external CRM/email lists or exported outside the analytics project, and verify geographic breakdowns are rolled up to `geo.region` or `geo.country` [1].

## Traps
- **Reported numbers change retroactively on recent dates.** You queried data inside the 72-hour finality lag window; data is refreshed daily and is only final 3 days after day-end [1].
- **Marketing attribution reports show distorted acquisition channels.** You did not remove suppressed sources; filter out events where `traffic_source.source = '(data deleted)'` [1].
- **Dashboard violates spatial compliance policies.** You displayed `geo.city` or `geo.metro` directly; these columns are Tier C3 restricted and must be rolled up to `geo.region` or `geo.country` [1].
- **Queries breach customer data protection rules.** You exported `user_pseudo_id` outside the analytics project or joined it with email/CRM tables; `user_pseudo_id` is Tier C2 pseudonymous and prohibited from external linkage [1].
- **Revenue totals are distorted by exchange rates.** You summed raw local currency fields; net revenue must be calculated strictly as `SUM(ecommerce.purchase_revenue_in_usd) - SUM(ecommerce.refund_value_in_usd)` [1].
- **Queries scan massive byte volumes and incur high query costs.** You omitted the partition predicate; always filter queries on `event_date_dt` or `_TABLE_SUFFIX` [1, 4, 5].
- **Session counts are inflated or inaccurate.** You counted rows directly instead of unnesting `event_params` for `key = 'ga_session_id'` and pairing with `user_pseudo_id`, or you failed to isolate the `session_start` event [1, 7].
- **Metrics cannot be reconciled against live GA4 demo accounts.** The sample dataset contains obfuscated placeholders (`<Other>`, `NULL`, `''`) introduced specifically to protect business privacy, limiting direct consistency with production GA4 accounts [2].
- **No data is returned for queries beyond January 2021.** The dataset covers a fixed historical window of 92 days from November 1, 2020, to January 31, 2021; no newer partitions exist [1, 2].

## Source References
1. Merch Store Clickstream: data policy and metric definitions — states the data tiers, finality lag, retention limits, and core business metric definitions for dataset `MSC-417`.
2. Google Analytics 4 BigQuery Public Dataset — states that public dataset records are obfuscated with placeholders and cover a fixed 92-day period from November 1, 2020, to January 31, 2021.
3. High-Level Event and User Volume — states that total unique users are derived from device cookies via `COUNT(DISTINCT user_pseudo_id)`.
4. Using Analytics Events — states how to query core events (`page_view`, `session_start`, `purchase`) across date ranges using wildcard table suffixes.
5. Querying a Specific Date Range — states that queries must filter on daily partition columns like `event_date_dt` to limit data scanned and optimize query cost.
6. Using Google Analytics 4 BigQuery Public Dataset — states that GA4 exports use nested arrays and structs that require `UNNEST()` to flatten for querying.
7. Session Analysis (Unnesting Parameters) — states that sessions require unnesting `ga_session_id` from `event_params` on `session_start` events.
8. E-Commerce Product Interest — states that item-level interactions like `add_to_cart` require unnesting the `items` array.

See also: `assets/bigquery/kc-okf-poc-261122/ga4_sample/events` — the table entry for `kc-okf-poc-261122.ga4_sample.events`.