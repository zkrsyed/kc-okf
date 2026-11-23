SELECT i.item_name, COUNT(*) AS added_to_cart_count
FROM `kc-okf-poc-261122.ga4_sample.events`, UNNEST(items) AS i
WHERE event_name = 'add_to_cart'
GROUP BY i.item_name ORDER BY added_to_cart_count DESC LIMIT 10
