# kcmd MCP probe: `results/03-studio/kcmd-okf`

Server: `{'name': 'kcmd', 'version': '1.0.0'}`

## tools/list

| Tool | Description | Inputs |
|---|---|---|
| `list-entries` | List names of all catalog entries. Each entry corresponds to a resource that has associated metadata. | `` |
| `lookup-entry` | Lookup the metadata of a specific catalog entry by name | `name` |
| `modify-entry` | Modify (either "resource" or an aspect key field) of a catalog entry by name | `name, field, updates` |

## list-entries (7 entries)

```json
[
  "agents",
  "assets",
  "documents",
  "documents/computing-standard-ecommerce-metrics",
  "documents/data-governance-and-quality-boundaries",
  "assets/bigquery/kc-okf-poc-261122/ga4_sample",
  "assets/bigquery/kc-okf-poc-261122/ga4_sample/events"
]
```

## lookup-entry `agents`

2,779 characters returned.

```json
{
  "name": "agents",
  "type": "dataplex-types.global.document",
  "resource": {
    "labels": {
      "generator": "enrichment_agent",
      "source": "knowledge_agent"
    },
    "location": "us"
  },
  "aspects": {
    "dataplex-types.global.document": {
      "job": {
        "name": "enrichment-agent/enrich-9eb2ed9719624d4e",
        "runTime": "2026-11-22T22:16:40Z"
      },
      "type": "context-set"
    },
    "dataplex-types.global.overview": {
      "content": "# GA4 Clickstream Analytics Guide\n\nIndex of the catalog root (2 item(s)).\n\n## What this is\n\nThis knowledge base covers Google Analytics 4 (GA4) clickstream events from the Google Merchandise Store, supporting analysis of user acquisition, session engagement, and e-commerce conversion performance. It documents the `kc-okf-poc-261122.ga4_sample.events` table (Merch Store Clickstream, dataset code `MSC-417`), also available in public BigQuery as `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`. The grain is one row per event, with nested records in `event_params`, `user_properties`, and `items` requiring unnesting. The dataset covers a fixed 92-day period from November 1, 2020, to January 31, 2021 (no new data will arrive), and revenue must be reported in USD using `ecommerce.purchase_revenue_in_usd` and `ecommerce.refund_value_in_usd`.\n\n## Top traps\n\n- **Queries scan entire tables instead of daily slices.** Filter on the table's designated partition column, `event_date_dt` (`DATE`).\n- **Data privacy violation on user identifiers.** `user_pseudo_id` is Tier C2 (pseudonymous) and must never be exported outside the analytics project or joined with CRM or external email lists.\n\n## How to navigate\n\nLook entries up by the ids below. A lookup returns only the entries it names -- a parent never arrives with its children -- so read this page for the id you want, then fetch that id.\n\n- `assets` — 1 table overlays, addressed as `assets/bigquery/<project>/<dataset>/<table>`. A dataset entry is its own index -- look the dataset up to see which tables it holds.\n- `documents` — 3 pages of knowledge rather than objects -- operational, one topic each.\n\nBudget about three searches and three lookups per question: search to find the right tier or dataset, then look up the two or three entries it names.\n\n## Contents\n\n| Path | Title | Type | Description |\n|------|-------|------|-------------|\n| catalog/assets | Assets | folder | Index of catalog/assets (1 item(s)). |\n| catalog/documents | Documents | folder | Cross-cutting reference pages for understand what each field means, how to query it correctly, and which business rules apply for analysts and AI agents: Analytics Guidelines and Operations. |",
      "contentType": "MARKDOWN"
    }
  }
}
```

## lookup-entry `assets/bigquery/kc-okf-poc-261122/ga4_sample/events`

6,239 characters returned.

```json
{
  "name": "assets/bigquery/kc-okf-poc-261122/ga4_sample/events",
  "type": "dataplex-types.global.document",
  "resource": {
    "labels": {
      "generator": "enrichment_agent",
      "source": "knowledge_agent"
    },
    "location": "us",
    "parent": "assets/bigquery/kc-okf-poc-261122/ga4_sample"
  },
  "aspects": {
    "dataplex-types.global.document": {
      "job": {
        "name": "enrichment-agent/enrich-9eb2ed9719624d4e",
        "runTime": "2026-11-22T22:16:40Z"
      },
      "type": "table-context"
    },
    "dataplex-types.global.overview": {
      "content": "# Events Overview\n\nThe table structure follows the Google Analytics 4 (GA4) event export format, storing user identifiers, nested event parameters, user properties, device specifications, geographic origins, traffic sources, and detailed e-commerce transaction payloads [1].\n\n## Purpose\n\nThe table provides granular event-level clickstream tracking for the merchandise store [1]. It is utilized for digital analytics, funnel analysis, user engagement tracking, and e-commerce conversion reporting [1].\n\n## Columns & Metrics\n\n### Schema Columns\n\n- **event_date** (`STRING`): Date of the event.\n- **event_timestamp** (`INTEGER`)\n- **event_name** (`STRING`): Name of the logged event (e.g., `add_to_cart`, `purchase`).\n- **event_params** (`RECORD`, repeated): Key-value parameters associated with the event, containing nested data types such as string, integer, float, and double values. Key parameters include `ga_session_id`, used in combination with `user_pseudo_id` to establish distinct browsing sessions [1].\n- **event_previous_timestamp** (`INTEGER`)\n- **event_value_in_usd** (`FLOAT`)\n- **event_bundle_sequence_id** (`INTEGER`)\n- **event_server_timestamp_offset** (`INTEGER`)\n- **user_id** (`STRING`)\n- **user_pseudo_id** (`STRING`)\n- **privacy_info** (`RECORD`): User privacy and consent states.\n- **user_properties** (`RECORD`, repeated): Repeated record holding persistent user-level properties and attributes.\n- **user_first_touch_timestamp** (`INTEGER`): Timestamp marking the first time the user interacted with the site.\n- **user_ltv** (`RECORD`): Lifetime value metrics for the user.\n- **device** (`RECORD`): Hardware and browser specifications, including device category, brand, and model details.\n- **geo** (`RECORD`)\n- **app_info** (`RECORD`)\n- **traffic_source** (`RECORD`): Source, medium, and campaign details associated with how the user arrived at the site [1].\n- **stream_id** (`INTEGER`)\n- **platform** (`STRING`)\n- **event_dimensions** (`RECORD`)\n- **ecommerce** (`RECORD`): E-commerce purchase, revenue, and refund attributes, including `purchase_revenue_in_usd` and `refund_value_in_usd` [1].\n- **items** (`RECORD`, repeated): Repeated record containing product and item-level details associated with e-commerce events.\n- **event_date_dt** (`DATE`): Date-typed event date column configured as the table's partition column [1].\n\n### Official Metric Definitions\n\n- **Engaged session**: A browsing session that lasted longer than 10 seconds, recorded 2 or more page views, or contained a purchase event [1]. Sessions are identified by combining `user_pseudo_id` with the `ga_session_id` value extracted from `event_params` [1].\n- **Active buyer (28d)**: A unique `user_pseudo_id` having at least one logged `purchase` event within the trailing 28 days [1].\n- **Net merch revenue**: Calculated as the sum of `ecommerce.purchase_revenue_in_usd` minus the sum of `ecommerce.refund_value_in_usd` [1]. Official metrics must always be reported in USD and must not use local-currency fields [1].\n- **Cart conversion rate**: Total count of sessions containing a `purchase` event divided by the total count of sessions containing an `add_to_cart` event [1].\n\n## Lineage\n\nThe dataset is populated as a copy of the public GA4 sample e-commerce export [1].\n\n## Owner\n\n- **Owning team**: Digital Insights Guild [1]\n- **Dataset reference code**: MSC-417 [1]\n- **Data steward**: Digital Insights Guild on-call steward (contact channel: `#msc-417-data`) [1]\n\n## Governance\n\n- **Sensitivity Classifications**:\n  - `user_pseudo_id`: Classified as **Tier C2 (pseudonymous)**. It must never be exported outside the analytics project and must never be joined with CRM or external email lists [1].\n  - `geo.city` and `geo.metro`: Classified as **Tier C3 (restricted)**. Reporting is permitted only when aggregated to the region or country level; dashboard reporting at the city or metro level is prohibited [1].\n  - `device.*`, `traffic_source.*`, and all other columns: Classified as **Tier C1 (internal)** with standard internal access policies [1].\n- **Retention**: Rows older than 14 months must be purged by the Digital Insights Guild [1].\n- **Refresh & Finality SLA**: The table is loaded once per day; daily data is considered final 72 hours after the calendar day ends [1]. Reporting must not treat data from the most recent 3 days as final numbers [1].\n\n## Data Quality\n\n- **Total Row Count**: The table contains 4,295,584 rows.\n- **Time Horizon**: The dataset covers a fixed historical span of 92 days, running from 2020-11-01 through 2021-01-31 [1]. No newer records will be ingested [1].\n\n## Usage\n\n- **Partition Pruning**: Queries must always filter on the partition column `event_date_dt` to restrict scanned bytes and limit query cost [1].\n- **Marketing Attribution Exclusions**: Any event where `traffic_source.source` is equal to `(data deleted)` must be excluded from marketing attribution analyses [1].\n- **Geographic Aggregations**: Because `geo.city` and `geo.metro` fall under Tier C3 restrictions, dashboard creators and analysts must aggregate geographic metrics up to `geo.region` or `geo.country` [1].\n- **Session Identification**: Because individual events do not carry a top-level session key, analysts must unnest `event_params` to locate `ga_session_id`, concatenating it with `user_pseudo_id` to evaluate session-level engagement and conversion rates [1].\n\n## Table Info\n\n`kc-okf-poc-261122.ga4_sample.events`\n\n## Source References\n1. Merch Store Clickstream: data policy and metric definitions",
      "contentType": "MARKDOWN"
    }
  }
}
```
