# Pitfalls that Silently Produce Wrong Answers

## Purpose
This page addresses why metric totals become inflated, query scan costs spike, or recent figures shift across query runs in GA4 clickstream event data. It provides the operational filters, unnesting logic, and business rules required to avoid silent calculation errors.

## How to Query
- **Filter daily partitions**: Always constrain the partition column `event_date_dt` (or `_TABLE_SUFFIX` when querying wildcard tables such as `events_*`) in the `WHERE` clause to avoid full-table scans across all 92 daily tables [1, 2, 6].
- **Exclude deleted attribution sources**: Filter out events where `traffic_source.source = '(data deleted)'` when calculating any marketing attribution metric [1].
- **Use USD revenue fields**: Calculate net merchandise revenue as `SUM(ecommerce.purchase_revenue_in_usd) - SUM(ecommerce.refund_value_in_usd)`; never query or sum local-currency revenue columns [1].
- **Unnest repeated records**: Flatten nested arrays such as `event_params`, `items`, and `user_properties` using `LEFT JOIN UNNEST(...)` or `CROSS JOIN UNNEST(...)` prior to referencing nested keys and attributes [5, 7].
- **Adhere to privacy tiers**: Do not export `user_pseudo_id` outside the analytics project or join it with external CRM/email lists (Tier C2); never display `geo.city` or `geo.metro` at city level in dashboards—aggregate them to region or country (Tier C3) [1].

```sql
-- Pattern: Pruning partitions, extracting session ID, and excluding deleted traffic
SELECT
  event_date_dt,
  COUNT(DISTINCT user_pseudo_id) AS active_users,
  COUNT(DISTINCT ep.value.int_value) AS total_sessions
FROM `kc-okf-poc-261122.ga4_sample.events`
LEFT JOIN UNNEST(event_params) AS ep
  ON ep.key = 'ga_session_id'
WHERE event_date_dt BETWEEN '2020-11-01' AND '2020-11-30'
  AND event_name = 'session_start'
  AND traffic_source.source != '(data deleted)'
GROUP BY event_date_dt;
```

## Traps
- **Query scan costs and runtimes are unexpectedly high.** You queried wildcard or partitioned event tables without partition pruning; filter directly on `event_date_dt` (or `_TABLE_SUFFIX` on `events_*`) to limit scanned partitions to the needed window [1, 2, 6].
- **Session counts equal event counts or are inflated.** You counted rows or distinct `ga_session_id` values across all events; sessions are not single rows, so you must isolate `event_name = 'session_start'` and unnest `event_params` to count distinct `value.int_value` where `key = 'ga_session_id'`, or uniquely identify sessions across broader event streams using `user_pseudo_id` combined with `ga_session_id` [1, 3].
- **Numbers for the most recent 3 days change or drop unexpectedly.** You reported unfinalized records; data refreshes daily but is finalized only 72 hours after the calendar day closes, meaning the trailing 3 days must not be published as final numbers [1].
- **Queries return zero rows for dates outside late 2020 and early 2021.** You queried dates outside the fixed dataset boundary; the sample table spans exactly November 1, 2020, to January 31, 2021 (92 daily tables), and no newer dates exist [1, 4].
- **Marketing campaign attribution totals do not tie to verified source figures.** You included redacted rows; marketing reports must explicitly exclude records where `traffic_source.source` equals `'(data deleted)'` [1].
- **Multicurrency revenue reports produce incorrect totals.** You aggregated local transaction values; calculate revenue exclusively using `ecommerce.purchase_revenue_in_usd` and subtract `ecommerce.refund_value_in_usd` [1].
- **Item-level metrics (such as add-to-cart or product views) fail to resolve.** You referenced `items.item_name` directly without flattening; e-commerce product interactions reside in the repeated `items` array and require `UNNEST(items)` to access item-level columns [5, 7].
- **Metrics do not match live Google Merchandise Store demo data.** You assumed the public export mirrors live property telemetry; public dataset values are deliberately obfuscated with placeholders such as `<Other>`, `NULL`, and empty strings `''` for privacy protection [4].
- **Compliance audit flags privacy policy violations.** You joined `user_pseudo_id` to external CRM records or displayed raw city dimensions; `user_pseudo_id` is restricted pseudonymous data (Tier C2), and geographic data in `geo.city` and `geo.metro` (Tier C3) may only be reported aggregated to the region or country level [1].

## Source References
1. Merch Store Clickstream: data policy and metric definitions — states the 72-hour finalization delay, partition filtering mandate on `event_date_dt`, attribution exclusion rule for `(data deleted)`, USD revenue formula, and C2/C3 data classification restrictions.
2. Querying a Specific Date Range — states that partitioning queries on `event_date_dt` reduces bytes scanned and demonstrates active user count query structure.
3. Session Analysis (Unnesting Parameters) — states that sessions are not independent rows and details unnesting `ga_session_id` from `event_params` on `session_start`.
4. Google Analytics 4 BigQuery Public Dataset — states that data covers 92 daily tables from November 1, 2020, to January 31, 2021, and contains obfuscation placeholders like `<Other>`.
5. E-Commerce Product Interest — states that item interactions are stored in the nested `items` array and require `UNNEST(items)` to access fields such as `item_name`.
6. Using Analytics Events — states that date-bound queries on wildcard tables like `events_*` require filtering with `_TABLE_SUFFIX`.
7. Using Google Analytics 4 BigQuery Public Dataset — states that GA4 data contains nested record structures and arrays that require BigQuery's `UNNEST()` function to process.

See also: `assets/bigquery/kc-okf-poc-261122/ga4_sample/events` — the table entry for `kc-okf-poc-261122.ga4_sample.events`.