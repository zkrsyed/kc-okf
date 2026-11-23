# Merch Store Clickstream: data policy and metric definitions

> **Fictional document written for a POC.** The company, team, codes and rules below are made up. They exist so we can trace whether an enrichment agent read this file.

Applies to: BigQuery table `kc-okf-poc-261122.ga4_sample.events` (a copy of the public GA4 sample e-commerce export).

## Ownership

- Business name of this table: **Merch Store Clickstream**.
- Dataset code: **MSC-417**. Use this code in tickets and access requests.
- Owning team: **Digital Insights Guild**. Data steward: the Guild's on-call steward (contact via the `#msc-417-data` channel).
- Refresh: loaded once per day; a day is final 72 hours after it ends. Do not report on the last 3 days as final numbers.

## Sensitivity classification

| Column | Classification | Rule |
|---|---|---|
| `user_pseudo_id` | **Tier C2 (pseudonymous)** | Never export outside the analytics project. Never join with CRM or email lists. |
| `geo.city`, `geo.metro` | **Tier C3 (restricted)** | Report only aggregated to region or country, never at city level in dashboards. |
| `device.*`, `traffic_source.*` | Tier C1 (internal) | No extra rules. |
| everything else | Tier C1 (internal) | No extra rules. |

Retention: rows older than **14 months** must be deleted by the Guild.

## Metric definitions (official)

- **Engaged session:** a session that lasted longer than 10 seconds, had 2 or more page views, or had a purchase. Identify sessions by `user_pseudo_id` plus the `ga_session_id` event parameter.
- **Active buyer (28d):** a `user_pseudo_id` with at least one `purchase` event in the trailing 28 days.
- **Net merch revenue:** sum of `ecommerce.purchase_revenue_in_usd` minus sum of `ecommerce.refund_value_in_usd`. Always report in USD; never use the local-currency columns.
- **Cart conversion rate:** sessions with a `purchase` divided by sessions with an `add_to_cart`.

## Reporting rules

- Exclude events where `traffic_source.source` is `(data deleted)` from all marketing attribution reports.
- Always filter on the partition column `event_date_dt` so queries scan only the needed days.
- The data covers 2020-11-01 to 2021-01-31 only (92 days). Nothing newer will arrive.
