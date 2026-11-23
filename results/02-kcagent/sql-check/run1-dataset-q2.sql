SELECT 
  event_date, 
  COUNT(DISTINCT user_pseudo_id) as active_users 
FROM 
  `kc-okf-poc-261122.ga4_sample` 
WHERE 
  event_date_dt BETWEEN PARSE_DATE('%Y%m%d', '20201201') AND PARSE_DATE('%Y%m%d', '20201231') 
GROUP BY 
  event_date 
ORDER BY 
  event_date ASC
