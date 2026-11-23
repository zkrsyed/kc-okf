SELECT event_date_dt, SUM(ecommerce.purchase_revenue_in_usd) - SUM(IFNULL(ecommerce.refund_value_in_usd, 0)) AS net_merch_revenue_usd
FROM `kc-okf-poc-261122.ga4_sample.events`
WHERE event_date_dt BETWEEN '2021-01-01' AND DATE_SUB('2021-01-31', INTERVAL 3 DAY)
GROUP BY event_date_dt ORDER BY event_date_dt
