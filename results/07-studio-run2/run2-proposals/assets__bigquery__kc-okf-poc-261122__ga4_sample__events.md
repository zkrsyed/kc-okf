# events Overview

The `events` table (business name: **Merch Store Clickstream**, dataset code: **MSC-417**) stores raw event-level user interaction and e-commerce tracking data [1]. The table is an ingest copy of the public Google Analytics 4 (GA4) sample e-commerce export, spanning the 92-day historical window from 2020-11-01 to 2021-01-31 [1]. Each record represents a single client-side event emitted during a user interaction, capturing event parameters, user and device identifiers, geolocation attributes, traffic acquisition dimensions, and e-commerce transactions [1].

## Purpose

The primary purpose of `events` is to provide clickstream analytics, conversion funnel tracking, attribution analysis, and digital merchandising telemetry for the online merchandise store [1]. In access tickets and project communications, this table and its dataset are referenced by the identifier **MSC-417** [1]. The table dataset represents a fixed historical benchmark covering 2020-11-01 through 2021-01-31; no newer partitions are delivered [1].

## Columns & Metrics

### Column Reference & Data Classification

Each column is detailed below with its base data type and data classification tier as designated by the governance policy [1]. Where a column or nested record is assigned a formal classification tier in the policy, its status as personal data is noted [1]. Columns not explicitly categorized in the policy carry standard metadata without an assigned policy tier.

*   `event_date` (`STRING`): Date of the event formatted as a text string.
*   `event_timestamp` (`INTEGER`): Timestamp indicating when the client logged the event.
*   `event_name` (`STRING`): Standard or custom event identifier (for example, `purchase` or `add_to_cart`).
*   `event_params` (`RECORD`, repeated): Key-value collection storing contextual parameters and telemetry associated with the event.
*   `event_previous_timestamp` (`INTEGER`): Microsecond timestamp of the prior event in the sequence.
*   `event_value_in_usd` (`FLOAT`): Monomorphic event value.
*   `event_bundle_sequence_id` (`INTEGER`): Sequential identifier assigned to the upload batch.
*   `event_server_timestamp_offset` (`INTEGER`): Microsecond offset between client timestamp capture and receipt by Google servers.
*   `user_id` (`STRING`): First-party authenticated user identifier.
*   `user_pseudo_id` (`STRING`): **Tier C2 (pseudonymous)** personal data; the pseudonymized client cookie or device-instance identifier [1].
*   `privacy_info` (`RECORD`): Container holding privacy-related event settings, such as consent state.
*   `user_properties` (`RECORD`, repeated): Key-value bag containing persistent dimensions set at the user level.
*   `user_first_touch_timestamp` (`INTEGER`): Microsecond timestamp marking when the user first interacted with the property.
*   `user_ltv` (`RECORD`): Nested lifetime value record computing customer value metrics over time.
*   `device` (`RECORD`): **Tier C1 (internal)** non-personal data container capturing hardware, operating system, browser, and network attributes [1].
*   `geo` (`RECORD`): Geolocation attributes determined from client network endpoints [1].
    *   `geo.city`: **Tier C3 (restricted)** quasi-identifying personal data; city-level geographic designation [1].
    *   `geo.metro`: **Tier C3 (restricted)** quasi-identifying personal data; metropolitan market area designation [1].
    *   Other `geo.*` fields: Standard regional and country geographic descriptors.
*   `app_info` (`RECORD`): Application environment information and software build versions.
*   `traffic_source` (`RECORD`): **Tier C1 (internal)** non-personal data container detailing the marketing channel, medium, and referral source [1].
*   `stream_id` (`INTEGER`): Numeric identifier of the GA4 measurement data stream.
*   `platform` (`STRING`): Platform environment delivering the event (e.g., web).
*   `event_dimensions` (`RECORD`): Operational dimensions accompanying the event record.
*   `ecommerce` (`RECORD`): Transaction-level and order-level e-commerce parameters [1].
    *   `ecommerce.purchase_revenue_in_usd`: Total gross purchase revenue recorded in USD [1].
    *   `ecommerce.refund_value_in_usd`: Total refunded value recorded in USD [1].
*   `items` (`RECORD`, repeated): Array of item-level line records detailing individual merchandise SKUs, quantities, and pricing.
*   `event_date_dt` (`DATE`): Date-typed representation of the event partition, used for partition-pruning filters [1].

### Business Glossary & Metric Definitions

*   **Engaged Session**: A user visit that meets at least one qualification threshold: duration exceeding 10 seconds, logging 2 or more page views, or containing at least one purchase transaction [1].
*   **Session Identification**: The composite session identity formed by concatenating `user_pseudo_id` with the `ga_session_id` event parameter [1].
*   **Active Buyer (28d)**: A user represented by a distinct `user_pseudo_id` that has logged at least one `purchase` event within the trailing 28 calendar days [1].
*   **Net Merch Revenue**: The total monetary merchandise yield, defined as the mathematical difference: `SUM(ecommerce.purchase_revenue_in_usd) - SUM(ecommerce.refund_value_in_usd)` [1].
*   **Cart Conversion Rate**: The proportion of shopping sessions resulting in an order, calculated as the count of unique sessions with a `purchase` event divided by the count of unique sessions with an `add_to_cart` event [1].

## Lineage

*   **Upstream Pipeline**: Ingested directly as a verbatim copy of the public Google Analytics 4 (GA4) sample e-commerce export dataset [1].
*   **Downstream Usage**: Serves as the base clickstream layer for merchandising metrics, attribution analyses, and digital store reporting [1].

## Owner

*   **Owning Team**: Digital Insights Guild [1].
*   **Data Steward**: Digital Insights Guild on-call steward, reachable via the `#msc-417-data` Slack channel [1].

## Governance

The data policy mandates compliance with the following operational rules:

1.  **Pseudonymous Identifier Export Restriction**: `user_pseudo_id` is designated as Tier C2 (pseudonymous) personal data; it must never be exported outside the analytics BigQuery project and must never be joined with customer relationship management (CRM) systems or marketing email distribution lists [1].
2.  **Geographic Reporting Masking**: Nested fields `geo.city` and `geo.metro` are classified as Tier C3 (restricted) data; dashboards and downstream reports must aggregate location strictly to the region or country level, and city-level data must never be displayed [1].
3.  **Internal Classification**: Attributes under `device.*` and `traffic_source.*` are classified as Tier C1 (internal) data with no specialized access constraints [1].
4.  **Data Retention and Purging**: The Digital Insights Guild is required to delete all records older than 14 months pursuant to retention policy requirements [1].
5.  **Reporting Finality Lag**: The table refreshes on a daily schedule, with data for any given date considered finalized 72 hours after day close; analysts must not report numbers from the most recent 3 days as final figures [1].
6.  **Monetary Reporting Standard**: All commercial and revenue calculations must be reported strictly in United States Dollars (USD) using the dedicated USD columns (`ecommerce.purchase_revenue_in_usd`, `ecommerce.refund_value_in_usd`), without relying on local-currency fields [1].
7.  **Marketing Attribution Exclusions**: All queries computing marketing attribution must explicitly filter out records where `traffic_source.source` equals `'(data deleted)'` [1].
8.  **Mandatory Partition Pruning**: Analytical queries must include partition filters targeting `event_date_dt` to restrict query scan bytes to the intended date ranges [1].

## Data Quality

*   **Total Row Count**: The table contains 4,295,584 rows [2].
*   **Temporal Boundary**: The dataset spans exactly 92 days between 2020-11-01 and 2021-01-31 [1]. As a static snapshot of public historical sample data, no newer data partitions arrive into this table [1].

## Usage

*   **Funnel Evaluation**: Cart conversion rate should be derived by evaluating whether a distinct session encountered both `add_to_cart` and `purchase` events [1].
*   **Attribution Cleansing**: Upstream attribution pipelines must incorporate a `WHERE traffic_source.source != '(data deleted)'` predicate to prevent tracking artifacts from distorting source-level performance [1].
*   **Query Cost Optimization**: All BigQuery jobs querying this table must supply a predicate against `event_date_dt` to prune partition scans [1].

## Table Info

`kc-okf-poc-261122.ga4_sample.events`

## Source References
1. Merch Store Clickstream: data policy and metric definitions
2. [table metadata: kc-okf-poc-261122.ga4_sample.events](about:sanitized) — the table's own BigQuery schema, read directly; the page STATES column names, types and modes from it