SELECT geo.country, geo.region, COUNT(DISTINCT user_pseudo_id) AS users
FROM `kc-okf-poc-261122.ga4_sample.events`
WHERE event_date_dt BETWEEN '2021-01-01' AND '2021-01-31'
GROUP BY geo.country, geo.region ORDER BY users DESC
