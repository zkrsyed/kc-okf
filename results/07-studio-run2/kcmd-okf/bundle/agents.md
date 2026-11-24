---
type: knowledge-base-root
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
        name: enrichment-agent/enrich-7939c61dc2724775
        runTime: 2026-11-24T19:45:19Z
---
# Merch Store Clickstream Knowledge Base

Index of the catalog root (2 item(s)).

## What this is

This knowledge base covers digital merchandising, e-commerce clickstream tracking, user journeys, conversion funnels, and marketing attribution across `kc-okf-poc-261122.ga4_sample.events` (governance code `MSC-417`, copied from `bigquery-public-data.ga4_obfuscated_sample_ecommerce`). Each row represents a single clickstream event, with session identifiers nested inside `event_params` and product interactions stored in the `items` array. Data coverage is a fixed 92-day historical benchmark spanning November 1, 2020, to January 31, 2021, with no incoming data. Monetary metrics are strictly reported in USD via dedicated columns like `ecommerce.purchase_revenue_in_usd`, while sequence timestamps such as `event_previous_timestamp` are recorded in microseconds.

## Top traps

- **Time interval calculations are off by a factor of one million.** The `event_previous_timestamp` field is an integer stored in microseconds.
- **Queries for recent dates return zero rows.** Dataset MSC-417 is a fixed historical benchmark covering 2020-11-01 through 2021-01-31 only.

## How to navigate

Look entries up by the ids below. A lookup returns only the entries it names -- a parent never arrives with its children -- so read this page for the id you want, then fetch that id.

- `assets` — 1 table overlays, addressed as `assets/bigquery/<project>/<dataset>/<table>`. A dataset entry is its own index -- look the dataset up to see which tables it holds.
- `documents` — 2 pages of knowledge rather than objects -- operational, one topic each.

Budget about three searches and three lookups per question: search to find the right tier or dataset, then look up the two or three entries it names.

## Contents

| Path | Title | Type | Description |
|------|-------|------|-------------|
| catalog/assets | Assets | folder | Index of catalog/assets (1 item(s)). |
| catalog/documents | Documents | folder | Cross-cutting reference pages for Document column descriptions, sensitivity tiers, and personal data flags for the events table, and define business glossary terms and data rules from the data policy: Analytics Operations. |
