SELECT (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'page_location') AS page_location, COUNT(*) AS page_views
FROM `kc-okf-poc-261122.ga4_sample.events`
WHERE event_name = 'page_view' AND event_date_dt = '2021-01-15'
GROUP BY page_location ORDER BY page_views DESC LIMIT 20
