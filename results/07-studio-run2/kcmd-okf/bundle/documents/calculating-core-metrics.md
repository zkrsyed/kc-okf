---
type: knowledge-base
x-kcmd:
  v: 1
  entryType: projects/dataplex-types/locations/global/entryTypes/document
  parentEntry: projects/kc-okf-poc-261122/locations/us/entryGroups/ga4-merch-context-r2/entries/documents
  entrySource:
    location: us
    labels:
      generator: enrichment_agent
      source: knowledge_agent
  trailingNewline: false
  aspects:
    dataplex-types.global.document:
      job:
        name: enrichment-agent/enrich-7939c61dc2724775
        runTime: 2026-11-24T19:45:19Z
---
# Calculating Core Clickstream and Ecommerce Metrics

## Purpose
This page documents how to calculate core clickstream and e-commerce metrics—including unique sessions, active buyers, engaged sessions, net revenue, and cart conversion rate—from nested event parameters in GA4 clickstream exports, alongside table-level governance rules, sensitivity tiers, and operational constraints [1, 2, 3, 4].

## Definitions
- **Active Buyer (28d)**: A distinct `user_pseudo_id` associated with at least one `purchase` event occurring within the trailing 28 days [1].
- **Engaged Session**: A session (`user_pseudo_id` plus `ga_session_id`) that lasts longer than 10 seconds, contains 2 or more page views, or records a `purchase` event [1].
- **Net Merch Revenue**: The total monetary value computed as the sum of `ecommerce.purchase_revenue_in_usd` minus the sum of `ecommerce.refund_value_in_usd`, reported strictly in USD [1].
- **Cart Conversion Rate**: The ratio calculated by dividing the number of unique sessions containing a `purchase` event by the number of unique sessions containing an `add_to_cart` event [1].

## How to Query

### Data Policy and Sensitivity Tiers
Field classifications and usage constraints are governed by policy `MSC-417` [1]:
- `user_pseudo_id`: Classified as **Tier C2 (pseudonymous personal data)** [1]. Never export outside the analytics project, and never join with CRM records or email lists [1].
- `geo.city` and `geo.metro`: Classified as **Tier C3 (restricted)** [1]. Must never be reported at the city level in dashboards; aggregate strictly to region or country [1].
- `device.*` and `traffic_source.*`: Classified as **Tier C1 (internal)** with no additional reporting restrictions [1].
- All other table columns: Classified as **Tier C1 (internal)** [1].

### Governance Rules and Reporting Constraints
- **Table Scope & Grain**: Applies to `kc-okf-poc-261122.ga4_sample.events` (business name: *Merch Store Clickstream*, dataset code `MSC-417`), owned by the Digital Insights Guild [1].
- **Partition Filtering**: Always include a partition filter on `event_date_dt` (or `_TABLE_SUFFIX` on partitioned exports) in the `WHERE` clause to avoid full-table scans [1].
- **Date Window**: The dataset contains 92 daily partitions covering `2020-11-01` to `2021-01-31`; no newer data will arrive [1].
- **Finality Window**: Data loads once daily and finalizes 72 hours after day-end [1]. Do not report final figures on the trailing 3 days [1].
- **Retention**: Rows older than 14 months must be deleted [1].
- **Marketing Attribution Exclusion**: Exclude records where `traffic_source.source = '(data deleted)'` from all attribution queries [1].

### SQL Pattern: Unnesting Sessions and Items

To query product details, flatten the nested `items` array using `UNNEST(items)` [4].

## Method
To compute core metrics across the clickstream log:

1. **Prune Partitions**: Apply a filter on `event_date_dt` or `_TABLE_SUFFIX` to scope the query window [1].
4. **Aggregate Metric Numerators and Denominators**:
   - For **Engaged Sessions**, identify session IDs meeting duration (>10s), page view count (>=2), or purchase criteria [1].
   - For **Net Merch Revenue**, compute `SUM(ecommerce.purchase_revenue_in_usd) - SUM(ecommerce.refund_value_in_usd)` [1].

## Traps
- **Marketing attribution counts include deleted traffic.** You omitted the exclusion filter; always add `WHERE traffic_source.source != '(data deleted)'` on marketing reports [1].
- **Full table scan costs are high.** You queried without the partition column; always supply an explicit date predicate on `event_date_dt` or `_TABLE_SUFFIX` [1].
- **Net revenue does not reconcile across regions.** You summed local currency columns instead of USD fields; sum `ecommerce.purchase_revenue_in_usd` and subtract `ecommerce.refund_value_in_usd` [1].
- **City-level dimensions appear in customer-facing dashboards.** You published `geo.city` or `geo.metro`; Tier C3 policy requires rolling up geographic metrics to region or country [1].

## Source References
1. `gs://kc-okf-poc-261122-signals/merch-store-data-policy.md` — states sensitivity tiers, data retention, partition filtering rules, attribution exclusions, and definitions for net merch revenue, active buyers, engaged sessions, and cart conversion rates.
2. `gs://kc-okf-poc-261122-signals/google-sample/example3.md` — states that session IDs reside nested inside `event_params` under `ga_session_id` and describes isolating `session_start` to count sessions.
3. `gs://kc-okf-poc-261122-signals/google-sample/example1.md` — states that unique users are identified via device cookies in `user_pseudo_id`.
4. `gs://kc-okf-poc-261122-signals/google-sample/example4.md` — states that e-commerce item attributes are stored in a nested `items` array requiring `UNNEST(items)` to analyze product events.

See also: `assets/bigquery/kc-okf-poc-261122/ga4_sample/events` — the table entry for `kc-okf-poc-261122.ga4_sample.events`.
