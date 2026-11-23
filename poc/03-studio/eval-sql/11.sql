WITH s AS (
  SELECT user_pseudo_id, (SELECT value.int_value FROM UNNEST(event_params) WHERE key = 'ga_session_id') AS session_id,
         (MAX(event_timestamp) - MIN(event_timestamp)) / 1e6 AS duration_s,
         COUNTIF(event_name = 'page_view') AS page_views,
         COUNTIF(event_name = 'purchase') AS purchases
  FROM `kc-okf-poc-261122.ga4_sample.events`
  WHERE event_date_dt BETWEEN '2021-01-01' AND '2021-01-31'
  GROUP BY 1, 2)
SELECT COUNTIF(duration_s > 10 OR page_views >= 2 OR purchases > 0) AS engaged_sessions FROM s
