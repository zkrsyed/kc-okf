SELECT event_date_dt, COUNT(DISTINCT user_pseudo_id) AS active_users
FROM `kc-okf-poc-261122.ga4_sample.events`
WHERE event_date_dt BETWEEN '2020-12-01' AND '2020-12-31'
GROUP BY event_date_dt ORDER BY event_date_dt
