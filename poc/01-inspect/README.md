# Step 1: inspect the catalog, commands

```bash
# 1a. table sizes (metadata only, 0 bytes billed)
bq query --project_id=kc-okf-poc-261122 --use_legacy_sql=false --format=pretty 'SELECT COUNT(*) AS tables, MIN(table_id) AS first_table, MAX(table_id) AS last_table, SUM(row_count) AS total_rows, ROUND(SUM(size_bytes)/POW(1024,3),2) AS total_gb, ROUND(AVG(size_bytes)/POW(1024,2),1) AS avg_mb_per_table FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.__TABLES__`'
```

```bash
# 1b. our dataset
bq mk --location=US --dataset --description="GA4 public sample copied as one partitioned table, for the KC/OKF POC" kc-okf-poc-261122:ga4_sample
# 1c. one partitioned table, as in Google's kcmd demo (reads ~3.3 GB, about $0.02)
bq query --project_id=kc-okf-poc-261122 --use_legacy_sql=false 'CREATE TABLE IF NOT EXISTS `kc-okf-poc-261122.ga4_sample.events` PARTITION BY event_date_dt AS SELECT *, PARSE_DATE("%Y%m%d", event_date) AS event_date_dt FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`'
```

```bash
export CLOUDSDK_ACTIVE_CONFIG_NAME=kc-okf
# catalog search (finds our table, not the public ones)
gcloud dataplex entries search "events" --project=kc-okf-poc-261122 --format=json
gcloud dataplex entries search "ga4_obfuscated_sample_ecommerce" --project=kc-okf-poc-261122 --scope=projects/bigquery-public-data
# exact lookup works for public tables
gcloud dataplex entries lookup "bigquery.googleapis.com/projects/bigquery-public-data/datasets/ga4_obfuscated_sample_ecommerce/tables/events_20210131" --entry-group=@bigquery --location=us --project=bigquery-public-data --billing-project=kc-okf-poc-261122 --view=FULL --format=yaml
gcloud dataplex entries lookup "bigquery.googleapis.com/projects/kc-okf-poc-261122/datasets/ga4_sample/tables/events" --entry-group=@bigquery --location=us --project=kc-okf-poc-261122 --view=FULL --format=yaml
```

```bash
# 1h. kcmd snapshot (read-only)
mkdir -p results/01-inspect/kcmd-before && cd results/01-inspect/kcmd-before
CLOUDSDK_ACTIVE_CONFIG_NAME=kc-okf npx kcmd init --bigquery-dataset kc-okf-poc-261122.ga4_sample --pull
```
