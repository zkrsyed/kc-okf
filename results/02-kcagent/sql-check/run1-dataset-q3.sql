SELECT 
  COUNT(DISTINCT value.int_value) AS total_sessions
FROM 
  `kc-okf-poc-261122.ga4_sample`, 
  UNNEST(event_params) 
WHERE 
  event_name = 'session_start' 
  AND key = 'ga_session_id'
