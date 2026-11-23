---
type: context-set
x-kcmd:
  v: 1
  entryType: projects/dataplex-types/locations/global/entryTypes/document
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
# GA4 Clickstream Analytics Guide

Index of the catalog root (2 item(s)).

## What this is

This knowledge base covers Google Analytics 4 (GA4) clickstream events from the Google Merchandise Store, supporting analysis of user acquisition, session engagement, and e-commerce conversion performance. It documents the `kc-okf-poc-261122.ga4_sample.events` table (Merch Store Clickstream, dataset code `MSC-417`), also available in public BigQuery as `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`. The grain is one row per event, with nested records in `event_params`, `user_properties`, and `items` requiring unnesting. The dataset covers a fixed 92-day period from November 1, 2020, to January 31, 2021 (no new data will arrive), and revenue must be reported in USD using `ecommerce.purchase_revenue_in_usd` and `ecommerce.refund_value_in_usd`.

## Top traps

- **Queries scan entire tables instead of daily slices.** Filter on the table's designated partition column, `event_date_dt` (`DATE`).
- **Data privacy violation on user identifiers.** `user_pseudo_id` is Tier C2 (pseudonymous) and must never be exported outside the analytics project or joined with CRM or external email lists.

## How to navigate

Look entries up by the ids below. A lookup returns only the entries it names -- a parent never arrives with its children -- so read this page for the id you want, then fetch that id.

- `assets` — 1 table overlays, addressed as `assets/bigquery/<project>/<dataset>/<table>`. A dataset entry is its own index -- look the dataset up to see which tables it holds.
- `documents` — 3 pages of knowledge rather than objects -- operational, one topic each.

Budget about three searches and three lookups per question: search to find the right tier or dataset, then look up the two or three entries it names.

## Contents

| Path | Title | Type | Description |
|------|-------|------|-------------|
| catalog/assets | Assets | folder | Index of catalog/assets (1 item(s)). |
| catalog/documents | Documents | folder | Cross-cutting reference pages for understand what each field means, how to query it correctly, and which business rules apply for analysts and AI agents: Analytics Guidelines and Operations. |
