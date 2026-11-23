SELECT 
  COUNT(*) AS total_events, 
  COUNT(DISTINCT user_pseudo_id) AS total_unique_users, 
  COUNT(DISTINCT event_date) AS total_days
FROM 
  `kc-okf-poc-261122.ga4_sample.events`
