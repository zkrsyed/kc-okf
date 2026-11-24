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
# Pitfalls that silently produce wrong answers

## Purpose
What querying mistakes, unfinalized date windows, obfuscation placeholders, and compliance violations will silently invalidate metrics or breach data governance on Merch Store clickstream data? This guide outlines the operational rules, metric calculations, and structural traps across table `kc-okf-poc-261122.ga4_sample.events` (code `MSC-417`) [1].

## Definitions
- **Active buyer (28d)**: A user identified by `user_pseudo_id` who generated at least one `purchase` event within the trailing 28 days [1].
- **Cart conversion rate**: Total distinct sessions that logged a `purchase` event divided by total distinct sessions that logged an `add_to_cart` event [1].
- **Engaged session**: A session identified by `user_pseudo_id` plus `ga_session_id` that lasted longer than 10 seconds, had 2 or more page views, or included a `purchase` event [1].
- **Net merch revenue**: Revenue calculated strictly as `SUM(ecommerce.purchase_revenue_in_usd) - SUM(ecommerce.refund_value_in_usd)`, reported in USD rather than local currency [1].
- **Data sensitivity tiers**: Field classifications governing project usage: Tier C1 (internal: `device.*`, `traffic_source.*`, and general unlisted columns), Tier C2 (pseudonymous personal data: `user_pseudo_id`), and Tier C3 (restricted: `geo.city` and `geo.metro`) [1].

## How to Query
- Filter every query by date on the partition column `event_date_dt` (or `_TABLE_SUFFIX` when querying table shards `events_*`) to limit byte scan volume and query costs [1, 3, 5].
- Bound analytics queries strictly between `2020-11-01` and `2021-01-31`, as this export is a static 92-day sample with no subsequent dates arriving [1, 2].
- When querying ongoing daily loads, exclude the trailing 3 days; records take 72 hours after day-end to become final [1].
- Exclude records where `traffic_source.source` equals `'(data deleted)'` from all marketing attribution reports [1].
- Aggregate geographic metrics exclusively to `geo.region` or `geo.country`; do not expose `geo.city` or `geo.metro` in dashboards [1].
- Keep `user_pseudo_id` inside the analytics warehouse; do not export it outside the analytics project or join it against CRM records or email lists [1].
- Note that rows older than 14 months are subject to deletion under retention policies stewarded by the Digital Insights Guild (`#msc-417-data`) [1].

The snippet demonstrates safe partition boundaries, attribution exclusion, session isolation, and USD revenue calculation [1, 3, 4, 5].

## Traps
- **Reported metric values change or drift over the last three days.** Daily ingestion is not final until 72 hours after the calendar day closes; do not report metrics from the last 3 days as final numbers [1].
- **Marketing attribution models assign credit to deleted or redacted sources.** Compliance privacy deletions populate the source column with placeholder text; add `traffic_source.source != '(data deleted)'` to all marketing attribution queries [1].
- **Revenue aggregates fail audit due to currency mix-ups or omitted returns.** Aggregating local currencies or ignoring refunds skews sales totals; calculate net merch revenue strictly as `SUM(ecommerce.purchase_revenue_in_usd) - SUM(ecommerce.refund_value_in_usd)` and avoid local currency columns [1].
- **Publishing dashboards creates a Tier C3 privacy violation.** Including `geo.city` or `geo.metro` violates access policy; roll up all geographic reporting to the country or region level [1].
- **Exporting user identifiers creates a Tier C2 personal data breach.** Moving `user_pseudo_id` outside the analytics project or joining it with CRM/email contact lists is prohibited; maintain user analysis strictly within pseudonymous project boundaries [1].
- **Session counts equal event counts or produce massive inflations.** GA4 records events rather than dedicated session rows; extract session identifiers by pairing `user_pseudo_id` with `ga_session_id` from `event_params`, or filter by `event_name = 'session_start'` [1, 4].

## Source References
1. Merch Store Data Governance and Policy — states the data governance rules, tier classifications, finalization windows, and metric definitions for dataset MSC-417; the page states these policies directly as query bounds and governance rules.
2. GA4 Sample Overview — states the 92-day table range and the use of `<Other>`, `NULL`, and empty string obfuscation placeholders; the page states these bounds and filters directly.
3. GA4 Query Example 2 — states that filtering on daily partitions reduces scan costs and demonstrates active user aggregation; the page states this filtering rule directly.
4. GA4 Query Example 3 — states that sessions are stored as nested `ga_session_id` parameters rather than rows; the page states this unnesting technique directly.
5. GA4 Export Events Specification — states that date filtering in event exports requires the `_TABLE_SUFFIX` pseudo-column; the page states this syntax directly.
6. GA4 Query Example 4 — states that product e-commerce analysis requires unnesting the `items` array; the page states this unnesting requirement directly.
7. GA4 Query Example 1 — states that unique users are calculated from device cookies in `user_pseudo_id`; the page states this calculation directly.
8. GA4 Export Usage Guide — states that GA4 exports utilize nested arrays and structs; the page states this schema structure directly.

See also: `assets/bigquery/kc-okf-poc-261122/ga4_sample/events` — the table entry for `kc-okf-poc-261122.ga4_sample.events`.
