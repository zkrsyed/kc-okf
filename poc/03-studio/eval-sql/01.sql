SELECT COUNT(DISTINCT CONCAT(user_pseudo_id, CAST(p.value.int_value AS STRING))) AS total_sessions
FROM `kc-okf-poc-261122.ga4_sample.events`, UNNEST(event_params) AS p
WHERE event_name = 'session_start' AND p.key = 'ga_session_id'
