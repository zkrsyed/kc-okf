---
type: knowledge-base
x-kcmd:
  v: 1
  entryType: projects/dataplex-types/locations/global/entryTypes/document
  parentEntry: projects/kc-okf-poc-261122/locations/us/entryGroups/ga4-merch-context/entries/documents
  entrySource:
    location: us
    labels:
      generator: enrichment_agent
      source: knowledge_agent
  trailingNewline: false
  aspects:
    dataplex-types.global.document:
      job:
        name: enrichment-agent/enrich-9eb2ed9719624d4e
        runTime: 2026-11-22T22:16:40Z
---
# Computing Standard E-Commerce Metrics

## Purpose
This page provides the operational logic, business rules, and SQL patterns required to calculate core e-commerce key performance indicators—such as net revenue, engaged sessions, active buyers, and cart conversion rate—from Google Analytics 4 (GA4) clickstream events.

## Definitions
- **Session**: A visit identified by combining `user_pseudo_id` and the nested integer event parameter `ga_session_id`.
- **Engaged Session**: A session that lasted longer than 10 seconds, recorded 2 or more `page_view` events, or contained a `purchase` event.
- **Active Buyer (28d)**: A distinct `user_pseudo_id` with at least one `purchase` event within the trailing 28 days.
- **Net Merch Revenue**: The total of `ecommerce.purchase_revenue_in_usd` minus `ecommerce.refund_value_in_usd`.
- **Cart Conversion Rate**: The count of distinct sessions containing a `purchase` event divided by the count of distinct sessions containing an `add_to_cart` event.

## How to Query
- **Partition pruning**: Always filter queries using the partition column `event_date_dt` (or `_TABLE_SUFFIX` on wildcard tables `events_*`) to limit scanned bytes and cost.
- **Session extraction**: Extract `ga_session_id` from the nested `event_params` array where `key = 'ga_session_id'` and read `value.int_value`.
- **Currency selection**: Aggregate revenue strictly using `ecommerce.purchase_revenue_in_usd` and `ecommerce.refund_value_in_usd`; never use local-currency fields.
- **Item-level unnesting**: Flatten the nested `items` array (`CROSS JOIN UNNEST(items) AS items`) when analyzing item-level interactions such as product additions or catalog views.
- **Attribution filtering**: Exclude rows where `traffic_source.source = '(data deleted)'` from all marketing attribution queries.
- **Data finalization window**: Do not report on the trailing 3 days as final; data is refreshed daily and finalizes 72 hours after the close of the day.
- **Privacy and governance constraints**: `user_pseudo_id` is Tier C2 and must not be joined with external CRM/email lists or exported outside the analytics project. Geographic fields `geo.city` and `geo.metro` are Tier C3 and must only be presented aggregated to region or country level.

## Method

### 1. Extracting Sessions and Calculating Cart Conversion Rate
To determine session-level conversion, isolate sessions that triggered `add_to_cart` and `purchase`, then divide the converted sessions by the cart-initiating sessions [1], [3].

### 3. Active Buyers (Trailing 28 Days)
Count distinct pseudonymous users who performed a `purchase` within the 28-day window preceding a target date [1].

## Traps
- **Underreported numbers due to processing lag.** Generating official metrics for dates within the last 72 hours yields incomplete counts; exclude the trailing 3 days from finalized reporting.

## Source References
1. Merch Store Clickstream: data policy and metric definitions — defines formulas for engaged sessions, active buyers (28d), net merch revenue, cart conversion rate, reporting exclusions, and sensitivity tiers.
2. Session Analysis (Unnesting Parameters) — describes extracting `ga_session_id` from the nested `event_params` array.
3. E-Commerce Product Interest — details flattening the nested `items` array to analyze product-level events.
