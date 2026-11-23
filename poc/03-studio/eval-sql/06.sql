SELECT SUM(ecommerce.purchase_revenue_in_usd) - SUM(IFNULL(ecommerce.refund_value_in_usd, 0)) AS net_merch_revenue_usd
FROM `kc-okf-poc-261122.ga4_sample.events`
WHERE event_date_dt BETWEEN '2020-12-01' AND '2020-12-31'
