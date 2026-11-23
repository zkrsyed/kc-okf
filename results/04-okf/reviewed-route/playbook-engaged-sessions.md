# Playbook: count engaged sessions

Hand-written by the data team (POC step 4, submitted as a reviewed change request). Follow this when a question asks how many sessions were "engaged" in a period.

## When to use

"How many engaged sessions in January?", "engaged session count by month", "share of sessions that were engaged".

## Approach

1. A session is `user_pseudo_id` + the `ga_session_id` value from `event_params` (`value.int_value`). Never count `ga_session_id` alone: different users can share a value.
2. Engaged = lasted more than 10 seconds (max minus min `event_timestamp`, in microseconds, divided by 1e6), **or** 2 or more `page_view` events, **or** at least one `purchase`.
3. Filter on the partition column `event_date_dt`.

## SQL

```sql
WITH s AS (
  SELECT user_pseudo_id,
         (SELECT value.int_value FROM UNNEST(event_params) WHERE key = 'ga_session_id') AS session_id,
         (MAX(event_timestamp) - MIN(event_timestamp)) / 1e6 AS duration_s,
         COUNTIF(event_name = 'page_view') AS page_views,
         COUNTIF(event_name = 'purchase') AS purchases
  FROM `kc-okf-poc-261122.ga4_sample.events`
  WHERE event_date_dt BETWEEN '2021-01-01' AND '2021-01-31'
  GROUP BY 1, 2)
SELECT COUNTIF(duration_s > 10 OR page_views >= 2 OR purchases > 0) AS engaged_sessions
FROM s
```
