SELECT event_date_dt, COUNT(*) AS purchases
FROM `kc-okf-poc-261122.ga4_sample.events`
WHERE event_name = 'purchase' AND event_date_dt BETWEEN '2021-01-01' AND '2021-01-07'
GROUP BY event_date_dt ORDER BY event_date_dt
