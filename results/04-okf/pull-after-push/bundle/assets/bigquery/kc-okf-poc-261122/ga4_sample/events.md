---
type: table-context
x-kcmd:
  v: 1
  entryType: projects/dataplex-types/locations/global/entryTypes/document
  parentEntry: projects/kc-okf-poc-261122/locations/us/entryGroups/ga4-merch-context/entries/assets/bigquery/kc-okf-poc-261122/ga4_sample
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
# Events Overview

The table structure follows the Google Analytics 4 (GA4) event export format, storing user identifiers, nested event parameters, user properties, device specifications, geographic origins, traffic sources, and detailed e-commerce transaction payloads [1].

## Purpose

The table provides granular event-level clickstream tracking for the merchandise store [1]. It is utilized for digital analytics, funnel analysis, user engagement tracking, and e-commerce conversion reporting [1].

## Columns & Metrics

### Schema Columns

- **event_date** (`STRING`): Date of the event.
- **event_timestamp** (`INTEGER`)
- **event_name** (`STRING`): Name of the logged event (e.g., `add_to_cart`, `purchase`).
- **event_params** (`RECORD`, repeated): Key-value parameters associated with the event, containing nested data types such as string, integer, float, and double values. Key parameters include `ga_session_id`, used in combination with `user_pseudo_id` to establish distinct browsing sessions [1].
- **event_previous_timestamp** (`INTEGER`)
- **event_value_in_usd** (`FLOAT`)
- **event_bundle_sequence_id** (`INTEGER`)
- **event_server_timestamp_offset** (`INTEGER`)
- **user_id** (`STRING`)
- **user_pseudo_id** (`STRING`)
- **privacy_info** (`RECORD`): User privacy and consent states.
- **user_properties** (`RECORD`, repeated): Repeated record holding persistent user-level properties and attributes.
- **user_first_touch_timestamp** (`INTEGER`): Timestamp marking the first time the user interacted with the site.
- **user_ltv** (`RECORD`): Lifetime value metrics for the user.
- **device** (`RECORD`): Hardware and browser specifications, including device category, brand, and model details.
- **geo** (`RECORD`)
- **app_info** (`RECORD`)
- **traffic_source** (`RECORD`): Source, medium, and campaign details associated with how the user arrived at the site [1].
- **stream_id** (`INTEGER`)
- **platform** (`STRING`)
- **event_dimensions** (`RECORD`)
- **ecommerce** (`RECORD`): E-commerce purchase, revenue, and refund attributes, including `purchase_revenue_in_usd` and `refund_value_in_usd` [1].
- **items** (`RECORD`, repeated): Repeated record containing product and item-level details associated with e-commerce events.
- **event_date_dt** (`DATE`): Date-typed event date column configured as the table's partition column [1].

### Official Metric Definitions

- **Engaged session**: A browsing session that lasted longer than 10 seconds, recorded 2 or more page views, or contained a purchase event [1]. Sessions are identified by combining `user_pseudo_id` with the `ga_session_id` value extracted from `event_params` [1].
- **Active buyer (28d)**: A unique `user_pseudo_id` having at least one logged `purchase` event within the trailing 28 days [1].
- **Net merch revenue**: Calculated as the sum of `ecommerce.purchase_revenue_in_usd` minus the sum of `ecommerce.refund_value_in_usd` [1]. Official metrics must always be reported in USD and must not use local-currency fields [1].
- **Cart conversion rate**: Total count of sessions containing a `purchase` event divided by the total count of sessions containing an `add_to_cart` event [1].

## Lineage

The dataset is populated as a copy of the public GA4 sample e-commerce export [1].

## Owner

- **Owning team**: Digital Insights Guild [1]
- **Dataset reference code**: MSC-417 [1]
- **Data steward**: Digital Insights Guild on-call steward (contact channel: `#msc-417-data`) [1]

## Governance

- **Sensitivity Classifications**:
  - `user_pseudo_id`: Classified as **Tier C2 (pseudonymous)**. It must never be exported outside the analytics project and must never be joined with CRM or external email lists [1].
  - `geo.city` and `geo.metro`: Classified as **Tier C3 (restricted)**. Reporting is permitted only when aggregated to the region or country level; dashboard reporting at the city or metro level is prohibited [1].
  - `device.*`, `traffic_source.*`, and all other columns: Classified as **Tier C1 (internal)** with standard internal access policies [1].
- **Retention**: Rows older than 14 months must be purged by the Digital Insights Guild [1].
- **Refresh & Finality SLA**: The table is loaded once per day; daily data is considered final 72 hours after the calendar day ends [1]. Reporting must not treat data from the most recent 3 days as final numbers [1].

## Data Quality

- **Total Row Count**: The table contains 4,295,584 rows.
- **Time Horizon**: The dataset covers a fixed historical span of 92 days, running from 2020-11-01 through 2021-01-31 [1]. No newer records will be ingested [1].

## Usage

- **Partition Pruning**: Queries must always filter on the partition column `event_date_dt` to restrict scanned bytes and limit query cost [1].
- **Marketing Attribution Exclusions**: Any event where `traffic_source.source` is equal to `(data deleted)` must be excluded from marketing attribution analyses [1].
- **Geographic Aggregations**: Because `geo.city` and `geo.metro` fall under Tier C3 restrictions, dashboard creators and analysts must aggregate geographic metrics up to `geo.region` or `geo.country` [1].
- **Session Identification**: Because individual events do not carry a top-level session key, analysts must unnest `event_params` to locate `ga_session_id`, concatenating it with `user_pseudo_id` to evaluate session-level engagement and conversion rates [1].

## Table Info

`kc-okf-poc-261122.ga4_sample.events`

## Source References
1. Merch Store Clickstream: data policy and metric definitions
