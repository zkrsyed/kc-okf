WITH s AS (
  SELECT user_pseudo_id, (SELECT value.int_value FROM UNNEST(event_params) WHERE key = 'ga_session_id') AS session_id,
         COUNTIF(event_name = 'purchase') > 0 AS has_purchase,
         COUNTIF(event_name = 'add_to_cart') > 0 AS has_add_to_cart
  FROM `kc-okf-poc-261122.ga4_sample.events`
  WHERE event_date_dt BETWEEN '2020-12-01' AND '2020-12-31'
  GROUP BY 1, 2)
SELECT SAFE_DIVIDE(COUNTIF(has_purchase), COUNTIF(has_add_to_cart)) AS cart_conversion_rate FROM s
