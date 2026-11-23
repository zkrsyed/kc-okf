SELECT COUNT(DISTINCT user_pseudo_id) AS active_buyers_28d
FROM `kc-okf-poc-261122.ga4_sample.events`
WHERE event_name = 'purchase' AND event_date_dt BETWEEN DATE_SUB('2021-01-31', INTERVAL 27 DAY) AND '2021-01-31'
