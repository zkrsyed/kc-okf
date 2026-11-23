SELECT traffic_source.source, COUNT(*) AS sessions
FROM `kc-okf-poc-261122.ga4_sample.events`
WHERE event_name = 'session_start' AND event_date_dt BETWEEN '2021-01-01' AND '2021-01-31'
  AND traffic_source.source != '(data deleted)'
GROUP BY traffic_source.source ORDER BY sessions DESC
