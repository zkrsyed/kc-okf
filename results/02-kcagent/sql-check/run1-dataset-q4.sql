SELECT 
  items.item_name, 
  COUNT(*) AS added_to_cart_count 
FROM 
  `kc-okf-poc-261122.ga4_sample`, 
  UNNEST(items) AS items
WHERE 
  event_name = 'add_to_cart' 
GROUP BY 
  items.item_name 
ORDER BY 
  added_to_cart_count DESC 
LIMIT 10
